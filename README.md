# Tuya Custom Integration

Custom Home Assistant integration derived from the official Tuya component. It
duplicates the upstream platforms and adds hooks for implementing polling
fallbacks, optimistic cover updates, and post-command refreshes when Tuya Cloud
fails to push MQTT state changes.

## Installation

1. Copy `custom_components/tuya_custom/` into your Home Assistant
   `/config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and select
   **Tuya Custom**.
4. Remove/disable the stock Tuya integration to avoid duplicate cloud sessions.

## Optional: install via HACS

1. Ensure this repository contains `hacs.json` (already included) and the
   structure shown below:

   ```text
   tuya_custom/
   ├── custom_components/
   │   └── tuya_custom/
   │       ...
   ├── hacs.json
   ├── README.md
   └── LICENSE
   ```

2. In Home Assistant, open **HACS → Integrations → ⋮ → Custom repositories**.
3. Enter your GitHub repository URL, choose **Integration**, and press **Add**.
4. Install “Tuya Custom” from HACS and restart Home Assistant.

## Workaround hooks

Editable placeholders live in `custom_components/tuya_custom/workarounds.py`:

- `polling_fallback()` – schedule periodic calls to
  `manager.update_device_cache()` via `async_track_time_interval` or similar.
- `optimistic_cover_update()` – immediately mirror expected DP values after
  sending a command so UI state updates without cloud confirmation.
- `post_command_refresh()` – delay briefly, then trigger
  `manager.update_device(device_id)` (or cache refresh) to fetch final states.

The cover platform already calls these helpers after open/close/stop/position
commands with inline comments explaining where to adapt logic.

## Attribution & License

This integration is based on the Tuya integration from the Home Assistant Core
repository (Apache License 2.0). Original copyright headers remain in the
copied files. See [`LICENSE`](LICENSE) for the full terms.

