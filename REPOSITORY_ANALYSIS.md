# Repository Analysis - Swiggy Instamart & Amazon Price Tracker

**Generated:** January 24, 2026  
**Repository:** Swiggy Instamart Price Tracker

---

## 📋 Executive Summary

This repository contains a comprehensive price tracking system for two major Indian e-commerce platforms:
1. **Amazon.in** - Automated deal tracking via GitHub Actions
2. **Swiggy Instamart** - Multiple tracking methods (Android automation, browser extension, web scraping)

The project is designed to automatically detect deep discounts, pricing errors, and price drops, then send notifications via Telegram.

---

## 🏗️ Project Structure

### Core Components

#### **Amazon Tracker**
- **File:** `amazon_price_tracker.py` (671 lines)
- **Purpose:** Scrapes Amazon deals and tracks price history
- **Deployment:** GitHub Actions (runs twice daily)
- **Features:**
  - Scrapes Today's Deals, Lightning Deals, Electronics
  - Smart duplicate detection using ASIN/product keys
  - Price history tracking (JSON-based)
  - Adaptive discount thresholds for electronics
  - Screenshot capture for debugging
  - Telegram notifications

#### **Swiggy Trackers** (Multiple Implementations)

1. **Android Automation** (`swiggy_android_tracker.py` - 395 lines)
   - Uses Appium for Android app automation
   - Most reliable method
   - Requires physical device/emulator

2. **Web Scraping** (`swiggy_instamart_tracker.py` - 572 lines)
   - Uses Playwright for browser automation
   - Accessibility snapshot parsing
   - HTML fallback parsing

3. **Stealth Tracker** (`swiggy_stealth_tracker.py` - 421 lines)
   - Enhanced bot detection bypass
   - Human-like typing simulation
   - Stealth browser configuration

4. **Browser Extension** (`swiggy-price-monitor.user.js` - 553 lines)
   - Tampermonkey userscript
   - Runs in browser context
   - Real-time monitoring while browsing

#### **MCP-Based Tools** (Model Context Protocol)

1. **Deal Hunter** (`swiggy_deal_hunter_mcp.py` - 222 lines)
   - Parses Playwright MCP snapshots
   - Calculates discounts and savings
   - Generates comprehensive reports

2. **Discount Finder** (`swiggy_discount_finder_mcp.py` - 176 lines)
   - Extracts products from MCP snapshots
   - Finds high discounts and pricing errors

3. **All Categories Scanner** (`swiggy_all_categories_scanner.py` - 360 lines)
   - Scans 8 product categories
   - 151+ search queries
   - Generates master reports

4. **Auto Scanner** (`auto_scan_all_categories.py` - 201 lines)
   - Automated workflow for category scanning
   - MCP execution guide

5. **Kodathi Scanner** (`swiggy_kodathi_scanner.py` - 179 lines)
   - Location-specific scanner (Kodathi, Bangalore)
   - Sample data analysis

6. **MCP Deal Finder** (`swiggy_mcp_deal_finder.py` - 141 lines)
   - Complete MCP workflow guide
   - Integration instructions

7. **Deal Extractor** (`extract_swiggy_deals.py` - 265 lines)
   - Standalone extraction from snapshot data
   - Quick analysis tool

---

## 📊 Key Features

### Amazon Tracker Features
- ✅ **Smart Duplicate Detection:** Uses ASIN + normalized product names
- ✅ **Price History Tracking:** JSON-based persistence
- ✅ **Adaptive Electronics Filtering:** Dynamic discount thresholds
- ✅ **New Deal Detection:** Only alerts on new products or significant price drops (>20%)
- ✅ **Screenshot Capture:** Debugging and verification
- ✅ **Multiple Data Sources:** Today's Deals, Lightning Deals, custom searches
- ✅ **Telegram Integration:** HTML-formatted alerts

### Swiggy Tracker Features
- ✅ **Multiple Implementation Methods:** Android, Web, Extension
- ✅ **Pricing Error Detection:** Flags 70%+ discounts as potential errors
- ✅ **Category Scanning:** 8 categories, 151+ search queries
- ✅ **Value Score Calculation:** Combines discount % and absolute savings
- ✅ **MCP Integration:** Playwright MCP for browser automation
- ✅ **Location-Specific:** Supports different delivery locations

---

## 🔧 Technology Stack

### Languages & Frameworks
- **Python 3.8+** - Main language
- **Playwright** - Browser automation
- **Appium** - Android automation
- **JavaScript** - Browser extension (Tampermonkey)

### Dependencies
```
requests==2.31.0
playwright==1.40.0
```

### Node.js Dependencies
```json
{
  "devDependencies": {
    "@playwright/mcp": "^0.0.58",
    "@playwright/test": "^1.58.0"
  }
}
```

