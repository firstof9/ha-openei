"""Tests for sensors."""

import pytest

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openei.const import DOMAIN
from tests.const import CONFIG_DATA

FAKE_MINCHARGE_SENSOR = "sensor.fake_utility_co_minimum_charge"
FAKE_CURRENT_RATE_SENSOR = "sensor.fake_utility_co_current_energy_rate"

pytestmark = pytest.mark.asyncio


async def test_sensors(hass, mock_sensors, mock_api):
    """Test settting up entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get(FAKE_MINCHARGE_SENSOR)
    assert state is not None
    assert state.state == "10"
    assert state.attributes["unit_of_measurement"] == "$/month"

    state = hass.states.get(FAKE_CURRENT_RATE_SENSOR)
    assert state is not None
    assert state.state == "0.24477"
    assert state.attributes["all_rates"] == [0.24477, 0.007]
