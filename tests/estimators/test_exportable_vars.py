"""Tests for estimator export metadata shared with the MATLAB implementation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from beast.cell_models import R0R1C1
from beast.estimators import ExposrtableVars, createEstimator
from conftest import covariance_for
from tests.helpers.cell_models import Dummy


@pytest.mark.parametrize(
    "selector, expected",
    [
        (
            "OPENLOOP",
            [
                ("xPold", "Nx", "xP_all", False),
                ("pPold", "Np", "pP_all", False),
            ],
        ),
        (
            "MIXALGORITHM",
            [
                ("xPold", "Nx", "xP_all", False),
                ("pPold", "Np", "pP_all", False),
                ("Lxold", "Nx", "Lx_all", False),
            ],
        ),
        (
            "ENHANCEDMIXALGORITHM",
            [
                ("xPold", "Nx", "xP_all", False),
                ("pPold", "Np", "pP_all", False),
            ],
        ),
        (
            "EKFDUAL",
            [
                ("xPold", "Nx", "xP_all", False),
                ("pPold", "Np", "pP_all", False),
                ("Lxold", "Nx", "Lx_all", False),
                ("Lpold", "Np", "Lp_all", False),
                ("sxPold", "Nx", "sxP_all", True),
                ("spPold", "Np", "spP_all", True),
                ("dyold", 1, "dy_all", False),
                ("xPold", 1, "SoC", True),
            ],
        ),
    ],
)
def test_exportable_vars_match_matlab_schema(selector, expected) -> None:
    estimator = createEstimator(selector, Dummy(), 0.1)

    assert not hasattr(estimator, "AvailablesVars")
    assert estimator.exportable_variables == estimator.ExportableVars
    assert all(isinstance(item, ExposrtableVars) for item in estimator.ExportableVars)

    actual = [
        (
            item.ClassVar,
            item.Size,
            item.ExportName,
            item.FunctionHandler is not None,
        )
        for item in estimator.ExportableVars
    ]
    resolved_expected = [
        (
            class_var,
            getattr(estimator, size) if isinstance(size, str) else size,
            export_name,
            has_handler,
        )
        for class_var, size, export_name, has_handler in expected
    ]

    assert actual == resolved_expected
    assert all(item.Save is True for item in estimator.ExportableVars)


def test_export_handlers_produce_declared_sizes() -> None:
    estimator = createEstimator("EKFDUAL", Dummy(), 0.1)
    values = {
        "sxPold": np.eye(estimator.Nx),
        "spPold": np.eye(estimator.Np),
        "xPold": np.arange(estimator.Nx, dtype=float),
    }

    for item in estimator.ExportableVars:
        if item.FunctionHandler is None:
            continue
        exported = np.asarray(item.FunctionHandler(values[item.ClassVar]))
        assert exported.size == item.Size


@pytest.mark.parametrize(
    "selector",
    ["OPENLOOP", "MIXALGORITHM", "ENHANCEDMIXALGORITHM", "EKFDUAL"],
)
def test_exportable_members_exist_after_initialization(selector, model_data) -> None:
    model = R0R1C1(
        model_data,
        covariance_for(R0R1C1),
        1.0,
    )
    estimator = createEstimator(selector, model, 1.0)
    estimator.initialize(
        np.array([0.8, 0.0]),
        np.array([0.01, 0.02, 1000.0]),
        np.array([1.0]),
        np.array([4.0]),
        0.0,
    )

    assert all(hasattr(estimator, item.ClassVar) for item in estimator.ExportableVars)


def test_exposrtable_vars_is_frozen() -> None:
    metadata = ExposrtableVars("xPold", 2, "xP_all", True)

    with pytest.raises(FrozenInstanceError):
        metadata.Size = 3


@pytest.mark.parametrize("invalid_size", [-1, 1.5, True])
def test_exposrtable_vars_rejects_invalid_size(invalid_size) -> None:
    with pytest.raises(ValueError):
        ExposrtableVars("xPold", invalid_size, "xP_all", True)
