"""Abstract interfaces for BEAST input-profile generators."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from beast.core.arrays import FloatArray


class Generator(ABC):
    """Base class for BEAST input-profile generators."""

    @abstractmethod
    def generate(self) -> tuple[FloatArray, FloatArray]:
        """Generate an equispaced time vector and its corresponding profile."""
        raise NotImplementedError

    @staticmethod
    def _validate_finite(value: float, name: str) -> float:
        """Return *value* as ``float`` if it is finite."""
        result = float(value)
        if not np.isfinite(result):
            raise ValueError(f"{name} must be a finite value")
        return result

    @classmethod
    def _validate_positive_finite(cls, value: float, name: str) -> float:
        """Return *value* as ``float`` if it is positive and finite."""
        result = cls._validate_finite(value, name)
        if result <= 0.0:
            raise ValueError(f"{name} must be a positive finite value")
        return result

    @classmethod
    def _validate_nonnegative_finite(cls, value: float, name: str) -> float:
        """Return *value* as ``float`` if it is nonnegative and finite."""
        result = cls._validate_finite(value, name)
        if result < 0.0:
            raise ValueError(f"{name} must be a nonnegative finite value")
        return result

    @staticmethod
    def _sample_count(duration: float, delta_t: float, *, name: str = "duration") -> int:
        """Return the number of full samples contained in *duration*.

        Profile durations use a half-open interval convention ``[0, duration)``.
        Therefore only complete samples separated by ``delta_t`` are emitted.
        """
        count = int(np.floor(duration / delta_t))
        if count <= 0:
            raise ValueError(f"{name} / delta_t must produce at least one sample")
        return count

    @staticmethod
    def _time_vector(sample_count: int, delta_t: float) -> FloatArray:
        """Build an equispaced time vector starting at zero."""
        return np.arange(sample_count, dtype=np.float64) * delta_t