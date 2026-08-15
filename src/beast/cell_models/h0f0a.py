"""Zero-dynamic-branch battery model ``CellModel_H0F0A``."""

from __future__ import annotations

from typing import Any, ClassVar
import warnings

import numpy as np

from beast.cell_models.base import CellModel
from beast.arrays import FloatArray, as_float_vector


class CellModel_H0F0A(CellModel):
    """Coulomb-counting state model with one ohmic-resistance parameter.

    State vector:
        ``x[0]`` is state of charge.

    Parameter vector:
        ``p[0]`` is ohmic resistance ``R0``.

    The output equation is ``v = OCV(SOC) - R0 * i`` using the active sign
    convention from the MATLAB source (positive current means discharge).
    """

    Nx: ClassVar[int] = 1
    Np: ClassVar[int] = 1

    def f0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate the discrete state transition."""
        x = self._state(xold)
        self._parameters(pold)
        u = self._input(uold)
        return np.array([x[0] - self.CoulombCountingConstant * u[0]], dtype=np.float64)

    def g0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate terminal voltage for the supplied state and input."""
        x = self._state(xold)
        p = self._parameters(pold)
        u = self._input(uold)
        return np.array([self._interp(self.lutocv0, x[0]) - p[0] * u[0]], dtype=np.float64)

    def f1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to state."""
        self._state(xold); self._parameters(pold); self._input(uold)
        return np.array([[1.0]], dtype=np.float64)

    def f1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to parameters."""
        self._state(xold); self._parameters(pold); self._input(uold)
        return np.zeros((1, 1), dtype=np.float64)

    def g1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to state."""
        x = self._state(xold); self._parameters(pold); self._input(uold)
        return np.array([[self._interp(self.lutocv1, x[0])]], dtype=np.float64)

    def g1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to parameters."""
        self._state(xold); self._parameters(pold); u = self._input(uold)
        return np.array([[-u[0]]], dtype=np.float64)

    @classmethod
    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        """Return a copy of the parameter vector projected onto valid bounds."""
        result = as_float_vector(parameters, name="parameters")
        if result.size != cls.Np:
            raise ValueError(f"parameters must have length {cls.Np}, got {result.size}")
        if result[0] <= 0.0:
            warnings.warn(
                f"{cls.__name__}: R0 must be positive; using {cls.zerohere:g}",
                RuntimeWarning,
                stacklevel=2,
            )
            result[0] = cls.zerohere
        return result
