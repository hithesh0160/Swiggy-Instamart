#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon.in Price Tracker for GitHub Actions
Monitors Amazon deals and sends Telegram notifications
"""

import os
import sys
import json
import csv
import time
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import requests
import re
from pathlib import Path

# Fix Windows Unicode encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SEARCH_QUERY = os.getenv('SEARCH_QUERY', '')

# Tracking configuration
CONFIG = {
    'price_threshold': 500,  # Alert for products under ₹500
    'discount_threshold': 50,  # Alert for >50% discount
    'price_drop_threshold': 20,  # Alert if price drops by >20%
    'max_products': 20,  # Reduced to handle many categories efficiently
    'only_new_deals': True,  # Only alert on NEW deals or price drops
    'telegram_deals_per_category': 15,  # Number of deals to show per category in Telegram (max 4096 chars)
    'categories': [
        # Electronics & Computers
        'electronics',
        'smartphones',
        'laptops',
        'tablets',
        'headphones',
        'televisions',
        'smart-home',
        'gaming',
        
        # Fashion & Apparel
        'fashion',
        'mens-clothing',
        'footwear',
        'watches',
        
        # Home & Kitchen
        'home',
        'kitchen',
        'furniture',
        'home-decor',
        'garden',
        'tools',
        
        # Clothing & Apparel
        'shirts',
        'tshirts',
        'sweatshirts',
        'hoodies',
                        
        # Sports & Outdoors
        'sports',
        'outdoor',
        'fitness',
        
        # Grocery & Food
        'grocery',
        'food',
        'beverages',
        'snacks',
        
        # Automotive
        'automotive',
        
        # Toys & Games
        'toys',
        'games',
        
        # Office & Stationery
        'office-products',
        'stationery',
        
        # Musical Instruments
        'Guitar',
    ],
    'amazon_fresh_categories': [
        # Fresh Produce
        'fruits',
        'vegetables',
        
        # Dairy & Eggs
        'dairy-products',
        'milk',
        'eggs',
        'cheese',
        'butter',
        'yogurt',
                
        # Bakery
        'cakes',
        'pastries',
        
        # Beverages
        'fresh-juices',
        'soft-drinks',
        
        # Snacks & Sweets
        'chocolates',
        'biscuits',
        'chips',
        'nuts',
        'dry-fruits',
        
        # Frozen Foods
        'ice-cream',
        
        # Pantry Staples
        'rice',
        
        # Personal Care (Fresh section)
        'fresh-personal-care',
        
        # Household Essentials
        'fresh-household',
        'cleaning-supplies',
        
        # Clothing in Fresh (if any)
        'shirts',
        'tshirts',
        'sweatshirts',
        'hoodies',
    ],
    'history_max_age_days': 90,  # Purge products not seen in 90 days
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
        'min_discount': 20,  # Start with 20% discount
        'max_discount': 60,  # Try up to 60%
        'discount_step': 10,  # Reduce by 10% each time
        'min_products': 5,   # Need at least 5 products
        'max_price': 50000   # Electronics can be expensive
    }
}

class AmazonPriceTracker:
    def __init__(self):
        self.deals = []
        self.price_history = self.load_price_history()
        self.new_deals = []
        self.price_drops = []
        self.screenshots_dir = Path('screenshots')
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def load_price_history(self):
        """Load and migrate price history to a unified key system"""
        history_file = Path('price_history.json')
        if not history_file.exists():
            return {}
            
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Load all and normalize keys
            raw_entries = []
            for k, v in history.items():
                # Extract clean ASIN if the key is just an ASIN or has asin_ prefix
                clean_key = k
                if k.startswith('asin_'):
                    clean_key = k[5:]
                elif k.startswith('name_'):
                    pass # Keep as is
                else:
                    # Check if it's a raw ASIN (usually 10 chars, alphanumeric)
                    if len(k) == 10 and k.isalnum():
                         pass # Keep as is (clean_key is raw ASIN)
                
                raw_entries.append((clean_key, v))

            # Migrate to unified keys: asin_{asin} (priority) or name_{norm_name}
            migrated = {}
            for old_key, data in raw_entries:
                # Determine the best unified key for this entry
                asin = data.get('asin') or (old_key if (len(old_key) == 10 and old_key.isalnum()) else None)
                name = data.get('name', '')
                
                if asin:
                    new_key = f"asin_{asin}"
                elif name:
                    new_key = f"name_{self.normalize_name(name)[:120]}"
                else:
                    new_key = old_key if old_key.startswith('name_') else f"name_{old_key}"
                
                # Merge logic: if we have multiple existing entries for the same product
                if new_key in migrated:
                    # Keep the alerted=True status if it exists in either
                    already_alerted = data.get('alerted', False) or migrated[new_key].get('alerted', False)
                    migrated[new_key]['alerted'] = already_alerted
                    # Keep the most recent last_seen
                    if data.get('last_seen', '') > migrated[new_key].get('last_seen', ''):
                        migrated[new_key]['last_seen'] = data.get('last_seen')
                        migrated[new_key]['price'] = data.get('price')
                else:
                    # Ensure alerted exists and is boolean
                    data['alerted'] = data.get('alerted', False)
                    migrated[new_key] = data
            
            # Purge old entries not seen in max_age_days
            max_age = CONFIG.get('history_max_age_days', 90)
            cutoff = (datetime.now() - timedelta(days=max_age)).isoformat()
            old_count = 0
            purged = {k: v for k, v in migrated.items() if v.get('last_seen', '') >= cutoff}
            old_count = len(migrated) - len(purged)
            if old_count > 0:
                print(f"Purged {old_count} entries older than {max_age} days")
                migrated = purged
            
            return migrated
        except Exception as e:
            print(f"Could not load price history: {e}")
            return {}
    
    def save_price_history(self):
        """Save price history"""
        try:
            with open('price_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.price_history, f, indent=2, ensure_ascii=False)
            print("✓ Price history saved")
        except Exception as e:
            print(f"Error saving price history: {e}")
        
    def split_message(self, message, max_length=4000):
        """Split a long message into chunks at safe points (after complete deal entries)"""
        if len(message) <= max_length:
            return [message]
        
        chunks = []
        current_pos = 0
        message_length = len(message)
        
        while current_pos < message_length:
            # Calculate remaining length
            remaining = message_length - current_pos
            
            if remaining <= max_length:
                # Last chunk - take everything remaining
                chunk = message[current_pos:]
                chunks.append(chunk)
                break
            
            # Find a safe split point (after a complete deal entry)
            # Look for the end of a deal entry (after </a> tag and newline)
            search_end = current_pos + max_length
            safe_split = -1
            
            # Look backwards from max_length for a safe split point
            for i in range(search_end, current_pos + max_length - 200, -1):
                if i >= len(message):
                    continue
                # Check if we're at the end of a deal entry
                # Pattern: </a>\n or \n\n (double newline between deals)
                if i + 1 < len(message):
                    if message[i:i+4] == '</a>' and (i+4 >= len(message) or message[i+4] == '\n'):
                        # Found end of a deal, find the next newline
                        next_nl = message.find('\n', i + 4)
                        if next_nl > 0:
                            safe_split = next_nl + 1
                            break
                    elif i > 0 and message[i-1:i+1] == '\n\n':
                        # Double newline - safe to split here
                        safe_split = i + 1
                        break
            
            # If no safe split found, find last newline
            if safe_split == -1:
                safe_split = message.rfind('\n', current_pos, current_pos + max_length)
                if safe_split == -1:
                    # Last resort: split at max_length
                    safe_split = current_pos + max_length
            
            # Extract chunk
            chunk = message[current_pos:safe_split]
            
            # Close any open HTML tags in this chunk
            open_b_tags = chunk.count('<b>') - chunk.count('</b>')
            open_a_tags = chunk.count('<a') - chunk.count('</a>')
            
            # Close open tags in reverse order
            for _ in range(open_a_tags):
                chunk += '</a>'
            for _ in range(open_b_tags):
                chunk += '</b>'
            
            chunks.append(chunk)
            current_pos = safe_split
            
            # Add continuation header for subsequent chunks
            if current_pos < message_length:
                chunk_header = f"\n\n📄 <b>Continued...</b> (Part {len(chunks) + 1})\n"
                # Adjust current_pos to account for header in next chunk
                # We'll prepend it to the next chunk instead
        
        # Add part numbers to chunks (except first)
        for i in range(1, len(chunks)):
            chunks[i] = f"📄 <b>Part {i + 1} of {len(chunks)}</b>\n\n" + chunks[i]
        
        return chunks
    
    def send_telegram_alert(self, message):
        """Send alert via Telegram (splits into multiple messages if needed)"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠ Telegram not configured, skipping notification")
            print(f"   TELEGRAM_BOT_TOKEN: {'Set' if TELEGRAM_BOT_TOKEN else 'NOT SET'}")
            print(f"   TELEGRAM_CHAT_ID: {'Set' if TELEGRAM_CHAT_ID else 'NOT SET'}")
            return
        
        # Split message if too long
        TELEGRAM_MAX_LENGTH = 4096
        chunks = self.split_message(message, max_length=TELEGRAM_MAX_LENGTH - 100)
        
        if len(chunks) > 1:
            print(f"📤 Splitting message into {len(chunks)} parts ({len(message)} total chars)...")
        
        # Send each chunk
        for i, chunk in enumerate(chunks, 1):
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': chunk,
                    'parse_mode': 'HTML'
                }
                print(f"📤 Sending Telegram message part {i}/{len(chunks)} ({len(chunk)} chars)...")
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        print(f"✓ Telegram message part {i}/{len(chunks)} sent successfully")
                        # Small delay between messages to avoid rate limiting
                        if i < len(chunks):
                            time.sleep(0.5)
                    else:
                        print(f"✗ Telegram API error in part {i}: {result.get('description', 'Unknown error')}")
                        break
                else:
                    print(f"✗ Telegram HTTP error in part {i}: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"✗ Network error sending Telegram part {i}: {e}")
                break
            except Exception as e:
                print(f"✗ Error sending Telegram part {i}: {e}")
                import traceback
                traceback.print_exc()
                break
    
    def extract_price(self, text):
        """Extract price from text"""
        import re
        matches = re.findall(r'₹\s*([0-9,]+(?:\.\d+)?)', text)
        if matches:
            price_str = matches[0].replace(',', '')
            try:
                return float(price_str)
            except:
                pass
        return None
    
    def extract_discount(self, text):
        """Extract discount percentage"""
        import re
        matches = re.findall(r'(\d+)%\s*off', text, re.IGNORECASE)
        if matches:
            return int(matches[0])
        return 0
    
    def scrape_deals_page(self, page, url, category='general'):
        """Scrape deals from a specific page"""
        print(f"\n{'='*60}")
        print(f"Scraping: {category}")
        print(f"URL: {url}")
        print('='*60)
        
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(2)
            
            # Scroll to load more products
            for i in range(2):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(0.5)
            
            # Take screenshot
            screenshot_path = self.screenshots_dir / f'{category}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            page.screenshot(path=str(screenshot_path))
            print(f"✓ Screenshot saved: {screenshot_path}")
            
            # Find product cards
            products = []
            
            # Try multiple selectors
            selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]',
                '.a-section.a-spacing-base'
            ]
            
            product_elements = []
            for selector in selectors:
                product_elements = page.query_selector_all(selector)
                if len(product_elements) > 5:
                    print(f"✓ Found {len(product_elements)} products using: {selector}")
                    break
            
            if not product_elements:
                print("✗ No products found")
                return []
            
            # Extract product data
            for element in product_elements[:CONFIG['max_products']]:
                try:
                    text = element.inner_text()
                    
                    # Extract product name
                    name_elem = element.query_selector('h2, .a-size-medium, .a-size-base-plus')
                    name = name_elem.inner_text() if name_elem else None
                    
                    if not name or len(name) < 5:
                        continue
                    
                    # Extract price
                    price = self.extract_price(text)
                    if not price:
                        continue
                    
                    # Extract discount
                    discount = self.extract_discount(text)
                    
                    # Extract ASIN
                    asin = element.get_attribute('data-asin')
                    
                    # Extract link
                    link_elem = element.query_selector('a.a-link-normal')
                    link = None
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        if href:
                            link = f"https://www.amazon.in{href}" if href.startswith('/') else href
                    
                    # Extract image
                    img_elem = element.query_selector('img')
                    image = img_elem.get_attribute('src') if img_elem else None
                    
                    # Extract rating
                    rating_elem = element.query_selector('[aria-label*="out of"]')
                    rating = rating_elem.get_attribute('aria-label') if rating_elem else None
                    
                    product = {
                        'name': name[:200],
                        'price': price,
                        'discount': discount,
                        'asin': asin,
                        'link': link,
                        'image': image,
                        'rating': rating,
                        'category': category,
                        'timestamp': datetime.now().isoformat(),
                        'is_deal': self.is_deal(price, discount)
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    continue
            
            print(f"✓ Extracted {len(products)} products")
            return products
            
        except Exception as e:
            print(f"✗ Error scraping {category}: {e}")
            return []
    
    def is_deal(self, price, discount):
        """Check if product qualifies as a deal"""
        if discount <= 0:
            return False
        if price <= CONFIG['price_threshold']:
            return True
        if discount >= CONFIG['discount_threshold']:
            return True
        return False
    
    def normalize_name(self, name):
        """Normalize product name for consistent matching, removing dynamic parts"""
        import re
        if not name:
            return ""
        # Remove common dynamic prefixes/suffixes that change between runs
        # Like "Deal of the Day:", "Limited time deal:", etc.
        patterns_to_remove = [
            r'(?i)deal of the day[:\s]*',
            r'(?i)limited time deal[:\s]*',
            r'(?i)lightning deal[:\s]*',
            r'(?i)sponsored[:\s]*',
            r'(?i)best seller[:\s]*',
        ]
        text = name
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text)
            
        # Standard normalization: lowercase, strip, remove non-alphanumeric
        normalized = ' '.join(text.lower().split())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized.strip()
    
    def get_product_key(self, product):
        """Generate a consistent product key: ASIN-based if possible, else Name-based"""
        if product.get('asin'):
            return f"asin_{product['asin']}"
        
        normalized_name = self.normalize_name(product['name'])
        if normalized_name:
            return f"name_{normalized_name[:120]}"
        
        return None
    
    def check_price_change(self, product):
        """Check if this is a new deal or price drop"""
        product_key = self.get_product_key(product)
        
        if not product_key:
            print(f"⚠ No key for product: {product['name'][:50]}")
            return 'new'  # No way to track, treat as new
        
        # Check if we've seen this product before
        if product_key not in self.price_history:
            print(f"🆕 New product: {product['name'][:50]} (key: {product_key[:50]})")
            return 'new'  # New product
        
        old_data = self.price_history[product_key]
        old_price = old_data.get('price', 0)
        already_alerted = old_data.get('alerted', False)
        
        if old_price == 0:
            return 'new'
        
        # If already alerted and price is same or higher, don't alert again
        if already_alerted and product['price'] >= old_price:
            print(f"✓ Already alerted, same/higher price: {product['name'][:50]} (₹{product['price']})")
            return 'already_alerted'
        
        # Check if price dropped significantly
        price_drop_pct = ((old_price - product['price']) / old_price) * 100
        
        if price_drop_pct >= CONFIG['price_drop_threshold']:
            product['old_price'] = old_price
            product['price_drop_pct'] = round(price_drop_pct, 1)
            print(f"📉 Price drop: {product['name'][:50]} (₹{old_price} → ₹{product['price']})")
            return 'price_drop'
        
        # Same or higher price
        if product['price'] >= old_price:
            print(f"✓ Same price: {product['name'][:50]} (₹{product['price']})")
            return 'same'
        
        # Small price drop (less than threshold)
        print(f"→ Minor drop: {product['name'][:50]} (₹{old_price} → ₹{product['price']})")
        return 'minor_drop'
    
    def update_price_history(self, product):
        """Update price history for a product"""
        product_key = self.get_product_key(product)
        
        if product_key:
            old_data = self.price_history.get(product_key, {})
            
            # Reset alerted flag if it's a new deal or price drop being processed
            # This ensures mark_deals_as_alerted can set it to True AFTER notification
            change_type = product.get('change_type')
            if change_type in ['new', 'price_drop']:
                alerted = False
            else:
                alerted = old_data.get('alerted', False)
            
            self.price_history[product_key] = {
                'name': product['name'],
                'price': product['price'],
                'discount': product['discount'],
                'last_seen': product['timestamp'],
                'asin': product.get('asin', ''),
                'alerted': alerted
            }
    
    def scrape_all_deals(self):
        """Scrape deals from multiple sources"""
        print("\n" + "="*60)
        print("AMAZON PRICE TRACKER - STARTING")
        print("="*60)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # Custom search query
                if SEARCH_QUERY:
                    url = f"https://www.amazon.in/s?k={SEARCH_QUERY}"
                    products = self.scrape_deals_page(page, url, 'custom_search')
                    self.deals.extend(products)
                
                # Today's Deals
                url = "https://www.amazon.in/gp/goldbox"
                products = self.scrape_deals_page(page, url, 'todays_deals')
                self.deals.extend(products)
                
                # Lightning Deals
                url = "https://www.amazon.in/gp/goldbox?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-lightning-deals%2522%257D"
                products = self.scrape_deals_page(page, url, 'lightning_deals')
                self.deals.extend(products)
                
                # Search queries
                for query in CONFIG['search_queries']:
                    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
                    products = self.scrape_deals_page(page, url, query.replace(' ', '_'))
                    self.deals.extend(products)
                    time.sleep(random.uniform(1.0, 2.0))  # Random rate limiting
                
                # Electronics with adaptive discount
                electronics_products = self.scrape_electronics_adaptive(page)
                self.deals.extend(electronics_products)
                
                # Scrape deals from all categories
                category_deals = self.scrape_category_deals(page)
                self.deals.extend(category_deals)
                
                # Scrape Amazon Fresh deals
                fresh_deals = self.scrape_amazon_fresh(page)
                self.deals.extend(fresh_deals)
                
            finally:
                browser.close()
        
        # Remove duplicates (prefer ones with ASIN or better discount)
        seen_keys = {}
        for deal in self.deals:
            # Use a deduplication key (name + rough size/category)
            # This is different from the history key to allow better intra-run dedupe
            dedupe_key = f"{self.normalize_name(deal['name'])[:100]}"
            
            if dedupe_key not in seen_keys:
                seen_keys[dedupe_key] = deal
            else:
                existing = seen_keys[dedupe_key]
                # Keep better deal
                if deal['discount'] > existing['discount'] or (not existing.get('asin') and deal.get('asin')):
                    seen_keys[dedupe_key] = deal
        
        self.deals = list(seen_keys.values())
        print(f"\n✓ Total unique deals found: {len(self.deals)}")
    
    def scrape_electronics_adaptive(self, page):
        """Scrape electronics with adaptive discount threshold"""
        print("\n" + "="*60)
        print("ELECTRONICS SECTION - ADAPTIVE DISCOUNT")
        print("="*60)
        
        all_electronics = []
        e_config = CONFIG['electronics_config']
        
        # Scrape all electronics queries first
        for query in CONFIG['electronics_queries']:
            url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            products = self.scrape_deals_page(page, url, f'electronics_{query.replace(" ", "_")}')
            all_electronics.extend(products)
            time.sleep(random.uniform(1.0, 2.0))  # Random rate limiting
        
        if not all_electronics:
            print("✗ No electronics products found")
            return []
        
        print(f"✓ Found {len(all_electronics)} total electronics products")
        
        # Try different discount thresholds
        current_discount = e_config['max_discount']
        min_discount = e_config['min_discount']
        step = e_config['discount_step']
        min_products = e_config['min_products']
        
        filtered_products = []
        
        while current_discount >= min_discount:
            # Filter by current discount threshold
            filtered = [
                p for p in all_electronics 
                if p['discount'] >= current_discount and p['price'] <= e_config['max_price']
            ]
            
            # Remove duplicates
            seen = set()
            unique_filtered = []
            for p in filtered:
                key = f"{p['name']}_{p['price']}"
                if key not in seen:
                    seen.add(key)
                    unique_filtered.append(p)
            
            print(f"  Trying {current_discount}% discount: {len(unique_filtered)} products")
            
            if len(unique_filtered) >= min_products:
                filtered_products = unique_filtered
                print(f"✓ Found {len(filtered_products)} electronics with ≥{current_discount}% discount")
                break
            
            # Lower threshold and try again
            current_discount -= step
        
        if not filtered_products and all_electronics:
            # If still no products, take top discounted ones
            sorted_electronics = sorted(all_electronics, key=lambda x: x['discount'], reverse=True)
            filtered_products = sorted_electronics[:min_products]
            print(f"✓ Taking top {len(filtered_products)} electronics by discount")
        
        # Mark as electronics category
        for product in filtered_products:
            product['category'] = 'electronics_featured'
        
        return filtered_products
    
    def scrape_category_deals(self, page):
        """Scrape deals from all configured categories"""
        print("\n" + "="*60)
        print("CATEGORY DEALS - SCRAPING ALL CATEGORIES")
        print("="*60)
        
        all_category_deals = []
        categories = CONFIG['categories']
        
        print(f"Scraping {len(categories)} categories...")
        
        for i, category in enumerate(categories, 1):
            try:
                print(f"\n[{i}/{len(categories)}] Scraping category: {category}")
                
                # Use search query pattern: "category deals" which is most reliable
                # This searches for deals within that category
                search_query = f"{category} deals"
                url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}"
                
                products = self.scrape_deals_page(page, url, category)
                
                if products:
                    all_category_deals.extend(products)
                    print(f"✓ Found {len(products)} products in {category}")
                else:
                    # Try alternative: just the category name
                    print(f"⚠ No products with 'deals', trying category search...")
                    url = f"https://www.amazon.in/s?k={category.replace(' ', '+')}"
                    products = self.scrape_deals_page(page, url, category)
                    if products:
                        all_category_deals.extend(products)
                        print(f"✓ Found {len(products)} products in {category} (category search)")
                
                # Rate limiting - random delay between categories (1-3s) to avoid detection
                time.sleep(random.uniform(1.0, 3.0))
                
            except Exception as e:
                print(f"✗ Error scraping category {category}: {e}")
                continue
        
        print(f"\n✓ Total products from categories: {len(all_category_deals)}")
        return all_category_deals
    
    def scrape_amazon_fresh(self, page):
        """Scrape deals from Amazon Fresh categories"""
        print("\n" + "="*60)
        print("AMAZON FRESH - SCRAPING GROCERY DEALS")
        print("="*60)
        
        all_fresh_deals = []
        fresh_categories = CONFIG.get('amazon_fresh_categories', [])
        
        if not fresh_categories:
            print("No Amazon Fresh categories configured")
            return []
        
        print(f"Scraping {len(fresh_categories)} Amazon Fresh categories...")
        
        # First, try to access Amazon Fresh main page
        try:
            print("\n[1/2] Accessing Amazon Fresh main page...")
            fresh_urls = [
                "https://www.amazon.in/amazonfresh",
                "https://www.amazon.in/amazonfresh?ref_=nav_cs_fresh",
                "https://www.amazon.in/gp/browse.html?node=4859467031&ref_=nav_cs_fresh"
            ]
            
            for url in fresh_urls:
                try:
                    products = self.scrape_deals_page(page, url, 'amazon_fresh_main')
                    if products:
                        all_fresh_deals.extend(products)
                        print(f"✓ Found {len(products)} products on Amazon Fresh main page")
                        break
                except Exception as e:
                    print(f"⚠ Could not access {url}: {e}")
                    continue
        except Exception as e:
            print(f"⚠ Error accessing Amazon Fresh main page: {e}")
        
        # Scrape individual Fresh categories
        print(f"\n[2/2] Scraping {len(fresh_categories)} Fresh categories...")
        for i, category in enumerate(fresh_categories, 1):
            try:
                print(f"\n[{i}/{len(fresh_categories)}] Scraping Fresh category: {category}")
                
                # Try multiple search patterns for Amazon Fresh
                search_patterns = [
                    f"amazon fresh {category}",
                    f"amazon fresh {category} deals",
                    f"{category} amazon fresh"
                ]
                
                products_found = False
                for pattern in search_patterns:
                    try:
                        url = f"https://www.amazon.in/s?k={pattern.replace(' ', '+')}"
                        products = self.scrape_deals_page(page, url, f'fresh_{category}')
                        
                        if products:
                            all_fresh_deals.extend(products)
                            print(f"✓ Found {len(products)} products in Fresh {category}")
                            products_found = True
                            break
                    except Exception as e:
                        continue
                
                if not products_found:
                    print(f"⚠ No products found for Fresh {category}")
                
                # Rate limiting - random delay between Fresh categories (1-3s)
                time.sleep(random.uniform(1.0, 3.0))
                
            except Exception as e:
                print(f"✗ Error scraping Fresh category {category}: {e}")
                continue
        
        # Mark all as Amazon Fresh
        for product in all_fresh_deals:
            if 'category' not in product or not product['category'].startswith('fresh_'):
                product['category'] = f"fresh_{product.get('category', 'amazon_fresh')}"
        
        print(f"\n✓ Total products from Amazon Fresh: {len(all_fresh_deals)}")
        return all_fresh_deals
    
    def analyze_deals(self):
        """Analyze and categorize deals"""
        if not self.deals:
            print("No deals to analyze")
            return
        
        print("\n" + "="*60)
        print("DEAL ANALYSIS")
        print("="*60)
        
        # Separate by category type
        electronics_deals = [d for d in self.deals if d.get('category') == 'electronics_featured']
        fresh_deals = [d for d in self.deals if d.get('category', '').startswith('fresh_')]
        other_deals = [d for d in self.deals if d.get('category') != 'electronics_featured' and not d.get('category', '').startswith('fresh_')]
        
        print(f"Total Deals Scraped: {len(self.deals)}")
        print(f"  - Electronics: {len(electronics_deals)}")
        print(f"  - Amazon Fresh: {len(fresh_deals)}")
        print(f"  - Other Deals: {len(other_deals)}")
        
        # Category breakdown
        category_counts = {}
        for deal in self.deals:
            cat = deal.get('category', 'unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if category_counts:
            print(f"\nCategory Breakdown:")
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            for cat, count in sorted_categories[:15]:  # Show top 15 categories
                print(f"  - {cat}: {count} deals")
            if len(sorted_categories) > 15:
                print(f"  ... and {len(sorted_categories) - 15} more categories")
        
        # Check each deal for price changes
        for deal in self.deals:
            change_type = self.check_price_change(deal)
            deal['change_type'] = change_type
            
            # Update price history (but don't mark as alerted yet)
            self.update_price_history(deal)
            
            # Categorize - only add if it's truly new or has a price drop
            if change_type == 'new':
                self.new_deals.append(deal)
            elif change_type == 'price_drop':
                self.price_drops.append(deal)
            # Skip 'same', 'minor_drop', and 'already_alerted'
        
        # Save updated price history
        self.save_price_history()
        
        # Filter deals based on config - ONLY new deals and price drops
        alert_worthy = self.new_deals + self.price_drops
        
        if not alert_worthy:
            print("\n✗ No new deals or price drops to alert")
            return {
                'total': len(self.deals),
                'new': 0,
                'price_drops': 0,
                'cheap': 0,
                'high_discount': 0,
                'alert_deals': [],
                'electronics_alerts': [],
                'fresh_alerts': []
            }
        
        # Further filter by thresholds
        cheap_deals = [d for d in alert_worthy if d['price'] <= CONFIG['price_threshold']]
        high_discount = [d for d in alert_worthy if d['discount'] >= CONFIG['discount_threshold']]
        
        # Separate alert-worthy deals by category
        electronics_alerts = [d for d in alert_worthy if d.get('category') == 'electronics_featured']
        fresh_alerts = [d for d in alert_worthy if d.get('category', '').startswith('fresh_')]
        other_alerts = [d for d in alert_worthy if d.get('category') != 'electronics_featured' and not d.get('category', '').startswith('fresh_')]
        
        print(f"New Deals: {len(self.new_deals)}")
        print(f"Price Drops: {len(self.price_drops)}")
        print(f"Alert-Worthy Deals: {len(alert_worthy)}")
        print(f"  - Cheap Deals (≤₹{CONFIG['price_threshold']}): {len(cheap_deals)}")
        print(f"  - High Discount (≥{CONFIG['discount_threshold']}%): {len(high_discount)}")
        print(f"  - Electronics: {len(electronics_alerts)}")
        print(f"  - Amazon Fresh: {len(fresh_alerts)}")
        print(f"  - Other: {len(other_alerts)}")
        
        # Combine and deduplicate - separate by category
        other_deals_dict = {d['name']: d for d in other_alerts}
        other_deals = list(other_deals_dict.values())
        fresh_deals_dict = {d['name']: d for d in fresh_alerts}
        fresh_deals_list = list(fresh_deals_dict.values())
        
        # Sort by discount
        other_deals.sort(key=lambda x: x['discount'], reverse=True)
        electronics_alerts.sort(key=lambda x: x['discount'], reverse=True)
        fresh_deals_list.sort(key=lambda x: x['discount'], reverse=True)
        
        if other_deals or electronics_alerts or fresh_deals_list:
            if other_deals:
                print("\n🔥 OTHER NEW DEALS:")
                for i, deal in enumerate(other_deals[:10], 1):
                    change_marker = "🆕" if deal['change_type'] == 'new' else "📉"
                    print(f"{change_marker} {i}. {deal['name'][:60]}")
                    print(f"   ₹{deal['price']} ({deal['discount']}% off)")
                    if deal['change_type'] == 'price_drop':
                        print(f"   Price dropped from ₹{deal['old_price']} ({deal['price_drop_pct']}% drop)")
                    print()
            
            if fresh_deals_list:
                print("\n🛒 AMAZON FRESH NEW DEALS:")
                for i, deal in enumerate(fresh_deals_list[:10], 1):
                    change_marker = "🆕" if deal['change_type'] == 'new' else "📉"
                    print(f"{change_marker} {i}. {deal['name'][:60]}")
                    print(f"   ₹{deal['price']} ({deal['discount']}% off)")
                    if deal['change_type'] == 'price_drop':
                        print(f"   Price dropped from ₹{deal['old_price']} ({deal['price_drop_pct']}% drop)")
                    print()
            
            if electronics_alerts:
                print("\n💻 ELECTRONICS NEW DEALS:")
                for i, deal in enumerate(electronics_alerts[:10], 1):
                    change_marker = "🆕" if deal['change_type'] == 'new' else "📉"
                    print(f"{change_marker} {i}. {deal['name'][:60]}")
                    print(f"   ₹{deal['price']} ({deal['discount']}% off)")
                    if deal['change_type'] == 'price_drop':
                        print(f"   Price dropped from ₹{deal['old_price']} ({deal['price_drop_pct']}% drop)")
                    print()
        
        return {
            'total': len(self.deals),
            'new': len(self.new_deals),
            'price_drops': len(self.price_drops),
            'cheap': len(cheap_deals),
            'high_discount': len(high_discount),
            'alert_deals': other_deals[:10],
            'electronics_alerts': electronics_alerts[:10],
            'fresh_alerts': fresh_deals_list[:10]
        }
    
    def format_category_name(self, category):
        """Format category name for display"""
        if not category:
            return "General"
        
        # Handle special categories
        if category == 'electronics_featured':
            return "Electronics"
        if category.startswith('fresh_'):
            # Convert fresh_fruits -> Fruits, fresh_vegetables -> Vegetables
            cat = category.replace('fresh_', '').replace('_', ' ').title()
            return f"Fresh: {cat}"
        if category.startswith('electronics_'):
            cat = category.replace('electronics_', '').replace('_', ' ').title()
            return f"Electronics: {cat}"
        
        # Format regular categories
        formatted = category.replace('-', ' ').replace('_', ' ').title()
        return formatted
    
    def send_summary_alert(self, analysis):
        """Send summary via Telegram"""
        print("\n" + "="*60)
        print("SENDING TELEGRAM ALERT")
        print("="*60)
        
        if not analysis:
            print("⚠ No analysis data - cannot send alert")
            return
        
        print(f"Analysis data received: {list(analysis.keys())}")
        
        # Check if there are any NEW deals or price drops
        new_count = analysis.get('new', 0)
        price_drop_count = analysis.get('price_drops', 0)
        
        if new_count == 0 and price_drop_count == 0:
            # No new deals or price drops - send simple message
            message = f"""🛒 <b>Amazon Deals Check</b>

✓ No new deals or price drops found

All tracked products have the same prices as before.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            self.send_telegram_alert(message)
            print("✓ Sent 'no new deals' notification")
            return
        
        # We have new deals or price drops - send detailed alert
        alert_deals = analysis.get('alert_deals', [])
        electronics_alerts = analysis.get('electronics_alerts', [])
        fresh_alerts = analysis.get('fresh_alerts', [])
        
        message = f"""🛒 <b>Amazon Deals Alert</b>

📊 <b>Summary:</b>
• New Deals: {analysis['new']}
• Price Drops: {analysis['price_drops']}
"""
        
        max_deals_per_cat = CONFIG.get('telegram_deals_per_category', 15)
        
        if electronics_alerts:
            message += f"\n💻 <b>Electronics Deals ({len(electronics_alerts)}):</b>\n"
            for i, deal in enumerate(electronics_alerts[:max_deals_per_cat], 1):
                change_marker = "🆕 NEW" if deal['change_type'] == 'new' else "📉 PRICE DROP"
                category_name = self.format_category_name(deal.get('category', ''))
                message += f"\n{change_marker}\n"
                message += f"{i}. {deal['name'][:80]}\n"
                message += f"   📁 {category_name}\n"
                message += f"   ₹{deal['price']:,} ({deal['discount']}% off)\n"
                
                if deal['change_type'] == 'price_drop':
                    message += f"   Was: ₹{deal['old_price']:,} (dropped {deal['price_drop_pct']}%)\n"
                
                if deal['link']:
                    message += f"   <a href='{deal['link']}'>View Deal</a>\n"
        
        if fresh_alerts:
            message += f"\n🛒 <b>Amazon Fresh Deals ({len(fresh_alerts)}):</b>\n"
            for i, deal in enumerate(fresh_alerts[:max_deals_per_cat], 1):
                change_marker = "🆕 NEW" if deal['change_type'] == 'new' else "📉 PRICE DROP"
                category_name = self.format_category_name(deal.get('category', ''))
                message += f"\n{change_marker}\n"
                message += f"{i}. {deal['name'][:80]}\n"
                message += f"   📁 {category_name}\n"
                message += f"   ₹{deal['price']:,} ({deal['discount']}% off)\n"
                
                if deal['change_type'] == 'price_drop':
                    message += f"   Was: ₹{deal['old_price']:,} (dropped {deal['price_drop_pct']}%)\n"
                
                if deal['link']:
                    message += f"   <a href='{deal['link']}'>View Deal</a>\n"
        
        if alert_deals:
            message += f"\n🔥 <b>Other Deals ({len(alert_deals)}):</b>\n"
            for i, deal in enumerate(alert_deals[:max_deals_per_cat], 1):
                change_marker = "🆕 NEW" if deal['change_type'] == 'new' else "📉 PRICE DROP"
                category_name = self.format_category_name(deal.get('category', ''))
                message += f"\n{change_marker}\n"
                message += f"{i}. {deal['name'][:80]}\n"
                message += f"   📁 {category_name}\n"
                message += f"   ₹{deal['price']:,} ({deal['discount']}% off)\n"
                
                if deal['change_type'] == 'price_drop':
                    message += f"   Was: ₹{deal['old_price']:,} (dropped {deal['price_drop_pct']}%)\n"
                
                if deal['link']:
                    message += f"   <a href='{deal['link']}'>View Deal</a>\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Message will be automatically split into multiple parts if too long
        # send_telegram_alert handles splitting at safe points
        self.send_telegram_alert(message)
        print("✓ Sent alert with new deals and price drops")
        
        # Mark all alerted deals as 'alerted' in price history
        self.mark_deals_as_alerted(analysis)
    
    def mark_deals_as_alerted(self, analysis):
        """Mark ALL identified new deals and price drops as 'alerted' in price history"""
        # Mark everything we found, not just what was sent in the top 10
        # This prevents "old" deals from cluttering future runs
        all_to_mark = self.new_deals + self.price_drops
        
        marked_count = 0
        for deal in all_to_mark:
            product_key = self.get_product_key(deal)
            if product_key and product_key in self.price_history:
                if not self.price_history[product_key].get('alerted'):
                    self.price_history[product_key]['alerted'] = True
                    marked_count += 1
        
        # Save updated price history with alerted flags
        self.save_price_history()
        print(f"✓ Marked {marked_count} NEW deals as alerted in price history")
    
    def save_results(self):
        """Save results to files"""
        if not self.deals:
            print("No deals to save")
            return
        
        # Save all deals (for reference)
        with open('amazon_deals.json', 'w', encoding='utf-8') as f:
            json.dump(self.deals, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(self.deals)} total deals to amazon_deals.json")
        
        # Save only new deals and price drops (what gets alerted)
        new_and_drops = self.new_deals + self.price_drops
        if new_and_drops:
            with open('amazon_deals_new.json', 'w', encoding='utf-8') as f:
                json.dump(new_and_drops, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(new_and_drops)} new/changed deals to amazon_deals_new.json")
        else:
            # Save empty file to indicate no new deals
            with open('amazon_deals_new.json', 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            print("✓ No new deals - saved empty amazon_deals_new.json")
        
        # Save price changes summary
        price_changes = {
            'timestamp': datetime.now().isoformat(),
            'new_deals': len(self.new_deals),
            'price_drops': len(self.price_drops),
            'total_scraped': len(self.deals),
            'deals': new_and_drops
        }
        with open('price_changes.json', 'w', encoding='utf-8') as f:
            json.dump(price_changes, f, indent=2, ensure_ascii=False)
        print("✓ Saved price changes summary to price_changes.json")
    
    def run(self):
        """Main execution"""
        try:
            # Scrape deals
            self.scrape_all_deals()
            
            # Analyze
            analysis = self.analyze_deals()
            
            # Save results
            self.save_results()
            
            # Send alerts - always send something
            self.send_summary_alert(analysis)
            
            print("\n" + "="*60)
            print("TRACKING COMPLETE")
            print("="*60)
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    tracker = AmazonPriceTracker()
    tracker.run()
