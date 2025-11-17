# Tuya Custom Integration - Installation Guide

Complete step-by-step installation instructions for Home Assistant OS.

## 📋 Prerequisites

- Home Assistant OS installed and running
- Access to Home Assistant via SSH or Terminal & SSH add-on
- Existing Tuya account with devices configured
- Basic knowledge of YAML and file editing

## 🔧 Installation Methods

### Method 1: Direct Installation (Recommended for Home Assistant OS)

#### Step 1: Access Home Assistant Terminal

**Option A: Using Terminal & SSH Add-on**
1. Install "Terminal & SSH" add-on from Add-on Store
2. Start the add-on
3. Click "Open Web UI"

**Option B: Using SSH Client**
1. Enable SSH in Home Assistant
2. Connect via SSH client: `ssh root@homeassistant.local`

#### Step 2: Navigate to Config Directory

```bash
cd /config
```

#### Step 3: Create Custom Components Directory

```bash
mkdir -p custom_components
cd custom_components
```

#### Step 4: Clone or Download This Repository

**Option A: Using Git (if available)**
```bash
git clone https://github.com/YOUR_USERNAME/tuya_custom.git
mv tuya_custom/custom_components/tuya_custom ./
rm -rf tuya_custom
```

**Option B: Manual Download**
1. Download the repository as ZIP from GitHub
2. Extract the ZIP file
3. Upload the `custom_components/tuya_custom` folder to `/config/custom_components/`

#### Step 5: Verify Installation

```bash
ls -la /config/custom_components/tuya_custom/
```

You should see files like:
- `__init__.py`
- `manifest.json`
- `const.py`
- `cover.py`
- `workarounds.py`
- etc.

#### Step 6: Set Correct Permissions

```bash
chown -R root:root /config/custom_components/tuya_custom
chmod -R 755 /config/custom_components/tuya_custom
```

#### Step 7: Restart Home Assistant

**Via UI:**
1. Go to **Settings** → **System** → **Restart**

**Via CLI:**
```bash
ha core restart
```

#### Step 8: Verify Integration is Loaded

Check the logs:
```bash
tail -f /config/home-assistant.log | grep tuya_custom
```

You should see something like:
```
INFO (MainThread) [homeassistant.setup] Setting up tuya_custom
```

---

### Method 2: HACS Installation

#### Step 1: Install HACS

If you don't have HACS installed:
1. Follow instructions at https://hacs.xyz/docs/setup/download

#### Step 2: Add Custom Repository

1. Open HACS in Home Assistant
2. Click the three dots (⋮) in the top right corner
3. Select **Custom repositories**
4. Add repository URL: `https://github.com/YOUR_USERNAME/tuya_custom`
5. Select category: **Integration**
6. Click **Add**

#### Step 3: Install Integration

1. In HACS, search for "Tuya Custom"
2. Click on the integration
3. Click **Download**
4. Select the latest version
5. Click **Download** again

#### Step 4: Restart Home Assistant

1. Go to **Settings** → **System** → **Restart**

---

## ⚙️ Configuration

### Step 1: Add Integration to Home Assistant

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for **Tuya Custom**
4. Click on it to start setup

### Step 2: Authenticate with Tuya

You'll be redirected to Tuya's authentication page:

1. Select your country/region
2. Enter your Tuya account credentials
3. Authorize Home Assistant to access your devices
4. You'll be redirected back to Home Assistant

### Step 3: Verify Devices

1. Go to **Settings** → **Devices & Services**
2. Click on **Tuya Custom**
3. You should see all your Tuya devices listed

---

## 🔄 Migrating from Official Tuya Integration

### Option A: Run Both Integrations (Recommended for Testing)

Both integrations can run simultaneously because they use different domains:
- Official: `tuya`
- Custom: `tuya_custom`

**Advantages:**
- Test the custom integration without losing existing setup
- Easy rollback if issues occur
- Compare behavior between integrations

**Disadvantages:**
- Duplicate entities for same devices
- Slightly higher resource usage

### Option B: Replace Official Integration

**⚠️ Warning:** This will remove all existing Tuya entities and automations will need updating.

1. **Export your configuration first:**
   ```bash
   cd /config
   cp configuration.yaml configuration.yaml.backup
   ```

2. **Note all automations using Tuya entities:**
   - Go to **Settings** → **Automations & Scenes**
   - Export or screenshot automations using Tuya devices

3. **Remove official Tuya integration:**
   - Go to **Settings** → **Devices & Services**
   - Find **Tuya** integration
   - Click three dots → **Delete**
   - Confirm deletion

4. **Add Tuya Custom integration** (follow steps above)

5. **Update automations:**
   - Entity IDs will change from `cover.tuya_*` to `cover.tuya_custom_*`
   - Update all automations and scripts accordingly

---

## 🛠️ Enabling Workarounds

The workarounds are **disabled by default**. Enable them only if you experience state update issues.

### Step 1: Edit cover.py

```bash
nano /config/custom_components/tuya_custom/cover.py
```

Or use File Editor add-on in Home Assistant.

### Step 2: Find Configuration Section

Search for (around line 270):
```python
# WORKAROUND CONFIGURATION
```

### Step 3: Enable Desired Workarounds

**Enable Polling:**
```python
self._enable_polling = True  # Changed from False
self._polling_interval = 30  # Adjust as needed
```

**Enable Optimistic Updates:**
```python
self._enable_optimistic = True  # Changed from False
```

