"""Test configurations."""

import re
from unittest.mock import patch

import pytest

from .common import load_fixture, make_config_entry

pytest_plugins = "pytest_homeassistant_custom_component"

TEST_PATTERN = r"^https://api\.openei\.org/utility_rates\?.*$"


def _mock_api_response(mock_aioclient, fixture_name: str) -> None:
    """Register a mocked OpenEI API response from a fixture file."""
    mock_aioclient.get(
        re.compile(TEST_PATTERN),
        status=200,
        text=load_fixture(fixture_name),
    )


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
def mock_aioclient(aioclient_mock):
    """Fixture to mock aioclient calls."""
    return aioclient_mock


@pytest.fixture(name="mock_api")
def mock_plandata(mock_aioclient):
    """Mock the status reply."""
    _mock_api_response(mock_aioclient, "plan_data.json")


@pytest.fixture(name="mock_api_err")
def mock_rate_limit(mock_aioclient):
    """Mock the rate limit reply."""
    _mock_api_response(mock_aioclient, "rate_limit.json")


@pytest.fixture
def mock_config_entry():
    """Return a default MockConfigEntry for OpenEI."""
    return make_config_entry()
