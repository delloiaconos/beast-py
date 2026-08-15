"""Base API and shared validation for battery cell models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Mapping
import warnings

import numpy as np
from numpy.typing import NDArray

from beast.core.arrays import (
    FloatArray,
    as_float_vector,
    as_history_matrix,
    get_field,
    scalar_from,
)

from beast.core.data import normalize_covariance


class CellModel(ABC):
    """Abstract interface implemented by every converted MATLAB cell model.

    Concrete classes intentionally retain the MATLAB method names ``f0``,
    ``g0``, ``f1x``, ``f1p``, ``g1x``, and ``g1p``.  States and parameters are
    represented by one-dimensional vectors in Python; Jacobians remain
    two-dimensional matrices.
    """

    Nx: ClassVar[int]
    Np: ClassVar[int]
    Nu: ClassVar[int] = 1
    Ny: ClassVar[int] = 1
    zerohere: ClassVar[float] = 1.0e-9
    Required: ClassVar[tuple[str, ...]] = ("Qn_Ah", "eta", "soc", "ocv0", "ocv1")

    def __init__(
        self,
        cell_model_data: Mapping[str, Any] | Any,
        covariance: Mapping[str, Any] | Any,
        deltat: float,
    ) -> None:
        """Initialize common battery and covariance data.

        Args:
            cell_model_data: Mapping or object containing fields listed in
                :attr:`Required`.
            covariance: Plain mapping or compatibility object containing
                ``sxW``, ``sxV``, ``spR``, and ``spE`` NumPy-compatible values.
            deltat: Fixed sampling interval in seconds.
        """

        self.Qnom_Ah = scalar_from(get_field(cell_model_data, "Qn_Ah"), name="Qn_Ah")
        self.Qnom = self.Qnom_Ah * 3600.0
        self.eta = scalar_from(get_field(cell_model_data, "eta"), name="eta")

        if not np.isfinite(self.Qnom_Ah) or self.Qnom_Ah <= 0:
            raise ValueError("Qn_Ah must be a positive finite value")
        
        if self.Qnom <= 0.0:
            raise ValueError("Qn_Ah must be positive")
        
        if not np.isfinite(self.eta):
            raise ValueError("eta must be finite")

        self.lutsoc = as_float_vector(get_field(cell_model_data, "soc"), name="soc")
        self.lutocv0 = as_float_vector(get_field(cell_model_data, "ocv0"), name="ocv0")
        self.lutocv1 = as_float_vector(get_field(cell_model_data, "ocv1"), name="ocv1")
        if not (self.lutsoc.size == self.lutocv0.size == self.lutocv1.size):
            raise ValueError("soc, ocv0, and ocv1 lookup arrays must have equal lengths")
        if self.lutsoc.size < 2:
            raise ValueError("OCV lookup tables require at least two points")
        if np.any(np.diff(self.lutsoc) <= 0.0):
            raise ValueError("soc lookup points must be strictly increasing")

        cov = normalize_covariance(covariance, nx=self.Nx, np=self.Np, ny=self.Ny)
        self.sxW = cov["sxW"]
        self.sxV = cov["sxV"]
        self.spR = cov["spR"]
        self.spE = cov["spE"]

        self.deltatfix = float(deltat)
        if not np.isfinite(self.deltatfix) or self.deltatfix <= 0.0:
            raise ValueError("deltat must be a positive finite value")
        self.CoulombCountingConstant = self.eta * self.deltatfix / self.Qnom

    @property
    def name(self) -> str:
        """Model selector without the ``CellModel_`` prefix."""

        return type(self).__name__.removeprefix("CellModel_")

    def state(self, value: Any) -> FloatArray:
        vector = as_float_vector(value, name="state")
        if vector.size != self.Nx:
            raise ValueError(f"state must have length {self.Nx}, got {vector.size}")
        return vector

    def parameters(self, value: Any) -> FloatArray:
        vector = as_float_vector(value, name="parameters")
        if vector.size != self.Np:
            raise ValueError(f"parameters must have length {self.Np}, got {vector.size}")
        return vector

    def _input(self, value: Any) -> FloatArray:
        vector = as_float_vector(value, name="input")
        if vector.size != self.Nu:
            raise ValueError(f"input must have length {self.Nu}, got {vector.size}")
        return vector

    def _interp(self, values: NDArray[np.float64], soc: float) -> float:
        """Match MATLAB ``interp1`` behavior without extrapolation."""

        if soc < self.lutsoc[0] or soc > self.lutsoc[-1] or not np.isfinite(soc):
            return float("nan")
        return float(np.interp(soc, self.lutsoc, values))

    @abstractmethod
    def f0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate the discrete state-transition function."""

    @abstractmethod
    def g0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate the terminal-voltage output function."""

    @abstractmethod
    def f1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the Jacobian of :meth:`f0` with respect to state."""

    @abstractmethod
    def f1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the Jacobian of :meth:`f0` with respect to parameters."""

    @abstractmethod
    def g1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the Jacobian of :meth:`g0` with respect to state."""

    @abstractmethod
    def g1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the Jacobian of :meth:`g0` with respect to parameters."""

    @classmethod
    def coerce_state(cls, state: Any) -> FloatArray:
        """Clamp state of charge to the physically valid interval ``[0, 1]``."""

        result = as_float_vector(state, name="state")
        if result.size != cls.Nx:
            raise ValueError(f"state must have length {cls.Nx}, got {result.size}")
        original = result[0]
        result[0] = np.clip(result[0], 0.0, 1.0)
        if result[0] != original:
            warnings.warn(
                f"{cls.__name__}: SOC {original:g} was clipped to {result[0]:g}",
                RuntimeWarning,
                stacklevel=2,
            )
        return result

    @classmethod
    @abstractmethod
    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        """Project parameters onto the model's admissible domain."""
    
    @classmethod
    def check_dimensions(cls, data: Any) -> None:
        """Validate legacy ``x0``, ``p0``, and ``u_all`` dimensions.

        Args:
            data: Mapping or object exposing the three named fields.

        Raises:
            ValueError: If any dimension is inconsistent with the class.
        """

        x0 = as_float_vector(get_field(data, "x0"), name="x0")
        p0 = as_float_vector(get_field(data, "p0"), name="p0")
        u_all = as_history_matrix(get_field(data, "u_all"), name="u_all")
        if x0.size != cls.Nx:
            raise ValueError(f"x0 must have length {cls.Nx}, got {x0.size}")
        if p0.size != cls.Np:
            raise ValueError(f"p0 must have length {cls.Np}, got {p0.size}")
        if u_all.shape[0] != cls.Nu:
            raise ValueError(f"u_all must have {cls.Nu} rows, got {u_all.shape[0]}")


