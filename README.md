# Swiggy Instamart & Amazon Price Tracker 🔥

Track deep discounts on Swiggy Instamart and Amazon.in automatically!

## 🎯 Available Trackers

### 1. 🛒 Amazon.in Tracker (GitHub Actions) ⭐ NEW!
- **Best for**: Automated cloud tracking
- **Runs on**: GitHub Actions (free)
- **Setup**: 5 minutes
- **Cost**: $0 forever
- **Frequency**: Every 6 hours (configurable)

### 2. 🤖 Swiggy Android Tracker
- **Best for**: 24/7 Swiggy monitoring
- **Runs on**: Android phone/emulator
- **Setup**: 15 minutes
- **Cost**: $0 (use spare phone)

### 3. 🌐 Swiggy Browser (Tampermonkey)
- **Best for**: Casual Swiggy monitoring
- **Runs on**: Your browser
- **Setup**: 2 minutes
- **Cost**: $0

---

## 🚀 Quick Start

### Amazon Tracker (Easiest!)

1. **Add GitHub Secrets**
   - Go to Settings → Secrets → Actions
   - Add `TELEGRAM_BOT_TOKEN`
   - Add `TELEGRAM_CHAT_ID`

2. **Enable Actions**
   - Go to Actions tab
   - Enable workflows

3. **Done!**
   - Runs automatically every 6 hours
   - Get Telegram notifications
   - Download deal reports

See: **[[AMAZON_TRACKER_GUIDE.md]]**

### Swiggy Tampermonkey (Simplest!)

1. **Install Tampermonkey**
   - Chrome: [Install](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)

2. **Add Script**
   - Copy `swiggy-price-monitor.user.js`
   - Paste in Tampermonkey

3. **Browse Swiggy**
   - Go to swiggy.com/instamart
   - Script runs automatically!

See: **[[TAMPERMONKEY_GUIDE.md]]**

### Swiggy Android (Most Reliable!)

1. **Install Appium**
   ```bash
   npm install -g appium
   appium driver install uiautomator2
   pip install Appium-Python-Client requests
   ```

2. **Connect Android**
   ```bash
   adb devices  # Verify connection
   ```

3. **Run**
   ```bash
   appium  # Terminal 1
   python swiggy_android_tracker.py  # Terminal 2
   ```

See: **[[ANDROID_SETUP.md]]**

---

## 📊 Comparison

| Feature | Amazon (Actions) | Swiggy (Tampermonkey) | Swiggy (Android) |
|---------|------------------|----------------------|------------------|
| Setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Reliability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 24/7 Monitoring | ✅ | ❌ | ✅ |
| Cost | $0 | $0 | $0 |
| Cloud-based | ✅ | ❌ | Optional |
| Automatic | ✅ | ✅ | ✅ |
| Device Needed | ❌ | ❌ | ✅ |

---

## 📁 Repository Structure

```
├── Amazon Tracker
│   ├── amazon_price_tracker.py          # Main tracker
│   ├── .github/workflows/
│   │   └── amazon-price-tracker.yml     # GitHub Actions workflow
│   └── AMAZON_TRACKER_GUIDE.md          # Complete guide
│
├── Swiggy Trackers
│   ├── swiggy_android_tracker.py        # Android automation
│   ├── swiggy-price-monitor.user.js     # Tampermonkey script
│   ├── swiggy_simple_browser.py         # Manual browser
│   ├── ANDROID_SETUP.md                 # Android guide
│   └── TAMPERMONKEY_GUIDE.md            # Tampermonkey guide
│
├── Documentation
│   ├── README.md                        # This file
│   ├── FREE_CLOUD_OPTIONS.md            # Free hosting
│   ├── GITHUB_ACTIONS.md                # CI/CD guide
│   └── wiki/                            # Detailed wiki
│
└── Testing
    └── test_with_sample_data.py         # Test script
```

---

## ⚙️ Configuration

### Amazon Tracker

Edit `amazon_price_tracker.py`:
```python
CONFIG = {
    'price_threshold': 500,      # Alert under ₹500
    'discount_threshold': 50,    # Alert >50% off
    'max_products': 50,
    'search_queries': [
        'lightning deals',
        'deals of the day'
    ]
}
```

### Swiggy Trackers

