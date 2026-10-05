"""Constants for the MK Plant System integration."""

DOMAIN = "plant_mk"

# Mapping: plant parameter -> (source entity key, min threshold key, max threshold key).
PARAM_CONFIG = {
    "moisture": ("moisture_sensor", "min_moisture", "max_moisture"),
    "temperature": ("temp_sensor", "min_temp", "max_temp"),
    "humidity": ("humi_sensor", "min_humi", "max_humi"),
}