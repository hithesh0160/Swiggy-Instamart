# Swiggy Instamart Price Tracker - Complete Guide

Track deep discounts and pricing errors on Swiggy Instamart automatically!

## 🎯 Available Methods

### 1. Android Automation (Recommended) ⭐

**Best for:** Reliable 24/7 monitoring

**Pros:**
- ✅ Most reliable
- ✅ Automatic searching
- ✅ Stable (app is consistent)
- ✅ Uses your logged-in account
- ✅ 24/7 capable on spare phone

**Cons:**
- ❌ Requires Android device/emulator
- ❌ More complex setup

### 2. Browser Extension (Tampermonkey)

**Best for:** Casual monitoring while browsing

**Pros:**
- ✅ Easiest setup (2 minutes)
- ✅ No servers needed
- ✅ Runs in your browser
- ✅ Stealthy (behaves like real user)

**Cons:**
- ❌ Only works when browsing
- ❌ Not 24/7

### 3. Browser Automation

**Best for:** Testing/development

**Pros:**
- ✅ No Android needed
- ✅ Quick checks

**Cons:**
- ❌ Website has loading issues
- ❌ Less reliable

---

## 🚀 Quick Start - Android (Recommended)

### Prerequisites

- **Node.js** (v14+)
- **Python** (3.8+)
- **Android device** or emulator
- **Java JDK** (8+)

### Installation

**1. Install Appium**
```bash
npm install -g appium
appium driver install uiautomator2
```

**2. Install Python dependencies**
```bash
pip install Appium-Python-Client requests
```

**3. Setup Android device**
```bash
# Enable USB debugging on phone
# Connect via USB
adb devices  # Verify connection
```

**4. Install Swiggy app**
- Install from Play Store
- Login to your account
- Set location to Bangalore

### Running

**1. Start Appium** (Terminal 1)
```bash
appium
```

**2. Run tracker** (Terminal 2)
```bash
python swiggy_android_tracker.py
```

### What Happens

1. Connects to Swiggy app
2. Navigates to Instamart
3. Searches for categories (snacks, chocolate, etc.)
4. Scrapes product names and prices
5. Alerts for products under ₹50 or >70% discount
6. Saves to `scraped_products.json`
7. Waits 5 minutes
8. Repeats

---

## 🌐 Quick Start - Tampermonkey

### Installation

**1. Install Tampermonkey**
- Chrome: [Install](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
- Firefox: [Install](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)

**2. Add script**
1. Click Tampermonkey icon
2. Click "Create a new script"
3. Copy content from `swiggy-price-monitor.user.js`
4. Paste and save (Ctrl+S)

**3. Browse Swiggy**
- Go to swiggy.com/instamart
- Script runs automatically!
- Check console (F12) for results

### Configuration

Edit script:
```javascript
const CONFIG = {
    telegram: {
        botToken: 'YOUR_BOT_TOKEN',
        chatId: 'YOUR_CHAT_ID',
        enabled: false  // Set true to enable
    },
    
    alerting: {
        condition: {
            price_drop_percentage: 70,  // Alert >70% discount
            price_threshold: 50         // Alert under ₹50
        }
    }
};
```

---

## ⚙️ Configuration - Android

Edit `swiggy_android_tracker.py`:

```python
# Alert threshold
PRICE_THRESHOLD = 50  # Products under this price

# Check interval
CHECK_INTERVAL = 300  # Seconds between checks

# Test mode
TEST_MODE = True  # False for Telegram alerts

# Categories to search
SEARCH_QUERIES = [
    "snacks",
    "biscuits",
    "chocolate",
    "bread",
    "milk",
    "vegetables",
    "fruits"
]

# Telegram (optional)
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

---

## 📱 Telegram Notifications

### Alert Format

```
🔥 PRICE ALERT!

Product: Chocolate Bar
Current Price: ₹9
Original Price: ₹50
Discount: 82%

⏰ 2026-01-23 09:00:00
```

### Setup

See [Telegram Setup Guide](TELEGRAM_SETUP.md)

---

## 🔄 Running 24/7

### Option 1: Spare Android Phone

1. Keep phone plugged in
2. Enable "Stay Awake" in Developer Options
3. Run tracker on PC (phone connected via USB)
4. Or use Termux to run directly on phone

### Option 2: Oracle Cloud

Free forever hosting:
1. Sign up at oracle.com/cloud/free
2. Create ARM VM
3. Install Android emulator
4. Run tracker as service

See [Cloud Hosting Guide](CLOUD_HOSTING.md)

### Option 3: Your PC

Run when computer is on:
1. Install dependencies
2. Connect Android device
3. Run tracker
4. Use Task Scheduler (Windows) or cron (Linux) to auto-start

---

## 🐛 Troubleshooting

### "Failed to connect to Appium"

**Check:**
```bash
# Is Appium running?
appium

# Is device connected?
adb devices
```

**Fix:**
```bash
# Restart Appium
pkill -f appium
appium
```

### "No devices found"

**Check:**
```bash
adb devices
```

**Fix:**
1. Reconnect USB cable
2. Accept USB debugging on phone
3. Restart adb:
   ```bash
   adb kill-server
   adb start-server
   ```

### "Could not find Instamart button"

**Fix:**
1. Manually open Swiggy app
2. Navigate to Instamart
3. Run tracker again

### "No products found"

**Check:**
1. Location set to Bangalore?
2. Logged into Swiggy app?
3. Products visible in app?

**Fix:**
- Manually verify app works
- Check location setting
- Update app

### Tampermonkey not running

**Check:**
1. Is Tampermonkey enabled?
2. Is script enabled?
3. Are you on swiggy.com/instamart?

**Fix:**
- Click Tampermonkey icon
- Enable script
- Refresh page

---

## 📊 Performance Tips

### Faster Execution

```python
# Reduce check interval
CHECK_INTERVAL = 180  # 3 minutes

# Fewer categories
SEARCH_QUERIES = ["snacks", "chocolate"]
```

### Battery Optimization

- Use emulator instead of phone
- Reduce check frequency
- Use WiFi (not mobile data)

---

## 💡 Use Cases

### Daily Deal Hunter
- Run on spare phone 24/7
- Get instant Telegram alerts
- Never miss pricing errors

### Casual Browser
- Use Tampermonkey script
- Browse while shopping
- Get alerts in browser

### Scheduled Checks
- Run on your PC
- Check every few hours
- Save to JSON for analysis

---

## 🔗 Related Guides

- [Telegram Setup](TELEGRAM_SETUP.md)
- [Cloud Hosting](CLOUD_HOSTING.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Ready to start?** Choose your method and start tracking deals!
