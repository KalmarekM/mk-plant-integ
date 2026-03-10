import voluptuous as vol
from homeassistant import config_entries # type: ignore
from homeassistant.core import callback # type: ignore
from .const import DOMAIN

class MKPlantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MK Plant System."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user enters plant data."""
        errors = {}
        if user_input is not None:
            # Tutaj można by dodać walidację danych
            return self.async_create_entry(title=user_input["plant_name"], data=user_input)

        # Formularz wyświetlany użytkownikowi
        data_schema = vol.Schema({
            vol.Required("plant_name"): str,
            vol.Required("moisture_sensor"): str,
            vol.Required("min_moisture", default=20): int,
            vol.Required("max_moisture", default=60): int,
            vol.Required("temp_sensor"): str,
            vol.Required("min_temp", default=15): int,
            vol.Required("max_temp", default=30): int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )