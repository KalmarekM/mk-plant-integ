import voluptuous as vol # type: ignore
from homeassistant import config_entries # type: ignore
from homeassistant.core import callback  # type: ignore
from homeassistant.helpers.selector import ( # type: ignore
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)
from .const import DOMAIN

class MKPlantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MK Plant System."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["plant_name"], data=user_input)

        data_schema = vol.Schema({
            vol.Required("plant_name"): str,
            
            # Selektor dla sensora wilgotności
            vol.Required("moisture_sensor"): EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class="moisture")
            ),
            vol.Required("min_moisture", default=20): NumberSelector(
                NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
            ),

            # Selektor dla sensora temperatury
            vol.Required("temp_sensor"): EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("min_temp", default=15): NumberSelector(
                NumberSelectorConfig(min=0, max=50, unit_of_measurement="°C", mode=NumberSelectorMode.BOX)
            ),
            
            # Selektor dla sensora wilgotności powietrza
            vol.Required("humi_sensor"): EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class="humidity")
            ),
            vol.Required("min_humi", default=30): NumberSelector(
                NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
            ),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MKPlantOptionsFlowHandler(config_entry)
    
class MKPlantOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for the plant (editing)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Formularz edycji (używamy danych z entry.data jako domyślnych)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("min_moisture", default=self.config_entry.data.get("min_moisture")): int,
                vol.Required("max_moisture", default=self.config_entry.data.get("max_moisture")): int,
                # Tutaj dodaj resztę pól, które chcesz edytować
            })
        )    