"""
MK Plant System Integration - mirrored plant sensors.
License: MIT
Author: Marek (KalmarekM)
"""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_PLANT_DESCRIPTION, DOMAIN, PARAM_CONFIG


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up mirrored plant sensors from a config entry."""
    # Options override data, so the merged config is always current after a reload.
    config = {**entry.data, **entry.options}
    plant_name = config.get("plant_name", "Plant")

    sensors: list[SensorEntity] = [
        MKPlantNumericSensor(
            entry,
            plant_name,
            param_type,
            config.get(source_key),
            config.get(min_key),
            config.get(max_key),
        )
        for param_type, (source_key, min_key, max_key) in PARAM_CONFIG.items()
    ]
    # Optional "About" sensor carrying the free-form plant description.
    sensors.append(
        MKPlantAboutSensor(entry, plant_name, config.get(CONF_PLANT_DESCRIPTION))
    )
    async_add_entities(sensors)


class MKPlantNumericSensor(SensorEntity):
    """Sensor mirroring the numeric value of a configured source sensor."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry, plant_name, param_type, source_id, min_val, max_val):
        """Initialize the mirrored sensor."""
        self._source_id = source_id
        self._min_val = min_val
        self._max_val = max_val
        # Unique ID is tied to the config entry: renaming the plant is safe and
        # two plants may share the same display name without collisions.
        self._attr_unique_id = f"{entry.entry_id}_{param_type}"
        self._attr_translation_key = param_type

        if param_type == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif param_type == "moisture":
            self._attr_device_class = SensorDeviceClass.MOISTURE
            self._attr_native_unit_of_measurement = PERCENTAGE
        else:
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=plant_name,
            manufacturer="Marek Custom",
            model="Plant System v1",
        )

    async def async_added_to_hass(self):
        """Mirror source updates immediately instead of polling."""
        if self._source_id:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, [self._source_id], self._handle_source_update
                )
            )

    @callback
    def _handle_source_update(self, event):
        """Write the new state when the source sensor changes."""
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the current numeric value of the source sensor."""
        if not self._source_id:
            return None
        source_state = self.hass.states.get(self._source_id)
        if source_state and source_state.state not in ["unknown", "unavailable"]:
            try:
                return float(source_state.state)
            except ValueError:
                return None
        return None

    @property
    def extra_state_attributes(self):
        """Expose thresholds and the source entity for transparency."""
        return {
            "min_threshold": self._min_val,
            "max_threshold": self._max_val,
            "source_entity": self._source_id,
        }


class MKPlantAboutSensor(SensorEntity):
    """Sensor holding the optional free-form plant description.

    The full (markdown) description lives in the `description` attribute so it
    is not limited by the 255-character entity state cap; the state only
    signals whether a description is present.
    """

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "about"
    _attr_icon = "mdi:information-outline"

    def __init__(self, entry, plant_name, description):
        """Initialize the About sensor."""
        self._description = (description or "").strip()
        self._attr_unique_id = f"{entry.entry_id}_about"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=plant_name,
            manufacturer="Marek Custom",
            model="Plant System v1",
        )

    @property
    def native_value(self):
        """Return a short state; the full text is in the attribute."""
        if not self._description:
            return None
        return "set"

    @property
    def extra_state_attributes(self):
        """Expose the full markdown description for a Lovelace markdown card."""
        return {"description": self._description}