### Infrastructure
- **GitHub Actions** - CI/CD and scheduled execution
- **Telegram Bot API** - Notifications
- **JSON Files** - Data persistence (price history, deals)

---

## 📁 File Organization

### Configuration Files
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `.gitignore` - Git ignore rules
- `.github/workflows/amazon-price-tracker.yml` - GitHub Actions workflow

### Data Files (Generated)
- `amazon_deals.json` - All Amazon deals
- `amazon_deals_new.json` - New/changed deals only
- `price_history.json` - Amazon price history
- `price_changes.json` - Price change summary
- `swiggy_deals.json` - Swiggy deals
- `swiggy_price_history.json` - Swiggy price history
- `scraped_products.json` - Android tracker output

### Documentation
- `README.md` - Main project overview
- `docs/` - Comprehensive guides:
  - `AMAZON_GUIDE.md` - Amazon setup guide
  - `SWIGGY_GUIDE.md` - Swiggy setup guide
  - `TELEGRAM_SETUP.md` - Telegram configuration
  - `CLOUD_HOSTING.md` - Free hosting options
  - `TROUBLESHOOTING.md` - Common issues
  - `SUMMARY.md` - Documentation index

---

## 🎯 Use Cases

### 1. Daily Deal Hunter
- Run Amazon tracker 2x daily for morning/evening deals
- Get alerts for new products and price drops

### 2. Grocery Saver
- Use Swiggy browser extension while shopping
- Get real-time alerts for pricing errors

### 3. 24/7 Monitor
- Setup Swiggy on spare phone + Amazon on GitHub Actions
- Continuous monitoring without manual intervention

### 4. Category Scanner
- Scan all product categories for comprehensive deal analysis
- Generate master reports with best deals across categories

---

## 🔍 Code Quality Analysis

### Strengths
1. **Modular Design:** Separate trackers for different platforms/methods
2. **Error Handling:** Try-catch blocks and fallback mechanisms
3. **Configuration:** Centralized config objects
4. **Documentation:** Comprehensive guides and inline comments
5. **Multiple Approaches:** Different methods for different use cases
6. **Data Persistence:** JSON-based storage for price history

### Areas for Improvement
1. **Code Duplication:** Similar logic across multiple Swiggy trackers
2. **Error Recovery:** Limited retry mechanisms
3. **Testing:** No unit tests visible
4. **Logging:** Basic print statements instead of proper logging
5. **Configuration Management:** Hardcoded values in some files
6. **Type Hints:** Limited use of type annotations

### Technical Debt
- Multiple Swiggy tracker implementations with overlapping functionality
- Some files appear to be experimental/development versions
- MCP tools seem to be newer additions, integration could be cleaner

---

## 📈 Functionality Breakdown

### Amazon Tracker (`amazon_price_tracker.py`)

**Key Classes:**
- `AmazonPriceTracker` - Main tracker class

**Key Methods:**
- `scrape_all_deals()` - Orchestrates scraping from multiple sources
- `scrape_deals_page()` - Scrapes individual pages
- `scrape_electronics_adaptive()` - Adaptive electronics filtering
- `check_price_change()` - Detects new deals and price drops
- `analyze_deals()` - Categorizes and filters deals
- `send_summary_alert()` - Sends Telegram notifications

**Data Flow:**
1. Scrape deals from multiple Amazon pages
2. Extract product data (name, price, discount, ASIN, link)
3. Check against price history
4. Identify new deals and price drops
5. Filter by thresholds
6. Send Telegram alerts
7. Save results to JSON files

### Swiggy Android Tracker (`swiggy_android_tracker.py`)

**Key Classes:**
- `SwiggyAndroidTracker` - Android automation tracker

**Key Methods:**
- `setup_driver()` - Initialize Appium connection
- `navigate_to_instamart()` - Navigate to Instamart section
- `search_products()` - Search and scrape products
- `scrape_current_screen()` - Extract products from current screen
- `check_prices()` - Analyze and alert on deals

**Data Flow:**
1. Connect to Android device via Appium
2. Navigate to Swiggy Instamart
3. Search for configured categories
4. Scrape product data from screen
5. Check for deals (price threshold or discount %)
6. Send Telegram alerts
7. Save to JSON file

### Swiggy Deal Hunter MCP (`swiggy_deal_hunter_mcp.py`)

**Key Classes:**
- `SwiggyDealHunter` - MCP-based deal analysis

**Key Methods:**
- `parse_snapshot_yaml()` - Parse Playwright accessibility snapshots
- `calculate_metrics()` - Calculate discounts and value scores
- `categorize_deals()` - Categorize by discount level
- `generate_report()` - Generate formatted reports

**Categories:**
- Pricing Errors: 70%+ discount
- High Discounts: 50-69%
- Good Deals: 30-49%
- Moderate Deals: 15-29%

---

## 🔐 Security & Privacy

