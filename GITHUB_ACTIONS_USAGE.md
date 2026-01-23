# GitHub Actions Free Tier Optimization Guide

## 📊 Free Tier Limits

### What You Get (Free)
- **2,000 minutes/month** for private repos
- **Unlimited** for public repos
- Resets monthly

### Current Usage Calculation

**Amazon Tracker:**
- ~8 minutes per run
- 2 runs/day = 16 min/day
- **480 min/month** (24% of free tier)

**With existing daily job:**
- Your job: ~X min/day
- Amazon: 16 min/day
- **Total: Well within limits!**

---

## ⏰ Recommended Schedule

### Option 1: Twice Daily (Recommended) ⭐

```yaml
schedule:
  # 9 AM and 9 PM IST (3:30 AM and 3:30 PM UTC)
  - cron: '30 3,15 * * *'
```

**Why this is best:**
- Catches morning deals (9 AM)
- Catches evening deals (9 PM)
- Only 16 min/day
- **480 min/month (24% of free tier)**

### Option 2: Once Daily (Most Conservative)

```yaml
schedule:
  # 9 AM IST only (3:30 AM UTC)
  - cron: '30 3 * * *'
```

**Usage:**
- 8 min/day
- **240 min/month (12% of free tier)**

### Option 3: Three Times Daily (Aggressive)

```yaml
schedule:
  # 9 AM, 3 PM, 9 PM IST
  - cron: '30 3,9,15 * * *'
```

**Usage:**
- 24 min/day
- **720 min/month (36% of free tier)**

---

## 🎯 Optimization Features

### 1. Only New Deals & Price Drops

```python
CONFIG = {
    'only_new_deals': True,  # Only alert on NEW deals
    'price_drop_threshold': 20,  # Alert if price drops >20%
}
```

**Benefits:**
- No duplicate alerts
- Only notified when something changes
- Cleaner notifications

### 2. Reduced Product Limit

```python
CONFIG = {
    'max_products': 30,  # Reduced from 50
}
```

**Benefits:**
- Faster execution (~8 min vs ~12 min)
- Less data to process
- Still catches best deals

### 3. Timeout Protection

```yaml
timeout-minutes: 10  # Kill job if it takes >10 min
```

**Benefits:**
- Prevents runaway jobs
- Protects your free tier
- Fails fast if issues

### 4. Dependency Caching

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
```

**Benefits:**
- Faster runs (saves ~2 min)
- Less bandwidth
- More efficient

### 5. Reduced Artifact Retention

```yaml
retention-days: 7  # Instead of 30
```

**Benefits:**
- Less storage used
- Faster cleanup
- Still enough for review

---

## 📈 Usage Monitoring

### Check Your Usage

1. Go to your repo
2. Click **Settings** → **Billing**
3. View **Actions minutes used**

### Monthly Breakdown

```
Total Free Tier: 2,000 minutes

Your Usage:
├── Existing daily job: ~300 min/month (15%)
├── Amazon tracker (2x/day): ~480 min/month (24%)
└── Buffer: ~1,220 min/month (61%)

Total: ~780 min/month (39% of free tier)
```

**You're safe!** ✅

---

## 🔔 Alert Logic

### What Triggers Alerts

**1. New Deals**
- Product never seen before
- Meets price/discount threshold

**2. Price Drops**
- Price dropped >20% from last seen
- Already a good deal

**3. Massive Discounts**
- >50% discount
- Under ₹500

### What DOESN'T Trigger Alerts

❌ Same price as before
❌ Price increased
❌ Small price drops (<20%)
❌ Products above thresholds

---

## 📊 Example Scenarios

### Scenario 1: First Run

**Products found:** 30
**New deals:** 30 (all new)
**Alert sent:** ✅ Yes

**Telegram:**
```
🛒 Amazon Deals Alert

📊 Summary:
• New Deals: 30
• Price Drops: 0

🔥 Top Deals:
🆕 NEW
1. Wireless Mouse
   ₹299 (70% off)
```

### Scenario 2: Second Run (No Changes)

**Products found:** 30
**New deals:** 0
**Price drops:** 0
**Alert sent:** ❌ No

**Console:**
```
✓ No new deals or price drops - No alert sent
```

### Scenario 3: Price Drop Detected

**Products found:** 30
**New deals:** 2
**Price drops:** 3
**Alert sent:** ✅ Yes

**Telegram:**
```
🛒 Amazon Deals Alert

📊 Summary:
• New Deals: 2
• Price Drops: 3

🔥 Top Deals:
📉 PRICE DROP
1. Laptop Stand
   ₹599 (60% off)
   Was: ₹799 (dropped 25%)

🆕 NEW
2. USB Hub
   ₹399 (55% off)
