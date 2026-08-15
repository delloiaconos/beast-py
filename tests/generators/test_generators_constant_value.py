"""Tests for :class:`beast.generators.Generator_ConstantValue`."""

import numpy as np
import pytest

from beast.generators import Generator_ConstantValue, Generator


def test_generator_constant_value_implements_profile_generator():
    generator = Generator_ConstantValue(2.5)
    assert isinstance(generator, Generator)


def test_generate_constant_value_profile():
    generator = Generator_ConstantValue(-4.0, t_start=0.0, t_stop=2.5, delta_t=0.5)

    time, values = generator.generate()

    print( f"Time: {time}, Values: {values}" )
    np.testing.assert_allclose(time, [0.0, 0.5, 1.0, 1.5, 2.0])
    np.testing.assert_allclose(values, [-4.0] * 5)
    assert time.dtype == np.float64
    assert values.dtype == np.float64


def test_generator_constant_value_uses_complete_samples_only():
    generator = Generator_ConstantValue(1.0, t_start=0.0, t_stop=2.9, delta_t=1.0)
    time, values = generator.generate()
    np.testing.assert_allclose(time, [0.0, 1.0])
    np.testing.assert_allclose(values, [1.0, 1.0])


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_generator_constant_value_must_be_finite(value):
    with pytest.raises(ValueError, match="value"):
        Generator_ConstantValue(value)


@pytest.mark.parametrize("name", ["t_start", "delta_t"])
@pytest.mark.parametrize("value", [-1.0, np.nan, np.inf, -np.inf])
def test_generator_constant_value_positive_parameters_are_validated(name, value):
    kwargs = {"t_start": 0.0, "t_stop": 1.0, "delta_t": 0.1}
    kwargs[name] = value
    with pytest.raises(ValueError):
        Generator_ConstantValue(1.0, **kwargs)


def test_generator_constant_value_must_contain_at_least_one_sample():
    with pytest.raises(ValueError, match="must be less than"):
        Generator_ConstantValue(1.0, t_start=0.0, t_stop=0.5, delta_t=1.0)
