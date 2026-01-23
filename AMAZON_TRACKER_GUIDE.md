# Amazon.in Price Tracker with GitHub Actions

Automatically track Amazon deals using GitHub Actions - runs completely free in the cloud!

## 🌟 Why Amazon + GitHub Actions?

### Advantages
- ✅ **Works on GitHub Actions** - No Android emulator needed
- ✅ **Completely free** - GitHub Actions free tier
- ✅ **Automated** - Runs twice daily (9 AM & 9 PM IST)
- ✅ **No server needed** - Runs in the cloud
- ✅ **Better API** - Amazon has more stable structure
- ✅ **Manual trigger** - Run anytime with one click
- ✅ **Smart alerts** - Only notifies on NEW deals or price drops

### How It Works
1. GitHub Actions runs twice daily (9 AM & 9 PM IST)
2. Scrapes Amazon deals pages + electronics section
3. Finds products under ₹500 or >50% discount
4. Tracks price history - only alerts on NEW deals or >20% price drops
5. Sends Telegram summary with separate sections for electronics
6. Saves results as artifacts
7. Commits price history to repository

---

## 🚀 Setup

### Step 1: Fork/Clone Repository

Already done! You have the code.

### Step 2: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

**TELEGRAM_BOT_TOKEN**
- Value: Your Telegram bot token
- Get from: @BotFather on Telegram

**TELEGRAM_CHAT_ID**
- Value: Your Telegram chat ID
- Get from: `https://api.telegram.org/bot<TOKEN>/getUpdates`

### Step 3: Enable GitHub Actions

1. Go to **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will run automatically!

### Step 4: Manual Trigger (Optional)

1. Go to **Actions** tab
2. Click "Amazon Price Tracker"
3. Click "Run workflow"
4. Optionally enter a search query
5. Click "Run workflow"

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
    # Twice daily: 9 AM and 9 PM IST (3:30 AM and 3:30 PM UTC)
    - cron: '30 3,15 * * *'
    
    # Every 6 hours
    # - cron: '0 */6 * * *'
    
    # Every 3 hours
    # - cron: '0 */3 * * *'
    
    # Every day at 9 AM IST
    # - cron: '30 3 * * *'
```

**Current schedule:** Twice daily (9 AM & 9 PM IST)
- Uses ~20 minutes/day
- ~600 minutes/month
- Only 30% of free tier (2,000 min/month)

---

## 📊 What Gets Tracked

### Automatic Sources

1. **Today's Deals**
   - https://www.amazon.in/gp/goldbox

2. **Lightning Deals**
   - Time-limited flash sales

3. **Search Queries**
   - "lightning deals"
   - "deals of the day"

4. **Electronics Section (Adaptive)**
   - TV deals
   - Laptop deals
   - Smartphone deals
   - Adaptive discount: 60% → 50% → 40% → 30% → 20%
   - Finds at least 5 products or takes top discounted ones

### Custom Search

Trigger manually with custom query:
- Go to Actions → Run workflow
- Enter: "laptop under 30000"
- Click Run

---

## 📱 Telegram Notifications

### Message Format

```
🛒 Amazon Deals Alert

📊 Summary:
• New Deals: 12
• Price Drops: 3
• Cheap Deals (≤₹500): 8
• High Discount (≥50%): 7

💻 Electronics Deals (5):

🆕 NEW
1. Samsung 32" Smart TV
   ₹15,999 (60% off)
   View Deal

📉 PRICE DROP
2. Dell Laptop i5 8GB
   ₹35,999 (45% off)
   Was: ₹42,000 (dropped 14.3%)
   View Deal

🔥 Other Top Deals (5):

🆕 NEW
1. Wireless Mouse
   ₹299 (70% off)
   View Deal

...

⏰ 2026-01-23 09:00:00
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

### Artifacts (Downloadable)

After each run, download:

1. **amazon_deals.json**
   - Complete deal data
   - JSON format
   - All fields included

2. **amazon_deals_new.json**
   - Only NEW deals and price drops
   - What triggered alerts
   - Filtered data

3. **price_history.json**
   - Historical price tracking
   - Committed to repo
   - Used for price drop detection

4. **price_changes.json**
   - Summary of changes
   - New deals count
   - Price drops count

