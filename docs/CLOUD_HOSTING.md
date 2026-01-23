# Free Cloud Hosting Guide

Run your price trackers 24/7 completely free!

## 🆓 Best Free Options

### 1. Oracle Cloud Free Tier ⭐⭐⭐⭐⭐

**FREE FOREVER - No expiry!**

#### What You Get
- **4 ARM VMs** (Ampere A1, up to 24GB RAM total)
- **200GB storage**
- **10TB bandwidth/month**
- **No credit card charges** - truly free forever

#### Why It's Best
- ✅ Free forever (not a trial)
- ✅ Powerful ARM processors
- ✅ Enough resources for Android emulator
- ✅ 24/7 uptime
- ✅ No hidden costs

#### Quick Setup

**1. Sign Up**
- Go to: https://www.oracle.com/cloud/free/
- Requires credit card for verification (won't charge)

**2. Create VM**
- Click "Create a VM instance"
- Name: `price-tracker`
- Image: Ubuntu 22.04
- Shape: VM.Standard.A1.Flex (ARM)
  - OCPUs: 2
  - Memory: 12GB
- Download SSH key

**3. Connect**
```bash
chmod 400 ssh-key.key
ssh -i ssh-key.key ubuntu@<VM_IP>
```

**4. Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Java & Python
sudo apt install -y default-jdk python3 python3-pip

# Install Appium
sudo npm install -g appium
appium driver install uiautomator2

# Install Python dependencies
pip3 install Appium-Python-Client requests
```

**5. Clone Repository**
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

**6. Configure**
```bash
nano swiggy_android_tracker.py
# Update TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
# Set TEST_MODE = False
```

**7. Run as Service**
```bash
sudo nano /etc/systemd/system/price-tracker.service
```

Add:
```ini
[Unit]
Description=Price Tracker
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo
ExecStart=/usr/bin/python3 swiggy_android_tracker.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable price-tracker
sudo systemctl start price-tracker
sudo systemctl status price-tracker
```

**Cost:** $0 forever!

---

### 2. GitHub Actions (Amazon Only)

**FREE - 2,000 minutes/month**

#### What You Get
- 2,000 minutes/month free
- Unlimited for public repos
- Built-in CI/CD

#### Setup
Already covered in [Amazon Guide](AMAZON_GUIDE.md)

**Cost:** $0 (within free tier)

---

### 3. Spare Android Phone ⭐⭐⭐⭐⭐

**EASIEST & FREE FOREVER**

#### What You Need
- Old Android phone (7.0+)
- USB cable
- Computer to run Appium

#### Setup
1. Enable USB debugging
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

**Cost:** $0 - Use old phone you already have!

---

### 4. AWS Free Tier

**FREE for 12 months**

#### What You Get
- t2.micro instance (1 vCPU, 1GB RAM)
- 750 hours/month
- 30GB storage

#### Setup
1. Sign up: https://aws.amazon.com/free/
2. Launch EC2 instance (t2.micro)
3. Follow Oracle Cloud installation steps

**Cost:** Free for 12 months, then ~$10/month

---

### 5. Google Cloud Free Tier

**$300 credit for 90 days**

#### What You Get
- $300 credit (3 months)
- e2-micro free after credits

#### Setup
1. Sign up: https://cloud.google.com/free
2. Create Compute Engine instance
3. Follow Oracle Cloud installation steps

**Cost:** $300 credit for 3 months, then limited free tier

---

## 📊 Comparison

| Option | Cost | Duration | Reliability | Setup | Android |
|--------|------|----------|-------------|-------|---------|
| **Oracle Cloud** | $0 | Forever | ⭐⭐⭐⭐⭐ | Hard | ✅ |
| **Spare Phone** | $0 | Forever | ⭐⭐⭐⭐⭐ | Easy | ✅ |
| **GitHub Actions** | $0 | Forever | ⭐⭐⭐⭐⭐ | Easy | ❌ |
| **Your PC** | $0 | When on | ⭐⭐⭐⭐ | Easy | ✅ |
| **AWS Free** | $0 | 12 months | ⭐⭐⭐⭐ | Medium | ✅ |
| **Google Cloud** | $0 | 3 months | ⭐⭐⭐⭐ | Medium | ✅ |

---

## 🎯 Recommendations

### For Amazon Tracking
**Use GitHub Actions**
- Free forever
- No setup needed
- Runs automatically

### For Swiggy Tracking (24/7)
**Use Spare Android Phone**
- Easiest setup
- Most reliable
- No cloud complexity

### For Swiggy Tracking (Cloud)
**Use Oracle Cloud**
- Free forever
- Professional setup
- 24/7 uptime

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
- Configure firewall properly

### Spare Phone
- Keep phone plugged in always
- Enable "Stay Awake" in developer options
- Use WiFi (not mobile data)
- Disable unnecessary apps

### GitHub Actions
- Use for Amazon only (no Android support)
- Monitor usage in Settings → Billing
- Optimize schedule to stay in free tier

### General
- Start with local testing
- Move to cloud when stable
- Monitor resource usage
- Setup Telegram alerts

---

## 🔒 Security

### Oracle Cloud
```bash
# Update firewall
sudo ufw allow 22/tcp
sudo ufw enable

# Disable password auth
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

### Environment Variables
```bash
# Don't hardcode tokens
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

---

## 🐛 Troubleshooting

### Oracle Cloud VM Not Starting

**Check:**
- Did you choose ARM shape?
- Is free tier available in your region?

**Fix:**
- Try different region
- Use AMD shape if ARM unavailable

### SSH Connection Failed

**Check:**
```bash
# Correct key permissions?
chmod 400 ssh-key.key

# Correct IP?
ping <VM_IP>
```

### Service Not Starting

**Check logs:**
```bash
sudo journalctl -u price-tracker -f
```

**Common issues:**
- Wrong file paths
- Missing dependencies
- Permission issues

---

## 🔗 Related Guides

- [Amazon Guide](AMAZON_GUIDE.md)
- [Swiggy Guide](SWIGGY_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Ready to deploy?** Choose your hosting option and start tracking 24/7!
