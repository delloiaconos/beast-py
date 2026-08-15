from __future__ import annotations

import pytest

from beast.estimators import createEstimator, ESTIMATOR_REGISTRY

def test_estimator_selector_accepts_class_name():
    assert createEstimator(" EKFDUAL ", cell_model=None, delta_t=0.1) is ESTIMATOR_REGISTRY["EKFDUAL"]

def test_unknown_estimator_has_actionable_error():
    with pytest.raises(ValueError, match="Unknown estimator"):
        createEstimator("missing", cell_model=None, delta_t=0.1)
