import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "plant_mk"

async def async_setup(hass, config):
    """Konfiguracja integracji przez plik configuration.yaml (opcjonalnie)."""
    _LOGGER.info("Inicjalizacja MK Plant System...")
    return True

async def async_setup_entry(hass, entry):
    """Konfiguracja integracji przez interfejs użytkownika (UI)."""
    hass.data.setdefault(DOMAIN, {})
    # Tutaj w przyszłości dodamy przekazywanie danych do sensorów
    return True
