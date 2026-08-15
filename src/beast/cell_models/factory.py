"""Cell-model selection and binary initialization factories."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, TypeAlias

import numpy as np

from beast.cell_models.base import CellModel
from beast.cell_models.h0f0a import CellModel_H0F0A
from beast.cell_models.r0a1b1 import CellModel_R0A1B1
from beast.cell_models.r0r1c1 import CellModel_R0R1C1
from beast.cell_models.r0r1c1r2c2 import CellModel_R0R1C1R2C2
from beast.cell_models.r0r1t1 import CellModel_R0R1T1
from beast.io.binary import read_float64_vector

CellModelClass: TypeAlias = type[CellModel]

CELL_MODEL_REGISTRY: dict[str, CellModelClass] = {
    "H0F0A": CellModel_H0F0A,
    "R0A1B1": CellModel_R0A1B1,
    "R0R1C1": CellModel_R0R1C1,
    "R0R1C1R2C2": CellModel_R0R1C1R2C2,
    "R0R1T1": CellModel_R0R1T1,
}


def selectCellModel(selector: str) -> CellModelClass:
    """Return the model class selected by a MATLAB-style name.

    Raises:
        ValueError: If no converted model matches the selector.
    """

    normalized = selector.strip().upper()
    if normalized.startswith("CELLMODEL_"):
        normalized = normalized.removeprefix("CELLMODEL_")
    try:
        return CELL_MODEL_REGISTRY[normalized]
    except KeyError as exc:
        choices = ", ".join(sorted(CELL_MODEL_REGISTRY))
        raise ValueError(f"Unknown cell model {selector!r}; choose one of {choices}") from exc


def createCellModel(
    selector: str,
    cell_model_data: Mapping[str, Any] | Any,
    covariance: Mapping[str, Any] | Any,
    delta_t: float,
) -> CellModel:
    """Instantiate a selected model from in-memory data."""

    return selectCellModel(selector)(cell_model_data, covariance, delta_t)


def initCellModel(
    basepath: str | Path,
    selector: str,
    prefix: str = "MD",
    binary_extension: str = ".in",
) -> CellModel:
    """Load legacy binary model data and instantiate a model.

    This is the direct Python counterpart of ``CellModelInit.m``.

    Args:
        basepath: Directory containing ``<prefix>_pfix_*.in`` and covariance
            files.
        selector: Model selector such as ``"R0R1C1"``.
        prefix: File prefix, usually ``"MD"``.
        binary_extension: Extension used by fixed-data and covariance files.
    """

    base = Path(basepath)
    extension = (
        binary_extension
        if binary_extension.startswith(".")
        else f".{binary_extension}"
    )
    model_class = selectCellModel(selector)
    model_data = {
        required: read_float64_vector(base / f"{prefix}_pfix_{required}{extension}")
        for required in model_class.Required
    }
    covariance = {
        "spE": np.diag(read_float64_vector(base / f"{prefix}_COV_spEvec{extension}")),
        "spR": np.diag(read_float64_vector(base / f"{prefix}_COV_spRvec{extension}")),
        "sxV": np.diag(read_float64_vector(base / f"{prefix}_COV_sxVvec{extension}")),
        "sxW": np.diag(read_float64_vector(base / f"{prefix}_COV_sxWvec{extension}")),
    }
    delta_values = read_float64_vector(base / f"{prefix}_deltat{extension}")
    if delta_values.size == 0:
        raise ValueError(f"{prefix}_deltat{extension} is empty")
    return model_class(model_data, covariance, float(delta_values[0]))
