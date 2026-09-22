"""Legacy MATLAB interoperability helpers.

This module contains compatibility code whose purpose is to read data produced
by the original MATLAB BEAST workflow or reproduce its binary file layout.
New numerical model and estimator code should not depend on this module unless
MATLAB interoperability is explicitly required.
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np

from beast.cell_models.cell_model import CellModel
from beast.core.arrays import FloatArray, IntArray

Pathish = str | PathLike[str]


def _existing_file(filename: Pathish) -> Path:
    path = Path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"Binary file not found: {path}")
    return path


def read_float64_vector(filename: Pathish) -> FloatArray:
    """Read all native-endian IEEE-754 doubles from a MATLAB binary file."""

    path = _existing_file(filename)
    return np.array(np.fromfile(path, dtype=np.float64), copy=True)


def read_int32_vector(filename: Pathish) -> IntArray:
    """Read all native-endian signed 32-bit integers from a MATLAB binary file."""

    path = _existing_file(filename)
    return np.array(np.fromfile(path, dtype=np.int32), copy=True)


def read_float64_matrix(filename: Pathish, rows: int, columns: int) -> FloatArray:
    """Read a fixed-size matrix written by MATLAB ``fwrite``."""

    if rows <= 0 or columns <= 0:
        raise ValueError("rows and columns must be positive")
    vector = read_float64_vector(filename)
    expected = rows * columns
    if vector.size != expected:
        raise ValueError(
            f"{filename} contains {vector.size} doubles; expected {expected} "
            f"for shape ({rows}, {columns})"
        )
    return vector.reshape((rows, columns), order="F")


def read_float64_matrix_with_n_columns(filename: Pathish, columns: int) -> FloatArray:
    """Read a MATLAB matrix when the number of columns is known."""

    if columns <= 0:
        raise ValueError("columns must be positive")
    vector = read_float64_vector(filename)
    if vector.size % columns != 0:
        raise ValueError(
            f"{filename} contains {vector.size} doubles, not divisible by {columns} columns"
        )
    return vector.reshape((vector.size // columns, columns), order="F")


def read_square_float64_matrix(filename: Pathish) -> FloatArray:
    """Read a square matrix in the format used by ``BINimport_MATdouble.m``."""

    vector = read_float64_vector(filename)
    size = int(round(np.sqrt(vector.size)))
    if size * size != vector.size:
        raise ValueError(f"{filename} does not contain a square number of doubles")
    return vector.reshape((size, size), order="F")


def write_float64_matrix(matrix: Any, filename: Pathish) -> int:
    """Write values using MATLAB ``fwrite`` column-major ordering."""

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.asarray(matrix, dtype=np.float64)
    flat = np.ravel(array, order="F")
    flat.tofile(path)
    return int(flat.size)


def write_int32_matrix(matrix: Any, filename: Pathish) -> int:
    """Write signed 32-bit integers using MATLAB column-major ordering."""

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.asarray(matrix, dtype=np.int32)
    flat = np.ravel(array, order="F")
    flat.tofile(path)
    return int(flat.size)


def init_CellModel(
    basepath: str | Path,
    selector: str,
    prefix: str = "MD",
    binary_extension: str = ".in",
) -> CellModel:
    """Load legacy MATLAB model files and instantiate a BEAST cell model.

    This function is the Python counterpart of the original ``CellModelInit.m``
    workflow. It remains camel-cased intentionally because it is part of the
    MATLAB compatibility layer.

    Args:
        basepath: Directory containing ``<prefix>_pfix_*`` and covariance files.
        selector: Cell-model selector such as ``"R0R1C1"``.
        prefix: Legacy file prefix, usually ``"MD"``.
        binary_extension: Extension used by the legacy binary files.
    """

    from beast.cell_models.factory import selectCellModel

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


__all__ = [
    "init_CellModel",
    "read_float64_vector",
    "read_int32_vector",
    "read_float64_matrix",
    "read_float64_matrix_with_n_columns",
    "read_square_float64_matrix",
    "write_float64_matrix",
    "write_int32_matrix",
]
