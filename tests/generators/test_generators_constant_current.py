"""Tests for :class:`beast.generators.Generator_ConstantCurrent`."""

import numpy as np
import pytest

from beast.generators import Generator_ConstantCurrent, Generator


def test_generator_constant_current_implements_profile_generator():
    generator = Generator_ConstantCurrent(2.5, duration=3.0, delta_t=1.0)
    assert isinstance(generator, Generator)


def test_generate_constant_current_profile():
    generator = Generator_ConstantCurrent(-4.0, duration=2.5, delta_t=0.5)

    time, current = generator.generate()

    np.testing.assert_allclose(time, [0.0, 0.5, 1.0, 1.5, 2.0])
    np.testing.assert_allclose(current, [-4.0] * 5)
    assert time.dtype == np.float64
    assert current.dtype == np.float64


def test_generator_constant_current_duration_uses_complete_samples_only():
    generator = Generator_ConstantCurrent(1.0, duration=2.9, delta_t=1.0)
    time, current = generator.generate()
    np.testing.assert_allclose(time, [0.0, 1.0])
    np.testing.assert_allclose(current, [1.0, 1.0])


@pytest.mark.parametrize("current", [np.nan, np.inf, -np.inf])
def test_generator_constant_current_current_must_be_finite(current):
    with pytest.raises(ValueError, match="current"):
        Generator_ConstantCurrent(current, duration=1.0, delta_t=0.1)


@pytest.mark.parametrize("name", ["duration", "delta_t"])
@pytest.mark.parametrize("value", [0.0, -1.0, np.nan, np.inf, -np.inf])
def test_generator_constant_current_positive_parameters_are_validated(name, value):
    kwargs = {"duration": 1.0, "delta_t": 0.1}
    kwargs[name] = value
    with pytest.raises(ValueError):
        Generator_ConstantCurrent(1.0, **kwargs)


def test_generator_constant_current_duration_must_contain_at_least_one_sample():
    with pytest.raises(ValueError, match="at least one sample"):
        Generator_ConstantCurrent(1.0, duration=0.5, delta_t=1.0)
