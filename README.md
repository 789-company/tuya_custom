# Tuya Custom Integration for Home Assistant

A custom integration based on the official Home Assistant Tuya integration, with added workarounds for devices that don't receive proper state updates from Tuya Cloud.

## 🎯 Purpose

This custom integration was created to solve a specific issue with Tuya curtain motors and other devices where **Tuya Cloud does not send MQTT push updates** for state changes. This means the device state in Home Assistant only updates when you manually reload the integration.

**Related Issue:** [home-assistant/core#156543](https://github.com/home-assistant/core/issues/156543)

### Key Features

✅ **All original Tuya integration features**  
✅ **Polling fallback** - Periodically fetch device state from Tuya Cloud  
✅ **Post-command refresh** - Force state update after sending commands  
✅ **Optimistic updates** - Immediate UI feedback before cloud confirmation  
✅ **Easy to enable/disable** - Workarounds are clearly marked and configurable  
✅ **Separate domain** - Runs alongside official integration without conflicts  

## 📋 Supported Platforms

This integration includes ALL platforms from the official Tuya integration:

- ✅ Alarm Control Panel
- ✅ Binary Sensor
- ✅ Button
- ✅ Camera
- ✅ Climate
- ✅ **Cover** (with special workarounds for curtains)
- ✅ Event
- ✅ Fan
- ✅ Humidifier
- ✅ Light
- ✅ Number
- ✅ Scene
- ✅ Select
- ✅ Sensor
- ✅ Siren
- ✅ Switch
- ✅ Vacuum
- ✅ Valve

## 🚀 Installation

### Method 1: Manual Installation (Recommended)

1. **Download this repository**
   ```bash
   cd /config
   git clone https://github.com/YOUR_USERNAME/tuya_custom.git
   ```

2. **Copy to custom_components**
   ```bash
   cp -r tuya_custom/custom_components/tuya_custom /config/custom_components/
   ```

3. **Restart Home Assistant**
   - Go to **Settings** → **System** → **Restart**

### Method 2: HACS Installation

1. **Add custom repository to HACS**
   - Open HACS
   - Click the three dots in the top right
   - Select "Custom repositories"
   - Add this repository URL
   - Select category: "Integration"

2. **Install via HACS**
   - Search for "Tuya Custom"
   - Click "Download"
   - Restart Home Assistant

## ⚙️ Configuration

### Step 1: Disable Official Tuya Integration (Optional)

If you want to completely replace the official integration:

1. Go to **Settings** → **Devices & Services**
2. Find the **Tuya** integration
3. Click the three dots → **Delete**

**Note:** You can run both integrations simultaneously if needed. They use different domains (`tuya` vs `tuya_custom`).

### Step 2: Add Tuya Custom Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Tuya Custom**
4. Follow the authentication flow (same as official Tuya)

### Step 3: Enable Workarounds (For Problematic Devices)

The workarounds are **disabled by default**. To enable them:

1. **Edit the cover.py file:**
   ```bash
   nano /config/custom_components/tuya_custom/cover.py
   ```

2. **Find the workaround configuration section** (around line 270):
   ```python
   # Enable polling fallback (periodically fetch state from cloud)
   self._enable_polling = False  # Set to True to enable
   self._polling_interval = 30  # seconds
   
   # Enable optimistic updates (immediate UI feedback)
   self._enable_optimistic = False  # Set to True to enable
   
   # Enable post-command refresh (force refresh after commands)
   self._enable_post_command_refresh = True  # Recommended: keep True
   self._post_command_delay = 3  # seconds
   ```

3. **Change the flags as needed:**
   ```python
   self._enable_polling = True  # Enable periodic polling
   self._enable_optimistic = True  # Enable optimistic updates
   self._enable_post_command_refresh = True  # Keep enabled
   ```

4. **Uncomment the workaround code blocks** in the methods:
   - Look for sections marked with `# WORKAROUND:`
   - Remove the `#` from the lines you want to enable

5. **Restart Home Assistant**

## 🔧 Workaround Details

### 1. Polling Fallback

**What it does:** Periodically fetches device state from Tuya Cloud API.

**When to use:** When your devices don't receive MQTT push updates.

**Configuration:**
```python
self._enable_polling = True
self._polling_interval = 30  # Poll every 30 seconds
```

**Pros:**
- Ensures state is always up-to-date
- Works even when MQTT is completely broken

**Cons:**
- Creates additional API calls
- May hit rate limits with many devices
- Slight delay in state updates

### 2. Post-Command Refresh

**What it does:** Forces a state refresh X seconds after sending a command.

**When to use:** Always recommended for covers.

**Configuration:**
```python
self._enable_post_command_refresh = True
self._post_command_delay = 3  # Wait 3 seconds before refresh
```

**Pros:**
- Ensures state updates after commands
- Minimal API overhead
- Works well for most devices

**Cons:**
- Fixed delay may not suit all devices
- Still requires cloud API call

### 3. Optimistic Updates

**What it does:** Immediately updates UI before cloud confirms.

**When to use:** For better user experience with slow devices.

**Configuration:**
```python
self._enable_optimistic = True
```

**Pros:**
- Instant UI feedback
- Better user experience
- No additional API calls

**Cons:**
- May show incorrect state temporarily
- State will be corrected when cloud updates arrive

## 🐛 Debugging

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.tuya_custom: debug
    custom_components.tuya_custom.workarounds: debug
    tuya_sharing: debug
```

### Check Logs

```bash
tail -f /config/home-assistant.log | grep tuya_custom
```

### Common Issues

**Issue:** Devices not showing up
- **Solution:** Check that device category is supported in `cover.py` COVERS dict

**Issue:** State not updating even with workarounds
- **Solution:** Verify Tuya Cloud credentials are valid, check API rate limits

**Issue:** Integration conflicts with official Tuya
- **Solution:** They use different domains, should work together. If issues persist, disable one.

## 📝 Maintenance

### Updating the Integration

When Home Assistant updates the official Tuya integration:

1. **Clone the latest HA core:**
   ```bash
   cd /tmp
   git clone --depth 1 https://github.com/home-assistant/core.git
   ```

2. **Copy updated files:**
   ```bash
   cp -r /tmp/core/homeassistant/components/tuya/* /config/custom_components/tuya_custom/
   ```

3. **Re-apply customizations:**
   - Update `manifest.json` domain to `tuya_custom`
   - Update `const.py` DOMAIN to `tuya_custom`
   - Re-add workaround code to `cover.py`
   - Test thoroughly

4. **Commit changes:**
   ```bash
   cd /config/custom_components/tuya_custom
   git add .
   git commit -m "Update to HA core version X.X.X"
   ```

### Keeping Workarounds Updated

The workaround functions are in `workarounds.py`. You can modify them without touching the core integration files.

## 🤝 Contributing

Found a bug or have an improvement? Please open an issue or pull request!

### Development Setup

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test with your Home Assistant installation
5. Submit a pull request

## 📄 License

This project is licensed under the same license as Home Assistant Core (Apache 2.0).

## 🙏 Credits

- Based on the official [Home Assistant Tuya Integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/tuya)
- Created to solve issue [#156543](https://github.com/home-assistant/core/issues/156543)
- Thanks to the Home Assistant and Tuya development teams

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/tuya_custom/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/tuya_custom/discussions)
- **Home Assistant Community:** [Community Forum](https://community.home-assistant.io/)

## ⚠️ Disclaimer

This is a custom integration and is not officially supported by Home Assistant or Tuya. Use at your own risk.

The workarounds create additional API calls to Tuya Cloud, which may impact rate limits. Monitor your usage and adjust polling intervals accordingly.

---

**Made with ❤️ for the Home Assistant community**