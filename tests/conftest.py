"""Shared synthetic battery data for the test suite."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def model_data() -> dict[str, np.ndarray]:
    soc = np.linspace(0.0, 1.0, 11)
    return {
        "Qn_Ah": np.array([2.0]),
        "eta": np.array([0.99]),
        "soc": soc,
        "ocv0": 3.0 + 1.2 * soc,
        "ocv1": np.full_like(soc, 1.2),
    }


def covariance_for(model_class) -> dict[str, np.ndarray]:
    """Return covariance matrices as a plain NumPy dictionary."""

    return {
        "sxW": np.eye(model_class.Nx) * 1.0e-8,
        "sxV": np.eye(model_class.Ny) * 1.0e-8,
        "spR": np.eye(model_class.Np) * 1.0e-8,
        "spE": np.eye(model_class.Ny) * 1.0e-4,
    }
