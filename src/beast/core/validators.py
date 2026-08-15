"""Validator utilities for BEAST.

This module contains shared validators.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

def validate_is_float( value: Any, name: str) -> float:
    """Return *value* as ``float`` if it is a float or can be converted to a float."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a float or convertible to a float!")
    return result

def validate_positive(value: float, name: str) -> float:
    """Return *value* as ``float`` if it is positive and finite."""
    result = validate_is_float(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be a positive value!")
    return result

def validate_finite(value: float, name: str) -> float:
    """Return *value* as ``float`` if it is finite."""
    result = validate_is_float(value, name)
    if not np.isfinite(result):
        raise ValueError(f"{name} must be a finite value!")
    return result

def validate_positive_finite(value: float, name: str) -> float:
    """Return *value* as ``float`` if it is positive and finite."""
    result = validate_finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be a positive finite value!")
    return result

def validate_nonnegative_finite(value: float, name: str) -> float:
    """Return *value* as ``float`` if it is nonnegative and finite."""
    result = validate_finite(value, name)
    if result < 0.0:
        raise ValueError(f"{name} must be a non-negative finite value!")
    return result

def validate_positive_finite(value: float, name: str) -> float:
    result = validate_is_float(value, name)
    if not np.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be a positive finite value!")
    return result

def validate_nonnegative_finite(value: float, name: str) -> float:
    result = validate_is_float(value, name)
    if not np.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be a non-negative finite value!")
    return result
