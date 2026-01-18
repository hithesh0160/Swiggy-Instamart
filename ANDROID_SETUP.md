# Android App Automation Setup

## Prerequisites

### 1. Install Node.js
Download from: https://nodejs.org/

### 2. Install Appium
```bash
npm install -g appium
npm install -g appium-doctor
```

### 3. Install Appium UiAutomator2 Driver
```bash
appium driver install uiautomator2
```

### 4. Install Python Appium Client
```bash
pip install Appium-Python-Client
```

### 5. Install Android SDK
- Download Android Studio: https://developer.android.com/studio
- Or install SDK command-line tools

### 6. Setup Environment Variables
Add to your system PATH:
- `ANDROID_HOME` = path to Android SDK
- `JAVA_HOME` = path to JDK

Example (Windows):
```
ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk
JAVA_HOME=C:\Program Files\Java\jdk-17
```

## Device Setup

### Option 1: Physical Android Device

1. **Enable Developer Options**:
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times

2. **Enable USB Debugging**:
   - Go to Settings → Developer Options
   - Enable "USB Debugging"

3. **Connect Device**:
   - Connect via USB cable
   - Verify: `adb devices`

### Option 2: Android Emulator

1. Open Android Studio
2. Go to Tools → Device Manager
3. Create a new virtual device
4. Start the emulator
5. Verify: `adb devices`

## Swiggy App Setup

1. **Install Swiggy App** on your device/emulator
2. **Login** to your account
3. **Set location** to Bangalore
4. Keep the app installed (don't uninstall)

## Running the Tracker

### 1. Start Appium Server
```bash
appium
```

Leave this terminal running.

### 2. Verify Setup
```bash
appium-doctor --android
```

All checks should pass.

### 3. Check Device Connection
```bash
adb devices
```

Should show your device.

### 4. Run the Tracker
In a new terminal:
```bash
python swiggy_android_tracker.py
```

## How It Works

1. Connects to Swiggy app on your Android device
2. Navigates to Instamart
3. Searches for multiple categories (snacks, biscuits, etc.)
4. Scrapes product names and prices
5. Alerts for products under ₹50 or >70% discount
6. Saves results to `scraped_products.json`

## Configuration

Edit `swiggy_android_tracker.py`:

```python
PRICE_THRESHOLD = 50      # Alert threshold
CHECK_INTERVAL = 300      # Check every 5 minutes
TEST_MODE = True          # False for Telegram alerts

SEARCH_QUERIES = [        # Categories to search
    "snacks",
    "biscuits",
    "chocolate"
]
```

## Troubleshooting

**"Failed to connect to Appium"**
- Make sure Appium server is running
- Check if device is connected: `adb devices`

**"Could not find Instamart button"**
- Manually open Instamart in the app first
- The script will continue from there

**"Could not find search box"**
- The app UI might have changed
- Check the app manually to see the layout

**App crashes or freezes**
- Restart the app manually
- Restart Appium server
- Reconnect device

## Advantages Over Web

✅ More stable than website
✅ Better performance
✅ Consistent UI
✅ No location issues
✅ Works with your logged-in account
✅ Can run 24/7 on a spare phone

## Tips

- Use an old Android phone dedicated to this
- Keep it plugged in and connected
- Run on WiFi for stability
- The app stays logged in
- Can run headless (no screen needed)
