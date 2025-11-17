# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-17

### Fixed
- Fixed thread safety issue in cover platform
- Changed `hass.async_create_task()` to use `hass.loop.call_soon_threadsafe()` in synchronous methods
- Resolved error: "Detected that custom integration calls hass.async_create_task from a thread other than the event loop"
- Affected methods: `open_cover()`, `close_cover()`, `stop_cover()`

## [1.0.0] - 2025-01-17

### Added
- Initial release of Tuya Custom integration
- Based on Home Assistant Core Tuya integration (latest dev branch)
- Custom domain `tuya_custom` to avoid conflicts with official integration
- Workaround module (`workarounds.py`) with three main functions:
  - `polling_fallback()` - Periodic state polling from Tuya Cloud
  - `post_command_refresh()` - Force refresh after sending commands
  - `optimistic_cover_update()` - Immediate UI feedback before cloud confirmation
- Enhanced cover platform with workaround integration points
- Comprehensive documentation (README.md, INSTALLATION.md)
- Clear comments and configuration flags for easy customization

### Changed
- Domain changed from `tuya` to `tuya_custom`
- Integration name changed to "Tuya Custom"
- All internal references updated to use custom domain

### Fixed
- Addresses issue where Tuya Cloud doesn't send MQTT push updates for certain devices
- Specifically targets curtain motors and similar devices that only update on integration reload
- Related to Home Assistant Core issue [#156543](https://github.com/home-assistant/core/issues/156543)

### Supported Platforms
- Alarm Control Panel
- Binary Sensor
- Button
- Camera
- Climate
- Cover (with special workarounds)
- Event
- Fan
- Humidifier
- Light
- Number
- Scene
- Select
- Sensor
- Siren
- Switch
- Vacuum
- Valve

### Documentation
- Complete README with feature overview and quick start
- Detailed INSTALLATION.md with step-by-step instructions
- Inline code comments explaining workaround integration points
- Troubleshooting guide and performance considerations

### Notes
- Workarounds are disabled by default for safety
- Users must manually enable workarounds based on their needs
- All workarounds are clearly marked and documented
- Integration can run alongside official Tuya integration

## [Unreleased]

### Planned Features
- Configuration flow options for workaround settings
- Per-device workaround configuration
- Automatic detection of problematic device categories
- Statistics and monitoring for API usage
- HACS integration for easier updates

---

## Version History

### How to Update

When updating to a new version:

1. **Backup your configuration:**
   ```bash
   cp -r /config/custom_components/tuya_custom /config/custom_components/tuya_custom.backup
   ```

2. **Download new version:**
   - Via HACS: Click "Update" button
   - Manual: Replace files in `/config/custom_components/tuya_custom/`

3. **Check changelog for breaking changes**

4. **Restart Home Assistant**

5. **Test your devices**

### Breaking Changes

None yet - this is the initial release.

### Deprecation Notices

None yet.

---

## Contributing

Found a bug or have a feature request? Please open an issue on GitHub!

When reporting issues, please include:
- Home Assistant version
- Integration version
- Device category and model
- Relevant logs
- Steps to reproduce

---

## Credits

- Based on [Home Assistant Core Tuya Integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/tuya)
- Created to solve [Issue #156543](https://github.com/home-assistant/core/issues/156543)
- Thanks to the Home Assistant community for testing and feedback