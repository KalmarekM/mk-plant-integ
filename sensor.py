# type: ignore
from homeassistant.components.sensor import SensorEntity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Konfiguracja sensorów z pliku YAML."""
    # Tu będziemy dodawać Twoje rośliny jako encje
    pass

class MKPlantSensor(SensorEntity):
    """Reprezentacja Twojej rośliny jako encji w HA."""
    
    def __init__(self, name, moisture_sensor, min_moisture):
        self._name = name
        self._moisture_sensor = moisture_sensor
        self._min_moisture = min_moisture
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def extra_state_attributes(self):
        """To są dane, które Twoja karta JS odczyta bez dodatkowych encji!"""
        return {
            "min_moisture": self._min_moisture,
            "plant_type": "Dracena",
            "fertilize_hint": "Przerwa zimowa"
        }