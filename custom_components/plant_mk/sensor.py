"""
MK Plant System Integration.
License: MIT
Author: Marek (KalmarekM)
"""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass # type: ignore
from homeassistant.const import PERCENTAGE, UnitOfTemperature # type: ignore

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for a specific plant entry."""
    config = entry.data
    plant_name = config["plant_name"]
    
    # We create 3 sensors for this specific plant
    sensors = [
        MKPlantNumericSensor(hass, plant_name, "moisture", config["moisture_sensor"], config["min_moisture"], config["max_moisture"]),
        MKPlantNumericSensor(hass, plant_name, "temperature", config["temp_sensor"], config["min_temp"], config["max_temp"]),
        MKPlantNumericSensor(hass, plant_name, "humidity", config["humi_sensor"], config["min_humi"], config["max_humi"]),
    ]
    
    async_add_entities(sensors)

class MKPlantNumericSensor(SensorEntity):
    """Numerical sensor for plant parameters."""

    def __init__(self, hass, plant_name, param_type, source_id, min_val, max_val):
        """Initialize the sensor."""
        self.hass = hass
        self._plant_name = plant_name
        self._param_type = param_type
        self._source_id = source_id
        self._min_val = min_val
        self._max_val = max_val
        self._state = None

        # Set units and device classes based on parameter type
        if param_type == "temperature":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        else:
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_device_class = SensorDeviceClass.HUMIDITY

        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._plant_name} {self._param_type.capitalize()}"

    @property
    def native_value(self):
        """Return the current value from the source sensor."""
        source_state = self.hass.states.get(self._source_id)
        if source_state and source_state.state not in ["unknown", "unavailable"]:
            return float(source_state.state)
        return None

    @property
    def extra_state_attributes(self):
        """Return min/max thresholds as attributes for the JS card."""
        return {
            "min_threshold": self._min_val,
            "max_threshold": self._max_val,
            "source_entity": self._source_id
        }
    
    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self._plant_name)}, # type: ignore
            "name": self._plant_name,
            "manufacturer": "Marek Custom",
            "model": "Plant System v1",
        }