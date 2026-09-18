"""Contract tests for the BEAST base estimator.

These tests intentionally focus on the architectural contract of Estimator.
Model-specific numerical behavior should be tested in the concrete estimator
test modules.
"""

from __future__ import annotations

import inspect

import pytest

from beast.estimators.base import Estimator


def test_estimator_is_a_class() -> None:
    """Estimator must be defined as a class."""
    assert inspect.isclass(Estimator)


def test_estimator_is_abstract() -> None:
    """The estimator must not be a concrete estimator."""
    assert inspect.isabstract(Estimator), (
        "Estimator should be an abstract base class so that concrete estimators "
        "models explicitly implement the required estimator contract."
    )


def test_estimator_defines_abstract_operations() -> None:
    """At least one operation must be required from concrete estimators."""
    abstract_methods = getattr(Estimator, "__abstractmethods__", frozenset())

    assert abstract_methods, (
        "Estimator does not define any abstract methods. "
        "A base estimator should declare the operations that concrete estimators "
        "are required to implement."
    )


@pytest.mark.parametrize(
    "method_name",
    sorted(getattr(Estimator, "__abstractmethods__", frozenset())),
)
def test_abstract_operations_exist_and_are_callable(method_name: str) -> None:
    """Every declared abstract operation must exist and be callable."""
    operation = getattr(Estimator, method_name, None)

    assert operation is not None, f"Missing abstract operation: {method_name}"
    assert callable(operation), f"Abstract operation {method_name!r} is not callable"


def test_abstract_operations_are_marked_as_abstract() -> None:
    """Declared abstract operations must retain the ABC marker."""
    for method_name in Estimator.__abstractmethods__:
        operation = getattr(Estimator, method_name)

        assert getattr(operation, "__isabstractmethod__", False), (
            f"{method_name!r} is listed in __abstractmethods__ but is not "
            "marked with @abstractmethod."
        )


def test_estimator_cannot_be_instantiated_directly() -> None:
    """Instantiating the abstract base class must fail."""
    with pytest.raises(TypeError):
        Estimator()


def test_estimator_has_documentation() -> None:
    """The public base estimator should document its purpose and contract."""
    assert Estimator.__doc__ is not None
    assert Estimator.__doc__.strip()


def test_estimator_abstract_methods_have_documentation() -> None:
    """Abstract methods should document the contract for implementers."""
    undocumented = []

    for method_name in Estimator.__abstractmethods__:
        operation = getattr(Estimator, method_name)
        if not inspect.getdoc(operation):
            undocumented.append(method_name)

    assert not undocumented, (
        "The following Estimator abstract methods have no docstring: "
        + ", ".join(sorted(undocumented))
    )
