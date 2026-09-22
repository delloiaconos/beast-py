"""Dual extended Kalman filter."""

from __future__ import annotations

from typing import Any
import warnings

import numpy as np

from beast.cell_models.base import CellModel
from beast.estimators.base import Estimator, ExposrtableVars


def _right_solve(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    """Compute MATLAB-style matrix right division ``numerator / denominator``."""

    try:
        return np.linalg.solve(denominator.T, numerator.T).T
    except np.linalg.LinAlgError:
        warnings.warn(
            "Innovation covariance is singular; using a Moore-Penrose inverse",
            RuntimeWarning,
            stacklevel=2,
        )
        return numerator @ np.linalg.pinv(denominator)


def _first_element(value: Any) -> Any:
    """Return the first flattened element of an exported value."""

    return np.asarray(value).reshape(-1)[0]


class EKFdual(Estimator):
    """Dual EKF that estimates cell state and model parameters in sequence.

    The operation ordering follows the ten sections in the MATLAB method.  A
    defect in the original initializer—calling ``g0`` without ``deltat``—is
    repaired here.  The fixed model sampling interval is still used.
    """

    def _exportable_vars(self) -> list[ExposrtableVars]:
        return (
            ExposrtableVars("xPold", self.Nx, "xP_all", True),
            ExposrtableVars("pPold", self.Np, "pP_all", True),
            ExposrtableVars("Lxold", self.Nx, "Lx_all", True),
            ExposrtableVars("Lpold", self.Np, "Lp_all", True),
            ExposrtableVars("sxPold", self.Nx, "sxP_all", True, np.diag),
            ExposrtableVars("spPold", self.Np, "spP_all", True, np.diag),
            ExposrtableVars("dyold", 1, "dy_all", True),
            ExposrtableVars("xPold", 1, "SoC", True, _first_element),
        )

    def __init__(self, objCellModel: CellModel, DeltaT: float) -> None:
        """Initialize zero-valued covariance, sensitivity, and gain matrices.

        Args:
            objCellModel: Battery model whose states and parameters are estimated.
            DeltaT: Positive fixed sampling interval in seconds.
        """

        super().__init__(objCellModel, DeltaT)
        self.eyeNp = np.eye(self.Np, dtype=np.float64)
        self.eyeNx = np.eye(self.Nx, dtype=np.float64)
        self.spPold = np.zeros((self.Np, self.Np), dtype=np.float64)
        self.sxPold = np.zeros((self.Nx, self.Nx), dtype=np.float64)
        self.dxMdpold = np.zeros((self.Nx, self.Np), dtype=np.float64)
        self.dgdpold = np.zeros((self.Ny, self.Np), dtype=np.float64)
        self.Lpold = np.zeros((self.Np, self.Ny), dtype=np.float64)
        self.Lxold = np.zeros((self.Nx, self.Ny), dtype=np.float64)

    def initialize(self, x0: Any, p0: Any, uold: Any, yXPold: Any, told: float) -> None:
        """Set initial state, parameters, gains, and sample metadata."""
        x = self._state(x0)
        p = self._parameters(p0)
        u = self._input(uold)
        y_measured = self._measurement(yXPold)
        self.told = float(told)
        self.uold = u
        self.xPold = x
        self.pPold = p

        # The MATLAB implementation deliberately replaces the first measured
        # output with the model-predicted value.
        self.yXPold = self.objCell.g0(x, p, u, self.deltat)
        self.dyold = y_measured - self.yXPold
        self._initialized = True

    def step(self, unew: Any, yXPnew: Any, tnew: float) -> None:
        """Advance the estimator by one input/measurement sample."""
        self._require_initialized()
        model = self.objCell
        u_new = self._input(unew)
        y_new = self._measurement(yXPnew)

        # (1) Parameter estimate time update.
        pMnew = self.pPold.copy()

        # (2) Parameter covariance time update.
        spMnew = self.spPold + model.spR

        # (3) State estimate time update.
        xMnew = model.f0(self.xPold, pMnew, self.uold, self.deltat)
        xMnew = model.coerce_state(xMnew)

        # (4) State covariance time update.
        f1xold = model.f1x(self.xPold, pMnew, self.uold, self.deltat)
        sxMnew = f1xold @ self.sxPold @ f1xold.T + model.sxW

        # (5) State Kalman gain.
        g1xnew = model.g1x(xMnew, pMnew, u_new, self.deltat)
        innovation_cov_x = g1xnew @ sxMnew @ g1xnew.T + model.sxV
        Lxnew = _right_solve(sxMnew @ g1xnew.T, innovation_cov_x)

        # (6) State measurement update.
        g0new = model.g0(xMnew, pMnew, u_new, self.deltat)
        innovation = y_new - g0new
        xPnew = model.coerce_state(xMnew + Lxnew @ innovation)

        # (7) State covariance measurement update.
        sxPnew = (self.eyeNx - Lxnew @ g1xnew) @ sxMnew

        # (8) Parameter Kalman gain.
        g1pnew = model.g1p(xMnew, pMnew, u_new, self.deltat)
        f1pold = model.f1p(self.xPold, pMnew, self.uold, self.deltat)
        dxPdpold = self.dxMdpold - self.Lxold @ self.dgdpold
        dxMdpnew = f1pold + f1xold @ dxPdpold
        dgdpnew = g1pnew + g1xnew @ dxMdpnew
        innovation_cov_p = dgdpnew @ spMnew @ dgdpnew.T + model.spE
        Lpnew = _right_solve(spMnew @ dgdpnew.T, innovation_cov_p)

        # (9) Parameter measurement update.
        pPnew = model.coerce_parameters(pMnew + Lpnew @ innovation)

        # (10) Parameter covariance measurement update.
        spPnew = (self.eyeNp - Lpnew @ dgdpnew) @ spMnew

        self.told = float(tnew)
        self.uold = u_new
        self.yXPold = y_new
        self.xPold = xPnew
        self.pPold = pPnew
        self.sxPold = sxPnew
        self.spPold = spPnew
        self.Lxold = Lxnew
        self.Lpold = Lpnew
        self.dxMdpold = dxMdpnew
        self.dgdpold = dgdpnew
        self.dyold = innovation
