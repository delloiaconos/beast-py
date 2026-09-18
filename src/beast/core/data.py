"""Core data handling utilities for BEAST.

This module is intended for shared data containers, normalization helpers,
validation routines, and data-oriented utilities used throughout the toolkit.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias

import numpy as np

from beast.core.arrays import (
    as_float_matrix,
    get_field,
)

PlainData: TypeAlias = dict[str, Any]
"""Basic dictionary containing Python values and NumPy arrays."""

InputData: TypeAlias = dict[str, Any]
"""Validated input dataset represented as a plain dictionary."""

ResultData: TypeAlias = dict[str, Any]
"""Estimator histories represented as a plain dictionary."""

ConfigData: TypeAlias = dict[str, Any]
"""Validated processing or post-processing options as a plain dictionary."""

_RESULT_ARRAY_NAMES = (
    "xP_all",
    "pP_all",
    "sxP_all",
    "spP_all",
    "Lx_all",
    "Lp_all",
)

def normalize_covariance(
    covariance: Mapping[str, Any] | Any,
    *,
    nx: int,
    np: int,
    ny: int,
) -> PlainData:
    """Validate covariance fields and return independent NumPy matrices.

    Args:
        covariance: Mapping or compatibility object exposing ``sxW``, ``sxV``,
            ``spR``, and ``spE``.
        nx: Number of model states.
        np: Number of estimated parameters.
        ny: Number of measured outputs.

    Returns:
        A dictionary whose four values are writable ``float64`` matrices.
    """

    matrices = {
        "sxW": as_float_matrix(get_field(covariance, "sxW"), name="sxW"),
        "sxV": as_float_matrix(get_field(covariance, "sxV"), name="sxV"),
        "spR": as_float_matrix(get_field(covariance, "spR"), name="spR"),
        "spE": as_float_matrix(get_field(covariance, "spE"), name="spE"),
    }
    expected = {
        "sxW": (nx, nx),
        "sxV": (ny, ny),
        "spR": (np, np),
        "spE": (ny, ny),
    }
    for name, shape in expected.items():
        if matrices[name].shape != shape:
            raise ValueError(f"{name} must have shape {shape}, got {matrices[name].shape}")
    return matrices

