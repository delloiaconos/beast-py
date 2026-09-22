from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest

import beast.estimators as estimators_package
from beast.estimators.estimator import Estimator
from beast.estimators.factory import ESTIMATOR_REGISTRY

def _concrete_estimator_classes() -> set[type[Estimator]]:
    classes: set[type[Estimator]] = set()

    for module_info in pkgutil.iter_modules(estimators_package.__path__):
        module = importlib.import_module(
            f"{estimators_package.__name__}.{module_info.name}"
        )

        for _, obj in inspect.getmembers(module, inspect.isclass):
            # Ignore classes merely imported by the module.
            if obj.__module__ != module.__name__:
                continue

            # Ignore the abstract base Estimator itself.
            if obj is Estimator:
                continue

            if issubclass(obj, Estimator) and not inspect.isabstract(obj):
                classes.add(obj)

    return classes


def test_estimator_all_classes_are_registered():
    implemented = _concrete_estimator_classes()
    registered = set(ESTIMATOR_REGISTRY.values())

    missing = implemented - registered

    assert not missing, (
        "Estimator classes missing from ESTIMATOR_REGISTRY: "
        + ", ".join(sorted(cls.__name__ for cls in missing))
    )