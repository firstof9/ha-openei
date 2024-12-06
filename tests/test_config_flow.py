"""Test OpenEI config flow."""

import logging
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

    with patch(
        "custom_components.openei.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.openei.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry, patch(
        "custom_components.openei.config_flow._lookup_plans",
        return_value={
            "Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}]
        },
    ), patch(
        "custom_components.openei.config_flow._get_entities",
        return_value=["(none)"],
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
    assert len(mock_setup.mock_calls) == 1
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

    with patch(
        "custom_components.openei.config_flow._lookup_plans",
        return_value={
            "Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}],
            "New Fake Utility Co": [{"name": "Fake Plan Name", "label": "new_randomstring"}]
        },
    ), patch(
        "custom_components.openei.config_flow._get_entities",
        return_value=["(none)"],
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