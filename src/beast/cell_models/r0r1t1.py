"""First-order ``R0-R1-tau1`` equivalent-circuit model."""

from __future__ import annotations

from typing import Any, ClassVar
import warnings

import numpy as np

from beast.cell_models.cell_model import CellModel
from beast.core.arrays import FloatArray, as_float_vector


class R0R1T1(CellModel):
    """One-RC-branch model parameterized by resistance and time constant.

    State vector is ``[SOC, vC1]`` and parameters are ``[R0, R1, tau1]``.
    This class also corrects the invalid ``obj.zerohere`` references in the
    MATLAB static parameter-coercion method.
    """

    Nx: ClassVar[int] = 2
    Np: ClassVar[int] = 3

    def _alpha(self, p: FloatArray) -> float:
        return float(np.exp(-self.deltatfix / p[2]))

    def f0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate the discrete state transition."""
        x = self.state(xold); p = self.parameters(pold); u = self.input(uold)
        alpha = self._alpha(p)
        return np.array(
            [
                x[0] - self.CoulombCountingConstant * u[0],
                alpha * x[1] + p[1] * (alpha - 1.0) * u[0],
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

        return np.array([[1.0, 0.0], [0.0, self._alpha(p)]], dtype=np.float64)

    def f1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to parameters."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        alpha = self._alpha(p)
        derivative_alpha_tau = alpha * self.deltatfix / (p[2] * p[2])
        result = np.zeros((2, 3), dtype=np.float64)
        result[1, 1] = (alpha - 1.0) * u[0]
        result[1, 2] = derivative_alpha_tau * (x[1] + p[1] * u[0])
        return result

    def g1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to state."""

        x = self.state(xold)
        _ = self.parameters(pold)
        _ = self.input(uold)
        
        return np.array([[self._interp(self.lutocv1, x[0]), 1.0]], dtype=np.float64)

    def g1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to parameters."""
        
        _ = self.state(xold)
        _ = self.parameters(pold)
        u = self.input(uold)

        return np.array([[-u[0], 0.0, 0.0]], dtype=np.float64)

    @classmethod
    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        """Return a copy of the parameter vector projected onto valid bounds."""
        result = as_float_vector(parameters, name="parameters")
        if result.size != cls.Np:
            raise ValueError(f"parameters must have length {cls.Np}, got {result.size}")
        labels = ("R0", "R1", "tau1")
        for index, label in enumerate(labels):
            if result[index] <= 0.0:
                warnings.warn(
                    f"{cls.__name__}: {label} must be positive; using {cls.zerohere:g}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                result[index] = cls.zerohere
        return result
