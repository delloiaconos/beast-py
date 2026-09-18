"""Tests for :class:`beast.generators.Generator_ConstantValue`."""

import numpy as np
import pytest

from beast.generators import Generator_ConstantValue, Generator


def test_generator_constant_value_implements_generator():
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


@pytest.mark.parametrize("t_start", [None, np.nan, np.inf, -np.inf, -1.0])
def test_generator_constant_value_tstart_is_valid(t_start):
    kwargs = {"value": 1.0, "t_start": t_start, "t_stop": np.inf, "delta_t": 0.1}
    with pytest.raises(ValueError):
        Generator_ConstantValue(**kwargs)

@pytest.mark.parametrize("t_stop", [None, np.nan, -np.inf, -1.0, 0.0, 0.5, 0.9])
def test_generator_constant_value_tstop_is_valid(t_stop):
    kwargs = {"value": 1.0, "t_start": 0.0, "t_stop": t_stop, "delta_t": 1.0}
    with pytest.raises(ValueError):
        Generator_ConstantValue(**kwargs)

@pytest.mark.parametrize("delta_t", [None, np.nan, -np.inf, np.inf, -1.0, 0.0, 1.0, 2.0])
def test_generator_constant_value_deltat_is_valid(delta_t):
    kwargs = {"value": 1.0, "t_start": 0.0, "t_stop": 1.0, "delta_t": delta_t}
    with pytest.raises(ValueError):
        Generator_ConstantValue(**kwargs)

def test_generator_constant_value_must_contain_at_least_one_sample():
    with pytest.raises(ValueError, match="must be less than"):
        Generator_ConstantValue(1.0, t_start=0.0, t_stop=0.5, delta_t=1.0)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf, None])
def test_generator_constant_value_must_be_real(value):
    kwargs = {"value": value, "t_start": 0.0, "t_stop": np.inf, "delta_t": 0.1}
    with pytest.raises(ValueError, match="value"):
        Generator_ConstantValue(**kwargs)