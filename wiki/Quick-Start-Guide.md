# Quick Start Guide

Get the Swiggy Instamart Price Tracker running in under 5 minutes!

## 🎯 Choose Your Method

### Method 1: Android App (Recommended) ⭐

**Best for**: Reliable 24/7 monitoring

**Requirements**:
- Android phone or emulator
- 5 minutes setup time

**Steps**:

1. **Install Appium**
   ```bash
   npm install -g appium
   appium driver install uiautomator2
   ```

2. **Install Python dependencies**
   ```bash
   pip install Appium-Python-Client requests
   ```

3. **Connect Android device**
   ```bash
   # Enable USB debugging on phone
   # Connect via USB
   adb devices  # Verify connection
   ```

4. **Start Appium**
   ```bash
   appium
   ```

5. **Run tracker** (in new terminal)
   ```bash
   python swiggy_android_tracker.py
   ```

✅ Done! The tracker will automatically search and monitor products.

---

### Method 2: Browser Automation

**Best for**: Quick checks without Android

**Requirements**:
- Any computer
- 2 minutes setup time

**Steps**:

1. **Install dependencies**
   ```bash
   pip install playwright requests
   python -m playwright install chromium
   ```

2. **Run tracker**
   ```bash
   python swiggy_simple_browser.py
   ```

3. **Manual setup**
   - Browser opens automatically
   - Browse to products you want to track
   - Press ENTER in terminal

✅ Done! Products will be scraped and analyzed.

---

## 📱 Enable Telegram Notifications (Optional)

1. **Create Telegram bot**
   - Open Telegram
   - Search for `@BotFather`
   - Send `/newbot`
   - Follow instructions
   - Save the bot token

2. **Get your chat ID**
   - Start chat with your bot
   - Send any message
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find `chat_id` in the response

3. **Configure tracker**
   - Open the tracker file you're using
   - Update these lines:
   ```python
   TELEGRAM_BOT_TOKEN = "your_bot_token_here"
   TELEGRAM_CHAT_ID = "your_chat_id_here"
   TEST_MODE = False  # Enable Telegram alerts
   ```

4. **Run again**
   - You'll now get Telegram notifications!

---

## ⚙️ Basic Configuration

Edit the tracker file:

```python
# Alert threshold
PRICE_THRESHOLD = 50  # Alert for products under ₹50

# Check frequency
CHECK_INTERVAL = 300  # Check every 5 minutes

# Test mode (console output only)
TEST_MODE = True  # Set to False for Telegram alerts

# Android only - categories to search
SEARCH_QUERIES = [
    "snacks",
    "biscuits",
    "chocolate",
    "bread",
    "milk"
]
```

---

## 🎉 What's Next?

- **[[Telegram Notifications]]** - Setup instant alerts
- **[[Cloud Deployment]]** - Run 24/7 for free
- **[[Configuration]]** - Customize tracking
- **[[Troubleshooting]]** - Fix issues

---

## 🆘 Having Issues?

**Android not connecting?**
- Check: `adb devices`
- Enable USB debugging
- See: **[[Android Issues]]**

**Browser not working?**
- Website has loading issues
- Use Android method instead
- See: **[[Browser Issues]]**

**No products found?**
- Check location is set to Bangalore
- Verify products are visible
- See: **[[Common Issues]]**

---

**Next**: [[Installation]] for detailed setup instructions
