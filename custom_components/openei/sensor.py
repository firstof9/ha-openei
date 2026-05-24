"""Sensor platform for OpenEI."""

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTRIBUTION, DOMAIN, SENSOR_TYPES


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices):
    """Set up sensor platform."""
    coordinator = entry.runtime_data

    sensors = []
    for sensor_key, sensor_description in SENSOR_TYPES.items():
        if sensor_key == "all_rates":
            continue
        sensors.append(OpenEISensor(sensor_description, entry, coordinator))

    async_add_devices(sensors, False)


class OpenEISensor(CoordinatorEntity, SensorEntity):
    """OpenEI Sensor class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        sensor_description: SensorEntityDescription,
        entry: ConfigEntry,
        coordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = sensor_description.name
        self._key = sensor_description.key
        self._unique_id = entry.entry_id
        self._config = entry
        self._icon = sensor_description.icon
        self.coordinator = coordinator

        self._attr_name = f"{slugify(self._config.title)}_{self._name}"
        self._attr_unique_id = f"{self._key}_{self._unique_id}"

    @property
    def native_value(self) -> Any:
        """Return the value of the sensor."""
        return self.coordinator.data.get(self._key)

    @property
    def native_unit_of_measurement(self) -> Any:
        """Return the unit of measurement."""
        if self._key in [
            "current_adjustment",
            "current_rate",
            "monthly_tier_rate",
            "current_sell_rate",
        ]:
            return f"{self.hass.config.currency}/kWh"
        if f"{self._key}_uom" in self.coordinator.data:
            return self.coordinator.data.get(f"{self._key}_uom")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return sensor attributes."""
        attrs = {}
        if self._key == "current_rate":
            attrs["all_rates"] = self.coordinator.data.get("all_rates")
            attrs["all_adjustments"] = self.coordinator.data.get("all_adjustments")
        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._icon

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._config.entry_id)},
            manufacturer="OpenEI",
            name="OpenEI",
        )
