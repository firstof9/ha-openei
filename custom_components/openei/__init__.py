"""Custom integration to integrate OpenEI with Home Assistant."""
import asyncio
from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import openeihttp

from .const import (
    BINARY_SENSORS,
    CONF_API_KEY,
    CONF_PLAN,
    CONF_RADIUS,
    DOMAIN,
    PLATFORMS,
    SENSOR_TYPES,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(minutes=15)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    coordinator = OpenEIDataUpdateCoordinator(hass, config=entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    entry.add_update_listener(async_reload_entry)
    return True


class OpenEIDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry) -> None:
        """Initialize."""
        self._config = config
        self.hass = hass
        self.interval = timedelta(seconds=30)
        self._data = {}

        _LOGGER.debug("Data will be updated at the top of every hour.")

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=self.interval)

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        if len(self._data) == 0:
            delta = timedelta(hours=1)
            now = datetime.now()
            next_hour = (now + delta).replace(microsecond=0, second=1, minute=0)
            wait_seconds = (next_hour - now).seconds

            _LOGGER.debug("Next update in %s seconds.", wait_seconds)
            async_call_later(self.hass, wait_seconds, self._async_refresh_data)
            try:
                self._data = await self.hass.async_add_executor_job(
                    get_sensors, self.hass, self._config
                )
            except Exception as exception:
                raise UpdateFailed() from exception
        return self._data

    async def _async_refresh_data(self, data=None) -> None:
        """Update data via library."""
        delta = timedelta(hours=1)
        now = datetime.now()
        next_hour = (now + delta).replace(microsecond=0, second=1, minute=0)
        wait_seconds = (next_hour - now).seconds

        _LOGGER.debug("Next update in %s seconds.", wait_seconds)
        async_call_later(self.hass, wait_seconds, self._async_refresh_data)
        try:
            self._data = await self.hass.async_add_executor_job(
                get_sensors, self.hass, self._config
            )
        except Exception as exception:
            raise UpdateFailed() from exception


def get_sensors(hass, config):
    api = config.data.get(CONF_API_KEY)
    lat = hass.config.latitude
    lon = hass.config.longitude
    plan = config.data.get(CONF_PLAN)
    radius = config.data.get(CONF_RADIUS)
    rate = openeihttp.Rates(api, lat, lon, plan, radius)
    rate.update()
    data = {}

    for sensor in SENSOR_TYPES:
        _sensor = {}
        _sensor[sensor] = getattr(rate, sensor)
        data.update(_sensor)

    for sensor in BINARY_SENSORS:
        _sensor = {}
        _sensor[sensor] = getattr(rate, sensor)
        data.update(_sensor)

    _LOGGER.debug("DEBUG: %s", data)
    return data


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
