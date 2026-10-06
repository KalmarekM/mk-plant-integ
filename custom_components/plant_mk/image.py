"""
MK Plant System Integration - plant photo image entity.
License: MIT
Author: Marek (KalmarekM)
"""
from __future__ import annotations

from pathlib import Path

from homeassistant.components.image import ImageEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import CONF_PLANT_IMAGE_PATH, DOMAIN
from .image_store import detect_content_type


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the plant photo image entity from a config entry."""
    config = {**entry.data, **entry.options}
    plant_name = config.get("plant_name", "Plant")
    image_path = config.get(CONF_PLANT_IMAGE_PATH)

    entities = []
    if image_path:
        entities.append(MKPlantImage(hass, entry, plant_name, image_path))
    async_add_entities(entities)


class MKPlantImage(ImageEntity):
    """Image entity serving the user-uploaded plant photo."""

    _attr_has_entity_name = True
    _attr_translation_key = "photo"

    def __init__(self, hass, entry, plant_name, image_path):
        """Initialize the plant photo image entity."""
        super().__init__(hass)
        self._image_path = image_path
        self._attr_unique_id = f"{entry.entry_id}_photo"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=plant_name,
            manufacturer="Marek Custom",
            model="Plant System v1",
        )
        self._attr_image_last_updated = dt_util.utcnow()

    def image(self) -> bytes | None:
        """Return bytes of the plant photo (run in the executor)."""
        path = Path(self._image_path)
        if not path.is_file():
            return None
        try:
            content = path.read_bytes()
        except OSError:
            return None
        content_type = detect_content_type(content)
        if content_type is None:
            return None
        self._attr_content_type = content_type
        return content
