"""Enhanced Self-Correcting (ESC) equivalent-circuit model."""

from __future__ import annotations

import warnings
from typing import Any, ClassVar

import numpy as np

from beast.cell_models.base import CellModel
from beast.core.arrays import FloatArray, as_float_vector


class CellModel_ESC(CellModel):
    """Enhanced Self-Correcting (ESC) model.

    State is ``[SOC, h, s, vC1]`` where `h` is dynamic hysteresis,
    `s` is instantaneous hysteresis, and `vC1` is the diffusion voltage.

    Parameters are ``[R0, R1, C1, gamma, M, M0]``. Terminal voltage is the OCV
    minus the ohmic drop plus diffusion voltage and hysteresis components.
    """

    Nx: ClassVar[int] = 4
    Np: ClassVar[int] = 6

    def _alphas(self, p: FloatArray) -> float:
        """Calculate the exponential decay factor for the RC branch."""
        return float(np.exp(-self.deltatfix / (p[1] * p[2])))
        
    def _A_H(self, p: FloatArray, u: float) -> float:
        """Calculate the exponential decay factor for dynamic hysteresis."""
        return float(np.exp(-abs(u * p[3] * self.CoulombCountingConstant)))

    def f0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate the discrete state transition."""
        x = self.state(xold); p = self.parameters(pold); u = self.input(uold)
        
        alpha1 = self._alphas(p)
        A_H = self._A_H(p, u[0])
        
        # Framework convention: u > 0 is discharge. 
        # Hysteresis approaches +1 on charge (u < 0) and -1 on discharge (u > 0).
        current_sign = np.sign(-u[0])
        s_next = x[2] if u[0] == 0.0 else current_sign
        h_next = A_H * x[1] + (1.0 - A_H) * current_sign if u[0] != 0.0 else x[1]

        return np.array(
            [
                x[0] - self.CoulombCountingConstant * u[0],
                h_next,
                s_next,
                alpha1 * x[3] + p[1] * (alpha1 - 1.0) * u[0],
            ],
            dtype=np.float64,
        )

    def g0(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Evaluate terminal voltage for the supplied state and input."""
        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        return np.array(
            [self._interp(self.lutocv0, x[0]) - p[0] * u[0] + x[3] + p[4] * x[1] + p[5] * x[2]],
            dtype=np.float64,
        )

    def f1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to state."""
        _ = self.state(xold) 
        p = self.parameters(pold)
        u = self.input(uold)

        alpha1 = self._alphas(p)
        A_H = self._A_H(p, u[0])
        s_deriv = 1.0 if u[0] == 0.0 else 0.0

        return np.diag([1.0, A_H, s_deriv, alpha1]).astype(np.float64)

    def f1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the state-transition Jacobian with respect to parameters."""
        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        tau1 = p[1] * p[2]
        alpha1 = self._alphas(p)
        adtrc1 = alpha1 * self.deltatfix / tau1
        
        result = np.zeros((self.Nx, self.Np), dtype=np.float64)
        
        # Derivative of vC1 wrt R1 and C1
        result[3, 1] = adtrc1 / p[1] * x[3] + (alpha1 - 1.0 + adtrc1) * u[0]
        result[3, 2] = adtrc1 / p[2] * (x[3] + p[1] * u[0])
        
        # Derivative of h wrt gamma (p[3])
        dA_H_dgamma = -abs(u[0] * self.CoulombCountingConstant) * self._A_H(p, u[0])
        current_sign = np.sign(-u[0])
        result[1, 3] = dA_H_dgamma * x[1] - dA_H_dgamma * current_sign

        return result

    def g1x(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to state."""
        x = self.state(xold)
        p = self.parameters(pold)
        _ = self.input(uold)

        # [dOCV/dSOC, dV/dh, dV/ds, dV/dvC1]
        return np.array([[self._interp(self.lutocv1, x[0]), p[4], p[5], 1.0]], dtype=np.float64)

    def g1p(self, xold: Any, pold: Any, uold: Any, deltat: float | None = None) -> FloatArray:
        """Return the output Jacobian with respect to parameters."""
        x = self.state(xold)
        _ = self.parameters(pold)
        u = self.input(uold)

        # [dV/dR0, dV/dR1, dV/dC1, dV/dgamma, dV/dM, dV/dM0]
        return np.array([[-u[0], 0.0, 0.0, 0.0, x[1], x[2]]], dtype=np.float64)

    @classmethod
    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        """Return a copy of the parameter vector projected onto valid bounds."""
        result = as_float_vector(parameters, name="parameters")
        if result.size != cls.Np:
            raise ValueError(f"parameters must have length {cls.Np}, got {result.size}")
        
        labels = ("R0", "R1", "C1", "gamma", "M", "M0")
        for index, label in enumerate(labels):
            if result[index] <= 0.0:
                warnings.warn(
                    f"{cls.__name__}: {label} must be positive; using {cls.zerohere:g}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                result[index] = cls.zerohere
        return result
