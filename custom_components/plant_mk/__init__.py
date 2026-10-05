"""MK Plant System integration."""
from homeassistant.const import Platform

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass, entry):
    """Set up MK Plant System from a config entry (one per plant)."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry (when the user deletes a plant)."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(hass, entry):
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)