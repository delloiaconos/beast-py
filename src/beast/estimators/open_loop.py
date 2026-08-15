"""Open-loop model propagation estimator."""

from __future__ import annotations

from typing import Any, ClassVar

from beast.estimators.base import Estimator


class Estimator_OpenLoop(Estimator):
    """Advance states using the model without measurement correction."""

    AvailablesVars: ClassVar[tuple[str, ...]] = ("xPold", "pPold")

    def initialize(self, x0: Any, p0: Any, uold: Any, yXPold: Any, told: float) -> None:
        """Set initial state, parameters, gains, and sample metadata."""
        self.xPold = self._state(x0)
        self.pPold = self._parameters(p0)
        self._input(uold)
        self._measurement(yXPold)
        self.told = float(told)
        self._initialized = True

    def step(self, unew: Any, yXPnew: Any, tnew: float) -> None:
        """Advance the estimator by one input/measurement sample."""
        self._require_initialized()
        u_new = self._input(unew)
        self._measurement(yXPnew)
        xPnew = self.objModel.f0(self.xPold, self.pPold, u_new, self.deltat)
        self.xPold = self.objModel.coerce_state(xPnew)
        self.told = float(tnew)
