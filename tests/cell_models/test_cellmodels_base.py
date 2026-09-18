"""Contract tests for the BEAST base cell model.

These tests intentionally focus on the architectural contract of CellModel.
Model-specific numerical behavior should be tested in the concrete cell-model
test modules.
"""

from __future__ import annotations

import inspect

import pytest

from beast.cell_models.base import CellModel


def test_cell_model_is_a_class() -> None:
    """CellModel must be defined as a class."""
    assert inspect.isclass(CellModel)


def test_cell_model_is_abstract() -> None:
    """The cell model must not be a concrete battery model."""
    assert inspect.isabstract(CellModel), (
        "CellModel should be an abstract base class so that concrete cell "
        "models explicitly implement the required model contract."
    )


def test_cell_model_defines_abstract_operations() -> None:
    """At least one operation must be required from concrete cell models."""
    abstract_methods = getattr(CellModel, "__abstractmethods__", frozenset())

    assert abstract_methods, (
        "CellModel does not define any abstract methods. "
        "A base model should declare the operations that concrete models "
        "are required to implement."
    )


@pytest.mark.parametrize(
    "method_name",
    sorted(getattr(CellModel, "__abstractmethods__", frozenset())),
)
def test_abstract_operations_exist_and_are_callable(method_name: str) -> None:
    """Every declared abstract operation must exist and be callable."""
    operation = getattr(CellModel, method_name, None)

    assert operation is not None, f"Missing abstract operation: {method_name}"
    assert callable(operation), f"Abstract operation {method_name!r} is not callable"


def test_abstract_operations_are_marked_as_abstract() -> None:
    """Declared abstract operations must retain the ABC marker."""
    for method_name in CellModel.__abstractmethods__:
        operation = getattr(CellModel, method_name)

        assert getattr(operation, "__isabstractmethod__", False), (
            f"{method_name!r} is listed in __abstractmethods__ but is not "
            "marked with @abstractmethod."
        )


def test_cell_model_cannot_be_instantiated_directly() -> None:
    """Instantiating the abstract base class must fail."""
    with pytest.raises(TypeError):
        CellModel()


def test_cell_model_has_documentation() -> None:
    """The public base model should document its purpose and contract."""
    assert CellModel.__doc__ is not None
    assert CellModel.__doc__.strip()


def test_cell_model_abstract_methods_have_documentation() -> None:
    """Abstract methods should document the contract for implementers."""
    undocumented = []

    for method_name in CellModel.__abstractmethods__:
        operation = getattr(CellModel, method_name)
        if not inspect.getdoc(operation):
            undocumented.append(method_name)

    assert not undocumented, (
        "The following CellModel abstract methods have no docstring: "
        + ", ".join(sorted(undocumented))
    )
