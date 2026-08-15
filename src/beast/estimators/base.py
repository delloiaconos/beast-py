"""Abstract estimator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from beast.cell_models.base import CellModel
from beast.core.arrays import FloatArray, as_float_vector


class Estimator(ABC):
    """Base class for state and parameter estimators.
    """

    AvailablesVars: ClassVar[tuple[str, ...]] = ()

    def __init__(self, objCellModel: CellModel, DeltaT: float) -> None:
        """Store the model interface and fixed estimator sampling interval.

        Args:
            objCellModel: Battery model used by the estimator.
            DeltaT: Positive sampling interval in seconds.

        Raises:
            TypeError: If ``objCellModel`` is not a ``CellModel`` instance.
            ValueError: If ``DeltaT`` is not positive.
        """

        if not isinstance(objCellModel, CellModel):
            raise TypeError(
                "objCellModel must be an instance of CellModel"
            )
        
        self.objModel = objCellModel
        self.deltat = float(DeltaT)
        if self.deltat <= 0.0:
            raise ValueError("DeltaT must be positive")
        self.Nx = objCellModel.Nx
        self.Np = objCellModel.Np
        self.Nu = objCellModel.Nu
        self.Ny = objCellModel.Ny
        self._initialized = False

    @property
    def available_variables(self) -> tuple[str, ...]:
        """Names of histories that the processing loop should collect."""

        return self.AvailablesVars

    def _state(self, value: Any) -> FloatArray:
        result = as_float_vector(value, name="x0")
        if result.size != self.Nx:
            raise ValueError(f"state must have length {self.Nx}, got {result.size}")
        return result

    def _parameters(self, value: Any) -> FloatArray:
        result = as_float_vector(value, name="p0")
        if result.size != self.Np:
            raise ValueError(f"parameters must have length {self.Np}, got {result.size}")
        return result

    def _input(self, value: Any) -> FloatArray:
        result = as_float_vector(value, name="input")
        if result.size != self.Nu:
            raise ValueError(f"input must have length {self.Nu}, got {result.size}")
        return result

    def _measurement(self, value: Any) -> FloatArray:
        result = as_float_vector(value, name="measurement")
        if result.size != self.Ny:
            raise ValueError(f"measurement must have length {self.Ny}, got {result.size}")
        return result

    def _require_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("Initialize must be called before Step")

    @abstractmethod
    def initialize(self, x0: Any, p0: Any, uold: Any, y_exp_old: Any, t_old: float) -> None:
        """Initialize the estimator at the first sample."""

    @abstractmethod
    def step(self, u_new: Any, y_exp_new: Any, t_new: float) -> None:
        """Advance the estimator by one sample."""
