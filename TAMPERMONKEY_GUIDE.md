# Tampermonkey Price Monitor Guide

The easiest way to monitor Swiggy Instamart prices - runs directly in your browser!

## 🌟 Why Tampermonkey?

### Advantages
- ✅ **Easiest setup** - Just install and browse
- ✅ **No servers needed** - Runs in your browser
- ✅ **Stealthy** - Behaves like a real user
- ✅ **No Android required** - Works on any browser
- ✅ **Automatic** - Monitors while you browse
- ✅ **Free** - No hosting costs

### How It Works
1. You browse Swiggy Instamart normally
2. Script automatically scrapes visible products
3. Checks for deals (under ₹50 or >70% discount)
4. Sends browser/Telegram notifications
5. Runs periodically (12-25 min intervals, randomized)

---

## 📦 Installation

### Step 1: Install Tampermonkey

**Chrome/Edge:**
- Install from: https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo

**Firefox:**
- Install from: https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/

**Safari:**
- Install from: https://apps.apple.com/app/tampermonkey/id1482490089

### Step 2: Install the Script

1. Click the Tampermonkey icon in your browser
2. Click "Create a new script"
3. Delete the default code
4. Copy the entire content from `swiggy-price-monitor.user.js`
5. Paste into the editor
6. Press `Ctrl+S` (or `Cmd+S` on Mac) to save

### Step 3: Configure (Optional)

Edit these lines in the script:

```javascript
const CONFIG = {
    // Telegram settings (optional)
    telegram: {
        botToken: 'YOUR_BOT_TOKEN_HERE',  // Your bot token
        chatId: 'YOUR_CHAT_ID_HERE',      // Your chat ID
        enabled: false                     // Set to true to enable
    },

    // Alert settings
    alerting: {
        condition: {
            price_drop_percentage: 70,     // Alert for >70% discount
            price_threshold: 50            // Alert for products under ₹50
        },
        cooldown_minutes: 30               // Wait 30 min between alerts for same product
    },

    // Limits
    limits: {
        max_alerts_per_day: 10,           // Max 10 alerts per day
        stop_if_errors: 3                  // Stop after 3 consecutive errors
    }
};
```

---

## 🚀 Usage

### Automatic Mode (Default)

1. Open Swiggy Instamart: https://www.swiggy.com/instamart
2. Browse normally (search, scroll, etc.)
3. Script runs automatically every 12-25 minutes
4. Get notifications for deals

### Manual Mode

1. Look for the "🔥 Price Monitor" panel (bottom-right corner)
2. Click "Check Now" button
3. View results in browser console (F12)

### View Results

Press `F12` to open browser console and see:
- Products found
- Deals detected
- Alerts sent
- Summary statistics

---

## ⚙️ Configuration Options

### Monitoring Frequency

```javascript
trigger: {
    frequency: {
        min_minutes: 12,      // Minimum interval
        max_minutes: 25,      // Maximum interval
        randomize: true       // Random interval (more human-like)
    }
}
```

**Recommended:** Keep randomized to avoid detection

### Alert Conditions

```javascript
alerting: {
    condition: {
        price_drop_percentage: 70,  // Discount threshold
        price_threshold: 50         // Price threshold
    }
}
```

**Examples:**
- `price_threshold: 30` - Alert for products under ₹30
- `price_drop_percentage: 80` - Alert for >80% discounts

### Products Per Session

```javascript
scope: {
    max_products_per_session: 20  // Scrape max 20 products per check
}
```

**Why limit?**
- Faster execution
- Less resource usage
- More stealthy

### Daily Limits

```javascript
limits: {
    max_alerts_per_day: 10,  // Max alerts per day
    stop_if_errors: 3        // Stop after errors
}
```

**Prevents:**
- Notification spam
- Excessive API calls
- Running on error

---

## 📱 Telegram Setup (Optional)

### Step 1: Create Bot

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow instructions
5. Save the bot token

### Step 2: Get Chat ID

1. Start chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find `chat_id` in JSON

### Step 3: Enable in Script

```javascript
telegram: {
    botToken: '123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
    chatId: '123456789',
    enabled: true  // Set to true
}
```

---

## 🎯 Features

### Detection Safety

The script is designed to be undetectable:

```javascript
detection_safety: {
    browser_context: 'real_user',      // Uses real browser context
    cookies: 'reuse_existing',         // Reuses your cookies
    local_storage: 'enabled',          // Uses local storage
    devtools_hooks: 'read_only'        // Read-only access
}
```

**What this means:**
- ✅ Uses your existing login
- ✅ Behaves like normal browsing
- ✅ No suspicious patterns
- ✅ Randomized timing

### Network Rules

```javascript
network_rules: {
    allow_only: ['same_origin_requests'],  // Only Swiggy requests
    deny: ['forced_refresh', 'background_spam_calls']
}
```

**Benefits:**
- No external requests (except Telegram)
- No forced page refreshes
- No background spam

### Smart Cooldown

```javascript
cooldown_minutes: 30  // Wait 30 min before alerting same product again
```

**Prevents:**
- Duplicate alerts
- Notification spam
- Alert fatigue

---

## 📊 Monitoring Dashboard

### Console Output

Press `F12` and check console for:

