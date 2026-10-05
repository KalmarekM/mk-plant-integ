"""
MK Plant System Integration - out-of-range problem binary sensors.
License: MIT
Author: Marek (KalmarekM)
"""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, PARAM_CONFIG


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up out-of-range problem binary sensors from a config entry."""
    # Options override data, so the merged config is always current after a reload.
    config = {**entry.data, **entry.options}
    plant_name = config.get("plant_name", "Plant")

    entities = [
        MKPlantProblemBinarySensor(
            entry,
            plant_name,
            param_type,
            config.get(source_key),
            config.get(min_key),
            config.get(max_key),
        )
        for param_type, (source_key, min_key, max_key) in PARAM_CONFIG.items()
    ]
    async_add_entities(entities)


class MKPlantProblemBinarySensor(BinarySensorEntity):
    """Binary sensor that turns on when a plant parameter leaves its range."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, entry, plant_name, param_type, source_id, min_val, max_val):
        """Initialize the problem binary sensor."""
        self._source_id = source_id
        self._min_val = self._coerce_threshold(min_val)
        self._max_val = self._coerce_threshold(max_val)
        self._attr_unique_id = f"{entry.entry_id}_{param_type}_problem"
        self._attr_translation_key = f"{param_type}_problem"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=plant_name,
            manufacturer="Marek Custom",
            model="Plant System v1",
        )

    @staticmethod
    def _coerce_threshold(value):
        """Return a float threshold or None when it cannot be parsed."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_added_to_hass(self):
        """React to source updates immediately instead of polling."""
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

    def _source_value(self):
        """Return the current numeric value of the source sensor or None."""
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
    def is_on(self):
        """Return True when the value is outside the configured range."""
        value = self._source_value()
        if value is None:
            return None
        if self._min_val is not None and value < self._min_val:
            return True
        if self._max_val is not None and value > self._max_val:
            return True
        return False

    @property
    def extra_state_attributes(self):
        """Expose thresholds and the source entity for transparency."""
        return {
            "min_threshold": self._min_val,
            "max_threshold": self._max_val,
            "source_entity": self._source_id,
        }
