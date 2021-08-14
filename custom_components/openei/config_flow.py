"""Adds config flow for Blueprint."""
from __future__ import annotations
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
import voluptuous as vol
import openei
import logging
from typing import Any, Dict, Optional
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_API_KEY,
    CONF_PLAN,
    CONF_UTILITY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class OpenEIFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._data = {}
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_user_2()

        return await self._show_config_form(user_input)

    async def async_step_user_2(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_user_3()

        return await self._show_config_form_2(user_input)

    async def async_step_user_3(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data[CONF_UTILITY], data=self._data
            )

        return await self._show_config_form_3(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OpenEIOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        defaults = {}
        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema_step_1(self.hass, user_input, defaults),
            errors=self._errors,
        )

    async def _show_config_form_2(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        defaults = {}
        utility_list = await _get_utility_list(self.hass, self._data)
        return self.async_show_form(
            step_id="user_2",
            data_schema=_get_schema_step_2(
                self.hass, self._data, defaults, utility_list
            ),
            errors=self._errors,
        )

    async def _show_config_form_3(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        defaults = {}
        plan_list = await _get_plan_list(self.hass, self._data)
        return self.async_show_form(
            step_id="user_3",
            data_schema=_get_schema_step_3(self.hass, self._data, defaults, plan_list),
            errors=self._errors,
        )


class OpenEIOptionsFlowHandler(config_entries.OptionsFlow):
    """Blueprint config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self._data = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_user_2()

        return await self._show_config_form(user_input)

    async def async_step_user_2(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_user_3()

        return await self._show_config_form_2(user_input)

    async def async_step_user_3(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)

        return await self._show_config_form_3(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema_step_1(self.hass, user_input, self._data),
            errors=self._errors,
        )

    async def _show_config_form_2(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        utility_list = await _get_utility_list(self.hass, self._data)
        return self.async_show_form(
            step_id="user_2",
            data_schema=_get_schema_step_2(
                self.hass, user_input, self._data, utility_list
            ),
            errors=self._errors,
        )

    async def _show_config_form_3(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        plan_list = await _get_plan_list(self.hass, self._data)
        return self.async_show_form(
            step_id="user_3",
            data_schema=_get_schema_step_3(
                self.hass, user_input, self._data, plan_list
            ),
            errors=self._errors,
        )


def _get_schema_step_1(
    hass: HomeAssistant,
    user_input: Optional[Dict[str, Any]],
    default_dict: Dict[str, Any],
    entry_id: str = None,
) -> vol.Schema:
    """Gets a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str, fallback_default: Any = None) -> None:
        """Gets default value for key."""
        return user_input.get(key, default_dict.get(key, fallback_default))

    return vol.Schema(
        {
            vol.Required(
                CONF_API_KEY, default=_get_default(CONF_API_KEY, "")
            ): cv.string,
        },
    )


def _get_schema_step_2(
    hass: HomeAssistant,
    user_input: Optional[Dict[str, Any]],
    default_dict: Dict[str, Any],
    utility_list: list,
    entry_id: str = None,
) -> vol.Schema:
    """Gets a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str, fallback_default: Any = None) -> None:
        """Gets default value for key."""
        return user_input.get(key, default_dict.get(key, fallback_default))

    return vol.Schema(
        {
            vol.Required(CONF_UTILITY, default=_get_default(CONF_UTILITY, "")): vol.In(
                utility_list
            ),
        },
    )


def _get_schema_step_3(
    hass: HomeAssistant,
    user_input: Optional[Dict[str, Any]],
    default_dict: Dict[str, Any],
    plan_list: list,
    entry_id: str = None,
) -> vol.Schema:
    """Gets a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str, fallback_default: Any = None) -> None:
        """Gets default value for key."""
        return user_input.get(key, default_dict.get(key, fallback_default))

    return vol.Schema(
        {
            vol.Required(CONF_PLAN, default=_get_default(CONF_PLAN, "")): vol.In(
                plan_list
            ),
        },
    )


async def _get_utility_list(hass, user_input) -> list | None:
    """Return list of utilities by lat/lon."""

    lat = hass.config.latitude
    lon = hass.config.longitude
    api = user_input[CONF_API_KEY]

    plans = openei.Rates(api, lat, lon)
    plans = await hass.async_add_executor_job(_lookup_plans, plans)
    utilities = []

    for utility in plans:
        utilities.append(utility)

    _LOGGER.debug("get_utility_list: %s", utilities)
    return utilities


async def _get_plan_list(hass, user_input) -> list | None:
    """Return list of rate plans by lat/lon."""

    lat = hass.config.latitude
    lon = hass.config.longitude
    api = user_input[CONF_API_KEY]
    utility = user_input[CONF_UTILITY]

    plans = openei.Rates(api, lat, lon)
    plans = await hass.async_add_executor_job(_lookup_plans, plans)
    value = {}

    for plan in plans[utility]:
        value[plan["label"]] = plan["name"]

    _LOGGER.debug("get_plan_list: %s", value)
    return value


def _lookup_plans(handler) -> list:
    """Return list of utilities and plans."""
    response = handler.lookup_plans()
    _LOGGER.debug("lookup_plans: %s", response)
    return response
