# Telegram Setup Guide

Get instant notifications for price drops and deals!

## 🤖 Create Telegram Bot

### Step 1: Open BotFather

1. Open Telegram app
2. Search for `@BotFather`
3. Start chat

### Step 2: Create Bot

1. Send `/newbot`
2. Choose a name (e.g., "My Price Tracker")
3. Choose a username (e.g., "my_price_tracker_bot")
4. BotFather will send you a token

**Example token:**
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Save this token!** You'll need it for configuration.

---

## 💬 Get Chat ID

### Method 1: Using getUpdates API

1. Start a chat with your bot
2. Send any message (e.g., "Hello")
3. Open this URL in browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   Replace `<YOUR_TOKEN>` with your bot token

4. Look for `"chat":{"id":` in the response
5. The number after `"id":` is your chat ID

**Example response:**
```json
{
  "ok": true,
  "result": [{
    "message": {
      "chat": {
        "id": 123456789,  ← This is your chat ID
        "first_name": "John"
      }
    }
  }]
}
```

### Method 2: Using @userinfobot

1. Open Telegram
2. Search for `@userinfobot`
3. Start chat
4. Bot will send your user ID

---

## ⚙️ Configure Tracker

### For Amazon (GitHub Actions)

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:

**Secret 1:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: Your bot token (e.g., `123456789:ABCdefGHI...`)

**Secret 2:**
- Name: `TELEGRAM_CHAT_ID`
- Value: Your chat ID (e.g., `123456789`)

### For Swiggy (Local)

Edit `swiggy_android_tracker.py`:

```python
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID = "123456789"
TEST_MODE = False  # Enable Telegram alerts
```

### For Tampermonkey

Edit `swiggy-price-monitor.user.js`:

```javascript
const CONFIG = {
    telegram: {
        botToken: '123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
        chatId: '123456789',
        enabled: true  // Enable Telegram
    }
};
```

---

## 📱 Test Your Setup

### Test Amazon Tracker

1. Go to Actions tab
2. Click "Run workflow"
3. Wait for completion
4. Check Telegram for notification

### Test Swiggy Tracker

```bash
python swiggy_android_tracker.py
```

Check Telegram for notification when deals are found.

---

## 👥 Group Notifications

Want multiple people to get alerts?

### Create Telegram Group

1. Create a new group in Telegram
2. Add your bot to the group
3. Send a message in the group
4. Get group chat ID using getUpdates API
5. Use group chat ID in configuration

**Note:** Group chat IDs are negative numbers (e.g., `-123456789`)

---

## 🔒 Security Best Practices

### Don't Commit Tokens

**Bad:**
```python
TELEGRAM_BOT_TOKEN = "123456789:ABCdef..."  # In code
```

**Good:**
```python
import os
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
```

### Use Environment Variables

**Windows:**
```cmd
setx TELEGRAM_BOT_TOKEN "your_token"
setx TELEGRAM_CHAT_ID "your_chat_id"
```

**Linux/Mac:**
```bash
echo 'export TELEGRAM_BOT_TOKEN="your_token"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="your_chat_id"' >> ~/.bashrc
source ~/.bashrc
```

### GitHub Secrets

For GitHub Actions, always use Secrets (not hardcoded in workflow files).

---

## 🐛 Troubleshooting

### "Unauthorized" Error

**Cause:** Wrong bot token

**Fix:**
1. Verify token from @BotFather
2. Check for typos
3. Regenerate token if needed

### "Chat not found" Error

**Cause:** Wrong chat ID or bot not started

**Fix:**
1. Start chat with bot first
2. Send a message
3. Verify chat ID using getUpdates
4. For groups, make sure bot is added

### No Notifications Received

**Check:**
1. Is bot token correct?
2. Is chat ID correct?
3. Did you start chat with bot?
4. Is TEST_MODE set to False?
5. Are deals actually found?

**Test manually:**
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=Test message"
```

### Rate Limiting

**Symptom:** Some messages not delivered

**Cause:** Sending too many messages too fast

**Fix:**
- Telegram allows 30 messages/second
- Add delays between messages
- Batch multiple deals in one message

---

## 📊 Message Formatting

### HTML Formatting

```python
message = """
<b>Bold text</b>
<i>Italic text</i>
<code>Code text</code>
<a href="https://example.com">Link</a>
"""

send_telegram(message, parse_mode='HTML')
```

### Markdown Formatting

```python
message = """
*Bold text*
_Italic text_
`Code text`
[Link](https://example.com)
"""

send_telegram(message, parse_mode='Markdown')
```

---

## 💡 Advanced Features

### Custom Keyboards

```python
keyboard = {
    'inline_keyboard': [[
        {'text': 'View Deal', 'url': 'https://amazon.in/...'}
    ]]
}

send_telegram(message, reply_markup=keyboard)
```

### Silent Notifications

```python
send_telegram(message, disable_notification=True)
```

### Disable Link Preview

```python
send_telegram(message, disable_web_page_preview=True)
```

---

## 🔗 Related Guides

- [Amazon Guide](AMAZON_GUIDE.md)
- [Swiggy Guide](SWIGGY_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Ready?** Configure your bot and start getting deal alerts!
