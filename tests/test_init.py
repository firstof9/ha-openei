"""Tests for init."""

import logging
import re
from unittest.mock import patch

import pytest
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from openeihttp import APIError, RateLimit
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openei.const import DOMAIN
from tests.common import load_fixture
from tests.const import CONFIG_DATA, CONFIG_DATA_MISSING_PLAN, CONFIG_DATA_WITH_SENSOR

pytestmark = pytest.mark.asyncio
TEST_PATTERN = r"^https://api\.openei\.org/utility_rates\?.*$"


async def test_setup_entry(hass, mock_aioclient, caplog):
    """Test settting up entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        re.compile(TEST_PATTERN),
        status=200,
        body=load_fixture("plan_data.json"),
        repeat=True,
    )

    with caplog.at_level(logging.DEBUG):

        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 10
        assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1


async def test_unload_entry(hass, mock_api):
    """Test unloading entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 10
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert await hass.config_entries.async_unload(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 10
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


async def test_rate_limit_error(hass, mock_api_err, caplog):
    """Test settting up entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert "API Rate limit exceded, retrying later." in caplog.text
