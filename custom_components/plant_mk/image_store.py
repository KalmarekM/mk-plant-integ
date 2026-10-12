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


async def async_save_image(
    hass: HomeAssistant, key: str, content: bytes, old_path: str | None = None
) -> str | None:
    """Persist image bytes under key. Returns the saved path or None if invalid.

    When old_path is given, the previously stored file is removed, so replacing
    a photo never leaves orphaned files on disk (the old file may have been
    named differently, e.g. by flow id at creation time).
    """

    content_type = detect_content_type(content)
    if content_type is None or len(content) > IMAGE_MAX_BYTES:
        return None

    def _write() -> str:
        directory = image_dir(hass)
        directory.mkdir(parents=True, exist_ok=True)
        if old_path:
            Path(old_path).unlink(missing_ok=True)
        else:
            # Remove any previous photo stored under this key.
            for old in directory.glob(f"{key}.*"):
                old.unlink(missing_ok=True)
        path = image_path_for(hass, key, content_type)
        path.write_bytes(content)
        return str(path)

    return await hass.async_add_executor_job(_write)


async def async_remove_image(hass: HomeAssistant, path: str) -> None:
    """Delete a previously persisted plant photo."""

    def _remove() -> None:
        Path(path).unlink(missing_ok=True)

    await hass.async_add_executor_job(_remove)
