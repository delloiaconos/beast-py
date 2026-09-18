"""Current-pulse profile generation."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from beast.core.arrays import FloatArray
from beast.core.validators import (validate_finite,
    validate_positive_finite)

from beast.generators.base import Generator


class Generator_Pulse(Generator):
    """Generate a pulse profile.
    Args:
        t_high: High-value duration of each pulse in seconds.
        t_low: Low-value duration of each pulse in seconds.
        v_high: Level during high-time.
        v_low: Level during low-time.
    """

    def __init__(
        self,
        t_start: float = 0.0,
        t_stop: float = np.inf,
        delta_t: float = 1e-3,
        Ng: int = 1,
        *,
        t_high: float,
        t_low: float,
        v_high: float,
        v_low: float = 0.0,
    ) -> None:

        super().__init__(t_start=t_start, t_stop=t_stop, delta_t=delta_t, Ng=Ng)

        self._t_high = validate_positive_finite(t_high, "t_high")
        self._t_low = validate_positive_finite(t_low, "t_low")
        self._v_high = validate_finite(v_high, "v_high")
        self._v_low = validate_finite(v_low, "v_low")

    @property
    def t_on(self) -> float:
        return self._t_on

    @property
    def t_off(self) -> float:
        return self._t_off

    @property
    def n_high_samples(self) -> int:
        """Number of high-value samples in each pulse."""
        return int(np.floor(self._t_high / self.delta_t))

    @property
    def n_low_samples(self) -> int:
        """Number of low-value samples in each pulse."""
        return int(np.floor(self._t_low / self.delta_t))
    
    def generate(self) -> tuple[FloatArray, FloatArray]:
        """Generate equispaced time and current vectors."""

        n_high = self.n_high_samples
        n_low = self.n_low_samples
        #samples_per_pulse = n_high + n_low

        output = np.concatenate(
            [
                np.concatenate(
                    [
                        np.full(n_high, self._v_high, dtype=np.float64),
                        np.full(n_low, self._v_low, dtype=np.float64),
                    ]
                )
                for _ in range(self.Ng)
            ]
        )

        time = np.arange(output.size, dtype=np.float64) * self._delta_t

        return time, output

    def generate_all(self, t_start : float, t_stop : float, delta_t : float = None) -> tuple[FloatArray, FloatArray]:
            raise NotImplementedError
        
    def generate_t(self, t : float) -> tuple[float, float]:
        raise NotImplementedError