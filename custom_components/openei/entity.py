"""Base entity for OpenEI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTRIBUTION, DOMAIN, NAME

if TYPE_CHECKING:
    from . import OpenEIDataUpdateCoordinator


class OpenEIEntity(CoordinatorEntity):
    """Base OpenEI entity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        description: EntityDescription,
        entry: ConfigEntry,
        coordinator: OpenEIDataUpdateCoordinator,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._config = entry

        self._attr_name = f"{slugify(entry.title)}_{description.name}"
        self._attr_unique_id = f"{description.key}_{entry.entry_id}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=NAME,
            name=NAME,
        )
