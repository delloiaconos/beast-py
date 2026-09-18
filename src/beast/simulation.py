"""Model simulation utility."""

from __future__ import annotations

from typing import Any

import numpy as np

from beast.cell_models.base import CellModel
from beast.core.arrays import FloatArray, as_float_vector, as_history_matrix

def simulate_model(
    model: CellModel,
    *,
    t_all: Any,
    u_all: Any,
    x0: Any,
    p0: Any,
    delta_t: float,
) -> tuple[FloatArray, FloatArray]:
    """Generate state and output histories without an estimator.

    The state and output stored at sample ``k`` are evaluated before the state
    is advanced, matching ``TSim.m``.
    """

    time = as_float_vector(t_all, name="t_all")
    inputs = as_history_matrix(u_all, name="u_all")
    state = as_float_vector(x0, name="x0")
    parameters = as_float_vector(p0, name="p0")
    if inputs.shape != (model.Nu, time.size):
        raise ValueError(
            f"u_all must have shape ({model.Nu}, {time.size}), got {inputs.shape}"
        )
    
    if state.size != model.Nx or parameters.size != model.Np:
        raise ValueError("Initial state or parameter dimensions do not match the model")

    x_all = np.zeros((model.Nx, time.size), dtype=np.float64)
    y_all = np.zeros((model.Ny, time.size), dtype=np.float64)
    for index in range(time.size):
        u = inputs[:, index]
        x_all[:, index] = state
        y_all[:, index] = model.g0(state, parameters, u, delta_t)
        state = model.coerce_state(model.f0(state, parameters, u, delta_t))
    
    return x_all, y_all
