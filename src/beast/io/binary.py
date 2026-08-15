"""MATLAB-compatible binary vector and matrix I/O.

MATLAB's ``fwrite`` serializes matrices in column-major order.  NumPy uses
row-major order by default, so every matrix writer in this module explicitly
flattens with ``order='F'`` and every reader reshapes with the same order.
This detail is required for byte-level interoperability with the original
``*.in`` and ``*.out`` files.
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np

from beast.core.arrays import FloatArray, IntArray

Pathish = str | PathLike[str]


def _existing_file(filename: Pathish) -> Path:
    path = Path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"Binary file not found: {path}")
    return path


def read_float64_vector(filename: Pathish) -> FloatArray:
    """Read all native-endian IEEE-754 doubles from a binary file."""

    path = _existing_file(filename)
    return np.array(np.fromfile(path, dtype=np.float64), copy=True)


def read_int32_vector(filename: Pathish) -> IntArray:
    """Read all native-endian signed 32-bit integers from a binary file."""

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
    """Read a matrix when the sample count (column count) is known."""

    if columns <= 0:
        raise ValueError("columns must be positive")
    vector = read_float64_vector(filename)
    if vector.size % columns != 0:
        raise ValueError(
            f"{filename} contains {vector.size} doubles, not divisible by {columns} columns"
        )
    return vector.reshape((vector.size // columns, columns), order="F")


def read_square_float64_matrix(filename: Pathish) -> FloatArray:
    """Read a square matrix, reproducing ``BINimport_MATdouble.m``."""

    vector = read_float64_vector(filename)
    size = int(round(np.sqrt(vector.size)))
    if size * size != vector.size:
        raise ValueError(f"{filename} does not contain a square number of doubles")
    return vector.reshape((size, size), order="F")


def write_float64_matrix(matrix: Any, filename: Pathish) -> int:
    """Write a scalar, vector, or matrix in MATLAB column-major order.

    Returns:
        Number of ``float64`` values written.
    """

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.asarray(matrix, dtype=np.float64)
    flat = np.ravel(array, order="F")
    flat.tofile(path)
    return int(flat.size)


def write_int32_matrix(matrix: Any, filename: Pathish) -> int:
    """Write signed 32-bit integers in MATLAB column-major order."""

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.asarray(matrix, dtype=np.int32)
    flat = np.ravel(array, order="F")
    flat.tofile(path)
    return int(flat.size)

