"""Config flow for OpenEI."""

from __future__ import annotations

import logging
from typing import Any

import openeihttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSORS_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_LOCATION,
    CONF_MANUAL_PLAN,
    CONF_PLAN,
    CONF_RADIUS,
    CONF_SENSOR,
    CONF_UTILITY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

CONF_SENSOR_NONE = "(none)"
SIGNUP_URL = "https://openei.org/services/api/signup/"


class OpenEIFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for OpenEI."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._data: dict[str, Any] = {}
        self._errors: dict[str, str] = {}
        self._entry: config_entries.ConfigEntry | None = None
        self._plans: dict[str, Any] | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_user_2()

        return self._show_step_1("user", user_input, {})

    async def async_step_user_2(self, user_input: dict[str, Any] | None = None):
        """Handle step 2 of a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_user_3()

        return await self._show_step_2("user_2")

    async def async_step_user_3(self, user_input: dict[str, Any] | None = None):
        """Handle step 3 of a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._apply_step_3_input(user_input)
            return self.async_create_entry(
                title=self._data[CONF_UTILITY], data=self._data
            )

        return await self._show_step_3("user_3")

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Add reconfigure step to allow to reconfigure a config entry."""
        self._entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert self._entry
        self._data = dict(self._entry.data)
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_reconfig_2()

        return self._show_step_1("reconfigure", user_input, self._data)

    async def async_step_reconfig_2(self, user_input: dict[str, Any] | None = None):
        """Handle step 2 of reconfigure flow."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_reconfig_3()

        return await self._show_step_2("reconfig_2")

    async def async_step_reconfig_3(self, user_input: dict[str, Any] | None = None):
        """Handle step 3 of reconfigure flow."""
        self._errors = {}

        if user_input is not None:
            self._apply_step_3_input(user_input)
            assert self._entry
            self.hass.config_entries.async_update_entry(self._entry, data=self._data)
            await self.hass.config_entries.async_reload(self._entry.entry_id)
            _LOGGER.debug("%s reconfigured.", DOMAIN)
            return self.async_abort(reason="reconfigure_successful")

        return await self._show_step_3("reconfig_3")

    def _apply_step_3_input(self, user_input: dict[str, Any]) -> None:
        """Normalize and merge step 3 input into flow data."""
        if user_input[CONF_SENSOR] == CONF_SENSOR_NONE:
            user_input.pop(CONF_SENSOR, None)
        self._data.update(user_input)

    def _show_step_1(
        self,
        step_id: str,
        user_input: dict[str, Any] | None,
        defaults: dict[str, Any],
    ):
        """Show the step 1 configuration form."""
        return self.async_show_form(
            step_id=step_id,
            data_schema=_get_schema_step_1(user_input, defaults),
            errors=self._errors,
            description_placeholders={"signup_url": SIGNUP_URL},
        )

    async def _show_step_2(self, step_id: str):
        """Show the step 2 configuration form."""
        self._plans = await _async_lookup_plans(self.hass, self._data)
        utility_list = list(self._plans.keys())
        _LOGGER.debug("Utility list: %s", utility_list)
        return self.async_show_form(
            step_id=step_id,
            data_schema=_get_schema_step_2(self._data, {}, utility_list),
            errors=self._errors,
        )

    async def _show_step_3(self, step_id: str):
        """Show the step 3 configuration form."""
        assert self._plans is not None
        utility = self._data[CONF_UTILITY]
        plan_list = {plan["label"]: plan["name"] for plan in self._plans[utility]}
        _LOGGER.debug("Plan list: %s", plan_list)
        return self.async_show_form(
            step_id=step_id,
            data_schema=_get_schema_step_3(self.hass, self._data, {}, plan_list),
            errors=self._errors,
        )


def _get_default(
    user_input: dict[str, Any],
    default_dict: dict[str, Any],
    key: str,
    fallback_default: Any = None,
) -> Any:
    """Get default value for key from user_input or default_dict."""
    return user_input.get(key, default_dict.get(key, fallback_default))


def _get_schema_step_1(
    user_input: dict[str, Any] | None,
    default_dict: dict[str, Any],
) -> vol.Schema:
    """Get a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    if user_input.get(CONF_LOCATION) == '""':
        user_input[CONF_LOCATION] = ""

    if default_dict.get(CONF_LOCATION) == '""':
        default_dict[CONF_LOCATION] = ""

    return vol.Schema(
        {
            vol.Required(
                CONF_API_KEY,
                default=_get_default(user_input, default_dict, CONF_API_KEY),
            ): str,
            vol.Optional(
                CONF_LOCATION,
                default=_get_default(user_input, default_dict, CONF_LOCATION, ""),
            ): str,
            vol.Required(
                CONF_RADIUS,
                default=_get_default(user_input, default_dict, CONF_RADIUS, 0),
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=200)),
        },
    )


def _get_schema_step_2(
    user_input: dict[str, Any] | None,
    default_dict: dict[str, Any],
    utility_list: list,
) -> vol.Schema:
    """Get a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    return vol.Schema(
        {
            vol.Required(
                CONF_UTILITY,
                default=_get_default(user_input, default_dict, CONF_UTILITY, ""),
            ): vol.In(utility_list),
        },
    )


def _get_schema_step_3(
    hass: HomeAssistant,
    user_input: dict[str, Any] | None,
    default_dict: dict[str, Any],
    plan_list: dict[str, str],
) -> vol.Schema:
    """Get a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    if default_dict.get(CONF_SENSOR) == CONF_SENSOR_NONE:
        default_dict.pop(CONF_SENSOR, None)

    return vol.Schema(
        {
            vol.Optional(
                CONF_PLAN, default=_get_default(user_input, default_dict, CONF_PLAN)
            ): vol.In(plan_list),
            vol.Optional(
                CONF_MANUAL_PLAN,
                default=_get_default(user_input, default_dict, CONF_MANUAL_PLAN, ""),
            ): str,
            vol.Required(
                CONF_SENSOR,
                default=_get_default(
                    user_input, default_dict, CONF_SENSOR, CONF_SENSOR_NONE
                ),
            ): vol.In(_get_entities(hass, SENSORS_DOMAIN, "energy", CONF_SENSOR_NONE)),
        },
    )


async def _async_lookup_plans(
    hass: HomeAssistant, user_input: dict[str, Any]
) -> dict[str, Any]:
    """Look up utilities and rate plans for the configured location."""
    lat = None
    lon = None
    api = user_input[CONF_API_KEY]
    address = user_input[CONF_LOCATION]
    radius = user_input[CONF_RADIUS]

    if not bool(address):
        lat = hass.config.latitude
        lon = hass.config.longitude
        address = None

    rates = openeihttp.Rates(
        api=api,
        lat=lat,
        lon=lon,
        radius=radius,
        address=address,
        session=async_get_clientsession(hass),
    )
    return await _lookup_plans(rates)


async def _lookup_plans(handler) -> dict[str, Any]:
    """Return dict of utilities and plans."""
    response = await handler.lookup_plans()
    _LOGGER.debug("lookup_plans: %s", response)
    return response


def _get_entities(
    hass: HomeAssistant,
    domain: str,
    search: str | None = None,
    extra_entities: str | None = None,
) -> list[str]:
    """Return entity IDs for the given domain, optionally filtered by device class."""
    registry = er.async_get(hass)
    data = [
        entry.entity_id
        for entry in registry.entities.values()
        if entry.domain == domain
        and (
            search is None
            or entry.device_class == search
            or entry.original_device_class == search
        )
    ]

    if extra_entities:
        data.insert(0, extra_entities)
    data.sort()
    return data
