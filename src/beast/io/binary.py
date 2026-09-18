"""Backward-compatible imports for MATLAB binary I/O.

MATLAB-specific binary interoperability now lives in :mod:`beast.legacy.matlab`.
This module is retained as a compatibility import path.
"""

from beast.legacy.matlab import (
    read_float64_matrix,
    read_float64_matrix_with_n_columns,
    read_float64_vector,
    read_int32_vector,
    read_square_float64_matrix,
    write_float64_matrix,
    write_int32_matrix,
)

__all__ = [
    "read_float64_vector",
    "read_int32_vector",
    "read_float64_matrix",
    "read_float64_matrix_with_n_columns",
    "read_square_float64_matrix",
    "write_float64_matrix",
    "write_int32_matrix",
]
