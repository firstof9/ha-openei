from unittest import mock
from unittest.mock import patch

import openeihttp
import pytest

from tests.common import load_fixture

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(name="mock_api")
def mock_api():
    """Mock the library calls."""
    with patch("custom_components.openei.openeihttp") as mock_api:
        mock_conn = mock.Mock(spec=openeihttp.Rates)
        mock_conn.return_value.current_rate.return_value = 0.24477
        mock_conn.return_value.distributed_generation.return_value = "Net Metering"
        mock_conn.return_value.approval.return_value = True
        mock_conn.return_value.rate_name.return_value = 0.24477

        yield mock_conn


@pytest.fixture(name="mock_sensors")
def mock_get_sensors():
    """Mock of get sensors function."""
    with patch("custom_components.openei.get_sensors", autospec=True) as mock_sensors:
        mock_sensors.return_value = {
            "current_rate": 0.24477,
            "distributed_generation": "Net Metering",
            "approval": True,
            "rate_name": "Fake Test Rate",
        }
    yield mock_sensors
