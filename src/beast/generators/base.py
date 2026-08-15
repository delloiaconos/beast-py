"""Abstract interfaces for BEAST input-profile generators."""

from __future__ import annotations

from abc import ABC, abstractmethod

from beast.core.arrays import FloatArray


class Generator(ABC):
    """Base class for BEAST input-profile generators."""

    @abstractmethod
    def generate(self) -> tuple[FloatArray, FloatArray]:
        """Generate an equispaced time vector and its corresponding profile."""
        raise NotImplementedError
