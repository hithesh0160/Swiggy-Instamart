# Quick Start Guide - Swiggy Price Tracker

## ✅ What's Working Now

You have a **browser-based tracker** that actually works! It will:
- Open Swiggy Instamart in a real browser
- Let YOU set the location to Bangalore
- Scrape all visible products
- Alert you for products under ₹50 or >70% discount

## 🚀 How to Use (Right Now!)

### Step 1: Run the Tracker

```bash
python swiggy_manual_tracker.py
```

### Step 2: In the Browser Window

A browser window will open automatically. Now:

1. **Set Location**: Click on the location field and enter "Bangalore"
2. **Select Area**: Choose your specific area in Bangalore
3. **Browse Products**: 
   - Scroll through the homepage, OR
   - Click on any category (Vegetables, Snacks, etc.), OR
   - Search for specific products
4. **Wait**: Let products load on the screen

### Step 3: Start Tracking

1. Come back to the terminal/command prompt
2. Press **ENTER**
3. The script will scrape all visible products and show you:
   - Products under ₹50
   - Products with >70% discount
   - Full product list with prices

## 📊 What You'll See

```
======================================================================
ALL PRODUCTS FOUND:
======================================================================
🔥  1. Chocolate Bar                    ₹   9.0 (MRP: ₹  50.0,  82.0% off)
🔥  2. Bread - White 400g               ₹  25.0 (MRP: ₹  30.0,  16.7% off)
    3. Milk - Toned 500ml               ₹  60.0 (MRP: ₹  65.0,   7.7% off)
...

======================================================================
PRODUCTS UNDER ₹50:
======================================================================
🔥 Chocolate Bar                         ₹   9.0 (82.0% off)
🔥 Bread - White 400g                    ₹  25.0 (16.7% off)
```

## ⚙️ Configuration

Edit `swiggy_manual_tracker.py`:

```python
PRICE_THRESHOLD = 50      # Change to alert for different price
CHECK_INTERVAL = 300      # Check every 5 minutes
TEST_MODE = True          # Set to False to enable Telegram
```

## 🔄 Continuous Monitoring

For continuous monitoring:

1. Set `TEST_MODE = False` in the script
2. Setup Telegram bot (see below)
3. Run the script
4. Browser stays open
5. Every 5 minutes it re-scrapes the current page
6. You can manually browse to different categories

## 📱 Telegram Setup (Optional)

### Create Bot:
1. Open Telegram, search `@BotFather`
2. Send `/newbot`
3. Follow instructions
4. Copy the bot token

### Get Chat ID:
1. Start chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find `chat_id` in the JSON

### Update Script:
```python
TELEGRAM_BOT_TOKEN = "123456:ABCdef..."
TELEGRAM_CHAT_ID = "123456789"
TEST_MODE = False
```

## 💡 Tips

- **Browse different categories**: The script scrapes whatever is visible
- **Search for specific items**: Search for "chocolate" or "bread" to find deals
- **Check different times**: Prices may change throughout the day
- **Run on a spare computer**: Keep it running 24/7 for best results

## 🐛 Troubleshooting

**"No products found"**
- Make sure products are actually visible in the browser
- Scroll down to load more products
- Try a different category
- Check `debug.png` screenshot

**Browser closes immediately**
- Check for Python errors in terminal
- Make sure Playwright is installed: `pip install playwright`
- Install browser: `python -m playwright install chromium`

**Products not being detected**
- The page structure might be different
- Check `page_source.html` to see what was captured
- Try scrolling more in the browser before pressing ENTER

## 🎯 Current Status

✅ Browser automation working
✅ Product scraping working  
✅ Price detection working
✅ Alert system working
✅ Telegram integration ready
✅ No API access needed!

You're all set! Just run the script and start tracking deals.
