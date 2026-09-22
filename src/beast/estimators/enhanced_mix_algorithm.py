"""Enhanced fixed-gain estimator."""

from __future__ import annotations

from typing import Any

import numpy as np

from beast.estimators.base import Estimator, ExportableVars


class EnhancedMixAlgorithm(Estimator):
    """Fixed-gain state and parameter correction algorithm.

    The source explicitly notes that the parameter-gain calculation is not
    generic.  For the converted models (all ``Ny == 1``), the scalar gain from
    ``diag(sxV)`` is broadcast to every parameter.
    """

    def _exportable_vars(self) -> list[ExportableVars]:
        return (
            ExportableVars("xPold", self.Nx, "xP_all", True),
            ExportableVars("pPold", self.Np, "pP_all", True),
        )

    def initialize(self, x0: Any, p0: Any, uold: Any, yXPold: Any, told: float) -> None:
        """Set initial state, parameters, gains, and sample metadata."""
        self.xPold = self._state(x0)
        self.pPold = self._parameters(p0)
        self._input(uold)
        self._measurement(yXPold)
        self.told = float(told)
        if self.Ny != 1:
            raise NotImplementedError("The original EnhancedMixAlgorithm supports Ny=1 only")
        self.Lxold = (1.0e5 * np.diag(self.objCell.sxW)).reshape(self.Nx, 1)
        self.Lpold = 1.0e5 * np.diag(self.objCell.sxV)
        self._initialized = True

    def step(self, unew: Any, yXPnew: Any, tnew: float) -> None:
        """Advance the estimator by one input/measurement sample."""
        self._require_initialized()
        u_new = self._input(unew)
        y_new = self._measurement(yXPnew)
        model = self.objCell
        xMnew = model.f0(self.xPold, self.pPold, u_new, self.deltat)
        g0new = model.g0(xMnew, self.pPold, u_new, self.deltat)
        error = y_new - g0new
        xPnew = model.coerce_state(xMnew + self.Lxold @ error)

        parameter_gain = self.Lpold
        if parameter_gain.size not in (1, self.Np):
            raise ValueError(
                "EnhancedMixAlgorithm parameter gain must be scalar or match Np"
            )
        correction = parameter_gain * float(error[0]) * float(np.sign(u_new[0]))
        pPnew = model.coerce_parameters(self.pPold + correction)

        self.told = float(tnew)
        self.pPold = pPnew
        self.xPold = xPnew
