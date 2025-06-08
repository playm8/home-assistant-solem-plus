# Home Assistant Solem Toolkit Plus

> **Parallel fork of [hcraveiro/Home-Assistant-Solem-Toolkit](https://github.com/hcraveiro/Home-Assistant-Solem-Toolkit)**  
> New domain: `solem_toolkit_plus` — can be installed alongside the original!

Integrate Solem Watering Bluetooth Controllers (tested on BL-IP & LR-IP4) into Home Assistant, **without LoRa gateway** or cloud.  
This fork brings more robust connection handling, better logging, and soon: full device setup via UI and status feedback.

---

## 🚀 What's New

- New domain: `solem_toolkit_plus` for parallel install.
- Improved BLE stability: automatic reconnection, retries, clearer error logs.
- Refactored core logic: central SolemClient class, easier code maintenance.
- Groundwork for Home Assistant config flow and polling.
- All credits preserved (see below).

---

## 🛠️ Installation

1. Copy this folder into your Home Assistant `custom_components`.
2. Restart Home Assistant.
3. Use services with `solem_toolkit_plus` as domain.

---

## ⚡ Services

All services are available under the `solem_toolkit_plus` domain.  
Supported :

- `turn_off_permanent`
- `turn_off_x_days`
- `turn_on`
- `sprinkle_station`
- `sprinkle_all`
- `run_program`
- `stop_manual`

_See `services.yaml` for detailed parameters and examples._

**Example (in Home Assistant UI or automation):**
```yaml
service: solem_toolkit_plus.sprinkle_station
data:
  device_mac: "00:11:22:33:44:55"
  station: 1
  minutes: 10


## Credits

- Forked from [hcraveiro/Home-Assistant-Solem-Toolkit](https://github.com/hcraveiro/Home-Assistant-Solem-Toolkit).
- Special thanks to [pcman75](https://github.com/pcman75) for BLE reverse engineering.

MIT License (see LICENSE)
