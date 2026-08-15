"""Tests for the BEAST core package."""

from __future__ import annotations

import importlib

import pytest


CORE_MODULES = (
    "beast.core",
    "beast.core.arrays",
)


@pytest.mark.parametrize("module_name", CORE_MODULES)
def test_core_modules_import(module_name: str) -> None:
    """All core modules should import without raising exceptions."""
    module = importlib.import_module(module_name)
    assert module is not None


@pytest.mark.parametrize("module_name", CORE_MODULES)
def test_core_modules_have_docstrings(module_name: str) -> None:
    """Core modules should provide basic module-level documentation."""
    module = importlib.import_module(module_name)

    assert module.__doc__ is not None
    assert module.__doc__.strip()


def test_core_package_is_available_from_beast() -> None:
    """The core package should be importable through the BEAST namespace."""
    import beast.core

    assert beast.core is not None