```

---

## 🎛️ Fine-Tuning

### More Aggressive (More Alerts)

```python
CONFIG = {
    'price_threshold': 1000,  # Higher threshold
    'discount_threshold': 40,  # Lower discount requirement
    'price_drop_threshold': 10,  # Alert on smaller drops
    'only_new_deals': False,  # Alert on all deals
}
```

### More Conservative (Fewer Alerts)

```python
CONFIG = {
    'price_threshold': 300,  # Lower threshold
    'discount_threshold': 60,  # Higher discount requirement
    'price_drop_threshold': 30,  # Only big drops
    'only_new_deals': True,  # Only new/changed
}
```

### Balanced (Recommended) ⭐

```python
CONFIG = {
    'price_threshold': 500,
    'discount_threshold': 50,
    'price_drop_threshold': 20,
    'only_new_deals': True,
}
```

---

## 💰 Cost Comparison

### If You Exceed Free Tier

**GitHub Actions Pricing:**
- $0.008 per minute (after free tier)
- ~$0.50 per 1,000 minutes

**Example:**
- Use 3,000 min/month
- Overage: 1,000 min
- Cost: **$0.50/month**

**Still cheaper than:**
- AWS EC2: $5-10/month
- DigitalOcean: $6/month
- Heroku: $7/month

---

## 📅 Best Practices

### 1. Start Conservative

Begin with:
- 2 runs/day
- `only_new_deals: True`
- Monitor for a week

### 2. Adjust Based on Results

If too many alerts:
- Increase thresholds
- Reduce frequency

If missing deals:
- Lower thresholds
- Increase frequency

### 3. Use Manual Triggers

For special occasions:
- Big sale days (Prime Day, etc.)
- Specific product searches
- Testing changes

### 4. Monitor Usage

Check monthly:
- Actions tab → Usage
- Adjust if needed
- Stay within limits

---

## 🚨 Emergency: Exceeding Limits

### If You're Running Out

**Quick fixes:**

1. **Reduce frequency**
   ```yaml
   # Once daily instead of twice
   - cron: '30 3 * * *'
   ```

2. **Disable temporarily**
   ```yaml
   # Comment out schedule
   # schedule:
   #   - cron: '30 3,15 * * *'
   ```

3. **Reduce products**
   ```python
   'max_products': 20,  # From 30
   ```

4. **Increase timeout**
   ```yaml
   timeout-minutes: 8  # From 10
   ```

---

## 📊 Tracking Price History

### How It Works

**First run:**
```json
{
  "B08XYZ123": {
    "name": "Wireless Mouse",
    "price": 299,
    "discount": 70,
    "last_seen": "2026-01-19T09:00:00"
  }
}
```

**Second run (price drop):**
```json
{
  "B08XYZ123": {
    "name": "Wireless Mouse",
    "price": 249,  // Dropped!
    "discount": 75,
    "last_seen": "2026-01-19T21:00:00"
  }
}
```

**Alert sent:** ✅ Price dropped 16.7%

---

## 🎓 Advanced Tips

### 1. Combine with Other Jobs

```yaml
jobs:
  all-trackers:
    steps:
      - name: Run Amazon
        run: python amazon_price_tracker.py
      
      - name: Run Other Tracker
        run: python other_tracker.py
```

**Benefit:** Share setup time

### 2. Conditional Execution

```yaml
- name: Run only on weekdays
  if: github.event.schedule == '30 3 * * 1-5'
  run: python amazon_price_tracker.py
```

### 3. Parallel Jobs

```yaml
jobs:
  amazon:
    runs-on: ubuntu-latest
    steps: [...]
  
  swiggy:
    runs-on: ubuntu-latest
    steps: [...]
```

**Note:** Uses 2x minutes but runs faster

---

## 📈 Expected Results

### Week 1
- Many new deals (first time)
- Lots of alerts
- Building price history

### Week 2+
- Fewer alerts (only changes)
- More relevant notifications
- Stable tracking

### Monthly
- ~60 runs (2x/day)
- ~480 minutes used
- ~20-30 alerts sent

---

## ✅ Recommended Setup

**For most users:**

```yaml
# Schedule: Twice daily
schedule:
  - cron: '30 3,15 * * *'

# Config
CONFIG = {
    'price_threshold': 500,
    'discount_threshold': 50,
    'price_drop_threshold': 20,
    'max_products': 30,
    'only_new_deals': True
}

# Timeout
timeout-minutes: 10

# Retention
retention-days: 7
```

**Usage:** ~480 min/month (24% of free tier)
**Alerts:** Only new deals and price drops
**Perfect balance!** ⭐

---

**Questions?** Check the main README or open an issue!
