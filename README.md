# Price Tracker - Amazon & Swiggy Instamart 🔥

Automatically track deep discounts on Amazon.in and Swiggy Instamart with Telegram notifications!

## 🚀 Quick Start

### Amazon Tracker (Recommended - Easiest!)

**Runs on GitHub Actions - completely free, no setup needed!**

1. Fork this repository
2. Add GitHub Secrets:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
   - `TELEGRAM_CHAT_ID` - Your Telegram chat ID
3. Enable GitHub Actions
4. Done! Runs automatically twice daily (9 AM & 9 PM IST)

**Features:**
- ✅ Tracks NEW deals only (no duplicates)
- ✅ Detects price drops >20%
- ✅ Separate electronics section
- ✅ Adaptive discount thresholds
- ✅ Free forever (GitHub Actions)

[📖 Full Amazon Guide →](docs/AMAZON_GUIDE.md)

### Swiggy Tracker (For Grocery Deals)

**Best method: Android automation**

1. Install Appium: `npm install -g appium`
2. Connect Android device
3. Run: `python swiggy_android_tracker.py`

[📖 Full Swiggy Guide →](docs/SWIGGY_GUIDE.md)

---

## 📊 Comparison

| Feature | Amazon (GitHub Actions) | Swiggy (Android) |
|---------|------------------------|------------------|
| Setup Difficulty | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐ Medium |
| Reliability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 24/7 Monitoring | ✅ Yes | ✅ Yes |
| Cost | $0 | $0 |
| Device Needed | ❌ No | ✅ Android |
| Cloud-based | ✅ Yes | Optional |

---

## 📱 Telegram Setup

### Create Bot
1. Open Telegram → @BotFather
2. Send `/newbot` and follow instructions
3. Save bot token

### Get Chat ID
1. Start chat with your bot
2. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find `chat_id` in response

### Configure
Add as GitHub Secrets (Amazon) or edit tracker file (Swiggy):
```python
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

---

## 📁 Repository Structure

```
├── amazon_price_tracker.py          # Amazon tracker (GitHub Actions)
├── swiggy_android_tracker.py        # Swiggy Android automation
├── swiggy-price-monitor.user.js     # Swiggy browser extension
├── .github/workflows/               # GitHub Actions workflows
├── docs/                            # Documentation
│   ├── AMAZON_GUIDE.md             # Complete Amazon guide
│   ├── SWIGGY_GUIDE.md             # Complete Swiggy guide
│   ├── TELEGRAM_SETUP.md           # Telegram configuration
│   ├── CLOUD_HOSTING.md            # Free cloud options
│   └── TROUBLESHOOTING.md          # Common issues & fixes
└── screenshots/                     # Debug screenshots
```

---

## ⚙️ Configuration

### Amazon Tracker
Edit `amazon_price_tracker.py`:
```python
CONFIG = {
    'price_threshold': 500,         # Alert under ₹500
    'discount_threshold': 50,       # Alert >50% off
    'price_drop_threshold': 20,     # Alert on >20% price drops
    'only_new_deals': True,         # No duplicate alerts
}
```

### Swiggy Tracker
Edit `swiggy_android_tracker.py`:
```python
PRICE_THRESHOLD = 50               # Alert under ₹50
CHECK_INTERVAL = 300               # Check every 5 minutes
SEARCH_QUERIES = [                 # Categories to search
    "snacks", "chocolate", "bread"
]
```

---

## 🎯 Features

### Amazon Tracker
- Scrapes Today's Deals, Lightning Deals, Electronics
- Smart duplicate detection (no repeat alerts)
- Price history tracking
- Adaptive discount thresholds for electronics
- Screenshots for debugging
- CSV/JSON exports

### Swiggy Tracker
- Android app automation (most reliable)
- Browser extension (Tampermonkey)
- Detects pricing errors
- Tracks products under ₹50
- Finds >70% discounts

---

## 📊 Example Alerts

### Amazon
```
🛒 Amazon Deals Alert

📊 Summary:
• New Deals: 5
• Price Drops: 2

💻 Electronics (3):
🆕 NEW
1. Samsung 32" TV - ₹15,999 (60% off)

📉 PRICE DROP
2. Dell Laptop - ₹35,999 (45% off)
   Was: ₹42,000 (dropped 14.3%)
```

### Swiggy
```
🔥 PRICE ALERT!

Product: Chocolate Bar
Current: ₹9
Original: ₹50
Discount: 82%
```

---

## 🆓 Free Hosting Options

### GitHub Actions (Amazon)
- **Cost:** $0
- **Runs:** 2,000 min/month free
- **Best for:** Amazon tracking

### Oracle Cloud (Swiggy)
- **Cost:** $0 forever
- **Resources:** 4 ARM VMs, 24GB RAM
- **Best for:** 24/7 Swiggy tracking

### Spare Phone (Swiggy)
- **Cost:** $0
- **Setup:** Easiest
- **Best for:** Dedicated monitoring

[📖 Full Cloud Guide →](docs/CLOUD_HOSTING.md)

---

## 🐛 Troubleshooting

### Amazon
- **No deals found:** Check screenshots in Actions artifacts
- **Workflow fails:** View logs in Actions tab
- **Duplicate alerts:** Update to latest code (fixed!)

### Swiggy
- **Android not connecting:** Run `adb devices`
- **No products found:** Check location setting
- **App crashes:** Restart Appium server

[📖 Full Troubleshooting Guide →](docs/TROUBLESHOOTING.md)

---

## 💡 Use Cases

**Daily Deal Hunter:** Run Amazon tracker 2x daily for morning/evening deals

**Grocery Saver:** Use Swiggy browser extension while shopping

**24/7 Monitor:** Setup Swiggy on spare phone + Amazon on GitHub Actions

---

## 🤝 Contributing

Contributions welcome!

1. Fork repository
2. Create feature branch
3. Make changes
4. Submit pull request

**Ideas:** Flipkart support, price history graphs, email notifications, Discord integration

---

## 📝 License

For personal use only. Respect platform Terms of Service.

---

## 🔗 Links

- **Issues:** https://github.com/hithesh0160/Swiggy-Instamart/issues
- **Discussions:** https://github.com/hithesh0160/Swiggy-Instamart/discussions

---

**Ready to start?**
- **Amazon:** Enable GitHub Actions now!
- **Swiggy:** Install Tampermonkey script or setup Android automation

