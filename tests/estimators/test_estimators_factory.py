from __future__ import annotations

import inspect
import pytest


from beast.estimators.estimator import Estimator
from beast.estimators.factory import createEstimator, selectEstimator, ESTIMATOR_REGISTRY

from tests.helpers.cell_models import Dummy

def _mixed_case(value: str) -> str:
    return "".join(
        char.upper() if i % 2 == 0 else char.lower()
        for i, char in enumerate(value)
    )

@pytest.mark.parametrize("selector, estimator_class", ESTIMATOR_REGISTRY.items())
def test_estimator_factory_selects_correct_estimator(selector, estimator_class):
    variants = (
        selector,
        selector.lower(),
        selector.upper(),
        selector.swapcase(),
        _mixed_case(selector),
        f"  {selector}  ",
        f"  {selector.lower()}  ",
        f"  {selector.swapcase()}  ",
        f"  {_mixed_case(selector)}  ",
    )

    for variant in variants:
        assert selectEstimator(variant) is estimator_class


@pytest.mark.parametrize("selector, estimator_class", ESTIMATOR_REGISTRY.items())
def test_estimator_factory_registry_entries_are_estimator_classes(
    selector,
    estimator_class,
):
    assert inspect.isclass(estimator_class), (
        f"{selector} is not registered as a class"
    )

    assert issubclass(estimator_class, Estimator), (
        f"{selector} does not reference an Estimator subclass"
    )


def test_estimator_factory_create_rejects_none_model():
    with pytest.raises(TypeError):
        createEstimator(" EKFDUAL ", cell_model=None, delta_t=0.1)


def test_estimator_factory_create_rejects_invalid_model():
    with pytest.raises(TypeError):
        createEstimator(" EKFDUAL ", cell_model=object(), delta_t=0.1)

def test_estimator_factory_create_has_actionable_error():
    with pytest.raises(ValueError, match="Unknown estimator"):
        createEstimator("missing", cell_model=None, delta_t=0.1)


def test_estimator_factory_create_rejects_zero_delta_t():
    with pytest.raises(ValueError):
        createEstimator(" EKFDUAL ", cell_model=Dummy(), delta_t=0.0)


def test_estimator_factory_create_rejects_nan_delta_t():
    with pytest.raises(ValueError):
        createEstimator(" EKFDUAL ", cell_model=Dummy(), delta_t=float("nan"))


def test_estimator_factory_create_rejects_infinite_delta_t():
    with pytest.raises(ValueError):
        createEstimator(" EKFDUAL ", cell_model=Dummy(), delta_t=float("inf"))
