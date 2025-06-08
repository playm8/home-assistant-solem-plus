# Solem Toolkit Plus – Home Assistant BLE Integration

[![GitHub license](https://img.shields.io/github/license/playm8/home-assistant-solem-plus)](LICENSE)

> **Inspired by [hcraveiro/Home-Assistant-Solem-Toolkit](https://github.com/hcraveiro/Home-Assistant-Solem-Toolkit) – credit and thanks to [@hcraveiro](https://github.com/hcraveiro) for the original work and BLE protocol insights.**

---

## Description

This custom integration brings native Bluetooth Low Energy (BLE) support for SOLEM irrigation controllers (LR-IP, BL-IP, etc.) to Home Assistant.

You can control watering (on/off), monitor battery level, and benefit from **automatic device discovery** using SOLEM’s official BLE manufacturer ID (`0x079E`, decimal `1950`).

---

## Features

- **BLE auto-discovery:** Any SOLEM device advertising Company ID `0x079E` is automatically detected, and Home Assistant will suggest integration setup.
- **Exposes entities:**  
  - `switch` entity for starting/stopping irrigation
  - `sensor` entity for battery level (percentage)
- **Manual setup available:** Add a device by entering its MAC address if needed.
- **Reliable polling and BLE commands:** For up-to-date status and actions.
- **All code and documentation in English.**

---

## Improvements over the original project

- **Native Home Assistant entities:** Provides `switch` and `sensor` rather than only services.
- **BLE auto-discovery:** Instantly detects SOLEM devices by Company ID (no more manual scanning required).
- **English codebase and UI**
- **Cleaner architecture:** Config Flow, DataUpdateCoordinator pattern, ready for multi-zone/sensor expansion.
- **Manual installation instructions:** Simple setup for users without HACS.

---

## Requirements

- Home Assistant (tested on Core 2024.x+)
- Compatible Bluetooth adapter (internal or USB)
- SOLEM BLE controller (LR-IP, BL-IP, etc.)

---

## Installation (manual, without HACS)

1. **Download or clone this repository.**

2. **Copy all files** in `custom_components/solem_toolkit_plus/` to your Home Assistant configuration folder:


3. **Restart Home Assistant.**

4. Go to **Settings → Devices & Services → Add Integration**.
- If your SOLEM controller is powered and broadcasting, Home Assistant will show a “Solem Toolkit Plus discovered” card.
- Otherwise, select "Solem Toolkit Plus" and enter the device MAC address manually.

---

## Supported Devices

Any SOLEM device broadcasting the manufacturer Company ID:
- **Manufacturer:** SOLEM Électronique
- **Company ID:** `0x079E` (1950 decimal)  
([Bluetooth SIG official database](https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/))

---

## Credits

- **Original BLE research and inspiration:**  
[hcraveiro/Home-Assistant-Solem-Toolkit](https://github.com/hcraveiro/Home-Assistant-Solem-Toolkit)
- **Improvements, English refactor, and Home Assistant entity architecture:**  
[Loïc V (playm8)](https://github.com/playm8)

---

## License

MIT License (see [LICENSE](LICENSE) file).

---

## Contribution

Contributions and bug reports are welcome!  
Please open issues or pull requests.

