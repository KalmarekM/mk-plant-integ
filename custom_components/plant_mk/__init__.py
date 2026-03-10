from .const import DOMAIN

async def async_setup_entry(hass, entry):
    """Set up MK Plant System from a config entry (one per plant)."""
    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry (when user deletes a plant)."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")