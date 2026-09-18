"""Fixed-gain mixed estimator."""

from __future__ import annotations

from typing import Any

import numpy as np

from beast.estimators.base import Estimator, ExposrtableVars


class Estimator_MixAlgorithm(Estimator):
    """Propagate the model and correct states with a fixed diagonal gain.

    The gain is initialized to ``1e5 * diag(model.sxW)`` and never updated.
    Parameters remain fixed.
    """

    def _exportable_vars(self) -> list[ExposrtableVars]:
        return (
            ExposrtableVars("xPold", self.Nx, "xP_all", True),
            ExposrtableVars("pPold", self.Np, "pP_all", True),
            ExposrtableVars("Lxold", self.Nx, "Lx_all", True),
        )

    def initialize(self, x0: Any, p0: Any, uold: Any, yXPold: Any, told: float) -> None:
        """Set initial state, parameters, gains, and sample metadata."""
        self.xPold = self._state(x0)
        self.pPold = self._parameters(p0)
        self._input(uold)
        self._measurement(yXPold)
        self.told = float(told)
        diagonal = np.diag(self.objCell.sxW)
        if diagonal.size != self.Nx:
            raise ValueError("sxW diagonal length must equal the number of states")
        self.Lxold = (1.0e5 * diagonal).reshape(self.Nx, 1)
        if self.Ny != 1:
            raise NotImplementedError("The original MixAlgorithm supports Ny=1 only")
        self._initialized = True

    def step(self, unew: Any, yXPnew: Any, tnew: float) -> None:
        """Advance the estimator by one input/measurement sample."""
        self._require_initialized()
        u_new = self._input(unew)
        y_new = self._measurement(yXPnew)
        model = self.objCell
        xMnew = model.f0(self.xPold, self.pPold, u_new, self.deltat)
        g0new = model.g0(xMnew, self.pPold, u_new, self.deltat)
        xPnew = model.coerce_state(xMnew + self.Lxold @ (y_new - g0new))
        self.xPold = xPnew
        self.told = float(tnew)
