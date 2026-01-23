# Troubleshooting Guide

Common issues and solutions for Amazon and Swiggy price trackers.

## 🛒 Amazon Tracker Issues

### Workflow Not Running

**Symptoms:**
- No workflow runs in Actions tab
- Scheduled runs not happening

**Check:**
1. Is GitHub Actions enabled?
   - Go to Actions tab
   - Click "I understand my workflows"
2. Are secrets configured?
   - Settings → Secrets → Actions
   - Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
3. Is schedule correct?
   - Check `.github/workflows/amazon-price-tracker.yml`

**Fix:**
```yaml
# Verify schedule format
on:
  schedule:
    - cron: '30 3,15 * * *'  # Must be valid cron
```

---

### No Deals Found

**Symptoms:**
- Workflow completes but finds 0 products
- "No deals found" in logs

**Check:**
1. Download screenshots from artifacts
2. View logs in Actions tab
3. Check if Amazon changed page structure

**Fix:**
1. Update selectors in `amazon_price_tracker.py`
2. Try manual trigger with different query
3. Check if Amazon is blocking

---

### Telegram Not Working

**Symptoms:**
- Workflow succeeds but no Telegram message
- "Telegram not configured" in logs

**Check:**
1. Are secrets set correctly?
   - Settings → Secrets → Actions
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
2. Did you start chat with bot?
3. Is bot token valid?

**Fix:**
```bash
# Test bot manually
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=Test"
```

---

### Duplicate Alerts

**Symptoms:**
- Same products alerted multiple times
- Getting notifications for already-seen deals

**Fix:**
Update to latest code - this is fixed in recent versions!

The tracker now uses:
- Normalized product names
- ASIN-based tracking
- Price history comparison

---

### Workflow Timeout

**Symptoms:**
- Workflow fails after 10 minutes
- "Job was cancelled" error

**Check:**
1. Is max_products too high?
2. Too many search queries?
3. Network issues?

**Fix:**
```python
# Reduce in amazon_price_tracker.py
CONFIG = {
    'max_products': 20,  # Reduce from 30
    'search_queries': ['lightning deals'],  # Fewer queries
}
```

---

### Git Push Failed

**Symptoms:**
- "Failed to push" in logs
- Price history not committed

**Check:**
1. Are there actual changes?
2. Merge conflicts?

**Fix:**
Already handled in workflow with `|| true` fallbacks.

---

## 🛍️ Swiggy Tracker Issues

### Failed to Connect to Appium

**Symptoms:**
- "Connection refused" error
- "Could not connect to Appium server"

**Check:**
```bash
# Is Appium running?
ps aux | grep appium

# Is port 4723 available?
netstat -an | grep 4723
```

**Fix:**
```bash
# Kill existing Appium
pkill -f appium

# Start fresh
appium

# Or specify port
appium --port 4723
```

---

### No Devices Found

**Symptoms:**
- "No devices attached" error
- Device not detected

**Check:**
```bash
# List devices
adb devices

# Should show:
# List of devices attached
# XXXXXXXXXX    device
```

**Fix:**
```bash
# Restart adb
adb kill-server
adb start-server

# Check USB connection
# Try different USB port
# Accept USB debugging on phone

# For emulator
emulator -list-avds
emulator -avd <avd_name>
```

---

### Could Not Find Instamart Button

**Symptoms:**
- "Element not found" error
- Can't navigate to Instamart

**Check:**
1. Is Swiggy app installed?
2. Is app logged in?
3. Did app UI change?

**Fix:**
1. Manually open Swiggy app
2. Navigate to Instamart
3. Run tracker again (it will continue from there)

Or update selectors in code:
```python
# Find new element ID/text
# Update in swiggy_android_tracker.py
```

---

### Could Not Find Search Box

**Symptoms:**
- "Search box not found" error
- Can't search for products

**Check:**
1. Is Instamart page loaded?
2. Did UI change?
3. Network issues?

**Fix:**
1. Wait longer for page load
2. Update app to latest version
3. Update selectors in code

---

### No Products Found

**Symptoms:**
- Search completes but 0 products
- "No products found" message

**Check:**
1. Is location set to Bangalore?
2. Are products available?
3. Is search query correct?

**Fix:**
```python
# Try different search queries
SEARCH_QUERIES = [
    "snacks",  # More general
    "chocolate",
    "biscuits"
]

# Check location manually in app
# Verify products are visible
```

---

### App Crashes or Freezes

**Symptoms:**
- App stops responding
- Tracker hangs
- No progress

**Check:**
1. Device memory
2. App version
3. Network connection

**Fix:**
```bash
# Force stop app
adb shell am force-stop in.swiggy.android

# Clear app cache
adb shell pm clear in.swiggy.android

# Restart tracker
python swiggy_android_tracker.py
```