Edit respective files:
```python
PRICE_THRESHOLD = 50      # Alert under ₹50
CHECK_INTERVAL = 300      # Check every 5 minutes
TEST_MODE = True          # False for Telegram
```

---

## 📱 Telegram Setup

### Create Bot
1. Open Telegram → @BotFather
2. Send `/newbot`
3. Save bot token

### Get Chat ID
1. Start chat with bot
2. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find `chat_id`

### Configure
```python
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
TEST_MODE = False
```

---

## 🎯 Features

### Amazon Tracker
- ✅ Runs on GitHub Actions (free)
- ✅ Scrapes Today's Deals
- ✅ Tracks Lightning Deals
- ✅ Custom search queries
- ✅ Telegram notifications
- ✅ CSV/JSON exports
- ✅ Screenshots
- ✅ Price history

### Swiggy Trackers
- ✅ Multiple automation methods
- ✅ Android app automation
- ✅ Browser-based (Tampermonkey)
- ✅ Detects pricing errors
- ✅ Tracks products under ₹50
- ✅ Finds >70% discounts
- ✅ Telegram alerts

---

## 📊 Example Outputs

### Amazon Alert
```
🛒 Amazon Deals Update

📊 Summary:
• Total Deals: 45
• Cheap Deals (≤₹500): 12
• High Discount (≥50%): 8

🔥 Top 5 Deals:
1. Wireless Mouse - ₹299 (70% off)
2. USB Cable - ₹199 (65% off)
...
```

### Swiggy Alert
```
🔥 PRICE ALERT!

Product: Chocolate Bar
Current Price: ₹9
Original Price: ₹50
Discount: 82%
```

---

## 🆓 Free Hosting Options

### GitHub Actions (Amazon)
- **Cost**: $0
- **Runs**: 2,000 min/month free
- **Best for**: Amazon tracking

### Oracle Cloud (Swiggy Android)
- **Cost**: $0 forever
- **Resources**: 4 ARM VMs, 24GB RAM
- **Best for**: 24/7 Swiggy tracking

### Spare Phone (Swiggy Android)
- **Cost**: $0
- **Setup**: Easiest
- **Best for**: Dedicated monitoring

See: **[[FREE_CLOUD_OPTIONS.md]]**

---

## 🐛 Troubleshooting

### Amazon Tracker
- **No deals found**: Check screenshots in artifacts
- **Workflow fails**: View logs in Actions tab
- **Telegram not working**: Verify secrets

### Swiggy Trackers
- **Android not connecting**: Run `adb devices`
- **Tampermonkey not running**: Check if enabled
- **No products found**: Check location setting

See: **[[FAQ]]** in wiki

---

## 📚 Documentation

### Guides
- **[[AMAZON_TRACKER_GUIDE.md]]** - Amazon setup
- **[[ANDROID_SETUP.md]]** - Android automation
- **[[TAMPERMONKEY_GUIDE.md]]** - Browser tracking
- **[[FREE_CLOUD_OPTIONS.md]]** - Free hosting

### Wiki
- **[[Home]]** - Wiki home
- **[[Quick Start Guide]]** - Get started
- **[[FAQ]]** - Common questions
- **[[Troubleshooting]]** - Fix issues

---

## 💡 Use Cases

### Daily Deal Hunter
- Run Amazon tracker 4x daily
- Get morning/evening deals
- Never miss lightning deals

### Grocery Saver
- Use Swiggy Tampermonkey
- Browse while shopping
- Catch pricing errors

### 24/7 Monitor
- Setup Swiggy on spare phone
- Run Amazon on GitHub Actions
- Get all deals automatically

---

## 🤝 Contributing

Contributions welcome!

1. Fork repository
2. Create feature branch
3. Make changes
4. Submit pull request

**Ideas:**
- More platforms (Flipkart, Myntra)
- Better deal detection
- Price history graphs
- Email notifications

---

## 📝 License

For personal use only. Respect platform Terms of Service.

---

## 🔗 Links

- **Repository**: https://github.com/hithesh0160/Swiggy-Instamart
- **Issues**: https://github.com/hithesh0160/Swiggy-Instamart/issues
- **Wiki**: https://github.com/hithesh0160/Swiggy-Instamart/wiki

---

**Ready to start?**

- **Amazon**: Enable GitHub Actions
- **Swiggy (Easy)**: Install Tampermonkey script
- **Swiggy (24/7)**: Setup Android automation
