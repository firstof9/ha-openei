"""Test OpenEI config flow."""

import re
from unittest.mock import patch

import pytest
from homeassistant import config_entries, setup
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openei.const import DOMAIN
from tests.common import load_fixture
from tests.const import CONFIG_DATA

pytestmark = pytest.mark.asyncio
TEST_PATTERN = r"^https://api\.openei\.org/utility_rates\?.*$"


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            {
                "api_key": "fakeAPIKey",
                "radius": 0,
                "location": "",
            },
            "user_2",
            {
                "utility": "Fake Utility Co",
            },
            "user_3",
            {
                "rate_plan": "randomstring",
                "sensor": "(none)",
                "manual_plan": "",
            },
            "Fake Utility Co",
            {
                "api_key": "fakeAPIKey",
                "radius": 0,
                "utility": "Fake Utility Co",
                "rate_plan": "randomstring",
                "location": "",
                "manual_plan": "",
            },
        ),
    ],
)
async def test_form(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    title,
    data,
    hass,
    mock_api,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result['title'] == title_1

    with (
        patch(
            "custom_components.openei.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
        patch(
            "custom_components.openei.config_flow._lookup_plans",
            return_value={
                "Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}]
            },
        ),
        patch(
            "custom_components.openei.config_flow._get_entities",
            return_value=["(none)"],
        ),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_1
        )
        assert result2["type"] == "form"
        assert result2["step_id"] == step_id_2

        result3 = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result3["type"] == "form"
        assert result3["step_id"] == step_id_3
        result4 = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

    assert result4["type"] == "create_entry"
    assert result4["title"] == title
    assert result4["data"] == data

    await hass.async_block_till_done()
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "step_id,input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            "reconfigure",
            {
                "api_key": "new_fakeAPIKey",
                "radius": 0,
                "location": "",
            },
            "reconfig_2",
            {
                "utility": "New Fake Utility Co",
            },
            "reconfig_3",
            {
                "rate_plan": "new_randomstring",
                "sensor": "(none)",
                "manual_plan": "",
            },
            "Fake Utility Co",
            {
                "api_key": "new_fakeAPIKey",
                "radius": 0,
                "utility": "New Fake Utility Co",
                "rate_plan": "new_randomstring",
                "location": "",
                "manual_plan": "",
            },
        ),
    ],
)
async def test_reconfig_form(
    step_id,
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    title,
    data,
    hass,
    mock_aioclient,
):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        re.compile(TEST_PATTERN),
        status=200,
        body=load_fixture("plan_data.json"),
        repeat=True,
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    reconfigure_result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == step_id

    with (
        patch(
            "custom_components.openei.config_flow._lookup_plans",
            return_value={
                "Fake Utility Co": [
                    {"name": "Fake Plan Name", "label": "randomstring"}
                ],
                "New Fake Utility Co": [
                    {"name": "Fake Plan Name", "label": "new_randomstring"}
                ],
            },
        ),
        patch(
            "custom_components.openei.config_flow._get_entities",
            return_value=["(none)"],
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"], input_1
        )
        assert result["type"] == "form"
        assert result["step_id"] == step_id_2

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_2
        )

        assert result["type"] == "form"
        assert result["step_id"] == step_id_3
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], input_3
        )

        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        await hass.async_block_till_done()

        entry = hass.config_entries.async_entries(DOMAIN)[0]
        assert entry.data.copy() == data


async def test_get_entities_helper(hass):
    """Test the _get_entities helper function."""
    from homeassistant.helpers import entity_registry as er

    from custom_components.openei.config_flow import _get_entities

    registry = er.async_get(hass)

    # Test case 1: no entities registered — should return empty list
    assert _get_entities(hass, "sensor") == []

    # Test case 2: register entities and retrieve all
    registry.async_get_or_create(
        "sensor",
        "test",
        "energy_usage",
        original_device_class="energy",
    )
    registry.async_get_or_create(
        "sensor",
        "test",
        "water_usage",
        original_device_class="water",
    )

    all_entities = _get_entities(hass, "sensor")
    assert len(all_entities) == 2

    # Test case 3: search filter matching device class
    energy_entities = _get_entities(hass, "sensor", search="energy")
    assert len(energy_entities) == 1
    assert energy_entities[0].startswith("sensor.")

    # Test case 4: extra entities inserted at front, list is sorted
    result = _get_entities(hass, "sensor", search="energy", extra_entities="(none)")
    assert result[0] == "(none)"
    assert len(result) == 2


async def test_get_schema_step_1():
    """Test _get_schema_step_1."""
    from custom_components.openei.config_flow import _get_schema_step_1
    # user_input is None
    schema = _get_schema_step_1(None, {})
    assert schema is not None

    # CONF_LOCATION is '""' in user_input
    schema = _get_schema_step_1({"location": '""', "api_key": "test"}, {})
    assert schema is not None

    # CONF_LOCATION is '""' in default_dict
    schema = _get_schema_step_1({}, {"location": '""'})
    assert schema is not None


async def test_get_schema_step_2():
    """Test _get_schema_step_2."""
    from custom_components.openei.config_flow import _get_schema_step_2
    # user_input is None
    schema = _get_schema_step_2(None, {}, ["Utility 1"])
    assert schema is not None


async def test_get_schema_step_3(hass):
    """Test _get_schema_step_3."""
    from custom_components.openei.config_flow import _get_schema_step_3
    # user_input is None
    schema = _get_schema_step_3(hass, None, {}, ["Plan 1"])
    assert schema is not None

    # CONF_SENSOR is '(none)' in default_dict
    schema = _get_schema_step_3(hass, {}, {"sensor": "(none)"}, ["Plan 1"])
    assert schema is not None


async def test_lookup_plans():
    """Test _lookup_plans."""
    from custom_components.openei.config_flow import _lookup_plans

    class MockHandler:
        async def lookup_plans(self):
            return {"Utility": [{"name": "Plan", "label": "label"}]}

    handler = MockHandler()
    result = await _lookup_plans(handler)
    assert result == {"Utility": [{"name": "Plan", "label": "label"}]}
