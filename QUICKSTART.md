# Quick Start Guide - Tuya Custom Integration

Get up and running in 5 minutes!

## 🚀 Fast Track Installation

### 1. Copy Files (2 minutes)

```bash
# SSH into Home Assistant
ssh root@homeassistant.local

# Navigate to config
cd /config

# Create directory
mkdir -p custom_components

# Copy the tuya_custom folder to custom_components/
# (Upload via File Editor add-on or SCP)
```

### 2. Restart Home Assistant (1 minute)

```bash
ha core restart
```

Or via UI: **Settings** → **System** → **Restart**

### 3. Add Integration (2 minutes)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Tuya Custom**
4. Follow authentication flow
5. Done! Your devices should appear

## ⚡ Enable Workarounds (Optional)

Only if your curtains/covers don't update automatically:

### Quick Enable - Post-Command Refresh (Recommended)

Already enabled by default! Your covers will refresh 3 seconds after each command.

### Enable Polling (For Stubborn Devices)

Edit `/config/custom_components/tuya_custom/cover.py`:

**Line ~270, change:**
```python
self._enable_polling = False
```
**To:**
```python
self._enable_polling = True
```

**Line ~295, uncomment these lines:**
```python
# Remove the # from these lines:
if self._enable_polling:
    from .workarounds import polling_fallback
    self._polling_task = self.hass.async_create_task(
        polling_fallback(
            self.hass,
            self.device_manager,
            self.device.id,
            interval=self._polling_interval,
        )
    )
    self.async_on_remove(lambda: self._polling_task.cancel())
```

Restart Home Assistant.

## 🧪 Test It

1. Open a cover from Home Assistant UI
2. Wait 3 seconds
3. State should update automatically
4. If not, check logs: `tail -f /config/home-assistant.log | grep tuya_custom`

## 📚 Need More Help?

- **Full Installation Guide:** See [INSTALLATION.md](INSTALLATION.md)
- **Complete Documentation:** See [README.md](README.md)
- **Troubleshooting:** Check logs and INSTALLATION.md troubleshooting section

## 🎯 Common Scenarios

### Scenario 1: Curtains Don't Update After Commands

**Solution:** Post-command refresh is already enabled by default. Just wait 3 seconds after each command.

### Scenario 2: Curtains Don't Update When Using Physical Button

**Solution:** Enable polling (see above). This will check for updates every 30 seconds.

### Scenario 3: Want Instant UI Feedback

**Solution:** Enable optimistic updates in `cover.py` (line ~272):
```python
self._enable_optimistic = True
```

Then uncomment the optimistic update code blocks in `open_cover()` and `close_cover()` methods.

## ⚙️ Configuration Summary

| Feature | Default | When to Enable |
|---------|---------|----------------|
| Post-Command Refresh | ✅ Enabled | Always (recommended) |
| Polling | ❌ Disabled | Physical button usage |
| Optimistic Updates | ❌ Disabled | Want instant UI feedback |

## 🔧 Adjust Settings

All settings are in `cover.py` around line 270:

```python
self._enable_polling = False          # True to enable polling
self._polling_interval = 30           # Seconds between polls
self._enable_optimistic = False       # True for instant UI updates
self._enable_post_command_refresh = True  # Keep True (recommended)
self._post_command_delay = 3          # Seconds to wait before refresh
```

## ✅ Checklist

- [ ] Files copied to `/config/custom_components/tuya_custom/`
- [ ] Home Assistant restarted
- [ ] Integration added via UI
- [ ] Devices showing up
- [ ] Covers respond to commands
- [ ] State updates after commands (wait 3 seconds)
- [ ] (Optional) Polling enabled if needed
- [ ] (Optional) Optimistic updates enabled if wanted

## 🎉 You're Done!

Your Tuya devices should now work properly with automatic state updates!

---

**Still having issues?** Check the full [INSTALLATION.md](INSTALLATION.md) guide or open an issue on GitHub.