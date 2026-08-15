"""Compatibility helpers for legacy BEAST workflows."""

from beast.legacy.matlab import (
    init_CellModel,
    read_float64_matrix,
    read_float64_matrix_with_n_columns,
    read_float64_vector,
    read_int32_vector,
    read_square_float64_matrix,
    write_float64_matrix,
    write_int32_matrix,
)

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
