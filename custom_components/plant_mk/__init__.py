from .const import DOMAIN

async def async_setup_entry(hass, entry):
    """Set up MK Plant System from a config entry (one per plant)."""
    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry (when user deletes a plant)."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")

async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)