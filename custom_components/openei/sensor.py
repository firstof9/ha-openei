"""Sensor platform for integration_blueprint."""
from .const import ATTRIBUTION, DOMAIN, SENSOR_TYPES
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from typing import Optional


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unique_id = entry.entry_id

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(OpenEISensor(sensor, unique_id, coordinator))

    async_add_devices(sensors, False)


class OpenEISensor(CoordinatorEntity, SensorEntity):
    """OpenEI Sensor class."""

    def __init__(self, sensor_type, unique_id, coordinator) -> None:
        """Initialize the sensor."""
        self._name = sensor_type
        self._unique_id = unique_id
        self.coordinator = coordinator

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._name}_{self._unique_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{SENSOR_TYPES[self._name][0]}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._name)

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._name][1]

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement of this sensor."""
        return SENSOR_TYPES[self._name][2]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_state_attributes(self) -> Optional[str]:
        """Return sesnsor attributes."""
        attrs = {}
        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attrs
