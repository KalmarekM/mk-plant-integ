import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Konfiguracja integracji przez plik configuration.yaml (opcjonalnie)."""
    _LOGGER.info("Inicjalizacja MK Plant System...")
    return True

async def async_setup_entry(hass, entry):
    """Set up MK Plant System from a config entry."""
    # Przekazuje dane z formularza do platformy sensorów
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
