# Free Cloud Hosting Options

Run your Swiggy price tracker 24/7 completely free!

## 🆓 Best Free Options

### 1. Oracle Cloud Free Tier ⭐⭐⭐⭐⭐

**FREE FOREVER - No expiry!**

#### What You Get
- **2 AMD VMs** (1/8 OCPU, 1GB RAM each)
- **OR 4 ARM VMs** (Ampere A1, up to 24GB RAM total)
- **200GB storage**
- **10TB bandwidth/month**
- **No credit card charges** - truly free forever

#### Why It's Best
- ✅ Free forever (not a trial)
- ✅ Powerful ARM processors
- ✅ Enough resources for Android emulator
- ✅ 24/7 uptime
- ✅ No hidden costs

#### Setup Guide

**Step 1: Sign Up**
1. Go to: https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in details (requires credit card for verification)
4. Verify email
5. Login to Oracle Cloud Console

**Step 2: Create VM Instance**
1. Click "Create a VM instance"
2. **Name**: swiggy-tracker
3. **Image**: Ubuntu 22.04
4. **Shape**: 
   - Click "Change Shape"
   - Select "Ampere" (ARM)
   - Choose: VM.Standard.A1.Flex
   - OCPUs: 2
   - Memory: 12GB
5. **Networking**: Use default
6. **SSH Keys**: 
   - Generate new key pair
   - Download private key
7. Click "Create"

**Step 3: Connect to VM**

```bash
# Make key private
chmod 400 ssh-key-*.key

# Connect
ssh -i ssh-key-*.key ubuntu@<VM_PUBLIC_IP>
```

**Step 4: Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Java
sudo apt install -y default-jdk

# Install Python
sudo apt install -y python3 python3-pip

# Install Appium
sudo npm install -g appium
appium driver install uiautomator2

# Install Android SDK
wget https://dl.google.com/android/repository/commandlinetools-linux-latest.zip
unzip commandlinetools-linux-latest.zip
mkdir -p ~/android-sdk/cmdline-tools
mv cmdline-tools ~/android-sdk/cmdline-tools/latest

# Set environment variables
echo 'export ANDROID_HOME=~/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.bashrc
source ~/.bashrc

# Install Python dependencies
pip3 install Appium-Python-Client requests
```

**Step 5: Setup Android Emulator**

```bash
# Accept licenses
yes | sdkmanager --licenses

# Install platform tools
sdkmanager "platform-tools" "platforms;android-30"

# Install emulator
sdkmanager "emulator" "system-images;android-30;google_apis;arm64-v8a"

# Create AVD
avdmanager create avd -n swiggy_device -k "system-images;android-30;google_apis;arm64-v8a"
```

**Step 6: Clone and Setup Tracker**

```bash
# Clone repository
git clone https://github.com/hithesh0160/Swiggy-Instamart.git
cd Swiggy-Instamart

# Configure
nano swiggy_android_tracker.py
# Update TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
# Set TEST_MODE = False
```

**Step 7: Create Systemd Service**

```bash
# Create service file
sudo nano /etc/systemd/system/swiggy-tracker.service
```

Add:
```ini
[Unit]
Description=Swiggy Price Tracker
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Swiggy-Instamart
ExecStartPre=/usr/bin/appium &
ExecStart=/usr/bin/python3 swiggy_android_tracker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable swiggy-tracker
sudo systemctl start swiggy-tracker

# Check status
sudo systemctl status swiggy-tracker

# View logs
sudo journalctl -u swiggy-tracker -f
```

#### Cost
**$0 forever!**

---

### 2. AWS Free Tier ⭐⭐⭐

**FREE for 12 months**

#### What You Get
- **t2.micro instance** (1 vCPU, 1GB RAM)
- **750 hours/month** (enough for 24/7)
- **30GB storage**
- **Free for 12 months**

#### Setup
Similar to Oracle Cloud, but:
1. Sign up at: https://aws.amazon.com/free/
2. Launch EC2 instance
3. Choose t2.micro (free tier eligible)
4. Follow same installation steps

#### Cost
- **Free for 12 months**
- Then ~$10/month

---

### 3. Google Cloud Free Tier ⭐⭐⭐

**$300 credit for 90 days**

#### What You Get
- **$300 credit** (3 months)
- **e2-micro** free after credits
- Good for testing

#### Setup
1. Sign up: https://cloud.google.com/free
2. Create Compute Engine instance
3. Follow installation steps

#### Cost
- **$300 credit** for 3 months
- Then e2-micro free (limited)

---

### 4. Spare Android Phone ⭐⭐⭐⭐⭐

**EASIEST & FREE FOREVER**

#### What You Need
- Old Android phone (any version 7.0+)
- USB cable
- Computer to run Appium

#### Setup
1. Enable USB debugging on phone
2. Connect to computer
3. Keep phone plugged in
4. Run tracker on computer
5. Phone stays connected 24/7

#### Advantages
- ✅ Completely free
- ✅ Most reliable
- ✅ No cloud setup
- ✅ Real device (not emulator)
- ✅ Uses your logged-in account

#### Cost
**$0 - Use old phone you already have!**

---

### 5. PythonAnywhere ⭐⭐

**FREE with limitations**

#### What You Get
- Free web hosting
- 1 scheduled task per day
- No Android support

#### Use Case
- Run browser automation once per day
- Good for daily price checks
- Not for real-time monitoring

#### Setup
1. Sign up: https://www.pythonanywhere.com/
2. Upload `swiggy_simple_browser.py`
3. Schedule daily task

#### Cost
**$0 but limited to 1 check/day**

---

## 📊 Comparison

| Option | Cost | Duration | Reliability | Setup | Android |
|--------|------|----------|-------------|-------|---------|
| **Oracle Cloud** | $0 | Forever | ⭐⭐⭐⭐⭐ | Hard | ✅ |
| **Spare Phone** | $0 | Forever | ⭐⭐⭐⭐⭐ | Easy | ✅ |
| **Your PC** | $0 | When on | ⭐⭐⭐⭐ | Easy | ✅ |
| **AWS Free** | $0 | 12 months | ⭐⭐⭐⭐ | Medium | ✅ |
| **Google Cloud** | $0 | 3 months | ⭐⭐⭐⭐ | Medium | ✅ |
| **PythonAnywhere** | $0 | Forever | ⭐⭐ | Easy | ❌ |

---

## 🎯 Recommendations

### For Best Results
**Use Oracle Cloud Free Tier**
- Free forever
- Powerful enough for Android emulator
- 24/7 uptime
- Professional setup

### For Easiest Setup
**Use Spare Android Phone**
- No cloud setup needed
- Most reliable
- Just plug in and run

### For Testing
**Use Your PC**
- Test locally first
- Move to cloud later
- Free and simple

---

## 💡 Pro Tips

### Oracle Cloud
- Use ARM instances (better performance)
- Setup monitoring alerts
- Enable automatic backups
- Use security groups properly

### Spare Phone
- Keep phone plugged in always
- Enable "Stay Awake" in developer options
- Use WiFi (not mobile data)
- Disable unnecessary apps

### General
- Start with local testing
- Move to cloud when stable
- Monitor resource usage
- Setup Telegram alerts

---

## 🔗 Related Pages

- **[[Oracle Cloud Setup]]** - Detailed Oracle guide
- **[[Android Automation]]** - Android setup
- **[[Troubleshooting]]** - Common issues
- **[[GitHub Actions]]** - CI/CD options

---

**Next**: [[Oracle Cloud Setup]] for step-by-step Oracle Cloud guide
