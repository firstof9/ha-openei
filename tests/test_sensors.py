"""Tests for sensors."""

import logging

import pytest

from tests.common import setup_integration

FAKE_MINCHARGE_SENSOR = "sensor.openei_fake_utility_co_minimum_charge"
FAKE_FIXEDCHARGE_SENSOR = "sensor.openei_fake_utility_co_fixed_charge_first_meter"
FAKE_CURRENT_RATE_SENSOR = "sensor.openei_fake_utility_co_current_energy_rate"
FAKE_CURRENT_SELL_RATE_SENSOR = "sensor.openei_fake_utility_co_current_energy_sell_rate"
FAKE_CURRENT_RATE_STRUCTURE_SENSOR = (
    "sensor.openei_fake_utility_co_current_energy_rate_structure"
)
FAKE_NEXT_RATE_SENSOR = "sensor.openei_fake_utility_co_next_energy_rate_structure"
FAKE_NEXT_RATE_TIME_SENSOR = (
    "sensor.openei_fake_utility_co_next_energy_rate_structure_time"
)

pytestmark = pytest.mark.asyncio


async def test_sensors(hass, mock_api, caplog):
    """Test setting up entities."""
    with caplog.at_level(logging.DEBUG):
        _, result = await setup_integration(hass)
        assert result

        state = hass.states.get(FAKE_MINCHARGE_SENSOR)
        assert state is not None
        assert state.state == "unknown"

        state = hass.states.get(FAKE_CURRENT_RATE_SENSOR)
        assert state is not None
        # all_rates is now the first element of the tuple returned by the library
        assert state.attributes["all_rates"] == [0.24477, 0.06118, 0.19847, 0.06116]
        # all_adjustments is the second element of the tuple
        assert state.attributes["all_adjustments"] == [
            0.02824917,
            0.02138383,
            0.02651779,
            0.02138308,
        ]

        state = hass.states.get(FAKE_CURRENT_RATE_STRUCTURE_SENSOR)
        assert state is not None

        state = hass.states.get(FAKE_NEXT_RATE_SENSOR)
        assert state is not None

        state = hass.states.get(FAKE_NEXT_RATE_TIME_SENSOR)
        assert state is not None

        state = hass.states.get(FAKE_FIXEDCHARGE_SENSOR)
        assert state is not None
        assert state.state == "16.91"

        state = hass.states.get(FAKE_CURRENT_SELL_RATE_SENSOR)
        assert state.state == "unknown"
