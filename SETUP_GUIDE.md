# Swiggy Instamart Price Tracker - Setup Guide

## The Challenge

Swiggy Instamart's API is protected and requires:
1. Authentication tokens
2. Session cookies
3. Location permissions
4. Dynamic API endpoints

## Solution: Two Approaches

### Approach 1: Manual API Discovery (Recommended)

1. **Open Swiggy Instamart in your browser**
   - Go to: https://www.swiggy.com/instamart
   - Set your location to Bangalore

2. **Open Browser DevTools**
   - Press `F12` or `Ctrl+Shift+I`
   - Go to the "Network" tab
   - Filter by "Fetch/XHR"

3. **Browse products and find API calls**
   - Scroll through products
   - Look for API calls that return product data
   - Common patterns:
     - `/instamart/...`
     - `/dapi/...`
     - `/mapi/...`
   
4. **Copy the API request**
   - Right-click on a successful API call
   - Select "Copy" → "Copy as cURL"
   - Or note down:
     - URL
     - Headers (especially cookies, authorization)
     - Query parameters

5. **Update the script**
   - Edit `swiggy_simple_tracker.py`
   - Add the correct URL in the `fetch_products()` method
   - Add required headers/cookies

### Approach 2: Use Sample Data for Testing

I've created a test mode that works with sample data:

1. **Create a sample data file** (`swiggy_sample.json`):

```json
{
  "data": {
    "widgets": [
      {
        "data": [
          {
            "id": "123",
            "display_name": "Amul Butter 100g",
            "price": 60,
            "mrp": 65
          },
          {
            "id": "124",
            "display_name": "Bread - White 400g",
            "price": 25,
            "mrp": 30
          },
          {
            "id": "125",
            "display_name": "Milk - Toned 500ml",
            "price": 28,
            "mrp": 30
          }
        ]
      }
    ]
  }
}
```

2. **Run the test script**:
```bash
python test_with_sample_data.py
```

## Telegram Bot Setup

Once you have the API working:

1. **Create Telegram Bot**:
   - Open Telegram, search for `@BotFather`
   - Send `/newbot`
   - Follow instructions
   - Save the bot token

2. **Get your Chat ID**:
   - Start a chat with your bot
   - Send any message
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find your `chat_id` in the JSON response

3. **Configure the script**:
   ```python
   TELEGRAM_BOT_TOKEN = "your_bot_token_here"
   TELEGRAM_CHAT_ID = "your_chat_id_here"
   TEST_MODE = False  # Enable Telegram alerts
   ```

## Alternative: Browser Extension

If API access is too complex, consider building a browser extension that:
- Runs in your browser while you browse Swiggy
- Monitors prices in real-time
- Sends alerts via Telegram

## Tips

- Swiggy's API may change frequently
- You might need to update headers/cookies periodically
- Consider using a proxy or VPN if you face rate limiting
- Run on a server/Raspberry Pi for 24/7 monitoring

## Legal Note

Web scraping should be done responsibly:
- Respect robots.txt
- Don't overload servers (reasonable intervals)
- Use data for personal use only
- Check Swiggy's Terms of Service
