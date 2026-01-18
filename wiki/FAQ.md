# Frequently Asked Questions (FAQ)

## General Questions

### What is this tool?
An automated price tracker for Swiggy Instamart that monitors products and alerts you when prices drop below ₹50 or discounts exceed 70%.

### Is it free?
Yes! The tool is completely free and open source. You can run it on:
- Your computer (free)
- Spare Android phone (free)
- Oracle Cloud (free forever)
- AWS/Google Cloud (free for 12 months)

### Is it legal?
The tool is for personal use only. It automates what you would do manually - browsing and checking prices. However:
- ✅ Use for personal price monitoring
- ✅ Respect Swiggy's Terms of Service
- ❌ Don't use for commercial purposes
- ❌ Don't overload their servers

### Does it work outside Bangalore?
Currently configured for Bangalore only, but you can modify the location in the code.

---

## Setup Questions

### Which method should I use - Android or Browser?
**Android is recommended** because:
- More reliable
- No website loading issues
- Automatic searching
- Better for 24/7 monitoring

Use browser only if you don't have Android device.

### Do I need a real Android phone?
No! You can use:
- Real Android phone (best)
- Android emulator (good)
- Cloud Android device (works)

### Can I run this on Windows/Mac/Linux?
Yes! Works on all platforms. Just install the required dependencies.

### How much technical knowledge do I need?
- **Basic**: Can copy-paste commands - Use spare phone method
- **Intermediate**: Comfortable with terminal - Use local setup
- **Advanced**: Can setup cloud servers - Use Oracle Cloud

---

## Functionality Questions

### How often does it check prices?
Default: Every 5 minutes (300 seconds)
Configurable in `CHECK_INTERVAL`

### What products does it track?
By default, searches for:
- Snacks
- Biscuits
- Chocolate
- Bread
- Milk
- Vegetables
- Fruits

You can customize in `SEARCH_QUERIES`.

### How does it detect deals?
Two conditions trigger alerts:
1. Product price ≤ ₹50
2. Discount ≥ 70%

### Can I track specific products?
Yes! Modify `SEARCH_QUERIES` to search for specific items:
```python
SEARCH_QUERIES = [
    "amul butter",
    "britannia bread",
    "cadbury dairy milk"
]
```

### Does it track price history?
Not by default, but you can add this feature. Each run saves to `scraped_products.json`.

---

## Telegram Questions

### Do I need Telegram?
No! You can run in TEST_MODE and see results in console. Telegram is optional for notifications.

### How do I create a Telegram bot?
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow instructions
5. Save the token

### How do I get my chat ID?
1. Start chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find `chat_id` in JSON response

### Can multiple people get alerts?
Yes! Create a Telegram group:
1. Add your bot to group
2. Get group chat ID
3. Use group ID in config

---

## Android Questions

### What Android version do I need?
Android 7.0 (Nougat) or higher

### Can I use iOS?
No, currently Android only. iOS automation is more complex and restricted.

### Do I need to root my phone?
No! Works on non-rooted devices.

### Will it drain my battery?
If running on phone:
- Keep phone plugged in
- Battery will stay charged
- Enable "Stay Awake" in developer options

### Can I use my phone while tracker runs?
Yes, but:
- Tracker controls the Swiggy app
- You can use other apps
- Don't close Swiggy app manually

---

## Cloud Questions

### Is Oracle Cloud really free forever?
Yes! Oracle's Always Free tier never expires. No credit card charges.

### What if I exceed free tier limits?
Oracle won't charge without your explicit upgrade. Your services will just stop if you exceed limits (which is unlikely with this tracker).

### Can I use GitHub Actions?
Not for Android (no emulator support). You can:
- Use self-hosted runner
- Use browser automation (has issues)
- See: [[GitHub Actions]]

### Which cloud is best?
**Oracle Cloud** - Free forever, powerful enough for Android emulator.

---

## Troubleshooting Questions

### "Failed to connect to Appium"
**Check:**
1. Is Appium server running? (`appium`)
2. Is device connected? (`adb devices`)
3. Correct port? (default: 4723)

