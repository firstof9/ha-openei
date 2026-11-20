"""Provide common pytest helpers."""

import os
from typing import Any

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openei.const import DOMAIN
from tests.const import CONFIG_DATA


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


def make_config_entry(
    data: dict[str, Any] | None = None,
    title: str = "Fake Utility Co",
) -> MockConfigEntry:
    """Create a MockConfigEntry for OpenEI."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=title,
        data=CONFIG_DATA if data is None else data,
    )


async def setup_integration(
    hass,
    data: dict[str, Any] | None = None,
    title: str = "Fake Utility Co",
) -> tuple[MockConfigEntry, bool]:
    """Create, register, and set up an OpenEI config entry."""
    entry = make_config_entry(data=data, title=title)
    entry.add_to_hass(hass)
    result = await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry, result
