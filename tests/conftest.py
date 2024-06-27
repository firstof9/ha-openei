"""Test configurations."""

from unittest.mock import patch
import openeihttp

import pytest


pytest_plugins = "pytest_homeassistant_custom_component"


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
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield

@pytest.fixture(name="mock_call_later", autouse=True)
def mock_call_later_fixture():
    """Mock async_call_later."""
    with patch("custom_components.openei.async_call_later"):
        yield

@pytest.fixture(name="mock_api")
def mock_api():
    """Mock the library calls."""
    with patch("custom_components.openei.openeihttp.Rates") as mock_api:
        # mock_api = mock.Mock(spec=openeihttp.Rates)
        mock_api.return_value.current_rate = 0.24477
        mock_api.return_value.distributed_generation = "Net Metering"
        mock_api.return_value.approval = True
        mock_api.return_value.rate_name = 0.24477
        mock_api.return_value.mincharge = (10, "$/month")
        mock_api.return_value.lookup_plans = (
            '"Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}]'
        )
        mock_api.return_value.all_rates = [0.24477, 0.007]

        yield mock_api


@pytest.fixture(name="mock_api_config")
def mock_api_config():
    """Mock the library calls."""
    with patch("custom_components.openei.config_flow.openeihttp.Rates") as mock_api:
        mock_return = mock_api.return_value
        mock_return.lookup_plans.return_value = {
            "Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}]
        }

        yield mock_return


@pytest.fixture(name="mock_sensors")
def mock_get_sensors():
    """Mock of get sensors function."""
    with patch("custom_components.openei.get_sensors", autospec=True) as mock_sensors:
        mock_sensors.return_value = {
            "current_rate": 0.24477,
            "distributed_generation": "Net Metering",
            "approval": True,
            "rate_name": "Fake Test Rate",
            "mincharge": 10,
            "mincharge_uom": "$/month",
            "all_rates": [0.24477, 0.007],
        }
    yield mock_sensors


@pytest.fixture(name="mock_sensors_err")
def mock_sensors_api_error():
    """Mock of get sensors function."""
    with patch("custom_components.openei.get_sensors") as mock_sensors:
        mock_sensors.side_effect = openeihttp.RateLimit("Error")
        yield mock_sensors
