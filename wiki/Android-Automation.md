# Android Automation Guide

The most reliable method for tracking Swiggy Instamart prices using the Android app.

## 🌟 Why Android Automation?

### Advantages
- ✅ **Most reliable** - No website loading issues
- ✅ **Automatic searching** - Searches multiple categories
- ✅ **Stable** - App is more consistent than website
- ✅ **Logged in** - Uses your existing account
- ✅ **24/7 capable** - Can run on spare phone

### Disadvantages
- ❌ Requires Android device or emulator
- ❌ More complex initial setup
- ❌ Needs Appium server running

---

## 📋 Prerequisites

### Required Software
- **Node.js** (v14 or higher)
- **Python** (3.8 or higher)
- **Android SDK**
- **Java JDK** (8 or higher)

### Required Hardware
Choose one:
- Android phone (any version 7.0+)
- Android emulator (Android Studio)
- Cloud Android device

---

## 🔧 Installation

### Step 1: Install Node.js

**Windows:**
- Download from: https://nodejs.org/
- Run installer
- Verify: `node --version`

**Linux/Mac:**
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install node
```

### Step 2: Install Appium

```bash
# Install Appium globally
npm install -g appium

# Install UiAutomator2 driver
appium driver install uiautomator2

# Verify installation
appium --version
```

### Step 3: Install Appium Doctor (Optional but recommended)

```bash
npm install -g appium-doctor

# Check Android setup
appium-doctor --android
```

Fix any issues reported by appium-doctor.

### Step 4: Install Android SDK

**Option A: Android Studio (Easiest)**
1. Download Android Studio: https://developer.android.com/studio
2. Install and open Android Studio
3. Go to: Tools → SDK Manager
4. Install:
   - Android SDK Platform-Tools
   - Android SDK Build-Tools
   - Android Emulator (if using emulator)

**Option B: Command Line Tools**
1. Download: https://developer.android.com/studio#command-tools
2. Extract to a folder
3. Set environment variables (see below)

### Step 5: Set Environment Variables

**Windows:**
```cmd
setx ANDROID_HOME "C:\Users\YourName\AppData\Local\Android\Sdk"
setx JAVA_HOME "C:\Program Files\Java\jdk-17"
setx PATH "%PATH%;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools"
```

**Linux/Mac:**
```bash
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools' >> ~/.bashrc
source ~/.bashrc
```

### Step 6: Install Python Dependencies

```bash
pip install Appium-Python-Client requests
```

---

## 📱 Device Setup

### Option 1: Physical Android Phone (Recommended)

1. **Enable Developer Options**
   - Go to: Settings → About Phone
   - Tap "Build Number" 7 times
   - Developer Options now enabled

2. **Enable USB Debugging**
   - Go to: Settings → Developer Options
   - Enable "USB Debugging"
   - Enable "Stay Awake" (optional, keeps screen on)

3. **Connect Device**
   - Connect phone via USB cable
   - Accept USB debugging prompt on phone
   - Verify connection:
     ```bash
     adb devices
     ```
   - Should show your device

4. **Install Swiggy App**
   - Install from Play Store
   - Login to your account
   - Set location to Bangalore
   - Close the app

### Option 2: Android Emulator

1. **Create Emulator in Android Studio**
   - Open Android Studio
   - Tools → Device Manager
   - Click "Create Device"
   - Choose: Pixel 4 (or any phone)
   - System Image: Android 11 or higher
   - Click Finish

2. **Start Emulator**
   - Click Play button in Device Manager
   - Wait for emulator to boot
   - Verify:
     ```bash
     adb devices
     ```

3. **Install Swiggy App**
   - Open Play Store in emulator
   - Search for "Swiggy"
   - Install and setup

---

## 🚀 Running the Tracker

### Step 1: Start Appium Server

Open a terminal and run:
```bash
appium
```

Keep this terminal open. You should see:
```
[Appium] Welcome to Appium v2.x.x
[Appium] Appium REST http interface listener started on 0.0.0.0:4723
```

### Step 2: Verify Device Connection

In a new terminal:
```bash
adb devices
```

Should show:
```
List of devices attached
XXXXXXXXXX    device
```

### Step 3: Run the Tracker

```bash
python swiggy_android_tracker.py
```

### What Happens:
1. Connects to Swiggy app
2. Navigates to Instamart
3. Searches for each category in `SEARCH_QUERIES`
4. Scrapes product names and prices
5. Checks for deals (under ₹50 or >70% off)
6. Sends alerts (console or Telegram)
7. Saves results to `scraped_products.json`
8. Waits 5 minutes (configurable)
9. Repeats

---

## ⚙️ Configuration

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
    "fruits",
    "dairy",
    "beverages",
    "instant food"
]

# Telegram (optional)
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

---

## 🔄 Running 24/7

### On Spare Android Phone

1. **Keep phone plugged in**
2. **Disable sleep**:
   - Settings → Developer Options
   - Enable "Stay Awake"
3. **Run tracker on PC** (phone connected via USB)
4. **Or use Termux** (run directly on phone):
   ```bash
   # Install Termux from F-Droid
   pkg install python
   pip install Appium-Python-Client requests
   python swiggy_android_tracker.py
   ```

### On Cloud VM

See: **[[Oracle Cloud Setup]]** for free 24/7 hosting

---

## 🐛 Troubleshooting

### "Failed to connect to Appium"

**Check:**
1. Is Appium server running?
   ```bash
   appium
   ```
2. Is it on port 4723?
3. Any firewall blocking?

**Fix:**
```bash
# Kill any existing Appium
pkill -f appium
# Start fresh
appium
```

### "No devices found"

**Check:**
```bash
adb devices
```

**If empty:**
1. Reconnect USB cable
2. Accept USB debugging on phone
3. Try different USB port
4. Restart adb:
   ```bash
   adb kill-server
   adb start-server
   ```

### "Could not find Instamart button"

**Fix:**
1. Manually open Swiggy app
2. Navigate to Instamart
3. Run tracker again
4. It will continue from there

### "Could not find search box"

**Possible causes:**
- App UI changed
- App not fully loaded
- Different app version

**Fix:**
1. Update Swiggy app
2. Wait longer for app to load
3. Check app manually

### App crashes or freezes

**Fix:**
1. Close Swiggy app manually
2. Restart Appium server
3. Run tracker again

---

## 📊 Performance Tips

### Faster Execution
```python
# Reduce wait times (if stable)
CHECK_INTERVAL = 180  # 3 minutes

