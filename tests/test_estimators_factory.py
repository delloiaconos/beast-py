from __future__ import annotations

import pytest

from beast.estimators.factory import createEstimator, selectEstimator, ESTIMATOR_REGISTRY

from tests.helpers.cell_models import CellModel_Dummy

def test_estimator_selector_accepts_class_name():
    assert selectEstimator(" EKFDUAL " ) is ESTIMATOR_REGISTRY["EKFDUAL"]


def test_estimator_rejects_none_model():
    with pytest.raises(TypeError):
        createEstimator(" EKFDUAL ", cell_model=None, delta_t=0.1)


def test_estimator_rejects_invalid_model():
    with pytest.raises(TypeError):
        createEstimator(" EKFDUAL ", cell_model=object(), delta_t=0.1)

def test_unknown_estimator_has_actionable_error():
    with pytest.raises(ValueError, match="Unknown estimator"):
        createEstimator("missing", cell_model=None, delta_t=0.1)


def test_estimator_rejects_zero_delta_t():
    with pytest.raises(ValueError):
        createEstimator(" EKFDUAL ", cell_model=CellModel_Dummy(), delta_t=0.0)


def test_estimator_rejects_nan_delta_t():
    with pytest.raises(ValueError):
        createEstimator(" EKFDUAL ", cell_model=CellModel_Dummy(), delta_t=float("nan"))


def test_estimator_rejects_infinite_delta_t():
    with pytest.raises(ValueError):
        createEstimator(" EKFDUAL ", cell_model=CellModel_Dummy(), delta_t=float("inf"))
