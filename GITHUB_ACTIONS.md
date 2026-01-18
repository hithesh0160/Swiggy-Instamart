# GitHub Actions Deployment

## ⚠️ Important Limitations

**GitHub Actions free tier does NOT support Android emulators** due to:
- No nested virtualization support
- Hardware acceleration (KVM) not available
- Emulator requires these features to run

## Alternative Cloud Solutions

### Option 1: Self-Hosted Runner (Best for Android)

Run GitHub Actions on your own machine with Android emulator:

1. **Setup Self-Hosted Runner**:
   - Go to your repo → Settings → Actions → Runners
   - Click "New self-hosted runner"
   - Follow setup instructions for your OS

2. **Install Requirements on Runner**:
   ```bash
   # Install Appium
   npm install -g appium
   appium driver install uiautomator2
   
   # Install Python dependencies
   pip install Appium-Python-Client requests
   
   # Setup Android emulator
   # (Follow ANDROID_SETUP.md)
   ```

3. **Create Workflow** (`.github/workflows/swiggy-tracker.yml`):
   ```yaml
   name: Swiggy Price Tracker
   
   on:
     schedule:
       - cron: '*/30 * * * *'  # Every 30 minutes
     workflow_dispatch:  # Manual trigger
   
   jobs:
     track-prices:
       runs-on: self-hosted
       
       steps:
         - uses: actions/checkout@v3
         
         - name: Start Appium
           run: |
             appium &
             sleep 5
         
         - name: Run Tracker
           env:
             TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
             TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
           run: python swiggy_android_tracker.py
         
         - name: Upload Results
           uses: actions/upload-artifact@v3
           with:
             name: scraped-products
             path: scraped_products.json
   ```

4. **Add Secrets**:
   - Go to repo → Settings → Secrets → Actions
   - Add `TELEGRAM_BOT_TOKEN`
   - Add `TELEGRAM_CHAT_ID`

### Option 2: Cloud Android Services

Use paid services that support Android automation:

#### AWS Device Farm
- Real Android devices in the cloud
- Pay per device hour
- Good for testing and automation

#### BrowserStack
- Real devices and emulators
- Appium support
- Free trial available

#### Sauce Labs
- Cloud-based testing platform
- Android emulator support
- Free trial for open source

### Option 3: Browser Automation on GitHub Actions

While Android won't work, browser automation CAN work on GitHub Actions:

**Workflow** (`.github/workflows/browser-tracker.yml`):
```yaml
name: Swiggy Browser Tracker

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  track-prices:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install playwright requests
          python -m playwright install chromium
          python -m playwright install-deps
      
      - name: Run Browser Tracker
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          # Note: This will have the same website loading issues
          # Better to run locally or use Android
          python swiggy_simple_browser.py
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: scraped-products
          path: |
            scraped_products.json
            debug.png
```

**Limitations:**
- Website has loading issues (as you experienced)
- Requires manual interaction
- Not reliable for automated runs
- Better to use Android locally

## Recommended Approach

### For 24/7 Monitoring:

**Option A: Spare Android Phone**
1. Use an old Android phone
2. Keep it plugged in
3. Run tracker locally
4. Most reliable and free

**Option B: Raspberry Pi + Android Emulator**
1. Setup Raspberry Pi 4 (4GB+ RAM)
2. Install Android emulator
3. Run tracker continuously
4. Low power consumption

**Option C: Cloud VM with Android**
1. Rent a cloud VM (AWS, DigitalOcean, etc.)
2. Setup Android emulator
3. Run tracker as a service
4. Costs ~$5-10/month

### For Scheduled Checks:

**Self-Hosted GitHub Runner**
1. Setup on your PC/laptop
2. Run when computer is on
3. Free and automated
4. Good for periodic checks

## Example: Running on Raspberry Pi

```bash
# Install dependencies
sudo apt update
sudo apt install -y nodejs npm default-jdk android-sdk

# Install Appium
npm install -g appium
appium driver install uiautomator2

# Install Python dependencies
pip3 install Appium-Python-Client requests

# Setup Android emulator
# (Use ARM-compatible emulator image)

# Run tracker
python3 swiggy_android_tracker.py
```

## Cost Comparison

| Solution | Cost | Reliability | Setup Difficulty |
|----------|------|-------------|------------------|
| Spare Android Phone | Free | ⭐⭐⭐⭐⭐ | Easy |
| Self-Hosted Runner | Free | ⭐⭐⭐⭐ | Medium |
| Raspberry Pi | $35 one-time | ⭐⭐⭐⭐ | Medium |
| Cloud VM | $5-10/month | ⭐⭐⭐⭐ | Hard |
| AWS Device Farm | $0.17/device-min | ⭐⭐⭐⭐⭐ | Medium |
| GitHub Actions (Browser) | Free | ⭐⭐ | Easy |

## Conclusion

**Best Option:** Run locally on a spare Android phone or use a self-hosted GitHub Actions runner.

**Why GitHub Actions free tier won't work for Android:**
- No nested virtualization
- No hardware acceleration
- Emulator won't start
- Would need paid cloud service

**What DOES work on GitHub Actions:**
- Browser automation (but has website issues)
- API-based solutions (if you had API access)
- Self-hosted runners with Android

For reliable 24/7 monitoring, use a dedicated device (phone, Raspberry Pi, or cloud VM).
