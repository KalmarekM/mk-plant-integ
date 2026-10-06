# MK Plant System

🇵🇱 **Polska wersja**: [README_PL.md](README_PL.md)

A custom [Home Assistant](https://www.home-assistant.io/) integration (HACS) for monitoring houseplants. Each plant gets its own device that groups [mirrored](#mirrored-source-sensor) readings from physical sensors together with binary alarm sensors that signal when a parameter leaves its configured range.

## Features

- **[Mirrored sensors](#mirrored-source-sensor)** — soil moisture, temperature, and air humidity mirror the values of the source sensors you pick, updated instantly on every source change (no polling).
- **Binary "problem" sensors** — turn `on` when a parameter leaves its configured min–max range. A ready-made trigger for automations.
- **100% UI configuration** — config flow with entity selectors and threshold sliders; the options flow lets you change source sensors and thresholds later without deleting the plant.
- **Range validation** — the form rejects a configuration where the minimum is greater than the maximum.
- **One config entry = one plant** — add any number of plants, each with its own thresholds.
- **PL / EN translations**.

## Requirements

- Home Assistant 2024.11 or newer (tested on 2025.1).
- Existing sensor entities (soil moisture, temperature, humidity) provided by other integrations, e.g. Xiaomi MiFlora, ESPHome, Zigbee2MQTT.

## Installation

### Via HACS (custom repository)

1. Open **HACS → Integrations**, menu **⋮** → **Custom repositories**.
2. Paste `https://github.com/KalmarekM/mk-plant-integ` and select the **Integration** category.
3. Install **MK Plant System** and restart Home Assistant.

### Manually

1. Copy the `custom_components/plant_mk` directory into your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. **Settings → Devices & Services → Add integration → MK Plant System**.
2. Enter the plant name, pick three source sensors, and set the min/max thresholds.
3. To change the settings of an existing plant: **Settings → Devices & Services → MK Plant System → Configure**. The entry reloads automatically after saving the options.

## Entities

For a plant named "Monstera", a device is created with the following entities:

| Entity | Description |
| --- | --- |
| `sensor.monstera_moisture` | Soil moisture ([mirror](#mirrored-source-sensor) of the source, %) |
| `sensor.monstera_temperature` | Temperature ([mirror](#mirrored-source-sensor) of the source, °C) |
| `sensor.monstera_humidity` | Air humidity ([mirror](#mirrored-source-sensor) of the source, %) |
| `binary_sensor.monstera_moisture_problem` | `on` when soil moisture is out of range |
| `binary_sensor.monstera_temperature_problem` | `on` when temperature is out of range |
| `binary_sensor.monstera_humidity_problem` | `on` when air humidity is out of range |

Every entity exposes the `min_threshold`, `max_threshold`, and `source_entity` attributes.

## Example automation

```yaml
alias: Plant needs attention
triggers:
  - trigger: state
    entity_id: binary_sensor.monstera_moisture_problem
    to: "on"
actions:
  - action: notify.notify
    data:
      message: "Monstera: soil moisture out of range!"
```

## Development and tests

- Environment: `.venv312` (Python 3.12).
- Tests: `pytest` with `pytest-homeassistant-custom-component`.

```powershell
.venv312/Scripts/python.exe -m pytest tests -q
```

## Changelog

### [1.1.0] — 2026-10-05

#### Added
- Binary `*_problem` sensors (device class PROBLEM) signaling when parameters leave the min–max range.
- Tests for the `sensor` and `binary_sensor` platforms.

#### Changed
- **Breaking change:** entity `unique_id`s are now based on the config entry ID instead of the plant name. Existing entities will be orphaned — remove them from the entity registry or delete and re-add your plants.
- Options are stored in `entry.options` following Home Assistant conventions (previously they overwrote `entry.data`).
- Entities update instantly on source sensor state changes (event tracking instead of polling every 30 s).
- After a validation error the form keeps the entered values (suggested values).
- Manifest: added `integration_type: device`, changed `iot_class` to `calculated`.

#### Removed
- Dead fallback import of `tests.common` in tests.

### [1.0.17]

- Config flow with min/max range validation.
- Options flow (editing source sensors and thresholds).
- PL/EN translations.
- Config flow and options flow tests.

## Mirrored source sensor

A **mirror** is a sensor that **does not measure anything itself — it reflects the value of another, selected source entity** in a 1:1 relationship. You pick the source sensor in the configuration (e.g. `sensor.soil_moisture_a` from ESPHome, Xiaomi MiFlora, or Zigbee2MQTT), and the created entity (e.g. `sensor.monstera_moisture`) always shows exactly the same value as its source:

| Source sensor | Mirror |
| --- | --- |
| `sensor.soil_moisture_a` = `25` | `sensor.monstera_moisture` = `25.0` |
| `sensor.soil_moisture_a` = `unavailable` | `sensor.monstera_moisture` = `unknown` |

How it works:

- The mirror **does not poll** the device — it listens for source entity state change events (`async_track_state_change_event`), so it updates instantly on every source change.
- When the source is `unknown` or `unavailable`, the mirror reports `unknown`.

Why use a mirror when the value is identical to the source? The integration adds **plant logic** on top of the mirror that the physical sensor does not have:

- it assigns the entity to a device (e.g. "Monstera"), so all of the plant's entities are grouped in the UI,
- it adds `min_threshold` and `max_threshold` attributes with the min/max thresholds,
- based on those thresholds it drives the `*_problem` binary sensor, which can trigger automations.

## License

MIT — see [LICENSE](LICENSE) and [LICENSE_PL](LICENSE_PL).
