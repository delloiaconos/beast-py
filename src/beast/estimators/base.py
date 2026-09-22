"""Abstract estimator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
import math
from dataclasses import dataclass
from typing import Any, Callable

from beast.cell_models.cell_model import CellModel
from beast.core.arrays import FloatArray, as_float_vector


@dataclass(frozen=True, slots=True)
class ExportableVars:
    """Metadata describing values exported by estimators.

    Describe one estimator member that can be saved or exported.
    ``FunctionHandler`` must be applied during export when the stored member must be
    reduced or reshaped to the declared ``Size``.
    """

    ClassVar: str
    Size: int
    ExportName: str
    Save: bool
    FunctionHandler: Callable[[Any], Any] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ClassVar, str) or not self.ClassVar:
            raise ValueError("ClassVar must be a non-empty string")
        if isinstance(self.Size, bool) or not isinstance(self.Size, int) or self.Size < 0:
            raise ValueError("Size must be a non-negative integer")
        if not isinstance(self.ExportName, str):
            raise TypeError("ExportName must be a string")
        if not isinstance(self.Save, bool):
            raise TypeError("Save must be a bool")
        if self.FunctionHandler is not None and not callable(self.FunctionHandler):
            raise TypeError("FunctionHandler must be callable or None")


class Estimator(ABC):
    """Base class for state and parameter estimators.
    """

    ExportableVars: list[ExportableVars]

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
    
        try:
            deltat = float(DeltaT)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "DeltaT must be a real number"
            ) from exc

        if not math.isfinite(deltat) or deltat <= 0.0:
            raise ValueError(
                "DeltaT must be positive and finite"
            )
        
        self.objCell = objCellModel
        self.deltat = float(DeltaT)
        self.Nx = objCellModel.Nx
        self.Np = objCellModel.Np
        self.Nu = objCellModel.Nu
        self.Ny = objCellModel.Ny
        self._initialized = False
        self.ExportableVars = self._exportable_vars()

    def _exportable_vars(self) -> list[ExportableVars]:
        """Build export metadata after model-dependent dimensions are known."""
        return []

    @property
    def exportable_variables(self) -> list[ExportableVars]:
        """Metadata for estimator members exposed to processing loops."""

        return self.ExportableVars

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
