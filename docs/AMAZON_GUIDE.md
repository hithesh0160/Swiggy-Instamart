# Amazon.in Price Tracker - Complete Guide

Automatically track Amazon deals using GitHub Actions - runs completely free in the cloud!

## 🌟 Why This Works

- ✅ **Runs on GitHub Actions** - No server needed
- ✅ **Completely free** - 2,000 minutes/month
- ✅ **Smart alerts** - Only NEW deals or price drops >20%
- ✅ **No duplicates** - Tracks price history
- ✅ **Automated** - Runs twice daily (9 AM & 9 PM IST)
- ✅ **Manual trigger** - Run anytime with one click

---

## 🚀 Setup (5 Minutes)

### Step 1: Fork Repository
Already done if you're reading this!

### Step 2: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

**TELEGRAM_BOT_TOKEN**
- Get from @BotFather on Telegram
- See [Telegram Setup Guide](TELEGRAM_SETUP.md)

**TELEGRAM_CHAT_ID**
- Get from `https://api.telegram.org/bot<TOKEN>/getUpdates`
- See [Telegram Setup Guide](TELEGRAM_SETUP.md)

### Step 3: Enable GitHub Actions

1. Go to **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"
3. Done! Workflow runs automatically

### Step 4: Manual Trigger (Optional)

1. Go to **Actions** tab
2. Click "Amazon Price Tracker"
3. Click "Run workflow"
4. Optionally enter a search query
5. Click "Run workflow" (green button)

---

## ⚙️ Configuration

### Tracking Settings

Edit `amazon_price_tracker.py`:

```python
CONFIG = {
    'price_threshold': 500,         # Alert for products under ₹500
    'discount_threshold': 50,       # Alert for >50% discount
    'price_drop_threshold': 20,     # Alert if price drops by >20%
    'max_products': 30,             # Max products per search
    'only_new_deals': True,         # Only alert on NEW deals or price drops
    
    'search_queries': [
        'lightning deals',
        'deals of the day'
    ],
    
    'electronics_queries': [
        'tv deals',
        'laptop deals',
        'smartphone deals'
    ],
    
    'electronics_config': {
        'min_discount': 20,         # Start with 20% discount
        'max_discount': 60,         # Try up to 60%
        'discount_step': 10,        # Reduce by 10% each time
        'min_products': 5,          # Need at least 5 products
        'max_price': 50000          # Electronics can be expensive
    }
}
```

### Schedule

Edit `.github/workflows/amazon-price-tracker.yml`:

```yaml
on:
  schedule:
    # Current: Twice daily (9 AM and 9 PM IST)
    - cron: '30 3,15 * * *'
    
    # Options:
    # Every 6 hours: '0 */6 * * *'
    # Every 3 hours: '0 */3 * * *'
    # Once daily: '30 3 * * *'
```

**Current usage:** ~20 min/day = ~600 min/month (30% of free tier)

---

## 📊 What Gets Tracked

### Automatic Sources

1. **Today's Deals** - https://www.amazon.in/gp/goldbox
2. **Lightning Deals** - Time-limited flash sales
3. **Search Queries** - "lightning deals", "deals of the day"
4. **Electronics Section** - TV, laptop, smartphone deals with adaptive discount

### Custom Search

Trigger manually with custom query:
- Go to Actions → Run workflow
- Enter: "laptop under 30000"
- Click Run

---

## 📱 Telegram Notifications

### Message Format

**When new deals found:**
```
🛒 Amazon Deals Alert

📊 Summary:
• New Deals: 5
• Price Drops: 2

💻 Electronics Deals (3):

🆕 NEW
1. Samsung 32" Smart TV
   ₹15,999 (60% off)
   View Deal

📉 PRICE DROP
2. Dell Laptop i5 8GB
   ₹35,999 (45% off)
   Was: ₹42,000 (dropped 14.3%)
   View Deal

🔥 Other Deals (4):

🆕 NEW
1. Wireless Mouse
   ₹299 (70% off)
   View Deal

⏰ 2026-01-23 09:00:00
```

