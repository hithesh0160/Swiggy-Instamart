# Amazon Tracker - Alert Behavior

## How Alerts Work Now

### ✅ When You GET Alerts

**1. New Deals (🆕 NEW)**
- Product never seen before
- First time appearing in tracking

**2. Price Drops (📉 PRICE DROP)**
- Price dropped by >20% from last seen price
- Shows old price and drop percentage

### ❌ When You DON'T Get Alerts

**1. Same Price**
- Product has same price as before
- No change detected

**2. Minor Price Changes**
- Price change less than 20%
- Not significant enough

**3. Price Increases**
- Product became more expensive
- Not a deal anymore

---

## Message Types

### Type 1: New Deals Found
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

### Type 2: No New Deals
```
🛒 Amazon Deals Check

✓ No new deals or price drops found

All tracked products have the same prices as before.

⏰ 2026-01-23 21:00:00
```

---

## How Price Tracking Works

### First Run
- All products are NEW
- Everything gets alerted
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

## Example Scenarios

### Scenario 1: Product Appears First Time
```
Run 1: Product A - ₹500 (50% off) → 🆕 ALERT
Run 2: Product A - ₹500 (50% off) → ❌ No alert (same price)
Run 3: Product A - ₹500 (50% off) → ❌ No alert (same price)
```

### Scenario 2: Price Drops Significantly
```
Run 1: Product B - ₹1000 (30% off) → 🆕 ALERT
Run 2: Product B - ₹1000 (30% off) → ❌ No alert (same price)
Run 3: Product B - ₹750 (50% off)  → 📉 ALERT (25% drop)
Run 4: Product B - ₹750 (50% off)  → ❌ No alert (same price)
```

### Scenario 3: Minor Price Change
```
Run 1: Product C - ₹500 (40% off) → 🆕 ALERT
Run 2: Product C - ₹480 (42% off) → ❌ No alert (only 4% drop)
Run 3: Product C - ₹500 (40% off) → ❌ No alert (back to original)
```

### Scenario 4: Price Increases
```
Run 1: Product D - ₹300 (70% off) → 🆕 ALERT
Run 2: Product D - ₹500 (50% off) → ❌ No alert (price increased)
Run 3: Product D - ₹300 (70% off) → 📉 ALERT (40% drop from ₹500)
```

---

## Configuration

### Price Drop Threshold
```python
'price_drop_threshold': 20  # Alert if price drops by >20%
```

**Examples:**
- 20% = Alert if ₹1000 → ₹800 or less
- 30% = Alert if ₹1000 → ₹700 or less
- 10% = Alert if ₹1000 → ₹900 or less

### Deal Thresholds
```python
'price_threshold': 500      # Alert for products under ₹500
'discount_threshold': 50    # Alert for >50% discount
```

**Both apply to NEW products only**

---

## Files Explained

### price_history.json
```json
{
  "B08X6PYCQV": {
    "name": "Samsung TV",
    "price": 15999,
    "discount": 60,
    "last_seen": "2026-01-23T09:00:00"
  }
}
```
- Tracks every product seen
- Updated after each run
- Used to detect price changes

### amazon_deals_new.json
```json
[
  {
    "name": "Samsung TV",
    "price": 15999,
    "discount": 60,
    "change_type": "new",
    "timestamp": "2026-01-23T09:00:00"
  }
]
```
- Only NEW deals and price drops
- What triggered the alert
- Empty if no changes

### price_changes.json
```json
{
  "timestamp": "2026-01-23T09:00:00",
  "new_deals": 5,
  "price_drops": 2,
  "total_scraped": 89,
  "deals": [...]
}
```
- Summary of changes
- Quick overview
- Includes all new/changed deals

---

## Benefits

### No Spam
- Won't get same deals repeatedly
- Only meaningful changes

### Real Deals
- Price drops are genuine
- Not just re-listing

### Clear Tracking
- Know what's new vs what changed
- See price history

### Efficient
- Doesn't waste your time
- Only important notifications

---

## Troubleshooting

### Getting Too Many Alerts?
**Increase price drop threshold:**
```python
'price_drop_threshold': 30  # Only alert on >30% drops
```

### Not Getting Enough Alerts?
**Decrease price drop threshold:**
```python
'price_drop_threshold': 10  # Alert on >10% drops
```

### Want to Reset History?
**Delete price_history.json:**
- All products will be "new" again
- Next run will alert everything
- History rebuilds from scratch

### Want to See All Deals?
**Check amazon_deals.json:**
- Contains ALL scraped deals
- Not just new/changed ones
- Updated every run

---

## Summary

**Simple Rule:**
- First time seeing product → Alert
- Price drops significantly → Alert
- Same price as before → No alert
- Minor changes → No alert

**Result:**
- Only get notified about genuinely new or better deals
- No repeated alerts for same products
- Clean, useful notifications

---

**Next scheduled run:** Check Actions tab at 9 AM or 9 PM IST
