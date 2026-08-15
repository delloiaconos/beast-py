from __future__ import annotations

import numpy as np

from beast.io.binary import (
    read_float64_matrix,
    read_float64_matrix_with_n_columns,
    write_float64_matrix,
)


def test_matrix_binary_order_matches_matlab(tmp_path):
    matrix = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    path = tmp_path / "matrix.bin"

    assert write_float64_matrix(matrix, path) == 6
    raw = np.fromfile(path, dtype=np.float64)
    np.testing.assert_array_equal(raw, np.array([1.0, 4.0, 2.0, 5.0, 3.0, 6.0]))
    np.testing.assert_array_equal(read_float64_matrix(path, 2, 3), matrix)
    np.testing.assert_array_equal(read_float64_matrix_with_n_columns(path, 3), matrix)


def test_matrix_reader_rejects_incompatible_shape(tmp_path):
    path = tmp_path / "bad.bin"
    np.arange(5.0).tofile(path)
    try:
        read_float64_matrix_with_n_columns(path, 2)
    except ValueError as exc:
        assert "not divisible" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
