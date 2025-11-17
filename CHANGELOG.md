# Changelog

All notable changes to the Tuya Custom integration will be documented in this file.

## [1.0.3] - 2025-11-18

### Fixed
- **CRITICAL FIX**: Changed cover position to use `percent_state` (actual position) instead of `percent_control` (command)
  - This fixes the issue where Home Assistant displays incorrect curtain positions
  - Tuya Cloud sends `percent_control` (last command) and `percent_state` (actual position) separately
  - When these values don't match, HA was showing the command instead of actual position
  - Now correctly displays the real curtain position from `percent_state`
- Applied fix to all curtain types:
  - `DeviceCategory.CL` (standard curtains) - line 124
  - `DeviceCategory.CLKG` (curtain switches) - lines 168, 177
  - Blind devices (switch_1) - line 159

### Technical Details
- Modified `TuyaCoverEntityDescription` for `DeviceCategory.CL`:
  - Before: `current_position=(DPCode.PERCENT_STATE, DPCode.PERCENT_CONTROL)`
  - After: `current_position=DPCode.PERCENT_STATE`
- This ensures Home Assistant always reads the actual curtain position, not the last command sent

### Why This Fix Is Needed
Tuya Cloud has a known issue where it doesn't send MQTT push updates after curtain movement completes.
This causes a mismatch between:
- `percent_control`: The command sent (e.g., "open to 100%")
- `percent_state`: The actual curtain position (e.g., still at 0%)

By using only `percent_state`, we ensure accurate position reporting.

## [1.0.2] - 2025-11-17

### Fixed
- Fixed thread safety issue in post-command refresh
- Changed `manager.update_device_list_in_smart_home()` to correct method `manager.update_device_cache()`
- Fixed "Detected that custom integration calls hass.async_create_task from a thread" error
- Used `hass.loop.call_soon_threadsafe()` for proper async task scheduling

### Added
- Post-command refresh enabled by default (3-second delay after open/close/stop commands)
- Thread-safe task scheduling for all workaround functions

## [1.0.1] - 2025-11-17

### Fixed
- Fixed Manager attribute error in workarounds.py
- Corrected method name from `update_device_list_in_smart_home` to `update_device_cache`

## [1.0.0] - 2025-11-17

### Added
- Initial release of Tuya Custom integration
- Cloned from official Home Assistant Tuya integration
- Changed domain from `tuya` to `tuya_custom`
- Added workarounds.py with three helper functions:
  - `polling_fallback()` - Periodic polling for state updates
  - `post_command_refresh()` - Force refresh after commands
  - `optimistic_cover_update()` - Immediate UI feedback
- Added integration points in cover.py for workarounds
- All 28 original files plus workarounds.py
- Complete documentation set (README, INSTALLATION, QUICKSTART, etc.)

### Purpose
This custom integration addresses Tuya Cloud's limitation where MQTT push updates
are not sent for curtain motor state changes. The workarounds provide:
- Polling fallback for periodic updates
- Post-command refresh for immediate state sync
- Optimistic updates for better UX