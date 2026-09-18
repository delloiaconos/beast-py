"""Abstract interfaces for BEAST profile generators."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from beast.core.arrays import FloatArray
from beast.core.validators import (
    validate_positive,
    validate_nonnegative_finite,
    validate_positive_finite )

class Generator(ABC):
    """Base class for BEAST profile generators."""

    def __init__( self,
        t_start: float = 0.0,
        t_stop: float = np.inf,
        delta_t: float = 1e-3,
        Ng : int = 1
    ):

        self._t_start = validate_nonnegative_finite(t_start, "t_start")
        self._t_stop = validate_positive(t_stop, "t_stop")

        validate_positive_finite(delta_t, "delta_t")

        if  np.isfinite(t_stop) and t_stop <= t_start:
            raise ValueError("t_stop must be greater than t_start")
    
        if np.isfinite(t_stop) and delta_t >= (t_stop - t_start):
            raise ValueError("delta_t must be less than (t_stop - t_start)")
    
        if Ng < 1:
            raise ValueError("Ng must be a positive integer")
        
        self._delta_t = validate_positive_finite(delta_t, "delta_t")
        self._Ng = Ng

    @property
    def duration(self) -> float:
        """Return the duration of the profile."""
        return self._t_stop - self._t_start

    @property
    def t_start(self) -> float:
        """Return the start time of the profile."""
        return self._t_start

    @property
    def t_stop(self) -> float:
        """Return the stop time of the profile."""
        return self._t_stop

    @property
    def delta_t(self) -> float:
        """Return the time step of the profile."""
        return self._delta_t

    @property
    def Ng(self) -> int:
        """Return the number of generated channels."""
        return self._Ng
    
    @property
    def n_samples(self) -> int:
        """Return the number of samples in the profile.
        It uses a half-open interval convention ``[0, duration)``.
        Therefore only complete samples separated by ``delta_t`` are emitted.
        """
        count = int(np.floor(self.duration / self.delta_t))
        if count <= 0:
            raise ValueError(f"duration / delta_t must produce at least one sample")
        return count

    @abstractmethod
    def generate_all(self, t_start : float, t_stop : float, delta_t : float = None) -> tuple[FloatArray, FloatArray]:
        """Generate an equispaced time vector and its corresponding profile."""
        raise NotImplementedError

    @abstractmethod
    def generate_t(self, t : float) -> tuple[float, float]:
        """Generate an equispaced time vector and its corresponding profile."""
        raise NotImplementedError

    @staticmethod
    def time_vector(n_samples: int, delta_t: float, t_start : float = 0.0) -> FloatArray:
        """Build an equispaced time vector starting at zero."""
        return np.arange(n_samples, dtype=np.float64) * delta_t + t_start

    @property
    def t_all( self ) -> FloatArray:
        """Build an equispaced time vector starting according to the generator's parameters."""
        return self.time_vector(self.n_samples, self.delta_t, self.t_start)