"""Estimator selection factory"""

from __future__ import annotations

from typing import TypeAlias

from beast.cell_models.base import CellModel

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

def createEstimator(
    selector: str,
    cell_model: CellModel,
    delta_t: float,
) -> Estimator:
    """Instantiate an estimator selected by its legacy token."""

    normalized = selector.strip().upper().replace("_", "")
    if normalized.startswith("ESTIMATOR"):
        normalized = normalized.removeprefix("ESTIMATOR")
    
    try:
        estimator_class = ESTIMATOR_REGISTRY[normalized]
    except KeyError as exc:
        choices = ", ".join(sorted(ESTIMATOR_REGISTRY))
        raise ValueError(f"Unknown estimator {selector!r}; choose one of {choices}") from exc
    return estimator_class(cell_model, delta_t)
