"""Constant-current profile generation."""

from __future__ import annotations

import numpy as np

from beast.core.arrays import FloatArray
from beast.generators.base import Generator


class Generator_ConstantCurrent(Generator):
    """Generate a constant-current input profile.

    Args:
        current: Constant current value. Positive current denotes discharge and
            negative current denotes charge.
        duration: Profile duration in seconds.
        delta_t: Sampling interval in seconds.

    Notes:
        The profile uses the half-open interval ``[0, duration)``. The number
        of samples is ``floor(duration / delta_t)``.
    """

    def __init__(self, current: float, *, duration: float, delta_t: float) -> None:
        self._current = self._validate_finite(current, "current")
        self._duration = self._validate_positive_finite(duration, "duration")
        self._delta_t = self._validate_positive_finite(delta_t, "delta_t")
        self._sample_count(self._duration, self._delta_t)

    @property
    def current(self) -> float:
        return self._current

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def delta_t(self) -> float:
        return self._delta_t

    @property
    def n_samples(self) -> int:
        """Number of generated samples."""
        return self._sample_count(self._duration, self._delta_t)

    def generate(self) -> tuple[FloatArray, FloatArray]:
        """Generate equispaced time and constant-current vectors."""
        time = self._time_vector(self.n_samples, self._delta_t)
        current = np.full(self.n_samples, self._current, dtype=np.float64)
        return time, current
