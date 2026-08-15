"""Current-pulse profile generation."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from beast.core.arrays import FloatArray
from beast.generators.base import Generator


class Generator_Pulse(Generator):
    """Generate a current-pulse profile from a sequence of SOC targets.

    Each transition between consecutive SOC targets is split into increments of
    ``delta_soc`` percentage points.  Every increment produces one constant-
    current pulse followed by an optional zero-current rest period.

    Positive current denotes discharge and negative current denotes charge.

    Args:
        soc_percent_history: Sequence of SOC targets expressed as percentages.
        delta_soc: SOC increment magnitude in percentage points.
        delta_t: Sampling interval in seconds.
        t_on: Active-current duration of each pulse in seconds.
        t_off: Rest duration after each pulse in seconds.
        q_nominal_coulomb: Nominal cell charge in coulombs.
    """

    def __init__(
        self,
        soc_percent_history: Sequence[float],
        *,
        delta_soc: float,
        delta_t: float,
        t_on: float,
        t_off: float,
        q_nominal_coulomb: float,
    ) -> None:
        self._soc_percent_history = self._validate_history(soc_percent_history)
        self._delta_soc = self._validate_positive_finite(delta_soc, "delta_soc")
        self._delta_t = self._validate_positive_finite(delta_t, "delta_t")
        self._t_on = self._validate_positive_finite(t_on, "t_on")
        self._t_off = self._validate_nonnegative_finite(t_off, "t_off")
        self._q_nominal_coulomb = self._validate_positive_finite(
            q_nominal_coulomb,
            "q_nominal_coulomb",
        )

        if self.n_on_samples <= 0:
            raise ValueError("t_on / delta_t must produce at least one sample")

    @property
    def soc_percent_history(self) -> FloatArray:
        """Return a copy of the configured SOC targets."""
        return self._soc_percent_history.copy()

    @property
    def delta_soc(self) -> float:
        return self._delta_soc

    @property
    def delta_t(self) -> float:
        return self._delta_t

    @property
    def t_on(self) -> float:
        return self._t_on

    @property
    def t_off(self) -> float:
        return self._t_off

    @property
    def q_nominal_coulomb(self) -> float:
        return self._q_nominal_coulomb

    @property
    def n_on_samples(self) -> int:
        """Number of active-current samples in each pulse."""
        return int(np.floor(self._t_on / self._delta_t))

    @property
    def n_off_samples(self) -> int:
        """Number of zero-current samples after each pulse."""
        return int(np.floor(self._t_off / self._delta_t))

    def generate(self) -> tuple[FloatArray, FloatArray]:
        """Generate equispaced time and current vectors."""
        soc_steps = self._build_soc_steps()
        soc_changes = np.diff(soc_steps)

        n_on = self.n_on_samples
        n_off = self.n_off_samples
        samples_per_pulse = n_on + n_off

        current_levels = (
            -soc_changes
            / 100.0
            * self._q_nominal_coulomb
            / (n_on * self._delta_t)
        )

        if current_levels.size == 0:
            return (
                np.empty(0, dtype=np.float64),
                np.empty(0, dtype=np.float64),
            )

        current = np.concatenate(
            [
                np.concatenate(
                    [
                        np.full(n_on, level, dtype=np.float64),
                        np.zeros(n_off, dtype=np.float64),
                    ]
                )
                for level in current_levels
            ]
        )
        time = np.arange(current.size, dtype=np.float64) * self._delta_t

        expected_size = current_levels.size * samples_per_pulse
        if current.size != expected_size:
            raise RuntimeError("Generated pulse profile has inconsistent length")

        return time, current

    def _build_soc_steps(self) -> FloatArray:
        steps = [float(self._soc_percent_history[0])]
        for target in self._soc_percent_history[1:]:
            interval = self._inclusive_soc_steps(
                steps[-1],
                float(target),
                self._delta_soc,
            )
            steps.extend(interval[1:].tolist())
        return np.asarray(steps, dtype=np.float64)

    @staticmethod
    def _inclusive_soc_steps(start: float, stop: float, step: float) -> FloatArray:
        """Return SOC steps including both endpoints and a partial final step."""
        if np.isclose(start, stop):
            return np.asarray([start], dtype=np.float64)

        direction = 1.0 if stop > start else -1.0
        count = int(np.floor(abs(stop - start) / step))
        values = start + direction * step * np.arange(count + 1, dtype=np.float64)

        if not np.isclose(values[-1], stop):
            values = np.append(values, stop)
        else:
            values[-1] = stop

        return np.asarray(values, dtype=np.float64)

    @staticmethod
    def _validate_history(values: Sequence[float]) -> FloatArray:
        history = np.asarray(values, dtype=np.float64).reshape(-1)
        if history.size < 2:
            raise ValueError("soc_percent_history requires at least two values")
        if not np.all(np.isfinite(history)):
            raise ValueError("soc_percent_history must contain finite values")
        return np.array(history, dtype=np.float64, copy=True)

    @staticmethod
    def _validate_positive_finite(value: float, name: str) -> float:
        result = float(value)
        if not np.isfinite(result) or result <= 0.0:
            raise ValueError(f"{name} must be a positive finite value")
        return result

    @staticmethod
    def _validate_nonnegative_finite(value: float, name: str) -> float:
        result = float(value)
        if not np.isfinite(result) or result < 0.0:
            raise ValueError(f"{name} must be a nonnegative finite value")
        return result
