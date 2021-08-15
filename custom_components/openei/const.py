"""Constants for integration_blueprint."""
from homeassistant.const import CURRENCY_DOLLAR

# Base component constants
NAME = "OpenEI"
DOMAIN = "openei"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ATTRIBUTION = "Data provided by http://openei.org/"
ISSUE_URL = "https://github.com/firstof9/ha-openei/issues"
PLATFORMS = ["sensor"]

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Configuration and options
CONF_API_KEY = "api_key"
CONF_PLAN = "rate_plan"
CONF_UTILITY = "utility"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
# property: name, icon, unit_of_measurement
SENSOR_TYPES = {
    "current_rate": ["Current Energy Rate", "mdi:currency-usd", CURRENCY_DOLLAR],
    "distributed_generation": ["Distributed Generation", "mdi:gauge", None],
    "approval": ["Approval", "mdi:check", None],
    "rate_name": ["Plan Name", "mdi:tag", None],
}
