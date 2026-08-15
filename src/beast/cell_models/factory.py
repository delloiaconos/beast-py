"""Cell-model registry and in-memory construction helpers."""

from __future__ import annotations

from typing import Any, Mapping, TypeAlias

from beast.cell_models.base import CellModel
from beast.cell_models.h0f0a import CellModel_H0F0A
from beast.cell_models.r0a1b1 import CellModel_R0A1B1
from beast.cell_models.r0r1c1 import CellModel_R0R1C1
from beast.cell_models.r0r1c1r2c2 import CellModel_R0R1C1R2C2
from beast.cell_models.r0r1t1 import CellModel_R0R1T1

CellModelClass: TypeAlias = type[CellModel]

CELL_MODEL_REGISTRY: dict[str, CellModelClass] = {
    "H0F0A": CellModel_H0F0A,
    "R0A1B1": CellModel_R0A1B1,
    "R0R1C1": CellModel_R0R1C1,
    "R0R1C1R2C2": CellModel_R0R1C1R2C2,
    "R0R1T1": CellModel_R0R1T1,
}


def selectCellModel(selector: str) -> CellModelClass:
    """Return the model class selected by name.

    Raises:
        ValueError: If no registered model matches the selector.
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


# Backward-compatible import. MATLAB-specific implementation lives in beast.legacy.matlab.
from beast.legacy.matlab import init_CellModel as initCellModel
