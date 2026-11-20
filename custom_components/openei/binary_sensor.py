"""Binary sensor platform for OpenEI."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import BINARY_SENSORS
from .entity import OpenEIEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices):
    """Set up binary_sensor platform."""
    coordinator = entry.runtime_data

    binary_sensors = [
        OpenEIBinarySensor(description, entry, coordinator)
        for description in BINARY_SENSORS
    ]

    async_add_devices(binary_sensors, False)


class OpenEIBinarySensor(OpenEIEntity, BinarySensorEntity):
    """OpenEI binary sensor class."""

    entity_description: BinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self.entity_description.key)
