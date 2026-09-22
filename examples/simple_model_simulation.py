"""Run a dual EKF on a synthetic R0-R1-C1 battery profile.

Execute from an installed project with::

    python examples/synthetic_run.py
"""

from __future__ import annotations

import numpy as np

from beast.cell_models.r0r1c1 import R0R1C1
from beast.simulation import simulate_model


def main() -> None:
    """Build plain NumPy data, run the estimator, and print final estimates."""

    delta_t = 1.0
    soc_grid = np.linspace(0.0, 1.0, 101)
    
    model_data = {
        "Qn_Ah": np.array([2.0]),
        "eta": np.array([0.99]),
        "soc": soc_grid,
        "ocv0": 3.0 + 1.2 * soc_grid,
        "ocv1": np.full_like(soc_grid, 1.2),
    }

    covariance = {
        "sxW": np.diag([1.0e-8, 1.0e-8]),
        "sxV": np.diag([1.0e-5]),
        "spR": np.diag([1.0e-10, 1.0e-10, 1.0e-6]),
        "spE": np.diag([1.0e-5]),
    }
    model = R0R1C1(model_data, covariance, delta_t)

    time = np.arange(300.0)
    current = np.zeros((1, time.size), dtype=np.float64)
    current[0, 20:220] = 1.0
    current[0, 240:280] = -0.5

    true_x0 = np.array([0.90, 0.0])
    true_parameters = np.array([0.010, 0.020, 1000.0])

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