**When no changes:**
```
🛒 Amazon Deals Check

✓ No new deals or price drops found

All tracked products have the same prices as before.

⏰ 2026-01-23 21:00:00
```

### Notification Triggers

Alerts sent ONLY when:
- NEW deals found (not seen before)
- Price drops by >20%
- Products under ₹500 OR >50% discount

**No alerts for:**
- Same price as before
- Minor price changes (<20%)
- Already notified products

---

## 📁 Output Files

### Downloadable Artifacts

After each run, download from Actions tab:

1. **amazon_deals.json** - All scraped deals
2. **amazon_deals_new.json** - Only NEW deals and price drops
3. **price_history.json** - Historical price tracking
4. **price_changes.json** - Summary of changes
5. **screenshots/** - Page screenshots for debugging

### How to Download

1. Go to **Actions** tab
2. Click on a workflow run
3. Scroll to **Artifacts**
4. Download `amazon-deals-XXX`

---

## 🎯 How It Works

### First Run
- All products are NEW
- Alerts sent for all qualifying products
- Prices saved to `price_history.json`

### Second Run
- Compares current prices with history
- Only alerts if:
  - Product is new (not in history)
  - Price dropped by >20%
- Updates history with current prices

### Third Run and Beyond
- Same logic as second run
- History keeps growing
- Only meaningful changes trigger alerts

---

## 💰 Cost Analysis

### GitHub Actions Free Tier

**Included:**
- 2,000 minutes/month (free)
- Unlimited for public repos

**Current usage:**
- ~10 minutes per run
- 2 runs/day = 20 min/day
- ~600 min/month
- **Only 30% of free tier!**

### Optimized for Free Tier

- Reduced search queries
- Faster page loads
- Shorter wait times
- Efficient scraping
- Stays well within limits

---

## 🐛 Troubleshooting

### Workflow Not Running

**Check:**
1. Is Actions enabled?
2. Are secrets set correctly?
3. Is schedule correct?

**Fix:**
- Go to Actions tab
- Enable workflows
- Check Settings → Actions

### No Deals Found

**Check screenshots in artifacts**

**Possible causes:**
1. Amazon changed structure
2. No deals available
3. Scraping blocked

**Fix:**
- Update selectors in code
- Try manual trigger
- Check logs

### Telegram Not Working

**Check:**
1. Correct bot token?
2. Correct chat ID?
3. Bot started?

**Fix:**
- Test bot manually
- Verify secrets
- Start chat with bot

### Duplicate Alerts

**Fixed in latest version!**

The tracker now uses normalized product names and ASINs to prevent duplicates.

---

## 📈 Advanced Usage

### Track Specific Products

```python
'search_queries': [
    'laptop under 30000',
    'wireless earbuds',
    'smart watch',
    'kindle',
    'echo dot'
]
```

### Adjust Sensitivity

```python
# More alerts
'price_drop_threshold': 10,  # Alert on >10% drops

# Fewer alerts
'price_drop_threshold': 30,  # Alert on >30% drops
```

### Reset Price History

To treat all products as "new" again:

```bash
git rm price_history.json
git commit -m "Reset price history"
git push
```

---

## 💡 Tips & Tricks

### Best Times to Check

- **9 AM** - New deals posted
- **12 PM** - Lunch deals
- **6 PM** - Evening deals
- **12 AM** - Midnight deals

### Categories to Watch

**High discount:**
- Electronics
- Fashion
- Books

**Best deals:**
- Lightning deals
- Today's deals
- Clearance

---

## 🔗 Related Guides

- [Telegram Setup](TELEGRAM_SETUP.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Cloud Hosting](CLOUD_HOSTING.md)

---

**Ready to start?** Enable GitHub Actions and get deal alerts!
