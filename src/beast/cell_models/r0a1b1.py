"""Discrete first-order equivalent-circuit model ``CellModel_R0A1B1``."""

from __future__ import annotations

from typing import Any, ClassVar
import warnings

import numpy as np

from beast.cell_models.base import CellModel
from beast.core.arrays import FloatArray, as_float_vector


class CellModel_R0A1B1(CellModel):
    """One-RC-branch model parameterized directly by ``A1`` and ``B1``.

    ``x = [SOC, vC1]`` and ``p = [R0, A1, B1]``.  The MATLAB conversion
    relations are ``R1 = B1 / (A1 - 1)`` and
    ``tau1 = -delta_t / log(A1)``.
    """

    Nx: ClassVar[int] = 2
    Np: ClassVar[int] = 3

    def f0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate the discrete state transition."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        return np.array(
            [
                x[0] - self.CoulombCountingConstant * u[0],
                p[1] * x[1] + p[2] * u[0],
            ],
            dtype=np.float64,
        )

    def g0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate terminal voltage for the supplied state and input."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        return np.array(
            [self._interp(self.lutocv0, x[0]) - p[0] * u[0] + x[1]],
            dtype=np.float64,
        )

    def f1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to state."""

        _ = self.state(xold) 
        p = self.parameters(pold)
        _ = self.input(uold)
        
        return np.array([[1.0, 0.0], [0.0, p[1]]], dtype=np.float64)

    def f1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to parameters."""

        x = self.state(xold) 
        _ =self.parameters(pold)
        u = self.input(uold)

        result = np.zeros((2, 3), dtype=np.float64)
        result[1, 1] = x[1]
        result[1, 2] = u[0]
        return result

    def g1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to state."""

        x = self.state(xold)
        _ = self.parameters(pold)
        _ = self.input(uold)

        return np.array([[self._interp(self.lutocv1, x[0]), 1.0]], dtype=np.float64)

    def g1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to parameters."""

        _ = self.state(xold); 
        _ = self.parameters(pold); 
        u = self.input(uold)

        return np.array([[-u[0], 0.0, 0.0]], dtype=np.float64)

    @classmethod
    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        """Return a copy of the parameter vector projected onto valid bounds."""

        result = as_float_vector(parameters, name="parameters")
        if result.size != cls.Np:
            raise ValueError(f"parameters must have length {cls.Np}, got {result.size}")
        if result[0] <= 0.0:
            warnings.warn(f"{cls.__name__}: R0 must be positive", RuntimeWarning, stacklevel=2)
            result[0] = cls.zerohere
        if result[1] <= 0.0:
            warnings.warn(f"{cls.__name__}: A1 must be in (0, 1]", RuntimeWarning, stacklevel=2)
            result[1] = cls.zerohere
        elif result[1] > 1.0:
            warnings.warn(f"{cls.__name__}: A1 must be in (0, 1]", RuntimeWarning, stacklevel=2)
            result[1] = 1.0
        if result[2] >= 0.0:
            warnings.warn(f"{cls.__name__}: B1 must be negative", RuntimeWarning, stacklevel=2)
            result[2] = -cls.zerohere
        return result
