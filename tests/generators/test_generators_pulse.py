"""Tests for :class:`beast.generators.PulseGenerator`."""

import numpy as np
import pytest

from beast.generators import Generator, Generator_Pulse

@pytest.fixture
def generator() -> Generator_Pulse:
    return Generator_Pulse(
        t_start=0.0,
        t_stop=10.0,
        delta_t=1.0,
        t_high=5.0,
        t_low=5.0,
        v_high=10.0,
        v_low=-10.0,
    )

def test_generator_pulse_implements_profile_generator(generator):
    assert isinstance(generator, Generator)

def test_generator_pulse_simeple_pulses(generator):
    t_all, v_all = generator.generate()

    np.testing.assert_array_equal(t_all, np.arange(10, dtype=np.float64))
    np.testing.assert_allclose(
        v_all,
        np.array([10.0, 10.0, 10.0, 10.0, 10.0, -10.0, -10.0, -10.0, -10.0, -10.0]),
    )

# Base Class Tests:

@pytest.mark.parametrize("t_start", [None, np.nan, np.inf, -np.inf, -1.0])
def test_generator_pulses_tstart_is_valid(t_start):
    kwargs = { "t_start": t_start, "t_stop": np.inf, "delta_t": 0.1,
               "v_high": 1.0, "v_low": -1.0, "t_high": 1.0, "t_low": 1.0 }
    with pytest.raises(ValueError):
        Generator_Pulse(**kwargs)

@pytest.mark.parametrize("t_stop", [None, np.nan, -np.inf, -1.0, 0.0, 0.5, 0.9])
def test_generator_pulses_tstop_is_valid(t_stop):
    kwargs = {"t_start": 0.0, "t_stop": t_stop, "delta_t": 1.0,
              "v_high": 1.0, "v_low": -1.0, "t_high": 1.0, "t_low": 1.0 }
    with pytest.raises(ValueError):
        Generator_Pulse(**kwargs)

@pytest.mark.parametrize("delta_t", [None, np.nan, -np.inf, np.inf, -1.0, 0.0, 1.0, 2.0])
def test_generator_pulses_deltat_is_valid(delta_t):
    kwargs = {"t_start": 0.0, "t_stop": 1.0, "delta_t": delta_t,
              "v_high": 1.0, "v_low": -1.0, "t_high": 1.0, "t_low": 1.0 }
    with pytest.raises(ValueError):
        Generator_Pulse(**kwargs)


@pytest.mark.parametrize("name", ["v_high", "v_low", "t_high", "t_low"])
@pytest.mark.parametrize("value", [None, np.nan, np.inf, -np.inf])
def test_generator_pulse_parameters_are_validated(name, value):
    kwargs = { "v_high": 1.0, "v_low": -1.0, "t_high": 1.0, "t_low": 1.0 }
    kwargs[name] = value

    with pytest.raises(ValueError):
        Generator_Pulse(**kwargs)

@pytest.mark.parametrize("name", ["t_high", "t_low"])
@pytest.mark.parametrize("value", [None, np.nan, np.inf, -np.inf, -1.0, -10.0, 0.0])
def test_generator_pulse_times_are_validated(name, value):
    kwargs = { "v_high": 1.0, "v_low": -1.0, "t_high": 1.0, "t_low": 1.0 }
    kwargs[name] = value

    with pytest.raises(ValueError):
        Generator_Pulse(**kwargs)