# Fewer categories
SEARCH_QUERIES = ["snacks", "chocolate"]

# Less scrolling
# Edit scrape_current_screen() to scroll less
```

### Battery Optimization
- Use emulator instead of phone
- Reduce check frequency
- Use headless mode (if supported)

---

## 🔐 Security

### Best Practices
1. **Don't commit credentials**
   - Use environment variables
   - Add to `.gitignore`

2. **Secure Telegram token**
   ```python
   import os
   TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
   ```

3. **Use separate account**
   - Create new Swiggy account for tracking
   - Don't use main account

---

## 📈 Advanced Usage

### Multiple Devices

Track on multiple phones simultaneously:

```python
# Device 1
options.udid = "device_id_1"

# Device 2  
options.udid = "device_id_2"
```

### Custom Search Logic

Modify `search_products()` to:
- Search specific brands
- Filter by price range
- Track specific products

### Data Analysis

```python
# Load scraped data
import json
with open('scraped_products.json') as f:
    products = json.load(f)

# Analyze
cheap_products = [p for p in products if p['price'] < 30]
high_discount = [p for p in products if (p['mrp'] - p['price']) / p['mrp'] > 0.7]
```

---

## 🔗 Related Pages

- **[[Installation]]** - Detailed installation
- **[[Troubleshooting]]** - Common issues
- **[[Cloud Deployment]]** - Run on cloud
- **[[API Documentation]]** - Code reference

---

**Next**: [[Telegram Notifications]] to get instant alerts
