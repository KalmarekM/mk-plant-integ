# MK Plant System

🇬🇧 **English version**: [README.md](README.md)

Niestandardowa integracja [Home Assistant](https://www.home-assistant.io/) (HACS) do monitorowania roślin domowych. Dla każdej rośliny tworzone jest osobne urządzenie, które grupuje [lustrzane](#lustro-sensora-źródłowego) odczyty z czujników fizycznych oraz binarne sensory alarmowe informujące o wyjściu parametrów poza zadane progi.

## Funkcje

- **[Lustrzane sensory](#lustro-sensora-źródłowego)** — wilgotność gleby, temperatura i wilgotność powietrza odzwierciedlają wartości wskazanych sensorów źródłowych i są aktualizowane natychmiast po każdej zmianie źródła (bez odpytywania).
- **Binarne sensory „problem”** — włączają się (`on`), gdy wartość parametru wyjdzie poza skonfigurowany zakres min–max. Idealne jako wyzwalacz automatyzacji.
- **Opis rośliny (opcjonalny)** — dowolny tekst markdown pokazywany na sensorze „O roślinie” i renderowany kartą Markdown w Lovelace.
- **Zdjęcie rośliny (opcjonalne)** — prześlij obraz; jest serwowany przez dedykowaną encję `image` na stronie urządzenia.
- **Konfiguracja w 100% z poziomu UI** — config flow z selektorami encji i suwakami progów; options flow pozwala później zmienić sensory źródłowe i progi bez usuwania rośliny.
- **Walidacja zakresów** — formularz odrzuca konfigurację, w której minimum jest większe niż maksimum.
- **Jeden wpis konfiguracyjny = jedna roślina** — można dodać dowolną liczbę roślin, każda z własnymi progami.
- **Tłumaczenia PL / EN**.

## Wymagania

- Home Assistant 2024.11 lub nowszy (testowane na 2025.1).
- Istniejące encje sensorów (wilgotność gleby, temperatura, wilgotność) dostarczane przez inne integracje, np. Xiaomi MiFlora, ESPHome, Zigbee2MQTT.

## Instalacja

### Przez HACS (niestandardowe repozytorium)

1. Otwórz **HACS → Integracje**, menu **⋮** → **Niestandardowe repozytoria**.
2. Wklej adres `https://github.com/KalmarekM/mk-plant-integ` i wybierz kategorię **Integracja**.
3. Zainstaluj **MK Plant System** i zrestartuj Home Assistant.

### Ręcznie

1. Skopiuj katalog `custom_components/plant_mk` do katalogu `config/custom_components` w Home Assistant.
2. Zrestartuj Home Assistant.

## Konfiguracja

1. **Ustawienia → Urządzenia i usługi → Dodaj integrację → MK Plant System**.
2. Podaj nazwę rośliny, wybierz trzy sensory źródłowe i ustaw progi min/max.
3. Aby zmienić ustawienia istniejącej rośliny: **Ustawienia → Urządzenia i usługi → MK Plant System → Konfiguruj**. Po zapisaniu opcji wpis jest przeładowywany automatycznie.

## Encje

Dla rośliny o nazwie „Monstera” powstaje urządzenie z encjami:

| Encja | Opis |
| --- | --- |
| `sensor.monstera_moisture` | Wilgotność gleby ([lustro](#lustro-sensora-źródłowego) źródła, %) |
| `sensor.monstera_temperature` | Temperatura ([lustro](#lustro-sensora-źródłowego) źródła, °C) |
| `sensor.monstera_humidity` | Wilgotność powietrza ([lustro](#lustro-sensora-źródłowego) źródła, %) |
| `binary_sensor.monstera_moisture_problem` | `on`, gdy wilgotność gleby poza zakresem |
| `binary_sensor.monstera_temperature_problem` | `on`, gdy temperatura poza zakresem |
| `binary_sensor.monstera_humidity_problem` | `on`, gdy wilgotność powietrza poza zakresem |
| `sensor.monstera_about` | Opcjonalny opis; pełny markdown w atrybucie `description` |
| `image.monstera_photo` | Opcjonalne zdjęcie rośliny (tylko po przesłaniu) |

Każdy lustrzany/problemowy sensor udostępnia atrybuty `min_threshold`, `max_threshold` i `source_entity`.

### Opis rośliny

Opcjonalny opis obsługuje **markdown** i jest przechowywany w atrybucie `description` encji `sensor.<nazwa>_about`. Aby ładnie wyświetlić go na pulpicie, dodaj kartę Markdown:

```yaml
type: markdown
title: O roślinie
content: "{{ state_attr('sensor.monstera_about', 'description') }}"
```

### Zdjęcie rośliny

Wybierz zdjęcie w config/options flow (JPEG/PNG/GIF/WebP, maks. 5 MB). Jest zapisywane w `config/plant_mk/images/` i serwowane przez uwierzytelnioną encję `image` — nie jest publicznie dostępne przez `/local/`.

## Przykładowa automatyzacja

```yaml
alias: Roślina wymaga uwagi
triggers:
  - trigger: state
    entity_id: binary_sensor.monstera_moisture_problem
    to: "on"
actions:
  - action: notify.notify
    data:
      message: "Monstera: wilgotność gleby poza zakresem!"
```

## Rozwój i testy

- Środowisko: `.venv312` (Python 3.12).
- Testy: `pytest` z `pytest-homeassistant-custom-component`.

```powershell
.venv312/Scripts/python.exe -m pytest tests -q
```

## Dziennik zmian

### [1.2.0] — 2026-10-06

#### Dodane
- Opcjonalny **opis rośliny** (markdown) na nowej encji `sensor.<nazwa>_about`; pełny tekst w atrybucie `description`.
- Opcjonalne **zdjęcie rośliny** przesyłane w config/options flow, serwowane przez nową encję `image.<nazwa>_photo`.
- Testy funkcji opisu i zdjęcia.

### [1.1.0] — 2026-10-05

#### Dodane
- Binarne sensory `*_problem` (klasa urządzenia PROBLEM) sygnalizujące wyjście parametrów poza zakres min–max.
- Testy platform `sensor` i `binary_sensor`.

#### Zmienione
- **Zmiana niekompatybilna:** `unique_id` encji jest teraz oparte na identyfikatorze wpisu konfiguracyjnego zamiast nazwy rośliny. Dotychczasowe encje zostaną osierocone — należy je usunąć z rejestru encji albo usunąć i ponownie dodać rośliny.
- Opcje są zapisywane w `entry.options` zgodnie z konwencją Home Assistant (wcześniej nadpisywały `entry.data`).
- Encje aktualizują się natychmiast po zmianie stanu sensora źródłowego (śledzenie zdarzeń zamiast odpytywania co 30 s).
- Po błędzie walidacji formularz zachowuje wpisane wartości (suggested values).
- Manifest: dodano `integration_type: device`, zmieniono `iot_class` na `calculated`.

#### Usunięte
- Martwy import zastępczy `tests.common` w testach.

### [1.0.17]

- Config flow z walidacją zakresów min/max.
- Options flow (edycja sensorów źródłowych i progów).
- Tłumaczenia PL/EN.
- Testy config flow i options flow.

## Lustro sensora źródłowego

**Lustro** (ang. *mirror*) to sensor, który **nie wykonuje własnego pomiaru — odzwierciedla wartość innej, wskazanej encji źródłowej** w relacji 1:1. Sensor źródłowy wybierasz w konfiguracji (np. `sensor.soil_moisture_a` z integracji ESPHome, Xiaomi MiFlora czy Zigbee2MQTT), a powstała encja (np. `sensor.monstera_moisture`) zawsze pokazuje dokładnie tę samą wartość co źródło:

| Sensor źródłowy | Lustro |
| --- | --- |
| `sensor.soil_moisture_a` = `25` | `sensor.monstera_moisture` = `25.0` |
| `sensor.soil_moisture_a` = `unavailable` | `sensor.monstera_moisture` = `unknown` |

Jak to działa:

- Lustro **nie odpytuje** urządzenia — nasłuchuje zdarzeń zmiany stanu encji źródłowej (`async_track_state_change_event`), więc aktualizuje się natychmiast po każdej zmianie źródła.
- Gdy źródło jest `unknown` lub `unavailable`, lustro przyjmuje stan `unknown`.

Po co stosować lustro, skoro wartość jest identyczna jak w źródle? Integracja dokłada na lustrze **logikę rośliny**, której nie ma sam fizyczny sensor:

- przypisuje encję do urządzenia (np. „Monstera”), dzięki czemu wszystkie jej encje są pogrupowane w UI,
- dodaje atrybuty `min_threshold` i `max_threshold` z progami min/max,
- na podstawie progów steruje binarnym sensorem `*_problem`, który może wyzwalać automatyzacje.

## Licencja

MIT — zobacz [LICENSE](LICENSE) oraz [LICENSE_PL](LICENSE_PL).