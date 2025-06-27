"""Custom integration to integrate OpenEI with Home Assistant."""

import logging
from datetime import datetime, timedelta

import openeihttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_call_later
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
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(minutes=15)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(  # pylint: disable-next=unused-argument
    hass: HomeAssistant, config: ConfigEntry
):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    if CONF_MANUAL_PLAN not in entry.data.keys() and CONF_PLAN not in entry.data.keys():
        _LOGGER.error("Plan configuration missing.")
        raise ConfigEntryNotReady

    entry.add_update_listener(update_listener)

    coordinator = OpenEIDataUpdateCoordinator(hass, config=entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


class OpenEIDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry) -> None:
        """Initialize."""
        self._config = config
        self.hass = hass
        self.interval = timedelta(seconds=30)
        self._data = {}
        self._rate_limit_count = 0

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
                await self.get_sensors()
            except openeihttp.RateLimit:
                pass
            except AssertionError:
                pass
            except Exception as exception:
                _LOGGER.debug("Exception: %s", exception)
                raise UpdateFailed() from exception
        return self._data

    async def _async_refresh_data(self, data=None) -> None:
        """Update data via library."""
        _LOGGER.debug("_async_refresh_data data: %s", str(data))
        delta = timedelta(hours=1)
        now = datetime.now()
        next_hour = (now + delta).replace(microsecond=0, second=1, minute=0)
        wait_seconds = (next_hour - now).seconds

        _LOGGER.debug("Next update in %s seconds.", wait_seconds)
        async_call_later(self.hass, wait_seconds, self._async_refresh_data)
        try:
            await self.get_sensors()
        except openeihttp.RateLimit:
            pass
        except AssertionError:
            pass
        except Exception as exception:
            _LOGGER.debug("Exception: %s", exception)
            raise UpdateFailed() from exception

    async def get_sensors(self) -> None:
        """Update sensor data."""
        api = self._config.data.get(CONF_API_KEY)
        plan = self._config.data.get(CONF_PLAN)
        meter = self._config.data.get(CONF_SENSOR)
        cache_file = f".storage/openei_{self._config.entry_id}"
        reading = None

        if self._config.data.get(CONF_MANUAL_PLAN):
            plan = self._config.data.get(CONF_MANUAL_PLAN)

        if meter:
            _LOGGER.debug("Using meter data from sensor: %s", meter)
            reading = self.hass.states.get(meter)
            if not reading:
                reading = None
                _LOGGER.warning("Sensor: %s is not valid.", meter)
            else:
                reading = reading.state

        rate = openeihttp.Rates(
            api=api,
            plan=plan,
            reading=reading,
            cache_file=cache_file,
        )
        if self._rate_limit_count == 0:
            try:
                await rate.update()
            except openeihttp.RateLimit:
                _LOGGER.error("API Rate limit exceded, retrying later.")
                if not self._data:
                    # 3 hour retry if we have no data
                    self._rate_limit_count = 3
                else:
                    # 6 hour retry after rate limited
                    self._rate_limit_count = 6
        elif self._rate_limit_count > 0:
            self._rate_limit_count -= 1

        data = {}

        for sensor in SENSOR_TYPES:  # pylint: disable=consider-using-dict-items
            _sensor = {}
            value = getattr(rate, SENSOR_TYPES[sensor].key)
            if isinstance(value, tuple):
                _sensor[sensor] = value[0]
                _sensor[f"{sensor}_uom"] = value[1]
            else:
                _sensor[sensor] = getattr(rate, SENSOR_TYPES[sensor].key)
            data.update(_sensor)

        for sensor in BINARY_SENSORS:  # pylint: disable=consider-using-dict-items
            _sensor = {}
            _sensor[sensor] = getattr(rate, sensor)
            data.update(_sensor)

        _LOGGER.debug("DEBUG: %s", data)
        self._data = data


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update listener."""
    if not config_entry.options:
        return

    _LOGGER.debug("Attempting to reload entities from the %s integration", DOMAIN)

    new_data = config_entry.options.copy()

    hass.config_entries.async_update_entry(
        entry=config_entry,
        data=new_data,
        options={},
    )

    await hass.config_entries.async_reload(config_entry.entry_id)
