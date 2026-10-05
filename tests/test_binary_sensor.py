"""Tests for the MK Plant problem binary sensors."""

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
async def test_problem_binary_sensors_created(hass) -> None:
    """Each plant parameter gets its own problem binary sensor."""
    await _setup_entry(hass)

    assert hass.states.get("binary_sensor.monstera_moisture_problem") is not None
    assert hass.states.get("binary_sensor.monstera_temperature_problem") is not None
    assert hass.states.get("binary_sensor.monstera_humidity_problem") is not None


@pytest.mark.asyncio
async def test_problem_on_when_below_minimum(hass) -> None:
    """Binary sensor turns on when the value drops below the minimum."""
    await _setup_entry(hass)

    hass.states.async_set("sensor.soil_moisture_a", "10")
    await hass.async_block_till_done()

    assert hass.states.get("binary_sensor.monstera_moisture_problem").state == "on"


@pytest.mark.asyncio
async def test_problem_on_when_above_maximum(hass) -> None:
    """Binary sensor turns on when the value rises above the maximum."""
    await _setup_entry(hass)

    hass.states.async_set("sensor.temperature_a", "35")
    await hass.async_block_till_done()

    assert hass.states.get("binary_sensor.monstera_temperature_problem").state == "on"


@pytest.mark.asyncio
async def test_problem_off_within_range(hass) -> None:
    """Binary sensor stays off when the value is within the range."""
    await _setup_entry(hass)

    hass.states.async_set("sensor.humidity_a", "50")
    await hass.async_block_till_done()

    assert hass.states.get("binary_sensor.monstera_humidity_problem").state == "off"


@pytest.mark.asyncio
async def test_problem_unknown_when_source_unavailable(hass) -> None:
    """Binary sensor reports unknown when the source is unavailable."""
    hass.states.async_set("sensor.soil_moisture_a", "unavailable")
    await _setup_entry(hass)

    assert hass.states.get("binary_sensor.monstera_moisture_problem").state == "unknown"
