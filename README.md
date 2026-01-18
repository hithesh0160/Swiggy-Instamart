# Swiggy Instamart Price Tracker 🔥

Track deep discounts on Swiggy Instamart (Bangalore) and get notified when products are priced very low (under ₹50 or >70% discount).

## ✅ Available Solutions

### 🤖 Android App Automation (RECOMMENDED)
- Most reliable and stable
- No website loading issues
- Works with your logged-in account
- Can run 24/7 on a spare phone
- **Best option for consistent results**

### 🌐 Browser Automation
- Works without Android device
- Manual control over browsing
- Good for occasional checks

## 🚀 Quick Start

### Option 1: Android App (Recommended)

#### Prerequisites
```bash
# Install Appium
npm install -g appium
appium driver install uiautomator2

# Install Python client
pip install Appium-Python-Client requests
```

#### Setup
1. Connect Android device or start emulator
2. Enable USB debugging
3. Install and login to Swiggy app
4. Set location to Bangalore

#### Run
```bash
# Start Appium server (in one terminal)
appium

# Run tracker (in another terminal)
python swiggy_android_tracker.py
```

See **ANDROID_SETUP.md** for detailed instructions.

### Option 2: Browser Automation

```bash
# Install dependencies
pip install playwright requests
python -m playwright install chromium

# Run tracker
python swiggy_simple_browser.py
```

Then manually browse to products and press ENTER to scrape.

## 📁 Files

### Android Automation
- **swiggy_android_tracker.py** - Android app automation ⭐
- **ANDROID_SETUP.md** - Detailed Android setup guide

### Browser Automation
- **swiggy_simple_browser.py** - Manual browser tracker
- **swiggy_manual_tracker.py** - Automated search (has issues)

### Testing
- **test_with_sample_data.py** - Test with sample data

## ⚙️ Configuration

Edit the tracker file you're using:

```python
PRICE_THRESHOLD = 50      # Alert for products under this price
CHECK_INTERVAL = 300      # Check every 5 minutes  
TEST_MODE = True          # False = enable Telegram alerts

# Android only - categories to search
SEARCH_QUERIES = [
    "snacks",
    "biscuits",
    "chocolate",
    "bread",
    "milk"
]
```

## 📱 Telegram Notifications

1. Create bot via @BotFather on Telegram
2. Get your chat ID from `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Update script with your credentials:
   ```python
   TELEGRAM_BOT_TOKEN = "your_token"
   TELEGRAM_CHAT_ID = "your_chat_id"
   TEST_MODE = False
   ```

## 📊 Example Output

```
🔥 PRICE ALERT! 🔥

Product: Chocolate Bar - Clearance
Current Price: ₹9.0
Original Price: ₹50.0
Discount: 82.0%
```

## 🎯 Features

### Android App Automation
- ✅ Automatic search across categories
- ✅ Stable and reliable
- ✅ No website loading issues
- ✅ Works with logged-in account
- ✅ Can run 24/7 on spare phone
- ✅ Detects products under ₹50
- ✅ Finds discounts over 70%

### Browser Automation
- ✅ No Android device needed
- ✅ Manual control
- ✅ Works for occasional checks

## 🤖 GitHub Actions (Limitations)

**Note:** GitHub Actions free tier doesn't support Android emulators due to nested virtualization limitations. 

**Alternatives:**
1. **Run locally** on your computer/spare phone (recommended)
2. **Use a cloud service** with Android emulator support:
   - AWS Device Farm
   - BrowserStack
   - Sauce Labs
3. **Self-hosted runner** with Android emulator

See **GITHUB_ACTIONS.md** for cloud deployment options.

## 💡 Recommended Setup

**For 24/7 monitoring:**
1. Use an old Android phone
2. Keep it plugged in and connected to WiFi
3. Run the Android tracker
4. Enable Telegram notifications
5. Let it run continuously

**For occasional checks:**
1. Use browser automation
2. Manually browse and scrape
3. Check whenever you want

## 🐛 Troubleshooting

### Android
- **Can't connect to Appium**: Make sure server is running and device is connected (`adb devices`)
- **App crashes**: Restart app and Appium server
- **No products found**: Check if you're logged in and location is set

### Browser
- **Page alignment issues**: The website has loading problems
- **Search not working**: Website requires manual interaction
- **Use manual mode**: Browse yourself, then press ENTER to scrape

## 📝 Notes

- Android automation is more reliable than browser
- Requires Android device or emulator
- For personal use only
- Respect Swiggy's Terms of Service
- Bangalore location only (configurable)

---

**Ready to start?** 

For best results: `python swiggy_android_tracker.py` (after Appium setup)

For quick test: `python swiggy_simple_browser.py` (manual browsing)
