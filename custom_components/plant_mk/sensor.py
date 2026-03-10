"""
MK Plant System Integration.
License: MIT
Author: Marek (KalmarekM)
"""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass # type: ignore
from homeassistant.const import PERCENTAGE, UnitOfTemperature # type: ignore
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    # Pobieramy dane z entry.data (zawsze aktualne po poprawce w config_flow)
    config = entry.data
    plant_name = config.get("plant_name", "Plant")

    sensors = [
        MKPlantNumericSensor(hass, plant_name, "moisture", config.get("moisture_sensor"), config.get("min_moisture"), config.get("max_moisture")),
        MKPlantNumericSensor(hass, plant_name, "temperature", config.get("temp_sensor"), config.get("min_temp"), config.get("max_temp")),
        MKPlantNumericSensor(hass, plant_name, "humidity", config.get("humi_sensor"), config.get("min_humi"), config.get("max_humi")),
    ]
    async_add_entities(sensors)

class MKPlantNumericSensor(SensorEntity):
    def __init__(self, hass, plant_name, param_type, source_id, min_val, max_val):
        self.hass = hass
        self._plant_name = plant_name
        self._param_type = param_type
        self._source_id = source_id
        self._min_val = min_val
        self._max_val = max_val
        self._attr_unique_id = f"{plant_name}_{param_type}"

        if param_type == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif param_type == "moisture":
            self._attr_device_class = SensorDeviceClass.MOISTURE # Poprawione!
            self._attr_native_unit_of_measurement = PERCENTAGE
        else:
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE

        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self):
        return f"{self._plant_name} {self._param_type.capitalize()}"

    @property
    def native_value(self):
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
        return {
            "min_threshold": self._min_val,
            "max_threshold": self._max_val,
            "source_entity": self._source_id
        }
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._plant_name)},
            "name": self._plant_name,
            "manufacturer": "Marek Custom",
            "model": "Plant System v1",
        }