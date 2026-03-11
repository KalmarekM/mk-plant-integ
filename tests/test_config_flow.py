"""Tests for the MK Plant config and options flow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

try:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
except ImportError:
    from tests.common import MockConfigEntry

from custom_components.plant_mk.const import DOMAIN


pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


TEST_USER_INPUT = {
    "plant_name": "Monstera",
    "moisture_sensor": "sensor.soil_moisture_a",
    "temp_sensor": "sensor.temperature_a",
    "humi_sensor": "sensor.humidity_a",
    "min_moisture": 20,
    "max_moisture": 60,
    "min_temp": 15,
    "max_temp": 30,
    "min_humi": 30,
    "max_humi": 80,
}

UPDATED_OPTIONS_INPUT = {
    "moisture_sensor": "sensor.soil_moisture_b",
    "temp_sensor": "sensor.temperature_b",
    "humi_sensor": "sensor.humidity_b",
    "min_moisture": 25,
    "max_moisture": 65,
    "min_temp": 16,
    "max_temp": 29,
    "min_humi": 35,
    "max_humi": 75,
}


@pytest.mark.asyncio
async def test_user_flow_creates_entry(hass) -> None:
    """Test creating an entry from the user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=TEST_USER_INPUT,
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == TEST_USER_INPUT["plant_name"]
    assert result["data"] == TEST_USER_INPUT


@pytest.mark.asyncio
async def test_options_flow_updates_sources_and_thresholds(hass) -> None:
    """Test editing source sensors and thresholds for an existing entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_USER_INPUT["plant_name"],
        data=TEST_USER_INPUT,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    schema_fields = {field.schema for field in result["data_schema"].schema}
    assert {"moisture_sensor", "temp_sensor", "humi_sensor"}.issubset(schema_fields)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=UPDATED_OPTIONS_INPUT,
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.data == {**TEST_USER_INPUT, **UPDATED_OPTIONS_INPUT}


@pytest.mark.asyncio
async def test_options_flow_rejects_invalid_ranges(hass) -> None:
    """Test validation for invalid threshold ranges in options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_USER_INPUT["plant_name"],
        data=TEST_USER_INPUT,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            **UPDATED_OPTIONS_INPUT,
            "min_moisture": 70,
            "max_moisture": 60,
            "min_temp": 31,
            "max_temp": 29,
            "min_humi": 80,
            "max_humi": 75,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    assert result["errors"] == {
        "min_moisture": "invalid_moisture_range",
        "min_temp": "invalid_temp_range",
        "min_humi": "invalid_humi_range",
    }


def test_polish_options_title_translation() -> None:
    """Test the options dialog title translation shown in Polish UI."""
    translation_path = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "plant_mk"
        / "translations"
        / "pl.json"
    )

    translations = json.loads(translation_path.read_text(encoding="utf-8"))

    assert translations["options"]["step"]["init"]["title"] == "Konfiguracja"