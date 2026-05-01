# Graph Report - D:\Swiggy Instamart  (2026-05-01)

## Corpus Check
- Large corpus: 335 files · ~1,082,209 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 115 nodes · 207 edges · 11 communities detected
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Swiggy Monitor Alert System|Swiggy Monitor Alert System]]
- [[_COMMUNITY_Amazon Deal Detection Concepts|Amazon Deal Detection Concepts]]
- [[_COMMUNITY_Documentation and Hosting|Documentation and Hosting]]
- [[_COMMUNITY_Amazon Scraper Pipeline|Amazon Scraper Pipeline]]
- [[_COMMUNITY_Price History and Change Tracking|Price History and Change Tracking]]
- [[_COMMUNITY_Amazon Tracker Core Class|Amazon Tracker Core Class]]
- [[_COMMUNITY_Alert Formatting and Output|Alert Formatting and Output]]
- [[_COMMUNITY_Swiggy Product Scraper|Swiggy Product Scraper]]
- [[_COMMUNITY_Telegram Message Splitting|Telegram Message Splitting]]
- [[_COMMUNITY_Price and Discount Extraction|Price and Discount Extraction]]
- [[_COMMUNITY_Summary Document|Summary Document]]

## God Nodes (most connected - your core abstractions)
1. `AmazonPriceTracker` - 24 edges
2. `Amazon Price Tracker (amazon_price_tracker.py)` - 19 edges
3. `README - Price Tracker Project Overview` - 13 edges
4. `Free Cloud Hosting Guide` - 10 edges
5. `Tracker Execution Logs` - 9 edges
6. `StateManager` - 8 edges
7. `Swiggy Android Tracker (swiggy_android_tracker.py)` - 8 edges
8. `AlertManager` - 7 edges
9. `Swiggy Instamart Price Tracker Guide` - 7 edges
10. `Telegram Bot Notifications` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Swiggy Android Tracker (swiggy_android_tracker.py)` --references--> `requests HTTP Library`  [INFERRED]
  docs/SWIGGY_GUIDE.md → requirements.txt
- `GitHub Actions CI/CD Workflow` --shares_data_with--> `Price History Tracking`  [INFERRED]
  README.md → docs/AMAZON_GUIDE.md
- `Manual Setup Guide` --references--> `Amazon Price Tracker (amazon_price_tracker.py)`  [INFERRED]
  MANUAL_SETUP.md → README.md
- `Amazon Price Tracker (amazon_price_tracker.py)` --references--> `Telegram Bot Notifications`  [EXTRACTED]
  README.md → docs/TELEGRAM_SETUP.md
- `Amazon Price Tracker (amazon_price_tracker.py)` --references--> `Playwright Web Scraping`  [INFERRED]
  README.md → requirements.txt

## Hyperedges (group relationships)
- **Amazon Deal Tracking Pipeline** — amazon_tracker, github_actions, telegram_bot, price_history, screenshot_debugging [EXTRACTED 1.00]
- **Free Hosting Options for 24/7 Tracking** — oracle_cloud, spare_phone, github_actions, aws_free_tier, gcp_free_tier [EXTRACTED 1.00]
- **Swiggy Instamart Tracking Methods** — swiggy_android_tracker, swiggy_browser_ext, appium, tampermonkey [EXTRACTED 1.00]

## Communities

### Community 0 - "Swiggy Monitor Alert System"
Cohesion: 0.15
Nodes (5): AlertManager, init(), PriceMonitor, startMonitor(), StateManager

### Community 1 - "Amazon Deal Detection Concepts"
Cohesion: 0.17
Nodes (21): Adaptive Discount Thresholds for Electronics, Amazon Fresh Grocery Scraping, Amazon Price Tracker (amazon_price_tracker.py), 31-Category Scraping Pipeline, Telegram Deal Alert Messages, Duplicate Deal Detection, Amazon Electronics Section (TV, Laptop, Smartphone), Amazon Lightning Deals (+13 more)

### Community 2 - "Documentation and Hosting"
Cohesion: 0.31
Nodes (17): Amazon.in Price Tracker Guide, Appium Android Automation, AWS Free Tier Hosting, Free Cloud Hosting Guide, Documentation Index, Google Cloud Free Tier Hosting, GitHub Actions CI/CD Workflow, Oracle Cloud Free Tier Hosting (+9 more)

### Community 3 - "Amazon Scraper Pipeline"
Cohesion: 0.21
Nodes (6): Scrape deals from a specific page, Check if product qualifies as a deal, Scrape deals from multiple sources, Scrape electronics with adaptive discount threshold, Scrape deals from all configured categories, Scrape deals from Amazon Fresh categories

### Community 4 - "Price History and Change Tracking"
Cohesion: 0.22
Nodes (5): Mark ALL identified new deals and price drops as 'alerted' in price history, Generate a consistent product key: ASIN-based if possible, else Name-based, Check if this is a new deal or price drop, Update price history for a product, Analyze and categorize deals

### Community 5 - "Amazon Tracker Core Class"
Cohesion: 0.28
Nodes (4): AmazonPriceTracker, Load and migrate price history to a unified key system, Extract discount percentage, Normalize product name for consistent matching, removing dynamic parts

### Community 6 - "Alert Formatting and Output"
Cohesion: 0.29
Nodes (3): Format category name for display, Send summary via Telegram, Save results to files

### Community 7 - "Swiggy Product Scraper"
Cohesion: 0.4
Nodes (1): ProductScraper

### Community 8 - "Telegram Message Splitting"
Cohesion: 0.5
Nodes (2): Split a long message into chunks at safe points (after complete deal entries), Send alert via Telegram (splits into multiple messages if needed)

### Community 9 - "Price and Discount Extraction"
Cohesion: 1.0
Nodes (1): Extract price from text

### Community 11 - "Summary Document"
Cohesion: 1.0
Nodes (1): Summary Document

## Knowledge Gaps
- **23 isolated node(s):** `Load and migrate price history to a unified key system`, `Split a long message into chunks at safe points (after complete deal entries)`, `Send alert via Telegram (splits into multiple messages if needed)`, `Extract price from text`, `Extract discount percentage` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Swiggy Product Scraper`** (5 nodes): `ProductScraper`, `.constructor()`, `.extractPrice()`, `.generateProductId()`, `.scrapeProducts()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Telegram Message Splitting`** (4 nodes): `.send_telegram_alert()`, `.split_message()`, `Split a long message into chunks at safe points (after complete deal entries)`, `Send alert via Telegram (splits into multiple messages if needed)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Price and Discount Extraction`** (2 nodes): `.extract_price()`, `Extract price from text`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Summary Document`** (1 nodes): `Summary Document`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AmazonPriceTracker` connect `Amazon Tracker Core Class` to `Amazon Scraper Pipeline`, `Price History and Change Tracking`, `Alert Formatting and Output`, `Telegram Message Splitting`, `Price and Discount Extraction`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `Amazon Price Tracker (amazon_price_tracker.py)` connect `Amazon Deal Detection Concepts` to `Documentation and Hosting`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `README - Price Tracker Project Overview` connect `Documentation and Hosting` to `Amazon Deal Detection Concepts`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Amazon Price Tracker (amazon_price_tracker.py)` (e.g. with `Playwright Web Scraping` and `Manual Setup Guide`) actually correct?**
  _`Amazon Price Tracker (amazon_price_tracker.py)` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Load and migrate price history to a unified key system`, `Split a long message into chunks at safe points (after complete deal entries)`, `Send alert via Telegram (splits into multiple messages if needed)` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._