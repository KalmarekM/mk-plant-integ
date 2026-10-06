import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

try:
    from homeassistant.helpers.selector import (
        EntitySelector,
        EntitySelectorConfig,
        FileSelector,
        FileSelectorConfig,
        NumberSelector,
        NumberSelectorConfig,
        NumberSelectorMode,
        TextSelector,
        TextSelectorConfig,
    )
    HAS_SELECTORS = True
except ImportError:  # pragma: no cover
    HAS_SELECTORS = False

from .const import (
    CONF_PLANT_DESCRIPTION,
    CONF_PLANT_IMAGE,
    CONF_PLANT_IMAGE_PATH,
    DESCRIPTION_MAX_LENGTH,
    DOMAIN,
)
from .image_store import async_save_image


def _num_default(defaults, key, fallback):
    """Return numeric default robustly, even for legacy string values."""
    value = defaults.get(key, fallback)
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _entry_defaults(config_entry):
    """Return editable defaults for the options flow."""
    defaults = dict(config_entry.data)
    defaults.update(config_entry.options)
    return defaults


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


def validate_description(data):
    """Validate the optional plant description length."""
    errors = {}
    description = data.get(CONF_PLANT_DESCRIPTION) or ""
    if len(description) > DESCRIPTION_MAX_LENGTH:
        errors[CONF_PLANT_DESCRIPTION] = "description_too_long"
    return errors


async def _async_persist_image(hass, entry_id, user_input, existing_path):
    """Persist an uploaded photo (if any) and record its path in user_input.

    Returns an error dict for the image field; empty when no photo was uploaded
    or the photo was saved successfully. When no new photo is uploaded the
    previously stored path is preserved.
    """
    file_id = user_input.pop(CONF_PLANT_IMAGE, None)
    if not file_id:
        if existing_path:
            user_input[CONF_PLANT_IMAGE_PATH] = existing_path
        return {}

    try:
        from homeassistant.components.file_upload import process_uploaded_file
    except ImportError:  # pragma: no cover
        return {CONF_PLANT_IMAGE: "image_upload_failed"}

    def _read_uploaded_file() -> bytes:
        """Read the uploaded file. Runs in the executor (blocking I/O).

        process_uploaded_file must be run on the executor thread pool: it
        removes the temp file in its teardown, which must not block the loop.
        """
        with process_uploaded_file(hass, file_id) as uploaded:
            return uploaded.read_bytes()

    try:
        content = await hass.async_add_executor_job(_read_uploaded_file)
    except ValueError:
        return {CONF_PLANT_IMAGE: "image_upload_failed"}

    saved_path = await async_save_image(hass, entry_id, content)
    if saved_path is None:
        return {CONF_PLANT_IMAGE: "invalid_image"}

    user_input[CONF_PLANT_IMAGE_PATH] = saved_path
    return {}


class MKPlantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def _user_schema(self, defaults):
        """Build the user (create) schema."""
        description_default = defaults.get(CONF_PLANT_DESCRIPTION, "")
        if HAS_SELECTORS:
            return vol.Schema({
                vol.Required("plant_name", default=defaults.get("plant_name", "")): str,
                vol.Required("moisture_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required("temp_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required("humi_sensor"): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Optional(CONF_PLANT_DESCRIPTION, default=description_default): TextSelector(
                    TextSelectorConfig(multiline=True)
                ),
                vol.Optional(CONF_PLANT_IMAGE): FileSelector(
                    FileSelectorConfig(accept="image/*")
                ),
            }).extend(plant_schema(defaults, use_selectors=True).schema)

        return vol.Schema({
            vol.Required("plant_name", default=defaults.get("plant_name", "")): str,
            vol.Required("moisture_sensor"): str,
            vol.Required("temp_sensor"): str,
            vol.Required("humi_sensor"): str,
            vol.Optional(CONF_PLANT_DESCRIPTION, default=description_default): str,
        }).extend(plant_schema(defaults, use_selectors=False).schema)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            errors = validate_thresholds(user_input)
            errors.update(validate_description(user_input))
            if not errors:
                # The entry does not exist yet; use the plant name as the
                # temporary photo filename key for the new entry.
                image_errors = await _async_persist_image(
                    self.hass, user_input["plant_name"], user_input, None
                )
                if not image_errors:
                    return self.async_create_entry(
                        title=user_input["plant_name"], data=user_input
                    )
                errors = image_errors

        full_schema = self._user_schema(user_input or {})
        if user_input:
            # Keep the values the user typed when re-showing the form after errors.
            full_schema = self.add_suggested_values_to_schema(full_schema, user_input)

        return self.async_show_form(step_id="user", data_schema=full_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MKPlantOptionsFlowHandler()


class MKPlantOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow storing editable settings in entry.options."""

    def _options_schema(self):
        """Build options schema with sensor bindings and thresholds."""
        defaults = _entry_defaults(self.config_entry)
        description_default = defaults.get(CONF_PLANT_DESCRIPTION, "")

        if HAS_SELECTORS:
            return vol.Schema({
                vol.Required(
                    "moisture_sensor",
                    default=defaults.get("moisture_sensor", ""),
                ): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required(
                    "temp_sensor",
                    default=defaults.get("temp_sensor", ""),
                ): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required(
                    "humi_sensor",
                    default=defaults.get("humi_sensor", ""),
                ): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Optional(
                    CONF_PLANT_DESCRIPTION, default=description_default
                ): TextSelector(TextSelectorConfig(multiline=True)),
                vol.Optional(CONF_PLANT_IMAGE): FileSelector(
                    FileSelectorConfig(accept="image/*")
                ),
            }).extend(plant_schema(defaults, use_selectors=True).schema)

        return vol.Schema({
            vol.Required("moisture_sensor", default=defaults.get("moisture_sensor", "")): str,
            vol.Required("temp_sensor", default=defaults.get("temp_sensor", "")): str,
            vol.Required("humi_sensor", default=defaults.get("humi_sensor", "")): str,
            vol.Optional(CONF_PLANT_DESCRIPTION, default=description_default): str,
        }).extend(plant_schema(defaults, use_selectors=False).schema)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            errors = validate_thresholds(user_input)
            errors.update(validate_description(user_input))
            if not errors:
                existing_path = self.config_entry.data.get(
                    CONF_PLANT_IMAGE_PATH
                ) or self.config_entry.options.get(CONF_PLANT_IMAGE_PATH)
                image_errors = await _async_persist_image(
                    self.hass, self.config_entry.entry_id, user_input, existing_path
                )
                if not image_errors:
                    # Options live in entry.options; the update listener reloads the entry.
                    return self.async_create_entry(title="", data=user_input)
                errors = image_errors
            return self.async_show_form(
                step_id="init",
                data_schema=self.add_suggested_values_to_schema(self._options_schema(), user_input),
                errors=errors,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self._options_schema(),
        )
