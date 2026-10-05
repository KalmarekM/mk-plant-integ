"""Tests for the MK Plant mirrored sensors."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.plant_mk.const import DOMAIN


pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


TEST_DATA = {
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


async def _setup_entry(hass) -> MockConfigEntry:
    """Create and set up a config entry for the tests."""
    entry = MockConfigEntry(domain=DOMAIN, title=TEST_DATA["plant_name"], data=TEST_DATA)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


@pytest.mark.asyncio
async def test_sensors_mirror_source_states(hass) -> None:
    """Mirrored sensors expose the numeric value of their source sensors."""
    await _setup_entry(hass)

    hass.states.async_set("sensor.soil_moisture_a", "25")
    hass.states.async_set("sensor.temperature_a", "21.5")
    hass.states.async_set("sensor.humidity_a", "55")
    await hass.async_block_till_done()

    assert hass.states.get("sensor.monstera_moisture").state == "25.0"
    assert hass.states.get("sensor.monstera_temperature").state == "21.5"
    assert hass.states.get("sensor.monstera_humidity").state == "55.0"


@pytest.mark.asyncio
async def test_sensor_updates_immediately_on_source_change(hass) -> None:
    """State tracking pushes the new value without waiting for a poll."""
    await _setup_entry(hass)

    hass.states.async_set("sensor.soil_moisture_a", "25")
    await hass.async_block_till_done()
    assert hass.states.get("sensor.monstera_moisture").state == "25.0"

    hass.states.async_set("sensor.soil_moisture_a", "42")
    await hass.async_block_till_done()
    assert hass.states.get("sensor.monstera_moisture").state == "42.0"


@pytest.mark.asyncio
async def test_sensor_unknown_when_source_unavailable(hass) -> None:
    """Mirrored sensor reports unknown when the source is unavailable."""
    hass.states.async_set("sensor.soil_moisture_a", "unavailable")
    await _setup_entry(hass)

    state = hass.states.get("sensor.monstera_moisture")
    assert state is not None
    assert state.state == "unknown"


@pytest.mark.asyncio
async def test_sensor_exposes_threshold_attributes(hass) -> None:
    """Thresholds and the source entity are exposed as attributes."""
    await _setup_entry(hass)

    attributes = hass.states.get("sensor.monstera_moisture").attributes
    assert attributes["min_threshold"] == 20
    assert attributes["max_threshold"] == 60
    assert attributes["source_entity"] == "sensor.soil_moisture_a"
