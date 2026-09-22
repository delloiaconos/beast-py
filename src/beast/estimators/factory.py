"""Estimator selection factory"""

from __future__ import annotations

from typing import TypeAlias

from beast.estimators.estimator import Estimator
from beast.estimators.ekf_dual import EKFdual
from beast.estimators.enhanced_mix_algorithm import EnhancedMixAlgorithm
from beast.estimators.mix_algorithm import MixAlgorithm
from beast.estimators.open_loop import OpenLoop

from beast.cell_models.cell_model import CellModel

EstimatorClass: TypeAlias = type[Estimator]

ESTIMATOR_REGISTRY: dict[str, EstimatorClass] = {
    "EKFDUAL": EKFdual,
    "MIXALGORITHM": MixAlgorithm,
    "ENHANCEDMIXALGORITHM": EnhancedMixAlgorithm,
    "OPENLOOP": OpenLoop,
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
    
    return selectEstimator(selector)(cell_model, delta_t)
