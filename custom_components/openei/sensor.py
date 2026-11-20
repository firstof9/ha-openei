"""Sensor platform for OpenEI."""

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import SENSOR_TYPES
from .entity import OpenEIEntity

RATE_UOM_KEYS = frozenset(
    {
        "current_adjustment",
        "current_rate",
        "monthly_tier_rate",
        "current_sell_rate",
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices):
    """Set up sensor platform."""
    coordinator = entry.runtime_data

    sensors = [
        OpenEISensor(description, entry, coordinator)
        for description in SENSOR_TYPES
        if description.key != "all_rates"
    ]

    async_add_devices(sensors, False)


class OpenEISensor(OpenEIEntity, SensorEntity):
    """OpenEI Sensor class."""

    entity_description: SensorEntityDescription

    @property
    def native_value(self) -> Any:
        """Return the value of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def native_unit_of_measurement(self) -> Any:
        """Return the unit of measurement."""
        key = self.entity_description.key
        if key in RATE_UOM_KEYS:
            return f"{self.hass.config.currency}/kWh"
        if f"{key}_uom" in self.coordinator.data:
            return self.coordinator.data.get(f"{key}_uom")
        return None

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return sensor attributes."""
        attrs = {}
        if self.entity_description.key == "current_rate":
            attrs["all_rates"] = self.coordinator.data.get("all_rates")
            attrs["all_adjustments"] = self.coordinator.data.get("all_adjustments")
        return attrs
