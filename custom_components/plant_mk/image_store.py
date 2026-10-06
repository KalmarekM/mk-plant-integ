"""Image file helpers for the MK Plant System integration."""
from __future__ import annotations

from pathlib import Path

from homeassistant.core import HomeAssistant

from .const import IMAGE_DIR_NAME, IMAGE_MAX_BYTES

# Magic-number (first bytes) -> content type, for the formats we accept.
_MAGIC_TO_CONTENT_TYPE = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF8": "image/gif",
    b"RIFF": "image/webp",  # WebP starts with RIFF....WEBP
}

# Map content type to a file extension.
_CONTENT_TYPE_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


def image_dir(hass: HomeAssistant) -> Path:
    """Return the directory where plant photos are stored."""
    return Path(hass.config.path(IMAGE_DIR_NAME))


def image_path_for(hass: HomeAssistant, entry_id: str, content_type: str) -> Path:
    """Return the target file path for a plant photo."""
    ext = _CONTENT_TYPE_EXT.get(content_type, ".jpg")
    return image_dir(hass) / f"{entry_id}{ext}"


def detect_content_type(content: bytes) -> str | None:
    """Return the image content type inferred from magic bytes, or None."""
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    for magic, content_type in _MAGIC_TO_CONTENT_TYPE.items():
        if magic == b"RIFF":
            continue  # handled above (needs the WEBP marker too)
        if content.startswith(magic):
            return content_type
    return None


def find_image_path(hass: HomeAssistant, entry_id: str) -> str | None:
    """Return the persisted photo path for an entry, scanning known extensions."""
    directory = image_dir(hass)
    for ext in _CONTENT_TYPE_EXT.values():
        candidate = directory / f"{entry_id}{ext}"
        if candidate.is_file():
            return str(candidate)
    return None


async def async_save_image(hass: HomeAssistant, entry_id: str, content: bytes) -> str | None:
    """Persist image bytes for an entry. Returns the saved path or None if invalid."""

    content_type = detect_content_type(content)
    if content_type is None or len(content) > IMAGE_MAX_BYTES:
        return None

    def _write() -> str:
        directory = image_dir(hass)
        directory.mkdir(parents=True, exist_ok=True)
        # Remove any previous photo of this entry regardless of extension.
        for old in directory.glob(f"{entry_id}.*"):
            old.unlink(missing_ok=True)
        path = image_path_for(hass, entry_id, content_type)
        path.write_bytes(content)
        return str(path)

    return await hass.async_add_executor_job(_write)