5. **screenshots/**
   - Page screenshots
   - Visual verification
   - Debugging

### How to Download

1. Go to **Actions** tab
2. Click on a workflow run
3. Scroll to **Artifacts**
4. Download `amazon-deals-XXX`

### Committed to Repository

Results also committed to repo:
- `amazon_deals.json` - Latest deals
- `price_history.json` - Price tracking database
- `price_changes.json` - Latest changes summary
- Track history with git

---

## 🎯 Features

### Smart Deal Detection

```python
def is_deal(price, discount):
    # Under ₹500
    if price <= 500:
        return True
    
    # Over 50% discount
    if discount >= 50:
        return True
    
    return False
```

### Duplicate Removal

Automatically removes duplicate products based on:
- Product name
- Price

### Rate Limiting

Built-in delays between requests:
- 2 seconds between searches
- 1 second between scrolls
- Prevents blocking

### Screenshot Capture

Every page scraped is screenshot:
- Saved to `screenshots/` folder
- Timestamped
- Useful for debugging

---

## 💰 Cost Analysis

### GitHub Actions Free Tier

**Included:**
- 2,000 minutes/month (free)
- Unlimited for public repos

**Usage per run:**
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

### Comparison

| Method | Cost | Runs/Day | Setup |
|--------|------|----------|-------|
| GitHub Actions | $0 | 4 | Easy |
| Oracle Cloud | $0 | Unlimited | Hard |
| Spare Phone | $0 | Unlimited | Easy |
| AWS | $10/mo | Unlimited | Medium |

---

## 🐛 Troubleshooting

### Workflow Not Running

**Check:**
1. Is Actions enabled?
2. Are secrets set?
3. Is schedule correct?

**Fix:**
- Go to Actions tab
- Enable workflows
- Check Settings → Actions

### No Deals Found

**Possible causes:**
1. Amazon changed structure
2. No deals available
3. Scraping blocked

**Fix:**
- Check screenshots in artifacts
- Update selectors in code
- Try manual trigger

### Telegram Not Working

**Check:**
1. Correct bot token?
2. Correct chat ID?
3. Bot started?

**Fix:**
- Test bot manually
- Check secrets
- Start chat with bot

### Workflow Fails

**Check logs:**
1. Go to Actions tab
2. Click failed run
3. View logs

**Common issues:**
- Timeout (increase timeout)
- Selector changed (update code)
- Rate limited (add delays)

---

## 📈 Advanced Usage

### Track Specific Products

```python
# Add to search_queries
'search_queries': [
    'laptop under 30000',
    'wireless earbuds',
    'smart watch',
    'kindle',
    'echo dot'
]
```

### Custom Price Thresholds

```python
# Different thresholds per category
def is_deal(price, discount, category):
    if category == 'electronics':
        return price <= 1000 or discount >= 60
    elif category == 'books':
        return price <= 200 or discount >= 40
    else:
        return price <= 500 or discount >= 50
```

### Price History Tracking

```python
# Load previous deals
with open('amazon_deals.json') as f:
    old_deals = json.load(f)

# Compare prices
for deal in new_deals:
    old_price = find_old_price(deal, old_deals)
    if old_price and deal['price'] < old_price:
        alert(f"Price drop: {deal['name']} from ₹{old_price} to ₹{deal['price']}")
```

### Multiple Telegram Groups

```python
# Send to multiple chats
CHAT_IDS = ['123456', '789012', '345678']

for chat_id in CHAT_IDS:
    send_telegram(message, chat_id)
```

---

## 🔒 Privacy & Security

### What Data is Collected?

**Stored in repository:**
- Product names
- Prices
- Discounts
- Links
- Timestamps

**Never stored:**
- Your Amazon credentials
- Personal information
- Browsing history

### Is It Safe?

✅ **Yes!**
- Runs in GitHub's infrastructure
- No login required
- Public data only
- Open source code

### Can Amazon Block It?

**Unlikely:**
- Uses standard browser
- Reasonable rate limits
- Public pages only
- No aggressive scraping

**Best practices:**
- Don't run too frequently
- Use delays between requests
- Respect robots.txt

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

### Search Strategies

```python
'search_queries': [
    # Brand specific
    'samsung deals',
    'apple deals',
    
    # Price range
    'under 500',
    'under 1000',
    
    # Occasion
    'sale',
    'clearance',
    'limited time'
]
```

---

## 🆚 Comparison

### vs Swiggy Tracker

| Feature | Amazon | Swiggy |
|---------|--------|--------|
| GitHub Actions | ✅ Works | ❌ Needs Android |
| Setup | Easy | Hard |
| Reliability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Deal Frequency | High | Medium |
| Product Range | Huge | Limited |

### vs Manual Checking

| Aspect | Automated | Manual |
|--------|-----------|--------|
| Time | 0 min | 30 min/day |
| Coverage | All deals | Limited |
| Consistency | Always | Sometimes |
| Alerts | Instant | Delayed |

---

## 🔗 Related

- **[[Swiggy Android Tracker]]** - For Swiggy Instamart
- **[[Tampermonkey Guide]]** - Browser-based tracking
- **[[Free Cloud Options]]** - Other hosting options

---

## 📝 Example Workflow

### Daily Routine

**9 AM:**
- GitHub Actions runs automatically
- Scrapes morning deals
- Sends Telegram summary

**You receive:**
```
🛒 Amazon Deals Update

📊 Summary:
• Total Deals: 23
• Cheap Deals: 8
• High Discount: 5

🔥 Top 5 Deals:
1. Wireless Mouse - ₹299 (70% off)
...
```

**You click:**
- View Deal link
- Check product
- Buy if interested

**3 PM:**
- Actions runs again
- New deals found
- Another notification

**Repeat 4x daily!**

---

## 🎓 Learning Resources

### GitHub Actions
- https://docs.github.com/en/actions

### Playwright
- https://playwright.dev/python/

### Amazon Scraping
- Respect robots.txt
- Use reasonable delays
- Public data only

---

## 🤝 Contributing

Want to improve the tracker?

1. Fork repository
2. Add features
3. Test thoroughly
4. Submit pull request

**Ideas:**
- More categories
- Better deal detection
- Price history graphs
- Email notifications
- Discord integration

---

**Ready to start?** Push the code and enable GitHub Actions!