**Fix:** Restart Appium server

### "No products found"
**Possible causes:**
1. Location not set to Bangalore
2. Not logged into Swiggy app
3. App UI changed
4. Network issues

**Fix:** 
- Manually open app and verify
- Check location setting
- Update app

### "Could not find search box"
**Cause:** Website/app UI changed

**Fix:**
- Update to latest version
- Use Android method (more stable)
- Report issue on GitHub

### Browser page alignment issues
**Cause:** Website has loading problems

**Fix:** Use Android automation instead

### Tracker stops after some time
**Possible causes:**
1. Network disconnected
2. Device went to sleep
3. App crashed
4. Appium server stopped

**Fix:**
- Enable "Stay Awake"
- Check logs
- Restart tracker

---

## Performance Questions

### How much data does it use?
Approximately:
- 10-20 MB per check
- ~1-2 GB per day (checking every 5 min)

Use WiFi for best results.

### How much CPU/RAM does it need?
**Minimum:**
- 2GB RAM
- Dual-core CPU

**Recommended:**
- 4GB RAM
- Quad-core CPU

### Can I run multiple trackers?
Yes! You can:
- Track different categories
- Use multiple devices
- Run on multiple servers

### How to make it faster?
```python
# Reduce check interval
CHECK_INTERVAL = 180  # 3 minutes

# Fewer categories
SEARCH_QUERIES = ["snacks", "chocolate"]

# Less scrolling (edit code)
```

---

## Privacy & Security Questions

### Is my data safe?
- Tool runs locally on your device
- No data sent to third parties
- Telegram token stored locally
- Open source - you can audit code

### What data is collected?
- Product names and prices (saved locally)
- No personal information
- No payment details
- No Swiggy credentials

### Can Swiggy detect this?
The tool behaves like a normal user:
- Uses official app
- Normal browsing patterns
- Reasonable check intervals

To be safe:
- Don't check too frequently
- Use reasonable intervals (5+ minutes)
- Don't run multiple instances

### Should I use a separate Swiggy account?
Recommended but not required. Using a separate account:
- ✅ Keeps main account safe
- ✅ Isolates tracking activity
- ✅ Better for testing

---

## Contribution Questions

### Can I contribute?
Yes! Contributions welcome:
- Bug fixes
- New features
- Documentation
- Testing

See: [[Contributing Guide]]

### How do I report bugs?
1. Check [[Troubleshooting]] first
2. Search existing issues
3. Create new issue with:
   - Description
   - Steps to reproduce
   - Error messages
   - System info

### Can I request features?
Yes! Open an issue with:
- Feature description
- Use case
- Why it's useful

### How do I submit code?
1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## Miscellaneous Questions

### Why are some products not found?
Possible reasons:
- Out of stock
- Not available in your area
- Search query doesn't match
- App UI changed

### Can I track other cities?
Yes! Modify the location:
```python
# In Android tracker
# Change location in app manually

# In browser tracker
# Set location when prompted
```

### Does it work with Swiggy Food?
No, currently Instamart only. Food delivery has different structure.

### Can I track Blinkit/Zepto?
Not currently. Would need separate implementation for each platform.

### How accurate is price detection?
Very accurate for:
- ✅ Regular products
- ✅ Clear pricing

May have issues with:
- ❌ Dynamic pricing
- ❌ Personalized offers
- ❌ Location-specific prices

### What happens if Swiggy changes their app?
The tracker may break. Solutions:
- Update selectors in code
- Report issue on GitHub
- Wait for fix
- Contribute fix yourself

---

## Still Have Questions?

- Check [[Troubleshooting]]
- Search [GitHub Issues](https://github.com/hithesh0160/Swiggy-Instamart/issues)
- Ask in [Discussions](https://github.com/hithesh0160/Swiggy-Instamart/discussions)
- Open new issue

---

**Related Pages:**
- [[Quick Start Guide]]
- [[Troubleshooting]]
- [[Android Automation]]
- [[Free Cloud Options]]
