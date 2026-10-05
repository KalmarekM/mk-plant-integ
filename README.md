# MK Plant System

Niestandardowa integracja [Home Assistant](https://www.home-assistant.io/) (HACS) do monitorowania roślin domowych. Dla każdej rośliny tworzone jest osobne urządzenie, które grupuje lustrzane odczyty z czujników fizycznych oraz binarne sensory alarmowe informujące o wyjściu parametrów poza zadane progi.

## Funkcje

- **Lustrzane sensory** — wilgotność gleby, temperatura i wilgotność powietrza odzwierciedlają wartości wskazanych sensorów źródłowych i są aktualizowane natychmiast po każdej zmianie źródła (bez odpytywania).
- **Binarne sensory „problem”** — włączają się (`on`), gdy wartość parametru wyjdzie poza skonfigurowany zakres min–max. Idealne jako wyzwalacz automatyzacji.
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
| `sensor.monstera_moisture` | Wilgotność gleby (lustro źródła, %) |
| `sensor.monstera_temperature` | Temperatura (lustro źródła, °C) |
| `sensor.monstera_humidity` | Wilgotność powietrza (lustro źródła, %) |
| `binary_sensor.monstera_moisture_problem` | `on`, gdy wilgotność gleby poza zakresem |
| `binary_sensor.monstera_temperature_problem` | `on`, gdy temperatura poza zakresem |
| `binary_sensor.monstera_humidity_problem` | `on`, gdy wilgotność powietrza poza zakresem |

Każda encja udostępnia atrybuty `min_threshold`, `max_threshold` i `source_entity`.

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

## Licencja

MIT — zobacz [LICENSE](LICENSE) oraz [LICENSE_PL](LICENSE_PL).