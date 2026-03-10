import voluptuous as vol # type: ignore
from homeassistant import config_entries # type: ignore
from homeassistant.core import callback # type: ignore
from homeassistant.helpers.selector import ( # type: ignore
    EntitySelector, EntitySelectorConfig,
    NumberSelector, NumberSelectorConfig, NumberSelectorMode,
)
from .const import DOMAIN

def plant_schema(defaults):
    """Pomocnicza funkcja generująca spójny schemat dla instalacji i opcji."""
    return vol.Schema({
        vol.Required("min_moisture", default=defaults.get("min_moisture", 20)): NumberSelector(
            NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
        ),
        vol.Required("max_moisture", default=defaults.get("max_moisture", 60)): NumberSelector(
            NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
        ),
        vol.Required("min_temp", default=defaults.get("min_temp", 15)): NumberSelector(
            NumberSelectorConfig(min=0, max=50, unit_of_measurement="°C", mode=NumberSelectorMode.BOX)
        ),
        vol.Required("max_temp", default=defaults.get("max_temp", 30)): NumberSelector(
            NumberSelectorConfig(min=0, max=50, unit_of_measurement="°C", mode=NumberSelectorMode.BOX)
        ),
        vol.Required("min_humi", default=defaults.get("min_humi", 30)): NumberSelector(
            NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
        ),
        vol.Required("max_humi", default=defaults.get("max_humi", 80)): NumberSelector(
            NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
        ),
    })

class MKPlantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Walidacja min < max
            if user_input["min_moisture"] >= user_input["max_moisture"]:
                errors["base"] = "min_moisture_error"
            else:
                return self.async_create_entry(title=user_input["plant_name"], data=user_input)

        # Do instalacji dodajemy jeszcze nazwę i sensory
        full_schema = vol.Schema({
            vol.Required("plant_name"): str,
            vol.Required("moisture_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
            vol.Required("temp_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
            vol.Required("humi_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
        }).extend(plant_schema({}).schema)

        return self.async_show_form(step_id="user", data_schema=full_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MKPlantOptionsFlowHandler(config_entry)

class MKPlantOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Kluczowe: aktualizujemy dane w entry.data, a nie tylko w options
            new_data = dict(self.config_entry.data)
            new_data.update(user_input)
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(step_id="init", data_schema=plant_schema(self.config_entry.data))