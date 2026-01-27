#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swiggy Instamart Price Tracker
Uses direct Playwright automation with stealth and location handling
Monitors Swiggy deals and sends Telegram notifications
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

import requests
from pathlib import Path

# Fix Windows Unicode encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Tracking configuration
CONFIG = {
    'price_threshold': 50,  # Alert for products under ₹50
    'discount_threshold': 50,  # Alert for >50% discount
    'price_drop_threshold': 20,  # Alert if price drops by >20%
    'max_products': 30,  # Products per category
    'only_new_deals': True,  # Only alert on NEW deals or price drops
    'telegram_deals_per_category': 15,  # Number of deals per category in Telegram
    'search_queries': [
        'chocolate',
    ],
    'base_url': 'https://www.swiggy.com/instamart/search',
}

class SwiggyPriceTracker:
    def __init__(self):
        self.deals = []
        self.price_history = self.load_price_history()
        self.new_deals = []
        self.price_drops = []
        self.screenshots_dir = Path('screenshots')
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def load_price_history(self):
        """Load previous price history"""
        try:
            if Path('swiggy_price_history.json').exists():
                with open('swiggy_price_history.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load price history: {e}")
        return {}
    
    def save_price_history(self):
        """Save price history"""
        try:
            with open('swiggy_price_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.price_history, f, indent=2, ensure_ascii=False)
            print("✓ Price history saved")
        except Exception as e:
            print(f"Error saving price history: {e}")
    
    def split_message(self, message, max_length=4000):
        """Split a long message into chunks"""
        if len(message) <= max_length:
            return [message]
        
        chunks = []
        current_pos = 0
        message_length = len(message)
        
        while current_pos < message_length:
            remaining = message_length - current_pos
            
            if remaining <= max_length:
                chunks.append(message[current_pos:])
                break
            
            safe_split = message.rfind('\n', current_pos, current_pos + max_length)
            if safe_split == -1:
                safe_split = current_pos + max_length
            
            chunk = message[current_pos:safe_split]
            chunks.append(chunk)
            current_pos = safe_split
        
        for i in range(1, len(chunks)):
            chunks[i] = f"📄 <b>Part {i + 1} of {len(chunks)}</b>\n\n" + chunks[i]
        
        return chunks
    
    def send_telegram_alert(self, message):
        """Send alert via Telegram"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠ Telegram not configured, skipping notification")
            return
        
        chunks = self.split_message(message, max_length=3900)
        
        if len(chunks) > 1:
            print(f"📤 Splitting message into {len(chunks)} parts...")
        
        for i, chunk in enumerate(chunks, 1):
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': chunk,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    print(f"✓ Telegram message part {i}/{len(chunks)} sent")
                    if i < len(chunks):
                        time.sleep(0.5)
                else:
                    print(f"✗ Telegram API error: {response.text}")
            except Exception as e:
                print(f"✗ Error sending Telegram: {e}")
    
    def extract_price(self, text):
        """Extract price from text"""
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
        matches = re.findall(r'(\d+)%\s*(?:off|OFF)', text)
        if matches:
            return int(matches[0])
        return 0
    
    def get_product_key(self, product):
        """Generate a consistent product key for tracking"""
        normalized_name = ' '.join(product.get('name', '').lower().split())
        normalized_name = re.sub(r'[^\w\s]', '', normalized_name)
        price = int(product.get('price', 0))
        return f"swiggy_{normalized_name[:100]}_{price}"
    
    def check_price_change(self, product):
        """Check if this is a new deal or price drop"""
        product_key = self.get_product_key(product)
        
        if not product_key:
            return 'new'
        
        # Check if we've seen this product before
        if product_key not in self.price_history:
            # Only print for real new products to reduce noise
            # print(f"🆕 New product: {product.get('name', 'Unknown')[:50]}")
            return 'new'
        
        old_data = self.price_history[product_key]
        old_price = old_data.get('price', 0)
        already_alerted = old_data.get('alerted', False)
        
        if old_price == 0:
            return 'new'
        
        current_price = product.get('price', 0)
        
        # If already alerted and price is same or higher, skip
        if already_alerted and current_price >= old_price:
            return 'already_alerted'
        
        # Check for significant price drop
        price_drop_pct = ((old_price - current_price) / old_price) * 100
        
        if price_drop_pct >= CONFIG['price_drop_threshold']:
            product['old_price'] = old_price
            product['price_drop_pct'] = round(price_drop_pct, 1)
            print(f"📉 Price drop: {product.get('name', 'Unknown')[:50]}")
            return 'price_drop'
        
        if current_price >= old_price:
            return 'same'
        
        return 'minor_drop'
    
    def update_price_history(self, product):
        """Update price history for a product"""
        product_key = self.get_product_key(product)
        
        if product_key:
            old_data = self.price_history.get(product_key, {})
            alerted = old_data.get('alerted', False)
            
            self.price_history[product_key] = {
                'name': product.get('name', 'Unknown'),
                'price': product.get('price', 0),
                'discount': product.get('discount', 0),
                'last_seen': product.get('timestamp', datetime.now().isoformat()),
                'alerted': alerted
            }
    
    def scrape_search_page(self, page, query):
        """Scrape products from a Swiggy search page"""
        print(f"\n{'='*60}")
        print(f"Searching: {query}")
        print('='*60)
        
        try:
            # Use query directly in URL
            search_url = f"{CONFIG['base_url']}?custom_back=true&query={query.replace(' ', '%20')}"
            
            # Navigate
            page.goto(search_url, wait_until='networkidle', timeout=60000)
            print("DEBUG: Waiting for search results to settle...")
            time.sleep(10)
            
            # Handle location popup if present (try multiple times)
            for _ in range(3):
                try:
                    close_btn = page.query_selector('[aria-label="close"], [data-testid="close-btn"]')
                    if close_btn:
                        print("DEBUG: Closing popup")
                        close_btn.click()
                        time.sleep(2)
                except:
                    pass
            
            # Scroll to load more products
            print("DEBUG: Scrolling to load more content...")
            for i in range(5):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(3)
            
            # Extra wait for lazy-loaded images/content
            time.sleep(5)
            
            # Take screenshot
            screenshot_path = self.screenshots_dir / f'swiggy_{query.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            page.screenshot(path=str(screenshot_path))
            print(f"✓ Screenshot saved: {screenshot_path}")
            
            # Find product cards
            products = []
            
            # Updated selectors based on common Swiggy patterns
            # Note: Swiggy uses styled components, so classes like 'sc-' are common but unstable
            # Relying on testids or structure is better
            selectors = [
                '[data-testid="product-card"]',
                '[data-testid="normal-product-card"]',
                '.product-card',
                'div[href*="/instamart/item/"]', # If items are links
                'a[href*="/instamart/item/"]'    # If items are wrapped in anchors
            ]
            
            product_elements = []
            for selector in selectors:
                elements = page.query_selector_all(selector)
                if len(elements) > 0:
                    print(f"Found {len(elements)} items with selector: {selector}")
                    product_elements = elements
                    break
            
            if not product_elements:
                print("⚠ No product elements found with standard selectors")
                # Fallback: dumping HTML for debug
                with open("debug_swiggy_failed.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                return []
            
            for element in product_elements[:CONFIG['max_products']]:
                try:
                    text = element.inner_text()
                    
                    # Extract product details
                    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
                    if len(lines) < 2:
                        continue
                    
                    # Heuristic: Name is usually the first non-empty line
                    name = lines[0]
                    
                    # Extract price
                    price = self.extract_price(text)
                    if not price:
                        continue
                    
                    # Extract discount
                    discount = self.extract_discount(text)
                    
                    # Extract original price if available
                    original_price = None
                    price_matches = re.findall(r'₹\s*([0-9,]+)', text)
                    if len(price_matches) > 1:
                        try:
                            # Usually the higher one is original
                            p1 = float(price_matches[0].replace(',', ''))
                            p2 = float(price_matches[1].replace(',', ''))
                            if p2 > p1:
                                original_price = p2
                            elif p1 > p2:
                                original_price = p1
                                price = p2 # Correct price if swapped
                        except:
                            pass
                    
                    product = {
                        'name': name[:200],
                        'price': price,
                        'discount': discount,
                        'original_price': original_price,
                        'category': query,
                        'timestamp': datetime.now().isoformat(),
                        'is_deal': self.is_deal(price, discount)
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    continue
            
            print(f"✓ Extracted {len(products)} products")
            return products
            
        except Exception as e:
            print(f"✗ Error scraping {query}: {e}")
            return []
    
    def is_deal(self, price, discount):
        """Check if product qualifies as a deal"""
        if price <= CONFIG['price_threshold']:
            return True
        if discount >= CONFIG['discount_threshold']:
            return True
        return False
    
    def scrape_all_deals(self):
        """Scrape deals from multiple search queries"""
        print("\n" + "="*60)
        print("SWIGGY INSTAMART PRICE TRACKER")
        print("="*60)
        
        with sync_playwright() as p:
            # Use non-headless mode to avoid detection
            # Remove channel='chrome' to use bundled chromium which works better with stealth
            browser = p.chromium.launch(headless=False)
            
            # Context with geolocation and permissions
            # Bangalore coordinates
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                geolocation={'latitude': 12.9716, 'longitude': 77.5946},
                permissions=['geolocation'],
                locale='en-IN',
                timezone_id='Asia/Kolkata'
            )
            
            # Set cookies for location (Critical for Swiggy)
            context.add_cookies([
                {'name': '_loc_user_lat', 'value': '12.9716', 'domain': '.swiggy.com', 'path': '/'},
                {'name': '_loc_user_lng', 'value': '77.5946', 'domain': '.swiggy.com', 'path': '/'},
                {'name': 'lat_long', 'value': '12.9716,77.5946', 'domain': '.swiggy.com', 'path': '/'},
                {'name': '_loc_city_name', 'value': 'Bangalore', 'domain': '.swiggy.com', 'path': '/'}
            ])
            
            page = context.new_page()
            
            # Apply stealth if available
            if stealth_sync:
                print("✓ Applying stealth mode")
                stealth_sync(page)
            
            try:
                # Setup location via Home Page first to ensure cookies work or prompt is handled
                print("DEBUG: Navigating to Instamart Home...")
                page.goto("https://www.swiggy.com/instamart", wait_until='networkidle', timeout=90000)
                print("DEBUG: Waiting for Home Page to load...")
                time.sleep(20) # Increased from 15
                
                # Check if we are stuck on "Location needed" page
                if "instamart" not in page.url or page.query_selector('text="Enter your delivery location"'):
                    print(f"DEBUG: Location needed. Attempting manual address entry...")
                    try:
                        # Try to find address input
                        address_input = page.query_selector('input[placeholder*="Address"], input[placeholder*="location"], #location')
                        if address_input:
                            print("→ Typing 'Bangalore' into address input")
                            address_input.fill("Bangalore")
                            time.sleep(3)
                            # Wait for dropdown and select first option
                            page.keyboard.press("ArrowDown")
                            time.sleep(1)
                            page.keyboard.press("Enter")
                            time.sleep(10)
                        else:
                            # Try Locate Me
                            locate_btn = page.query_selector('button:has-text("Locate Me"), [data-testid="locate-me-cta"]')
                            if locate_btn:
                                print("→ Clicking 'Locate Me'")
                                locate_btn.click()
                                time.sleep(10)
                    except Exception as e:
                        print(f"Error handling location: {e}")
                
                # Double check we are finally in Instamart
                if "instamart" not in page.url:
                    print("DEBUG: Still not in Instamart, forcing navigation to search page...")
                    page.goto(f"{CONFIG['base_url']}?custom_back=true", wait_until='networkidle')
                    time.sleep(15)
                
                # Start scraping
                import random
                for query in CONFIG['search_queries']:
                    products = self.scrape_search_page(page, query)
                    self.deals.extend(products)
                    
                    # Random jitter between searches
                    jitter = random.uniform(5, 12)
                    print(f"DEBUG: Sleeping for {jitter:.2f}s before next search...")
                    time.sleep(jitter)
                    
            finally:
                browser.close()
        
        # Remove duplicates
        seen = set()
        unique_deals = []
        for deal in self.deals:
            key = f"{deal['name']}_{deal['price']}"
            if key not in seen:
                seen.add(key)
                unique_deals.append(deal)
        
        self.deals = unique_deals
        print(f"\n✓ Total unique deals found: {len(self.deals)}")
    
    def analyze_deals(self):
        """Analyze and categorize deals"""
        if not self.deals:
            print("No deals to analyze")
            return None
        
        print("\n" + "="*60)
        print("DEAL ANALYSIS")
        print("="*60)
        
        # Check each deal for price changes
        for deal in self.deals:
            change_type = self.check_price_change(deal)
            deal['change_type'] = change_type
            
            self.update_price_history(deal)
            
            if change_type == 'new':
                self.new_deals.append(deal)
            elif change_type == 'price_drop':
                self.price_drops.append(deal)
        
        self.save_price_history()
        
        # Filter alert candidates
        alert_worthy = self.new_deals + self.price_drops
        
        if not alert_worthy:
            print("\n✗ No new deals or price drops to alert")
            return {
                'total': len(self.deals),
                'new': 0,
                'price_drops': 0,
                'alert_deals': []
            }
        
        # Filter by threshold
        cheap_deals = [d for d in alert_worthy if d.get('price', 0) <= CONFIG['price_threshold']]
        high_discount = [d for d in alert_worthy if d.get('discount', 0) >= CONFIG['discount_threshold']]
        
        print(f"New Deals: {len(self.new_deals)}")
        print(f"Price Drops: {len(self.price_drops)}")
        print(f"Alert-Worthy Deals: {len(alert_worthy)}")
        
        # Sort by discount
        alert_worthy.sort(key=lambda x: x.get('discount', 0), reverse=True)
        
        return {
            'total': len(self.deals),
            'new': len(self.new_deals),
            'price_drops': len(self.price_drops),
            'cheap': len(cheap_deals),
            'high_discount': len(high_discount),
            'alert_deals': alert_worthy[:20]
        }
    
    def send_summary_alert(self, analysis):
        """Send summary via Telegram"""
        if not analysis:
            return
        
        new_count = analysis.get('new', 0)
        price_drop_count = analysis.get('price_drops', 0)
        
        if new_count == 0 and price_drop_count == 0:
            return
        
        alert_deals = analysis.get('alert_deals', [])
        
        message = f"""🛒 <b>Swiggy Instamart Deals Alert</b>

📊 <b>Summary:</b>
• New Deals: {analysis['new']}
• Price Drops: {analysis['price_drops']}
"""
        
        for i, deal in enumerate(alert_deals[:CONFIG['telegram_deals_per_category']], 1):
            change_marker = "🆕 NEW" if deal['change_type'] == 'new' else "📉 PRICE DROP"
            name = deal.get('name', 'Unknown')[:80]
            price = deal.get('price', 0)
            discount = deal.get('discount', 0)
            category = deal.get('category', 'General')
            
            message += f"\n{change_marker}\n"
            message += f"{i}. {name}\n"
            message += f"   📁 {category.title()}\n"
            message += f"   ₹{price:,.0f}"
            if discount > 0:
                message += f" ({discount}% off)"
            message += "\n"
            
            if deal['change_type'] == 'price_drop':
                message += f"   Was: ₹{deal.get('old_price', 0):,.0f} (dropped {deal.get('price_drop_pct', 0)}%)\n"
            
            if i >= CONFIG['telegram_deals_per_category']:
                break
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_telegram_alert(message)
        print("✓ Sent alert with new deals and price drops")
        
        # Mark deals as alerted
        self.mark_deals_as_alerted(analysis)
    
    def mark_deals_as_alerted(self, analysis):
        """Mark all deals that were sent in Telegram as 'alerted'"""
        alert_deals = analysis.get('alert_deals', [])
        
        # Limit to the ones we actually sent (top N)
        sent_deals = alert_deals[:CONFIG['telegram_deals_per_category']]
        
        for deal in sent_deals:
            product_key = self.get_product_key(deal)
            if product_key and product_key in self.price_history:
                self.price_history[product_key]['alerted'] = True
        
        self.save_price_history()
        print(f"✓ Marked {len(sent_deals)} deals as alerted")
    
    def save_results(self):
        """Save results to files"""
        if not self.deals:
            print("No deals to save")
            return
        
        with open('swiggy_deals.json', 'w', encoding='utf-8') as f:
            json.dump(self.deals, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(self.deals)} total deals to swiggy_deals.json")
        
        new_and_drops = self.new_deals + self.price_drops
        if new_and_drops:
            with open('swiggy_deals_new.json', 'w', encoding='utf-8') as f:
                json.dump(new_and_drops, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(new_and_drops)} new/changed deals to swiggy_deals_new.json")
        else:
            with open('swiggy_deals_new.json', 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
    
    def run(self):
        """Main execution"""
        try:
            self.scrape_all_deals()
            analysis = self.analyze_deals()
            self.save_results()
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
    tracker = SwiggyPriceTracker()
    tracker.run()
