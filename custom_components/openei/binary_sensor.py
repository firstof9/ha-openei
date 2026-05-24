"""Binary sensor platform for OpenEI."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import BINARY_SENSORS, DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices):
    """Set up binary_sensor platform."""
    coordinator = entry.runtime_data

    binary_sensors = []
    for binary_sensor in BINARY_SENSORS:  # pylint: disable=consider-using-dict-items
        binary_sensors.append(
            OpenEIBinarySensor(BINARY_SENSORS[binary_sensor], entry, coordinator)
        )

    async_add_devices(binary_sensors, False)


class OpenEIBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """OpenEI binary sensor class."""

    def __init__(
        self,
        sensor_description: BinarySensorEntityDescription,
        entry: ConfigEntry,
        coordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = sensor_description.name
        self._key = sensor_description.key
        self._unique_id = entry.entry_id
        self._icon = sensor_description.icon
        self._config = entry
        self.coordinator = coordinator

        self._attr_name = f"{slugify(self._config.title)}_{self._name}"
        self._attr_unique_id = f"{self._key}_{self._unique_id}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self._key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

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
