"""Run a simulation on a synthetic battery profile using the ESC model.

Execute from an installed project with::

    python examples/synthetic_esc_run.py
"""

from __future__ import annotations

import numpy as np

from beast.cell_models.esc import CellModel_ESC
from beast.simulation import simulate_model


def main() -> None:
    """Build plain NumPy data, run the simulation, and print final outputs."""

    delta_t = 1.0
    soc_grid = np.linspace(0.0, 1.0, 101)
    
    model_data = {
        "Qn_Ah": np.array([1.1]),
        "eta": np.array([1.0]),
        "soc": soc_grid,
        "ocv0": 2.8 + 0.8 * soc_grid,  
        "ocv1": np.full_like(soc_grid, 0.8),
    }

    covariance = {
        "sxW": np.diag([1.0e-8, 1.0e-8, 1.0e-8, 1.0e-8]),
        "sxV": np.diag([1.0e-5]),
        "spR": np.diag([1.0e-10] * 6),
        "spE": np.diag([1.0e-5]),
    }
    
    model = CellModel_ESC(model_data, covariance, delta_t)

    time = np.arange(300.0)
    current = np.zeros((1, time.size), dtype=np.float64)
    current[0, 20:220] = 1.0
    current[0, 240:280] = -0.5

    # [SOC, h, s, vC1]
    true_x0 = np.array([0.90, 0.0, 0.0, 0.0])

    # [R0, R1, C1, gamma, M, M0]
    true_parameters = np.array([0.157, 0.0511, 1750.0, 1.2, 0.100, 0.0067])

    x, y = simulate_model(
        model,
        t_all=time,
        u_all=current,
        x0=true_x0,
        p0=true_parameters,
        delta_t=delta_t,
    )

    print("Final state estimate:", x[:, -1])
    print("Final parameter estimate:", y[:, -1])


if __name__ == "__main__":
    main()