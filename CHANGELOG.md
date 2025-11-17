# Changelog

All notable changes to the Tuya Custom integration will be documented in this file.

## [1.0.5] - 2025-11-18

### Fixed
- **CRITICAL PERFORMANCE FIX**: Implemented throttling for polling to prevent redundant API calls
  - Previous implementation called `update_device_cache()` once per cover entity (22+ times every 30 seconds)
  - Now throttled to only call once every 25 seconds regardless of entity count
  - Reduces API load by ~95% (from 22 calls to 1 call per polling cycle)
  - Uses module-level timestamp cache keyed by Manager ID to support multiple accounts

### Changed
- Added `datetime` import to [cover.py:6](custom_components/tuya_custom/cover.py:6)
- Added module-level throttle variables `_last_cache_update` and `_CACHE_UPDATE_THROTTLE` ([cover.py:29-32](custom_components/tuya_custom/cover.py:29))
- Enhanced `async_update()` method with time-based throttling logic ([cover.py:397-424](custom_components/tuya_custom/cover.py:397))
- Fixed CHANGELOG documentation to use correct method name `update_device_cache()`

### Technical Details
- Throttle period: 25 seconds (slightly less than HA's 30s default `scan_interval`)
- First entity to poll in each cycle triggers the API call; subsequent entities skip
- Each Manager instance has its own throttle tracking (supports multi-account setups)
- Method already uses correct `update_device_cache()` - no method name changes needed

## [1.0.4] - 2025-11-18

### Added
- **Automatic Polling**: Cover entities now poll Tuya Cloud every 30 seconds (default HA polling interval)
  - Fixes the issue where curtain state only updates after manual integration reload
  - Tuya Cloud does not send MQTT push updates for curtain motors
  - Polling ensures state is always up-to-date without manual intervention

### Changed
- Set `_attr_should_poll = True` for `TuyaCoverEntity` class ([`cover.py:250`](custom_components/tuya_custom/cover.py:250))
- Added `async_update()` method to fetch latest device status from Tuya Cloud ([`cover.py:389-399`](custom_components/tuya_custom/cover.py:389))

### Technical Details
- Polling calls `device_manager.update_device_cache()` to refresh all device states
- Home Assistant default polling interval is 30 seconds (configurable via `scan_interval`)
- This is a workaround for Tuya Cloud limitation (GitHub issue #156543)
- Only cover entities poll; other entity types remain push-based via MQTT

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