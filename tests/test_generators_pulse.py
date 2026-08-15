"""Tests for :class:`beast.generators.PulseGenerator`."""

import numpy as np
import pytest

from beast.generators import Generator, Generator_Pulse


@pytest.fixture
def generator() -> Generator_Pulse:
    return Generator_Pulse(
        [100.0, 90.0],
        delta_soc=5.0,
        delta_t=1.0,
        t_on=2.0,
        t_off=1.0,
        q_nominal_coulomb=3600.0,
    )


def test_generator_pulse_implements_profile_generator(generator):
    assert isinstance(generator, Generator)


def test_generator_pulse_discharge_pulses(generator):
    time, current = generator.generate()

    np.testing.assert_array_equal(time, np.arange(6, dtype=np.float64))
    np.testing.assert_allclose(
        current,
        np.array([90.0, 90.0, 0.0, 90.0, 90.0, 0.0]),
    )


def test_generator_pulse_charge_pulses_uses_negative_current():
    generator = Generator_Pulse(
        [80.0, 90.0],
        delta_soc=5.0,
        delta_t=1.0,
        t_on=2.0,
        t_off=0.0,
        q_nominal_coulomb=3600.0,
    )

    _, current = generator.generate()

    np.testing.assert_allclose(current, [-90.0, -90.0, -90.0, -90.0])


def test_generator_pulse_supports_partial_final_soc_step():
    generator = Generator_Pulse(
        [100.0, 88.0],
        delta_soc=5.0,
        delta_t=1.0,
        t_on=1.0,
        t_off=0.0,
        q_nominal_coulomb=100.0,
    )

    _, current = generator.generate()

    np.testing.assert_allclose(current, [5.0, 5.0, 2.0])


def test_generator_pulse_supports_multiple_soc_targets():
    generator = Generator_Pulse(
        [100.0, 90.0, 95.0],
        delta_soc=5.0,
        delta_t=1.0,
        t_on=1.0,
        t_off=0.0,
        q_nominal_coulomb=100.0,
    )

    _, current = generator.generate()

    np.testing.assert_allclose(current, [5.0, 5.0, -5.0])


def test_generator_pulse_generated_time_is_equispaced():
    generator = Generator_Pulse(
        [100.0, 95.0],
        delta_soc=5.0,
        delta_t=0.5,
        t_on=1.0,
        t_off=0.5,
        q_nominal_coulomb=3600.0,
    )

    time, _ = generator.generate()

    np.testing.assert_allclose(np.diff(time), 0.5)


def test_generator_pulse_soc_history_property_returns_copy(generator):
    history = generator.soc_percent_history
    history[0] = 0.0

    assert generator.soc_percent_history[0] == 100.0


@pytest.mark.parametrize(
    "history",
    [
        [],
        [100.0],
        [100.0, np.nan],
        [100.0, np.inf],
    ],
)
def test_generator_pulse_invalid_soc_history_is_rejected(history):
    with pytest.raises(ValueError):
        Generator_Pulse(
            history,
            delta_soc=5.0,
            delta_t=1.0,
            t_on=1.0,
            t_off=0.0,
            q_nominal_coulomb=3600.0,
        )


@pytest.mark.parametrize("name", ["delta_soc", "delta_t", "t_on", "q_nominal_coulomb"])
@pytest.mark.parametrize("value", [0.0, -1.0, np.nan, np.inf, -np.inf])
def test_generator_pulse_positive_parameters_are_validated(name, value):
    kwargs = {
        "delta_soc": 5.0,
        "delta_t": 1.0,
        "t_on": 1.0,
        "t_off": 0.0,
        "q_nominal_coulomb": 3600.0,
    }
    kwargs[name] = value

    with pytest.raises(ValueError):
        Generator_Pulse([100.0, 90.0], **kwargs)


@pytest.mark.parametrize("value", [-1.0, np.nan, np.inf, -np.inf])
def test_generator_pulse_t_off_must_be_nonnegative_and_finite(value):
    with pytest.raises(ValueError):
        Generator_Pulse(
            [100.0, 90.0],
            delta_soc=5.0,
            delta_t=1.0,
            t_on=1.0,
            t_off=value,
            q_nominal_coulomb=3600.0,
        )


def test_generator_pulse_t_on_must_produce_at_least_one_sample():
    with pytest.raises(ValueError, match="at least one sample"):
        Generator_Pulse(
            [100.0, 90.0],
            delta_soc=5.0,
            delta_t=1.0,
            t_on=0.5,
            t_off=0.0,
            q_nominal_coulomb=3600.0,
        )
