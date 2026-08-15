"""NumPy array utilities for BEAST.

This module contains shared helpers for array conversion, shape normalization,
validation, and other NumPy-oriented operations used throughout the toolkit.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
"""One- or two-dimensional NumPy array containing ``float64`` values."""

IntArray = NDArray[np.int32]
"""One- or two-dimensional NumPy array containing ``int32`` values."""

_MISSING = object()


def as_float_vector(value: Any, *, name: str = "value") -> FloatArray:
    """Return *value* as a writable one-dimensional ``float64`` array.

    Args:
        value: Scalar, sequence, or NumPy array.
        name: Name included in validation errors.

    Returns:
        A copied vector with shape ``(n,)``.

    Raises:
        ValueError: If the input is empty or cannot be represented as a vector.
    """

    array = np.asarray(value, dtype=np.float64)
    if array.size == 0:
        raise ValueError(f"{name} must not be empty")
    if array.ndim > 2 or (array.ndim == 2 and 1 not in array.shape):
        raise ValueError(f"{name} must be a scalar or vector, got shape {array.shape}")
    return np.array(array.reshape(-1), dtype=np.float64, copy=True)


def as_float_matrix(value: Any, *, name: str = "value") -> FloatArray:
    """Return *value* as a writable two-dimensional ``float64`` array."""

    array = np.asarray(value, dtype=np.float64)
    if array.ndim == 0:
        array = array.reshape(1, 1)
    elif array.ndim == 1:
        array = array.reshape(-1, 1)
    elif array.ndim != 2:
        raise ValueError(f"{name} must be a matrix, got shape {array.shape}")
    return np.array(array, dtype=np.float64, copy=True)


def as_history_matrix(value: Any, *, name: str = "value") -> FloatArray:
    """Return a variables-by-samples history matrix.

    A one-dimensional input is interpreted as one variable sampled over time
    and therefore becomes shape ``(1, n)``.
    """

    array = np.asarray(value, dtype=np.float64)
    if array.ndim == 0:
        array = array.reshape(1, 1)
    elif array.ndim == 1:
        array = array.reshape(1, -1)
    elif array.ndim != 2:
        raise ValueError(f"{name} must be a vector or matrix, got shape {array.shape}")
    return np.array(array, dtype=np.float64, copy=True)


def scalar_from(value: Any, *, name: str = "value") -> float:
    """Extract one Python ``float`` from a scalar-like object."""

    vector = as_float_vector(value, name=name)
    if vector.size != 1:
        raise ValueError(f"{name} must contain exactly one value, got {vector.size}")
    return float(vector[0])


def get_field(source: Mapping[str, Any] | Any, name: str) -> Any:
    """Read a field from a dictionary or an attribute-based compatibility object.

    Args:
        source: Plain mapping or object exposing attributes.
        name: Required key or attribute name.

    Raises:
        KeyError: If *name* is not available.
    """

    if isinstance(source, Mapping):
        try:
            return source[name]
        except KeyError as exc:
            raise KeyError(f"Required field {name!r} is missing") from exc
    if hasattr(source, name):
        return getattr(source, name)
    raise KeyError(f"Required field {name!r} is missing")


def get_optional_field(
    source: Mapping[str, Any] | Any,
    name: str,
    default: Any = None,
) -> Any:
    """Read an optional mapping key or object attribute."""

    if isinstance(source, Mapping):
        return source.get(name, default)
    return getattr(source, name, default)


def get_first_field(
    source: Mapping[str, Any] | Any,
    names: Sequence[str],
    *,
    default: Any = _MISSING,
) -> Any:
    """Return the first available field among *names*.

    This helper is useful at the MATLAB compatibility boundary where the same
    value can have a modern Python name and a legacy workspace name.
    """

    for name in names:
        try:
            return get_field(source, name)
        except KeyError:
            continue
    if default is not _MISSING:
        return default
    choices = ", ".join(repr(name) for name in names)
    raise KeyError(f"None of the required fields are available: {choices}")
