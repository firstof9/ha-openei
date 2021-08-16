"""Binary sensor platform for OpenEI."""
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BINARY_SENSORS, DOMAIN


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    binary_sensors = []
    for binary_sensor in BINARY_SENSORS:
        binary_sensors.append(OpenEIBinarySensor(coordinator, entry, binary_sensor))

    async_add_devices(binary_sensors, False)


class OpenEIBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(self, coordinator, entry, sensor_type) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = sensor_type
        self._config = entry
        self.coordinator = coordinator

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._config.entry_id

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return f"{BINARY_SENSORS[self._name][0]}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get(self._name)