```
[Monitor] Starting price check...
[Scraper] Found 45 products using: [data-testid*="product"]
[Scraper] Extracted 20 products
[Alert] 🔥 PRICE ALERT!
Product: Chocolate Bar
Current Price: ₹9
Original Price: ₹50
Discount: 82%

============================================================
SWIGGY INSTAMART PRICE MONITOR - SUMMARY
============================================================
Total Products: 20
Products under ₹50: 8
High Discounts (>70%): 3
Alerts Sent: 3
============================================================

🔥 CHEAP PRODUCTS:
1. Chocolate Bar - ₹9 (82% off)
2. Biscuits Pack - ₹15 (75% off)
3. Bread Loaf - ₹25 (17% off)
...
```

### Control Panel

Bottom-right corner shows:
- 🔥 Price Monitor
- "Check Now" button
- Status indicator

---

## 🐛 Troubleshooting

### Script Not Running

**Check:**
1. Is Tampermonkey enabled?
2. Is script enabled in Tampermonkey dashboard?
3. Are you on `swiggy.com/instamart`?

**Fix:**
- Click Tampermonkey icon
- Ensure script is enabled
- Refresh page

### No Products Found

**Possible causes:**
1. Page not fully loaded
2. Different page structure
3. No products visible

**Fix:**
- Wait for page to load completely
- Scroll to see products
- Check console for errors

### Telegram Not Working

**Check:**
1. Is `enabled: true`?
2. Correct bot token?
3. Correct chat ID?

**Fix:**
- Test bot manually
- Check token/ID
- View console for errors

### Too Many/Few Alerts

**Adjust:**
```javascript
// More alerts
price_threshold: 100  // Higher threshold
price_drop_percentage: 50  // Lower discount requirement

// Fewer alerts
price_threshold: 20  // Lower threshold
price_drop_percentage: 80  // Higher discount requirement
```

---

## 🔒 Privacy & Security

### What Data is Collected?

**Stored locally:**
- Product names and prices
- Alert history
- Error counts

**Never sent anywhere:**
- Your Swiggy credentials
- Personal information
- Browsing history

**Only sent to Telegram (if enabled):**
- Product deals (name, price, discount)

### Is It Safe?

✅ **Yes!**
- Runs in your browser
- Uses your existing session
- No external servers
- Open source code
- You control everything

### Can Swiggy Detect It?

**Very unlikely:**
- Uses real browser context
- Randomized timing
- Normal browsing patterns
- No suspicious requests
- Read-only access

**Best practices:**
- Don't check too frequently
- Keep randomization enabled
- Use reasonable limits

---

## 💡 Tips & Tricks

### Maximize Deals

1. **Browse different categories**
   - Snacks
   - Groceries
   - Personal care
   - Household items

2. **Check at different times**
   - Morning (8-10 AM)
   - Afternoon (2-4 PM)
   - Evening (6-8 PM)
   - Late night (10-12 PM)

3. **Search specific items**
   - "chocolate"
   - "biscuits"
   - "bread"

### Optimize Performance

```javascript
// Faster checks
max_products_per_session: 10  // Fewer products

// Less frequent
min_minutes: 20
max_minutes: 40

// More alerts
max_alerts_per_day: 20
```

### Multiple Browsers

Run on multiple browsers simultaneously:
- Chrome (work)
- Firefox (personal)
- Edge (backup)

Each runs independently!

---

## 🆚 Comparison with Other Methods

| Feature | Tampermonkey | Android | Browser Automation |
|---------|--------------|---------|-------------------|
| Setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Reliability | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Stealth | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Cost | Free | Free | Free |
| 24/7 | ❌ | ✅ | ✅ |
| Automatic | ✅ | ✅ | ✅ |

**Best for:**
- **Tampermonkey**: Casual monitoring while browsing
- **Android**: 24/7 dedicated monitoring
- **Browser Automation**: Testing/development

---

## 🔗 Related

- **[[Android Automation]]** - For 24/7 monitoring
- **[[Free Cloud Options]]** - For cloud hosting
- **[[FAQ]]** - Common questions

---

## 📝 Advanced Customization

### Custom Alert Logic

```javascript
shouldAlert(product) {
    // Custom conditions
    if (product.name.includes('chocolate') && product.price < 20) {
        return true;
    }
    
    if (product.discount > 80) {
        return true;
    }
    
    return false;
}
```

### Track Specific Brands

```javascript
const TRACKED_BRANDS = ['amul', 'britannia', 'nestle'];

shouldAlert(product) {
    const hasTrackedBrand = TRACKED_BRANDS.some(brand => 
        product.name.toLowerCase().includes(brand)
    );
    
    return hasTrackedBrand && product.discount > 50;
}
```

### Price History

```javascript
// Store price history
const priceHistory = GM_getValue('price_history', {});

// Track price changes
if (priceHistory[product.id]) {
    const oldPrice = priceHistory[product.id];
    if (product.price < oldPrice) {
        // Price dropped!
        alert(`Price drop: ${product.name} from ₹${oldPrice} to ₹${product.price}`);
    }
}

priceHistory[product.id] = product.price;
GM_setValue('price_history', priceHistory);
```

---

**Ready to start?** Install Tampermonkey and add the script!
