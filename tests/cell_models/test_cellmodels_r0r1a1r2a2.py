"""Numerical tests for the discrete two-branch R0R1A1R2A2 model."""

from __future__ import annotations

import numpy as np
import pytest

from beast.cell_models import R0R1A1R2A2
from conftest import covariance_for


def test_r0r1a1r2a2_equations_match_matlab_reference(model_data):
    model = R0R1A1R2A2(
        model_data,
        covariance_for(R0R1A1R2A2),
        1.0,
    )
    x = np.array([0.8, -0.1, -0.2])
    p = np.array([0.01, 0.02, 0.9, 0.03, 0.8])
    u = np.array([2.0])

    expected_state = np.array(
        [
            0.8 - (0.99 / (2.0 * 3600.0)) * 2.0,
            0.9 * -0.1 + 0.02 * (0.9 - 1.0) * 2.0,
            0.8 * -0.2 + 0.03 * (0.8 - 1.0) * 2.0,
        ]
    )
    expected_output = np.array([3.0 + 1.2 * 0.8 - 0.01 * 2.0 - 0.1 - 0.2])

    np.testing.assert_allclose(model.f0(x, p, u), expected_state)
    np.testing.assert_allclose(model.g0(x, p, u), expected_output)


def test_r0r1a1r2a2_parameter_coercion_matches_matlab_bounds():
    with pytest.warns(RuntimeWarning):
        corrected = R0R1A1R2A2.coerce_parameters(
            [-1.0, 0.0, 0.0, -2.0, 1.0]
        )

    np.testing.assert_array_equal(
        corrected,
        np.array(
            [
                R0R1A1R2A2.zerohere,
                R0R1A1R2A2.zerohere,
                R0R1A1R2A2.zerohere,
                R0R1A1R2A2.zerohere,
                1.0 - R0R1A1R2A2.zerohere,
            ]
        ),
    )


def test_r0r1a1r2a2_rejects_wrong_parameter_dimension():
    with pytest.raises(ValueError, match="parameters must have length 5"):
        R0R1A1R2A2.coerce_parameters([0.01, 0.02, 0.9])
