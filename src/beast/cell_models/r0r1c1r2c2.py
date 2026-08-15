"""Second-order ``R0-R1-C1-R2-C2`` equivalent-circuit model."""

from __future__ import annotations

from typing import Any, ClassVar
import warnings

import numpy as np

from beast.cell_models.base import CellModel
from beast.core.arrays import FloatArray, as_float_vector


class CellModel_R0R1C1R2C2(CellModel):
    """Two-RC-branch model with state ``[SOC, vC1, vC2]``.

    Parameters are ``[R0, R1, C1, R2, C2]``.  Terminal voltage is the OCV
    minus the ohmic drop plus both branch voltages.
    """

    Nx: ClassVar[int] = 3
    Np: ClassVar[int] = 5

    def _alphas(self, p: FloatArray) -> tuple[float, float]:
        alpha1 = float(np.exp(-self.deltatfix / (p[1] * p[2])))
        alpha2 = float(np.exp(-self.deltatfix / (p[3] * p[4])))
        return alpha1, alpha2

    def f0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate the discrete state transition."""
        x = self.state(xold); p = self.parameters(pold); u = self.input(uold)
        alpha1, alpha2 = self._alphas(p)
        return np.array(
            [
                x[0] - self.CoulombCountingConstant * u[0],
                alpha1 * x[1] + p[1] * (alpha1 - 1.0) * u[0],
                alpha2 * x[2] + p[3] * (alpha2 - 1.0) * u[0],
            ],
            dtype=np.float64,
        )

    def g0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate terminal voltage for the supplied state and input."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        return np.array(
            [self._interp(self.lutocv0, x[0]) - p[0] * u[0] + x[1] + x[2]],
            dtype=np.float64,
        )

    def f1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to state."""

        _ = self.state(xold) 
        p = self.parameters(pold)
        _ = self.input(uold)

        alpha1, alpha2 = self._alphas(p)
        return np.diag([1.0, alpha1, alpha2]).astype(np.float64)

    def f1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to parameters."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        tau1 = p[1] * p[2]
        tau2 = p[3] * p[4]
        alpha1, alpha2 = self._alphas(p)
        adtrc1 = alpha1 * self.deltatfix / tau1
        adtrc2 = alpha2 * self.deltatfix / tau2
        result = np.zeros((3, 5), dtype=np.float64)
        result[1, 1] = adtrc1 / p[1] * x[1] + (alpha1 - 1.0 + adtrc1) * u[0]
        result[1, 2] = adtrc1 / p[2] * (x[1] + p[1] * u[0])
        result[2, 3] = adtrc2 / p[3] * x[2] + (alpha2 - 1.0 + adtrc2) * u[0]
        result[2, 4] = adtrc2 / p[4] * (x[2] + p[3] * u[0])
        return result

    def g1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to state."""

        x = self.state(xold)
        _ = self.parameters(pold)
        _ = self.input(uold)

        return np.array([[self._interp(self.lutocv1, x[0]), 1.0, 1.0]], dtype=np.float64)

    def g1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to parameters."""
        _ = self.state(xold)
        _ = self.parameters(pold)
        u = self.input(uold)

        return np.array([[-u[0], 0.0, 0.0, 0.0, 0.0]], dtype=np.float64)

    @classmethod
    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        """Return a copy of the parameter vector projected onto valid bounds."""
        result = as_float_vector(parameters, name="parameters")
        if result.size != cls.Np:
            raise ValueError(f"parameters must have length {cls.Np}, got {result.size}")
        labels = ("R0", "R1", "C1", "R2", "C2")
        for index, label in enumerate(labels):
            if result[index] <= 0.0:
                warnings.warn(
                    f"{cls.__name__}: {label} must be positive; using {cls.zerohere:g}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                result[index] = cls.zerohere
        return result
