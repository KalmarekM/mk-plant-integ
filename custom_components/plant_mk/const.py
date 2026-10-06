"""Constants for the MK Plant System integration."""

DOMAIN = "plant_mk"

# Mapping: plant parameter -> (source entity key, min threshold key, max threshold key).
PARAM_CONFIG = {
    "moisture": ("moisture_sensor", "min_moisture", "max_moisture"),
    "temperature": ("temp_sensor", "min_temp", "max_temp"),
    "humidity": ("humi_sensor", "min_humi", "max_humi"),
}

# Config entry keys for the optional plant description and photo.
CONF_PLANT_DESCRIPTION = "plant_description"
CONF_PLANT_IMAGE = "plant_image"  # upload file_id (transient, config flow only)
CONF_PLANT_IMAGE_PATH = "plant_image_path"  # persisted absolute path

# Description limits (markdown content shown via a Lovelace markdown card).
DESCRIPTION_MAX_LENGTH = 2000

# Photo storage under the Home Assistant config dir.
IMAGE_DIR_NAME = "plant_mk/images"
IMAGE_MAX_BYTES = 5 * 1024 * 1024  # 5 MB