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


def test_generator_pulse_discharge_pulses(generator):
    t_all, v_all = generator.generate()

    np.testing.assert_array_equal(t_all, np.arange(10, dtype=np.float64))
    np.testing.assert_allclose(
        v_all,
        np.array([10.0, 10.0, 10.0, 10.0, 10.0, -10.0, -10.0, -10.0, -10.0, -10.0]),
    )