---

### Tampermonkey Script Not Running

**Symptoms:**
- No console output
- Script not detecting products

**Check:**
1. Is Tampermonkey enabled?
2. Is script enabled?
3. Are you on swiggy.com/instamart?

**Fix:**
1. Click Tampermonkey icon
2. Enable script
3. Refresh page
4. Check console (F12) for errors

---

## 📱 Telegram Issues

### Unauthorized Error

**Cause:** Wrong bot token

**Fix:**
1. Get token from @BotFather
2. Check for typos
3. Regenerate if needed

---

### Chat Not Found

**Cause:** Wrong chat ID or bot not started

**Fix:**
1. Start chat with bot
2. Send a message
3. Get chat ID from getUpdates
4. For groups, add bot first

---

### No Messages Received

**Check:**
1. Bot token correct?
2. Chat ID correct?
3. Started chat with bot?
4. TEST_MODE = False?
5. Are deals actually found?

**Test:**
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=Test message"
```

---

## 🖥️ System Issues

### Python Module Not Found

**Symptoms:**
- "ModuleNotFoundError: No module named 'X'"

**Fix:**
```bash
# Install missing module
pip install <module_name>

# Or install all requirements
pip install -r requirements.txt
```

---

### Permission Denied

**Symptoms:**
- "Permission denied" errors
- Can't write files

**Fix:**
```bash
# Linux/Mac
chmod +x script.py
sudo chown $USER:$USER file.json

# Windows
# Run as Administrator
```

---

### Port Already in Use

**Symptoms:**
- "Address already in use"
- Can't start Appium

**Fix:**
```bash
# Find process using port
lsof -i :4723  # Linux/Mac
netstat -ano | findstr :4723  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

---

## 🌐 Network Issues

### Connection Timeout

**Symptoms:**
- "Connection timeout" errors
- Pages not loading

**Check:**
1. Internet connection
2. Firewall settings
3. VPN/proxy

**Fix:**
```python
# Increase timeout
page.goto(url, timeout=60000)  # 60 seconds

# Add retries
for i in range(3):
    try:
        page.goto(url)
        break
    except:
        time.sleep(5)
```

---

### Rate Limiting

**Symptoms:**
- "Too many requests" errors
- Blocked by website

**Fix:**
```python
# Add delays
time.sleep(2)  # Between requests

# Randomize delays
import random
time.sleep(random.uniform(2, 5))

# Reduce frequency
CHECK_INTERVAL = 600  # 10 minutes instead of 5
```

---

## 🔧 Performance Issues

### Slow Execution

**Symptoms:**
- Takes too long to complete
- Timeout errors

**Fix:**
```python
# Reduce products
'max_products': 20,

# Fewer queries
'search_queries': ['lightning deals'],

# Shorter waits
time.sleep(1)  # Instead of 2
```

---

### High Memory Usage

**Symptoms:**
- System slows down
- Out of memory errors

**Fix:**
```python
# Close browser between runs
browser.close()

# Limit concurrent operations
# Process in batches

# Use headless mode
browser = p.chromium.launch(headless=True)
```

---

## 📊 Data Issues

### JSON Decode Error

**Symptoms:**
- "JSONDecodeError" when loading files

**Fix:**
```python
# Check file exists and is valid
import json
try:
    with open('file.json') as f:
        data = json.load(f)
except json.JSONDecodeError:
    # File corrupted, reset
    data = {}
```

---

### Price History Not Updating

**Symptoms:**
- Same deals alerted repeatedly
- History file not changing

**Check:**
1. Is file being written?
2. Correct permissions?
3. Git committing changes?

**Fix:**
```bash
# Check file
cat price_history.json

# Check git status
git status

# Manual commit
git add price_history.json
git commit -m "Update history"
git push
```

---

## 🆘 Still Having Issues?

### Get Help

1. **Check logs:**
   - GitHub Actions: View workflow logs
   - Local: Check console output
   - System: Check `journalctl` or Event Viewer

2. **Enable debug mode:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Search existing issues:**
   - https://github.com/hithesh0160/Swiggy-Instamart/issues

4. **Open new issue:**
   - Include error messages
   - Include system info
   - Include steps to reproduce

5. **Ask in discussions:**
   - https://github.com/hithesh0160/Swiggy-Instamart/discussions

---

## 🔗 Related Guides

- [Amazon Guide](AMAZON_GUIDE.md)
- [Swiggy Guide](SWIGGY_GUIDE.md)
- [Telegram Setup](TELEGRAM_SETUP.md)
- [Cloud Hosting](CLOUD_HOSTING.md)

---

**Can't find your issue?** Open a GitHub issue with details!
