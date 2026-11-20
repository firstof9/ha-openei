"""Tests for init."""

import logging
from unittest.mock import PropertyMock, patch

import pytest
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from openeihttp import APIError, NotAuthorized

from custom_components.openei.const import DOMAIN
from tests.common import setup_integration
from tests.const import CONFIG_DATA_MISSING_PLAN, CONFIG_DATA_WITH_SENSOR

pytestmark = pytest.mark.asyncio


async def test_setup_entry(hass, mock_api, caplog):
    """Test setting up entities."""
    with caplog.at_level(logging.DEBUG):
        _, result = await setup_integration(hass)

    assert result
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 11
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_unload_entry(hass, mock_api):
    """Test unloading entities."""
    _, result = await setup_integration(hass)
    assert result

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 11
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert await hass.config_entries.async_unload(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 11
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 1
    assert len(hass.states.async_entity_ids(DOMAIN)) == 0

    assert await hass.config_entries.async_remove(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 0


@pytest.mark.parametrize(
    ("side_effect", "log_level", "expected_log", "expect_runtime_data"),
    [
        (APIError, logging.DEBUG, None, False),
        (NotAuthorized, logging.ERROR, "Invalid OpenEI API key.", False),
        (
            AssertionError("Mock error"),
            logging.DEBUG,
            "Data not yet available: Mock error",
            True,
        ),
        (
            Exception("Mock exception"),
            logging.DEBUG,
            "Unexpected exception: Mock exception",
            False,
        ),
    ],
)
async def test_setup_update_errors(
    hass, caplog, side_effect, log_level, expected_log, expect_runtime_data
):
    """Test handling exceptions during openeihttp.Rates.update."""
    with (
        caplog.at_level(log_level),
        patch("openeihttp.Rates.update", side_effect=side_effect),
    ):
        entry, _ = await setup_integration(hass)

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    if expect_runtime_data:
        assert getattr(entry, "runtime_data", None) is not None
    else:
        assert getattr(entry, "runtime_data", None) is None
    if expected_log is not None:
        assert expected_log in caplog.text


@pytest.mark.parametrize(
    ("sensor_state", "expected_logs"),
    [
        (
            None,
            [
                "Using meter data from sensor: sensor.fakesensor",
                "Sensor: sensor.fakesensor is not valid.",
            ],
        ),
        (
            "unavailable",
            ["Sensor: sensor.fakesensor state is unavailable, skipping reading."],
        ),
        (
            "non-numeric",
            [
                "Sensor: sensor.fakesensor has non-numeric state 'non-numeric', skipping reading."
            ],
        ),
    ],
)
async def test_setup_entry_sensor_states(
    hass, mock_api, caplog, sensor_state, expected_logs
):
    """Test setting up entities with invalid/unavailable/non-numeric meter sensors."""
    if sensor_state is not None:
        hass.states.async_set("sensor.fakesensor", sensor_state)

    with caplog.at_level(logging.DEBUG):
        _, result = await setup_integration(hass, data=CONFIG_DATA_WITH_SENSOR)

    assert result
    for expected_log in expected_logs:
        assert expected_log in caplog.text


async def test_setup_entry_sensor_plan_error(hass, mock_api, caplog):
    """Test setting up entities with missing plan configuration."""
    _, result = await setup_integration(hass, data=CONFIG_DATA_MISSING_PLAN)
    assert not result
    assert "Plan configuration missing." in caplog.text


async def test_rate_limit_error(hass, mock_api_err, caplog):
    """Test setting up entities when API rate limit is exceeded."""
    _, result = await setup_integration(hass)
    assert result
    assert "API Rate limit exceeded, retrying later." in caplog.text


async def test_setup_entry_no_all_rates(hass, mock_api):
    """Test setting up entities with no all_rates."""
    with patch(
        "openeihttp.Rates.all_rates", new_callable=PropertyMock, return_value=None
    ):
        _, result = await setup_integration(hass)

    assert result
