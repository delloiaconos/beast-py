from __future__ import annotations

import numpy as np
import pytest

from beast.cell_models import (
    CellModel_H0F0A,
    CellModel_R0A1B1,
    CellModel_R0R1C1,
    CellModel_R0R1C1R2C2,
    CellModel_R0R1T1,
)
from conftest import covariance_for


CASES = [
    (CellModel_H0F0A, np.array([0.7]), np.array([0.01])),
    (CellModel_R0A1B1, np.array([0.7, -0.02]), np.array([0.01, 0.95, -0.001])),
    (CellModel_R0R1C1, np.array([0.7, -0.02]), np.array([0.01, 0.02, 1000.0])),
    (
        CellModel_R0R1C1R2C2,
        np.array([0.7, -0.02, -0.01]),
        np.array([0.01, 0.02, 1000.0, 0.03, 2000.0]),
    ),
    (CellModel_R0R1T1, np.array([0.7, -0.02]), np.array([0.01, 0.02, 20.0])),
]


def finite_difference(function, value, epsilon=1.0e-6):
    base = np.asarray(value, dtype=float)
    result0 = np.asarray(function(base), dtype=float)
    jacobian = np.zeros((result0.size, base.size))
    for index in range(base.size):
        plus = base.copy(); plus[index] += epsilon
        minus = base.copy(); minus[index] -= epsilon
        jacobian[:, index] = (function(plus) - function(minus)) / (2.0 * epsilon)
    return jacobian


@pytest.mark.parametrize("model_class,x,p", CASES)
def test_model_shapes_and_jacobians(model_data, model_class, x, p):
    model = model_class(model_data, covariance_for(model_class), 1.0)
    u = np.array([1.5])

    assert model.f0(x, p, u).shape == (model.Nx,)
    assert model.g0(x, p, u).shape == (model.Ny,)
    assert model.f1x(x, p, u).shape == (model.Nx, model.Nx)
    assert model.f1p(x, p, u).shape == (model.Nx, model.Np)
    assert model.g1x(x, p, u).shape == (model.Ny, model.Nx)
    assert model.g1p(x, p, u).shape == (model.Ny, model.Np)

    fd_f_x = finite_difference(lambda trial: model.f0(trial, p, u), x)
    fd_f_p = finite_difference(lambda trial: model.f0(x, trial, u), p)
    fd_g_x = finite_difference(lambda trial: model.g0(trial, p, u), x)
    fd_g_p = finite_difference(lambda trial: model.g0(x, trial, u), p)

    np.testing.assert_allclose(model.f1x(x, p, u), fd_f_x, rtol=1e-5, atol=1e-7)
    np.testing.assert_allclose(model.f1p(x, p, u), fd_f_p, rtol=2e-4, atol=1e-7)
    np.testing.assert_allclose(model.g1x(x, p, u), fd_g_x, rtol=1e-5, atol=1e-7)
    np.testing.assert_allclose(model.g1p(x, p, u), fd_g_p, rtol=1e-5, atol=1e-7)


@pytest.mark.parametrize("model_class,x,p", CASES)
def test_soc_is_clipped(model_class, x, p):
    high = x.copy(); high[0] = 1.5
    low = x.copy(); low[0] = -0.5
    with pytest.warns(RuntimeWarning):
        assert model_class.coerce_state(high)[0] == 1.0
    with pytest.warns(RuntimeWarning):
        assert model_class.coerce_state(low)[0] == 0.0


def test_parameter_coercion_repairs_matlab_static_method_bug():
    with pytest.warns(RuntimeWarning):
        corrected = CellModel_R0R1T1.coerce_parameters([-1.0, -2.0, -3.0])
    assert np.all(corrected > 0.0)
