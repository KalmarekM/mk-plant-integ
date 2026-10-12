"""Tests for the MK Plant description (About) and photo (image) features."""

from __future__ import annotations

import pytest
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.plant_mk.const import (
    CONF_PLANT_DESCRIPTION,
    CONF_PLANT_IMAGE_PATH,
    DOMAIN,
)


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

# 1x1 px PNG (magic bytes) for the photo tests.
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
)


async def _setup_entry(hass, extra=None) -> MockConfigEntry:
    """Create and set up a config entry for the tests."""
    data = {**TEST_DATA, **(extra or {})}
    entry = MockConfigEntry(domain=DOMAIN, title=TEST_DATA["plant_name"], data=data)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


@pytest.mark.asyncio
async def test_about_sensor_created(hass) -> None:
    """The About sensor is always created for a plant."""
    await _setup_entry(hass)

    assert hass.states.get("sensor.monstera_about") is not None


@pytest.mark.asyncio
async def test_about_sensor_holds_description(hass) -> None:
    """Full markdown description is exposed in the attribute."""
    description = "**Zamiokulkas** — wytrzymała roślina.\n\n- Światło: półcień"
    await _setup_entry(hass, {CONF_PLANT_DESCRIPTION: description})

    state = hass.states.get("sensor.monstera_about")
    assert state is not None
    assert state.state == "set"
    assert state.attributes["description"] == description


@pytest.mark.asyncio
async def test_about_sensor_empty_without_description(hass) -> None:
    """Without a description the About sensor state is unknown."""
    await _setup_entry(hass)

    state = hass.states.get("sensor.monstera_about")
    assert state is not None
    assert state.state == "unknown"
    assert state.attributes["description"] == ""


@pytest.mark.asyncio
async def test_image_entity_created_when_photo(hass, tmp_path) -> None:
    """The photo image entity is created when an image path is stored."""
    image_file = tmp_path / "monstera.png"
    image_file.write_bytes(PNG_BYTES)

    await _setup_entry(hass, {CONF_PLANT_IMAGE_PATH: str(image_file)})

    state = hass.states.get("image.monstera_photo")
    assert state is not None


@pytest.mark.asyncio
async def test_image_entity_absent_without_photo(hass) -> None:
    """No image entity is created when no photo was stored."""
    await _setup_entry(hass)

    assert hass.states.get("image.monstera_photo") is None


@pytest.mark.asyncio
async def test_options_flow_shows_current_photo_status(hass, tmp_path) -> None:
    """Options flow shows the current photo filename and a remove checkbox."""
    image_file = tmp_path / "monstera.png"
    image_file.write_bytes(PNG_BYTES)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_DATA["plant_name"],
        data={**TEST_DATA, CONF_PLANT_IMAGE_PATH: str(image_file)},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["description_placeholders"] == {"current_photo": "monstera.png"}
    schema_fields = {field.schema for field in result["data_schema"].schema}
    assert "remove_photo" in schema_fields


@pytest.mark.asyncio
async def test_options_flow_shows_no_photo_status(hass) -> None:
    """Options flow shows an em dash when no photo is stored."""
    entry = MockConfigEntry(domain=DOMAIN, title=TEST_DATA["plant_name"], data=TEST_DATA)
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["description_placeholders"] == {"current_photo": "—"}


@pytest.mark.asyncio
async def test_options_flow_removes_photo(hass, tmp_path) -> None:
    """The remove checkbox deletes the photo file and clears the stored path."""
    image_file = tmp_path / "monstera.png"
    image_file.write_bytes(PNG_BYTES)
    entry = await _setup_entry(hass, {CONF_PLANT_IMAGE_PATH: str(image_file)})
    assert hass.states.get("image.monstera_photo") is not None

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "moisture_sensor": "sensor.soil_moisture_a",
            "temp_sensor": "sensor.temperature_a",
            "humi_sensor": "sensor.humidity_a",
            "min_moisture": 20,
            "max_moisture": 60,
            "min_temp": 15,
            "max_temp": 30,
            "min_humi": 30,
            "max_humi": 80,
            "remove_photo": True,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert not image_file.exists()
    # The path is cleared from both data and options, so the photo stays gone.
    config = {**entry.data, **entry.options}
    assert CONF_PLANT_IMAGE_PATH not in config
    assert "remove_photo" not in entry.options
    # Per HA convention the entity stays in the registry as unavailable
    # (restored) once it is no longer provided; the user can delete it from
    # the entity registry. It no longer serves an image.
    state = hass.states.get("image.monstera_photo")
    assert state is not None
    assert state.state == "unavailable"
    assert state.attributes.get("restored") is True
