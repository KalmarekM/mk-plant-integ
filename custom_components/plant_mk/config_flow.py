import voluptuous as vol # type: ignore
from homeassistant import config_entries # type: ignore
from homeassistant.core import callback # type: ignore

try:
    from homeassistant.helpers.selector import ( # type: ignore
        EntitySelector,
        EntitySelectorConfig,
        NumberSelector,
        NumberSelectorConfig,
        NumberSelectorMode,
    )
    HAS_SELECTORS = True
except ImportError:  # pragma: no cover
    HAS_SELECTORS = False

from .const import DOMAIN


def _num_default(defaults, key, fallback):
    """Return numeric default robustly, even for legacy string values."""
    value = defaults.get(key, fallback)
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback

def plant_schema(defaults, use_selectors=False):
    """Build threshold schema for setup and options flows."""
    if use_selectors and HAS_SELECTORS:
        return vol.Schema({
            vol.Required("min_moisture", default=_num_default(defaults, "min_moisture", 20)): NumberSelector(
                NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
            ),
            vol.Required("max_moisture", default=_num_default(defaults, "max_moisture", 60)): NumberSelector(
                NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
            ),
            vol.Required("min_temp", default=_num_default(defaults, "min_temp", 15)): NumberSelector(
                NumberSelectorConfig(min=0, max=50, unit_of_measurement="°C", mode=NumberSelectorMode.BOX)
            ),
            vol.Required("max_temp", default=_num_default(defaults, "max_temp", 30)): NumberSelector(
                NumberSelectorConfig(min=0, max=50, unit_of_measurement="°C", mode=NumberSelectorMode.BOX)
            ),
            vol.Required("min_humi", default=_num_default(defaults, "min_humi", 30)): NumberSelector(
                NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
            ),
            vol.Required("max_humi", default=_num_default(defaults, "max_humi", 80)): NumberSelector(
                NumberSelectorConfig(min=0, max=100, mode=NumberSelectorMode.SLIDER)
            ),
        })

    return vol.Schema({
        vol.Required("min_moisture", default=_num_default(defaults, "min_moisture", 20)): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        vol.Required("max_moisture", default=_num_default(defaults, "max_moisture", 60)): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        vol.Required("min_temp", default=_num_default(defaults, "min_temp", 15)): vol.All(vol.Coerce(float), vol.Range(min=0, max=50)),
        vol.Required("max_temp", default=_num_default(defaults, "max_temp", 30)): vol.All(vol.Coerce(float), vol.Range(min=0, max=50)),
        vol.Required("min_humi", default=_num_default(defaults, "min_humi", 30)): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        vol.Required("max_humi", default=_num_default(defaults, "max_humi", 80)): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
    })


def validate_thresholds(data):
    """Validate all min/max threshold pairs."""
    errors = {}
    if data["min_moisture"] > data["max_moisture"]:
        errors["min_moisture"] = "invalid_moisture_range"
    if data["min_temp"] > data["max_temp"]:
        errors["min_temp"] = "invalid_temp_range"
    if data["min_humi"] > data["max_humi"]:
        errors["min_humi"] = "invalid_humi_range"
    return errors

class MKPlantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            errors = validate_thresholds(user_input)
            if not errors:
                return self.async_create_entry(title=user_input["plant_name"], data=user_input)

        if HAS_SELECTORS:
            full_schema = vol.Schema({
                vol.Required("plant_name"): str,
                vol.Required("moisture_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required("temp_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required("humi_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
            }).extend(plant_schema({}, use_selectors=True).schema)
        else:
            full_schema = vol.Schema({
                vol.Required("plant_name"): str,
                vol.Required("moisture_sensor"): str,
                vol.Required("temp_sensor"): str,
                vol.Required("humi_sensor"): str,
            }).extend(plant_schema({}, use_selectors=False).schema)

        return self.async_show_form(step_id="user", data_schema=full_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MKPlantOptionsFlowHandler(config_entry)

class MKPlantOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    def _options_schema(self):
        """Build options schema with sensor bindings and thresholds."""
        defaults = self._config_entry.data
        return vol.Schema({
            vol.Required("moisture_sensor", default=defaults.get("moisture_sensor", "")): str,
            vol.Required("temp_sensor", default=defaults.get("temp_sensor", "")): str,
            vol.Required("humi_sensor", default=defaults.get("humi_sensor", "")): str,
        }).extend(plant_schema(defaults, use_selectors=False).schema)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            errors = validate_thresholds(user_input)
            if not errors:
                # Persist thresholds in entry.data to keep entity setup logic simple.
                new_data = dict(self._config_entry.data)
                new_data.update(user_input)
                self.hass.config_entries.async_update_entry(self._config_entry, data=new_data)
                return self.async_create_entry(title="", data={})
            return self.async_show_form(
                step_id="init",
                data_schema=self._options_schema(),
                errors=errors,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self._options_schema(),
        )