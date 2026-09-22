"""Second-order discrete ``R0-R1-A1-R2-A2`` equivalent-circuit model."""

from __future__ import annotations

from typing import Any, ClassVar
import warnings

import numpy as np

from beast.cell_models.cell_model import CellModel
from beast.core.arrays import FloatArray, as_float_vector


class R0R1A1R2A2(CellModel):
    """Two-branch model parameterized by discrete decay coefficients.

    The state is ``[SOC, v1, v2]`` and the parameter vector is
    ``[R0, R1, A1, R2, A2]``. ``A1`` and ``A2`` are discrete-time decay
    coefficients constrained to the open interval ``(0, 1)``.

    This is the NumPy counterpart of ``beast.CellModels.R0R1A1R2A2``. The
    state and output equations follow the MATLAB implementation. Its copied
    resistance derivatives in ``f1p`` are replaced by the exact derivatives
    of this model's directly parameterized state equation.
    """

    Nx: ClassVar[int] = 3
    Np: ClassVar[int] = 5

    def f0(
        self,
        xold: Any,
        pold: Any,
        uold: Any,
        deltat: float | None = None,
    ) -> FloatArray:
        """Evaluate the discrete state transition."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        return np.array(
            [
                x[0] - self.CoulombCountingConstant * u[0],
                p[2] * x[1] + p[1] * (p[2] - 1.0) * u[0],
                p[4] * x[2] + p[3] * (p[4] - 1.0) * u[0],
            ],
            dtype=np.float64,
        )

    def g0(
        self,
        xold: Any,
        pold: Any,
        uold: Any,
        deltat: float | None = None,
    ) -> FloatArray:
        """Evaluate terminal voltage for the supplied state and input."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        return np.array(
            [self._interp(self.lutocv0, x[0]) - p[0] * u[0] + x[1] + x[2]],
            dtype=np.float64,
        )

    def f1x(
        self,
        xold: Any,
        pold: Any,
        uold: Any,
        deltat: float | None = None,
    ) -> FloatArray:
        """Return the state-transition Jacobian with respect to state."""

        self.state(xold)
        p = self.parameters(pold)
        self.input(uold)

        return np.diag([1.0, p[2], p[4]]).astype(np.float64)

    def f1p(
        self,
        xold: Any,
        pold: Any,
        uold: Any,
        deltat: float | None = None,
    ) -> FloatArray:
        """Return the exact transition Jacobian with respect to parameters."""

        x = self.state(xold)
        p = self.parameters(pold)
        u = self.input(uold)

        result = np.zeros((self.Nx, self.Np), dtype=np.float64)
        result[1, 1] = (p[2] - 1.0) * u[0]
        result[1, 2] = x[1] + p[1] * u[0]
        result[2, 3] = (p[4] - 1.0) * u[0]
        result[2, 4] = x[2] + p[3] * u[0]
        return result

    def g1x(
        self,
        xold: Any,
        pold: Any,
        uold: Any,
        deltat: float | None = None,
    ) -> FloatArray:
        """Return the output Jacobian with respect to state."""

        x = self.state(xold)
        self.parameters(pold)
        self.input(uold)

        return np.array(
            [[self._interp(self.lutocv1, x[0]), 1.0, 1.0]],
            dtype=np.float64,
        )

    def g1p(
        self,
        xold: Any,
        pold: Any,
        uold: Any,
        deltat: float | None = None,
    ) -> FloatArray:
        """Return the output Jacobian with respect to parameters."""

        self.state(xold)
        self.parameters(pold)
        u = self.input(uold)

        return np.array([[-u[0], 0.0, 0.0, 0.0, 0.0]], dtype=np.float64)

    @classmethod
    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        """Project resistances and decay coefficients onto valid bounds."""

        result = as_float_vector(parameters, name="parameters")
        if result.size != cls.Np:
            raise ValueError(f"parameters must have length {cls.Np}, got {result.size}")

        for index, label in ((0, "R0"), (1, "R1"), (3, "R2")):
            if result[index] <= 0.0:
                warnings.warn(
                    f"{cls.__name__}: {label} must be positive; using {cls.zerohere:g}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                result[index] = cls.zerohere

        for index, label in ((2, "A1"), (4, "A2")):
            if result[index] <= 0.0:
                warnings.warn(
                    f"{cls.__name__}: {label} must be in (0, 1); using {cls.zerohere:g}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                result[index] = cls.zerohere
            elif result[index] >= 1.0:
                warnings.warn(
                    f"{cls.__name__}: {label} must be in (0, 1); using 1 - zerohere",
                    RuntimeWarning,
                    stacklevel=2,
                )
                result[index] = 1.0 - cls.zerohere

        return result
