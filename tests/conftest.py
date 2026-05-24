"""Test configurations."""

import re
from unittest.mock import patch

import openeihttp
import pytest
from aioresponses import aioresponses

from .common import load_fixture

pytest_plugins = "pytest_homeassistant_custom_component"

TEST_PATTERN = r"^https://api\.openei\.org/utility_rates\?.*$"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integration tests."""
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


@pytest.fixture
def mock_aioclient():
    """Fixture to mock aioclient calls."""
    with aioresponses() as m:
        yield m


@pytest.fixture(name="mock_api")
def mock_plandata(mock_aioclient):
    """Mock the status reply."""
    mock_aioclient.get(
        re.compile(TEST_PATTERN),
        status=200,
        body=load_fixture("plan_data.json"),
        repeat=True,
    )


@pytest.fixture(name="mock_api_err")
def mock_rate_limit(mock_aioclient):
    """Mock the status reply."""
    mock_aioclient.get(
        re.compile(TEST_PATTERN),
        status=200,
        body=load_fixture("rate_limit.json"),
        repeat=True,
    )


@pytest.fixture(name="mock_api_config")
def mock_lookup(mock_aioclient):
    """Mock the status reply."""
    mock_aioclient.get(
        re.compile(TEST_PATTERN),
        status=200,
        body=load_fixture("lookup.json"),
        repeat=True,
    )


@pytest.fixture(name="mock_sensors")
def mock_get_sensors():
    """Mock of get sensors function."""
    with patch(
        "custom_components.openei.OpenEIDataUpdateCoordinator._get_sensors",
        autospec=True,
    ) as mock_sensors:
        mock_sensors.return_value = {
            "current_rate": 0.24477,
            "distributed_generation": "Net Metering",
            "approval": True,
            "rate_name": "Fake Test Rate",
            "mincharge": 10,
            "mincharge_uom": "$/month",
            "all_rates": [0.24477, 0.007],
            "all_adjustments": [0.02824917, 0.0],
        }
        yield mock_sensors


@pytest.fixture(name="mock_sensors_err")
def mock_sensors_api_error():
    """Mock of get sensors function."""
    with patch(
        "custom_components.openei.OpenEIDataUpdateCoordinator._get_sensors"
    ) as mock_sensors:
        mock_sensors.side_effect = openeihttp.RateLimit("Error")
        yield mock_sensors
