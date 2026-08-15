"""Estimator selection factory"""

from __future__ import annotations

from typing import TypeAlias

from beast.cell_models.base import CellModel

from beast.cell_models.factory import CELL_MODEL_REGISTRY
from beast.cell_models.factory import CELL_MODEL_REGISTRY
from beast.estimators.base import Estimator
from beast.estimators.ekf_dual import Estimator_EKFdual
from beast.estimators.enhanced_mix_algorithm import Estimator_EnhancedMixAlgorithm
from beast.estimators.mix_algorithm import Estimator_MixAlgorithm
from beast.estimators.open_loop import Estimator_OpenLoop

EstimatorClass: TypeAlias = type[Estimator]

ESTIMATOR_REGISTRY: dict[str, EstimatorClass] = {
    "EKFDUAL": Estimator_EKFdual,
    "MIXALGORITHM": Estimator_MixAlgorithm,
    "ENHANCEDMIXALGORITHM": Estimator_EnhancedMixAlgorithm,
    "OPENLOOP": Estimator_OpenLoop,
}


def selectEstimator(selector: str) -> EstimatorClass:
    """Return the estimator class selected by a MATLAB-style name.

    Raises:
        ValueError: If no converted estimator matches the selector.
    """

    normalized = selector.strip().upper()
    if normalized.startswith("ESTIMATOR_"):
        normalized = normalized.removeprefix("ESTIMATOR_")
    try:
        return ESTIMATOR_REGISTRY[normalized]
    except KeyError as exc:
        choices = ", ".join(sorted(ESTIMATOR_REGISTRY))
        raise ValueError(f"Unknown estimator {selector!r}; choose one of {choices}") from exc


def createEstimator(
    selector: str,
    cell_model: CellModel,
    delta_t: float,
) -> Estimator:
    """Select an estimator selected by its legacy token."""

    estimator_class = selectEstimator(selector)

    return estimator_class(cell_model, delta_t)
