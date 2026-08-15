"""Constant-current profile generation."""

from __future__ import annotations

import numpy as np

from beast.core.arrays import FloatArray
from beast.core.validators import validate_finite

from beast.generators.base import Generator

class Generator_ConstantValue(Generator):
    """Generate a constant-value input profile.

    Args:
        value: Constant value. Positive value denotes discharge and
            negative value denotes charge.
        duration: Profile duration in seconds.
        delta_t: Sampling interval in seconds.

    Notes:
        The profile uses the half-open interval ``[0, duration)``. The number
        of samples is ``floor(duration / delta_t)``.
    """

    def __init__( self,
            value : float,
            *,
            t_start: float = 0.0,
            t_stop: float = np.inf,
            delta_t: float = 1e-3,
            Ng : int = 1,
        ):
        super().__init__(t_start=t_start, t_stop=t_stop, delta_t=delta_t, Ng=Ng)

        self._value = validate_finite(value, "value")
    
    def generate(self) -> tuple[FloatArray, FloatArray]:
        """Generate equispaced time and constant-value vectors."""
        t_all = self.t_all
        value = np.full(self.n_samples, self._value, dtype=np.float64)
        return t_all, value

    def generate_all(self, t_start : float, t_stop : float, delta_t : float = None) -> tuple[FloatArray, FloatArray]:
        raise NotImplementedError
    
    def generate_t(self, t : float) -> tuple[float, float]:
        raise NotImplementedError