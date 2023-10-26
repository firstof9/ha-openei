"""Tests for init."""
import pytest
from unittest.mock import patch

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from openeihttp import APIError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openei.const import DOMAIN
from tests.const import CONFIG_DATA, CONFIG_DATA_MISSING_PLAN, CONFIG_DATA_WITH_SENSOR

pytestmark = pytest.mark.asyncio

async def test_setup_entry(hass, mock_sensors, mock_api):
    """Test settting up entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 6
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1


async def test_unload_entry(hass, mock_sensors, mock_api):
    """Test unloading entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 6
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert await hass.config_entries.async_unload(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 6
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
    assert len(hass.states.async_entity_ids(DOMAIN)) == 0

    assert await hass.config_entries.async_remove(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 0


async def test_setup_api_error(hass):
    """Test settting up entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    with patch("openeihttp.Rates.update", side_effect=APIError):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert not hass.data.get(DOMAIN)


async def test_setup_entry_sensor_error(hass, mock_api, caplog):
    """Test settting up entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA_WITH_SENSOR,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert "Using meter data from sensor: sensor.fakesensor" in caplog.text
    assert "Sensor: sensor.fakesensor is not valid." in caplog.text


async def test_setup_entry_sensor_plan_error(hass, mock_api, caplog):
    """Test settting up entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA_MISSING_PLAN,
    )

    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert "Plan configuration missing." in caplog.text