### Current State
- Telegram tokens stored as environment variables (GitHub Secrets)
- No hardcoded credentials in code
- `.gitignore` properly configured for sensitive files

### Recommendations
- Consider using encrypted storage for price history
- Add rate limiting for API calls
- Implement request throttling
- Add user authentication for local deployments

---

## 🚀 Deployment Options

### Amazon Tracker
- **Primary:** GitHub Actions (free tier)
- **Schedule:** Twice daily (9 AM & 9 PM IST)
- **Manual Trigger:** Available via GitHub UI
- **Storage:** GitHub repository (commits price history)

### Swiggy Tracker
1. **Android:** Physical device or emulator
2. **Browser Extension:** Tampermonkey (user-side)
3. **Web Automation:** Local machine or cloud VM
4. **Cloud Options:** Oracle Cloud (free tier), spare phone

---

## 📊 Data Models

### Product Structure
```python
{
    'name': str,              # Product name
    'price': float,          # Current price
    'mrp': float,            # Original/MRP price
    'discount': float,        # Discount percentage
    'asin': str,              # Amazon ASIN (if applicable)
    'link': str,              # Product URL
    'image': str,             # Product image URL
    'rating': str,            # Product rating
    'category': str,          # Product category
    'timestamp': str,         # ISO timestamp
    'is_deal': bool,          # Qualifies as deal
    'change_type': str,       # 'new', 'price_drop', 'same', 'minor_drop'
    'old_price': float,      # Previous price (if price drop)
    'price_drop_pct': float   # Price drop percentage
}
```

### Price History Structure
```python
{
    'product_key': {
        'name': str,
        'price': float,
        'discount': float,
        'last_seen': str,     # ISO timestamp
        'asin': str
    }
}
```

---

## 🐛 Known Issues & Limitations

### Amazon Tracker
- Screenshots saved to repository (storage concern)
- Limited to 30 products per search (configurable)
- May miss deals if Amazon changes page structure
- Rate limiting not implemented

### Swiggy Trackers
- Website scraping is less reliable than Android
- Browser extension requires manual browsing
- Android method requires device/emulator
- MCP tools require Playwright MCP setup

### General
- No database (JSON files only)
- No retry mechanisms for failed requests
- Limited error recovery
- No monitoring/alerting for tracker failures

---

## 🔮 Future Enhancements

### Suggested Improvements
1. **Unified Tracker Interface:** Single interface for all trackers
2. **Database Integration:** Replace JSON with SQLite/PostgreSQL
3. **Web Dashboard:** Visual interface for deals and history
4. **Email Notifications:** Alternative to Telegram
5. **Price Prediction:** ML-based price forecasting
6. **Multi-Platform:** Add Flipkart, Myntra support
7. **API Endpoints:** REST API for external integrations
8. **Scheduled Reports:** Daily/weekly summary emails
9. **Price Alerts:** Set custom price targets
10. **Wishlist Tracking:** Track specific products

---

## 📝 Documentation Quality

### Strengths
- Comprehensive setup guides
- Multiple deployment options documented
- Troubleshooting guide included
- Clear step-by-step instructions
- Examples and code snippets

### Coverage
- ✅ Amazon setup
- ✅ Swiggy setup (multiple methods)
- ✅ Telegram configuration
- ✅ Cloud hosting options
- ✅ Troubleshooting
- ✅ Quick start guides

---

## 🎓 Learning Resources

The codebase demonstrates:
- Web scraping with Playwright
- Android automation with Appium
- Browser extension development
- GitHub Actions workflows
- Telegram bot integration
- Data persistence strategies
- Price tracking algorithms
- MCP (Model Context Protocol) integration

---

## 📊 Statistics

### Code Metrics
- **Total Python Files:** 12
- **Total Lines of Code:** ~4,500+
- **Main Trackers:** 2 (Amazon, Swiggy)
- **Swiggy Implementations:** 7 variations
- **Documentation Files:** 6 guides
- **Configuration Files:** 4

### Feature Count
- **Tracking Methods:** 4 (GitHub Actions, Android, Browser, Extension)
- **Notification Channels:** 1 (Telegram)
- **Data Sources:** Multiple (Amazon deals pages, Swiggy search)
- **Categories Scanned:** 8 (Swiggy)
- **Search Queries:** 151+ (Swiggy)

---

## ✅ Conclusion

This is a well-structured price tracking system with multiple implementation approaches. The code demonstrates good understanding of web scraping, automation, and notification systems. The project is actively maintained with comprehensive documentation.

**Key Strengths:**
- Multiple implementation methods
- Comprehensive documentation
- Free deployment options
- Smart duplicate detection
- Price history tracking

**Recommendations:**
- Consolidate duplicate Swiggy tracker code
- Add proper logging framework
- Implement retry mechanisms
- Add unit tests
- Consider database for scalability

---

**Analysis Date:** January 24, 2026  
**Analyzer:** AI Code Analysis Tool