**Enable Post-Command Refresh (Recommended):**
```python
self._enable_post_command_refresh = True  # Keep as True
self._post_command_delay = 3  # Adjust as needed
```

### Step 4: Uncomment Workaround Code

Find sections marked with:
```python
# ============================================================================
# WORKAROUND: [NAME]
# ============================================================================
```

Remove the `#` from the lines you want to enable.

**Example - Enable Polling:**

Before:
```python
# if self._enable_polling:
#     from .workarounds import polling_fallback
#     self._polling_task = self.hass.async_create_task(
```

After:
```python
if self._enable_polling:
    from .workarounds import polling_fallback
    self._polling_task = self.hass.async_create_task(
```

### Step 5: Save and Restart

```bash
# Save the file (Ctrl+X, then Y, then Enter in nano)
# Restart Home Assistant
ha core restart
```

---

## 🧪 Testing

### Test 1: Basic Functionality

1. Open Home Assistant
2. Go to **Developer Tools** → **States**
3. Find your cover entity (e.g., `cover.tuya_custom_living_room_curtain`)
4. Note the current state

5. Use the UI to open/close the cover
6. Verify the state updates correctly

### Test 2: Workaround Verification

**With Polling Enabled:**
1. Manually operate the curtain using physical button or Tuya app
2. Wait for polling interval (default 30 seconds)
3. Check if Home Assistant state updates

**With Post-Command Refresh:**
1. Send open/close command from Home Assistant
2. Wait for delay (default 3 seconds)
3. Verify state updates

**With Optimistic Updates:**
1. Send command from Home Assistant
2. UI should update immediately
3. State should be corrected when cloud confirms

### Test 3: Check Logs

```bash
tail -f /config/home-assistant.log | grep -E "tuya_custom|workaround"
```

Look for:
- `Starting polling fallback for device...`
- `Polling device state for...`
- `Executing post-command refresh for device...`

---

## 🐛 Troubleshooting

### Integration Not Showing Up

**Check installation:**
```bash
ls -la /config/custom_components/tuya_custom/manifest.json
```

**Check logs:**
```bash
grep -i "tuya_custom" /config/home-assistant.log
```

**Solution:**
- Verify all files are present
- Check file permissions
- Restart Home Assistant
- Clear browser cache

### Authentication Failed

**Symptoms:**
- "Authentication failed" error during setup
- "sign invalid" in logs

**Solutions:**
1. Verify Tuya account credentials
2. Check internet connection
3. Try re-authenticating
4. Check Tuya Cloud status

### Devices Not Updating

**Without workarounds:**
- This is expected behavior due to Tuya Cloud issue
- Enable workarounds as described above

**With workarounds enabled:**
1. Check logs for errors
2. Verify workaround code is uncommented
3. Check API rate limits
4. Increase polling interval if hitting limits

### High CPU/Memory Usage

**Cause:** Polling too frequently or too many devices

**Solutions:**
1. Increase polling interval:
   ```python
   self._polling_interval = 60  # Poll every 60 seconds instead of 30
   ```

2. Disable polling for devices that work fine:
   ```python
   # Only enable for specific categories
   if self.device.category in [DeviceCategory.CL, DeviceCategory.CLKG]:
       self._enable_polling = True
   ```

3. Use post-command refresh only (disable polling)

### Entities Have Wrong Names

**Cause:** Entity IDs changed from official integration

**Solution:**
1. Go to **Settings** → **Devices & Services** → **Tuya Custom**
2. Click on device
3. Click on entity
4. Click gear icon
5. Change entity ID to match old one

Or update automations to use new entity IDs.

---

## 📊 Performance Considerations

### API Rate Limits

Tuya Cloud has rate limits. With polling enabled:

- **1 device, 30s interval:** ~2,880 API calls/day
- **10 devices, 30s interval:** ~28,800 API calls/day
- **10 devices, 60s interval:** ~14,400 API calls/day

**Recommendations:**
- Start with 60-second intervals
- Monitor for rate limit errors
- Adjust based on your needs
- Use post-command refresh instead of polling when possible

### Resource Usage

**Minimal (post-command refresh only):**
- CPU: Negligible
- Memory: ~5-10 MB
- Network: Only when commands sent

**Moderate (polling enabled, 60s interval):**
- CPU: <1%
- Memory: ~10-20 MB
- Network: Constant but minimal

**High (polling enabled, 10s interval, many devices):**
- CPU: 1-2%
- Memory: ~20-50 MB
- Network: Moderate constant usage

---

## 🔄 Updating

### Update Custom Integration

```bash
cd /config/custom_components
rm -rf tuya_custom
# Re-download latest version
# Follow installation steps again
```

### Update from HACS

1. Open HACS
2. Find "Tuya Custom"
3. Click **Update** if available
4. Restart Home Assistant

---

## 📝 Next Steps

1. ✅ Integration installed and working
2. ✅ Devices showing up in Home Assistant
3. ✅ Workarounds enabled (if needed)
4. ⬜ Create automations using your devices
5. ⬜ Monitor logs for any issues
6. ⬜ Fine-tune workaround settings

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs first:**
   ```bash
   tail -100 /config/home-assistant.log | grep -i error
   ```

2. **Enable debug logging:**
   Add to `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.tuya_custom: debug
   ```

3. **Open an issue on GitHub:**
   - Include Home Assistant version
   - Include integration version
   - Include relevant logs
   - Describe the problem clearly

4. **Community support:**
   - Home Assistant Community Forum
   - GitHub Discussions

---

**Installation complete! Enjoy your working Tuya devices! 🎉**