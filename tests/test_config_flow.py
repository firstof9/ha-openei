"""Test OpenEI config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, setup
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openei.const import DOMAIN


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            {
                "api_key": "fakeAPIKey",
                "radius": "",
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
                "radius": None,
                "utility": "Fake Utility Co",
                "rate_plan": "randomstring",
                "sensor": "(none)",
                "location": None,
                "manual_plan": None,
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
    # assert result["title"] == title_1

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
    "input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            {
                "api_key": "fakeAPIKey_new",
                "radius": "20",
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
                "api_key": "fakeAPIKey_new",
                "radius": "20",
                "utility": "Fake Utility Co",
                "rate_plan": "randomstring",
                "sensor": None,
                "location": "",
                "manual_plan": "",
            },
        ),
    ],
)
async def test_options_flow(
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
    """Test config flow options."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data={
            "api_key": "fakeAPIKey",
            "radius": "",
            "location": "",
            "utility": "Fake Utility Co",
            "rate_plan": "randomstring",
            "sensor": "(none)",
            "manual_plan": "",
        },
    )

    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch("custom_components.openei.async_setup", return_value=True), patch(
        "custom_components.openei.async_setup_entry",
        return_value=True,
    ), patch(
        "custom_components.openei.config_flow._lookup_plans",
        return_value={
            "Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}]
        },
    ), patch(
        "custom_components.openei.config_flow._get_entities",
        return_value=["(none)"],
    ):

        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_1
        )
        await hass.async_block_till_done()

        assert result2["type"] == "form"
        assert result2["step_id"] == step_id_2

        result3 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_2
        )
        await hass.async_block_till_done()

        assert result3["type"] == "form"
        assert result3["step_id"] == step_id_3
        result4 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_3
        )
        await hass.async_block_till_done()
        assert result4["type"] == "create_entry"
        assert data == entry.data.copy()

        await hass.async_block_till_done()


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            {
                "api_key": "fakeAPIKey",
                "radius": "",
                "location": "",
            },
            "user_2",
            {
                "utility": "Fake Utility Co",
            },
            "user_3",
            {
                "rate_plan": "randomstring",
                "sensor": ["(none)"],
                "manual_plan": "",
            },
            "Fake Utility Co",
            {
                "api_key": "fakeAPIKey",
                "radius": "",
                "utility": "Fake Utility Co",
                "rate_plan": "randomstring",
                "sensor": None,
                "location": "",
                "manual_plan": "",
            },
        ),
    ],
)
async def test_options_flow_no_changes(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    title,
    data,
    hass,
    mock_api,
    caplog,
):
    """Test config flow options."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data={
            "api_key": "fakeAPIKey",
            "radius": "",
            "location": "",
            "utility": "Fake Utility Co",
            "rate_plan": "randomstring",
            "sensor": "(none)",
            "manual_plan": "",
        },
    )

    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch("custom_components.openei.async_setup", return_value=True), patch(
        "custom_components.openei.async_setup_entry",
        return_value=True,
    ), patch(
        "custom_components.openei.config_flow._lookup_plans",
        return_value={
            "Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}]
        },
    ):

        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_1
        )
        await hass.async_block_till_done()

        assert result2["type"] == "form"
        assert result2["step_id"] == step_id_2

        result3 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_2
        )
        await hass.async_block_till_done()

        assert result3["type"] == "form"
        assert result3["step_id"] == step_id_3
        result4 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_3
        )
        await hass.async_block_till_done()
        assert result4["type"] == "create_entry"
        assert data == entry.data.copy()

        await hass.async_block_till_done()
        assert (
            "Attempting to reload entities from the openei integration" in caplog.text
        )


@pytest.mark.parametrize(
    "input_1,step_id_2,input_2,step_id_3,input_3,title,data",
    [
        (
            {
                "api_key": "fakeAPIKey",
                "radius": "",
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
                "radius": "",
                "utility": "Fake Utility Co",
                "rate_plan": "randomstring",
                "sensor": None,
                "location": "",
                "manual_plan": "",
            },
        ),
    ],
)
async def test_options_flow_some_changes(
    input_1,
    step_id_2,
    input_2,
    step_id_3,
    input_3,
    title,
    data,
    hass,
    mock_api,
    caplog,
):
    """Test config flow options."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fake Utility Co",
        data={
            "api_key": "fakeAPIKey",
            "radius": "",
            "location": "12345",
            "utility": "Fake Utility Co",
            "rate_plan": "randomstring",
            "sensor": "(none)",
            "manual_plan": "",
        },
    )

    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["errors"] == {}
    # assert result["title"] == title_1

    with patch("custom_components.openei.async_setup", return_value=True), patch(
        "custom_components.openei.async_setup_entry",
        return_value=True,
    ), patch(
        "custom_components.openei.config_flow._lookup_plans",
        return_value={
            "Fake Utility Co": [{"name": "Fake Plan Name", "label": "randomstring"}]
        },
    ):

        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_1
        )
        await hass.async_block_till_done()

        assert result2["type"] == "form"
        assert result2["step_id"] == step_id_2

        result3 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_2
        )
        await hass.async_block_till_done()

        assert result3["type"] == "form"
        assert result3["step_id"] == step_id_3
        result4 = await hass.config_entries.options.async_configure(
            result["flow_id"], input_3
        )
        await hass.async_block_till_done()
        assert result4["type"] == "create_entry"
        assert data == entry.data.copy()

        await hass.async_block_till_done()
        assert (
            "Attempting to reload entities from the openei integration" in caplog.text
        )