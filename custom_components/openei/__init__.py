"""Custom integration to integrate OpenEI with Home Assistant."""

import logging
from datetime import timedelta

import openeihttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BINARY_SENSORS,
    CONF_API_KEY,
    CONF_MANUAL_PLAN,
    CONF_PLAN,
    CONF_SENSOR,
    DOMAIN,
    PLATFORMS,
    SENSOR_TYPES,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if CONF_MANUAL_PLAN not in entry.data and CONF_PLAN not in entry.data:
        _LOGGER.error("Plan configuration missing.")
        raise ConfigEntryNotReady

    coordinator = OpenEIDataUpdateCoordinator(hass, config=entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


class OpenEIDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry) -> None:
        """Initialize."""
        self._config = config

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        try:
            return await self._get_sensors()
        except openeihttp.RateLimit:
            _LOGGER.error("API Rate limit exceeded, retrying later.")
            # Return previously cached data if available, else empty dict
            return self.data or {}
        except openeihttp.NotAuthorized:
            _LOGGER.error("Invalid OpenEI API key.")
            raise UpdateFailed("Invalid API key") from None
        except openeihttp.APIError as exception:
            _LOGGER.debug("API error: %s", exception)
            raise UpdateFailed(f"OpenEI API error: {exception}") from exception
        except AssertionError as exception:
            _LOGGER.debug("Data not yet available: %s", exception)
            return self.data or {}
        except Exception as exception:
            _LOGGER.debug("Unexpected exception: %s", exception)
            raise UpdateFailed(f"Unexpected error: {exception}") from exception

    async def _get_sensors(self) -> dict:
        """Fetch and return sensor data from the API."""
        api = self._config.data.get(CONF_API_KEY)
        plan = self._config.data.get(CONF_PLAN)
        meter = self._config.data.get(CONF_SENSOR)
        cache_file = (
            f"{self.hass.config.config_dir}/.storage/openei_{self._config.entry_id}"
        )
        reading: float = 0.0

        if self._config.data.get(CONF_MANUAL_PLAN):
            plan = self._config.data.get(CONF_MANUAL_PLAN)

        if meter:
            _LOGGER.debug("Using meter data from sensor: %s", meter)
            state_obj = self.hass.states.get(meter)
            if not state_obj:
                _LOGGER.warning("Sensor: %s is not valid.", meter)
            elif state_obj.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                _LOGGER.warning(
                    "Sensor: %s state is %s, skipping reading.",
                    meter,
                    state_obj.state,
                )
            else:
                try:
                    reading = float(state_obj.state)
                except ValueError:
                    _LOGGER.warning(
                        "Sensor: %s has non-numeric state '%s', skipping reading.",
                        meter,
                        state_obj.state,
                    )

        rate = openeihttp.Rates(
            api=api,
            plan=plan,
            reading=reading,
            cache_file=cache_file,
        )
        await rate.update()

        data = {}

        for sensor in SENSOR_TYPES:  # pylint: disable=consider-using-dict-items
            _sensor: dict = {}
            if sensor == "all_rates":
                value = rate.all_rates
                if value is not None:
                    _sensor["all_rates"] = value[0]
                    _sensor["all_adjustments"] = value[1]
                else:
                    _sensor["all_rates"] = None
                    _sensor["all_adjustments"] = None
            else:
                value = getattr(rate, SENSOR_TYPES[sensor].key)
                if isinstance(value, tuple):
                    _sensor[sensor] = value[0]
                    _sensor[f"{sensor}_uom"] = value[1]
                else:
                    _sensor[sensor] = value
            data.update(_sensor)

        for sensor in BINARY_SENSORS:  # pylint: disable=consider-using-dict-items
            data[sensor] = getattr(rate, sensor)

        _LOGGER.debug("DEBUG: %s", data)
        return data


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
