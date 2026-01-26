#!/usr/bin/env python3
"""
Swiggy Instamart Price Tracker for GitHub Actions
Monitors Swiggy Instamart deals and sends Telegram notifications
"""

import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
from pathlib import Path
import re
import sys

# Windows Unicode fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Tracking configuration
CONFIG = {
    'price_threshold': 50,  # Alert for products under ₹50
    'discount_threshold': 70,  # Alert for >70% discount
    'price_drop_threshold': 20,  # Alert if price drops by >20%
    'max_products': 50,
    'only_new_deals': True,
    'search_queries': [
        'chocolate',
        'biscuits',
        'snacks',
        'bread',
        'milk',
        'chips',
        'cookies',
        'namkeen'
    ]
}

class SwiggyInstamartTracker:
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
    
    def send_telegram_alert(self, message):
        """Send alert via Telegram"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("Telegram not configured, skipping notification")
            return
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✓ Telegram notification sent")
            else:
                print(f"✗ Telegram error: {response.status_code}")
        except Exception as e:
            print(f"Error sending Telegram: {e}")

    def normalize_name(self, name):
        """Normalize product name for consistent matching"""
        normalized = ' '.join(name.lower().split())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def get_product_key(self, product):
        """Generate a consistent product key for tracking"""
        normalized_name = self.normalize_name(product['name'])
        return f"name_{normalized_name[:100]}_{int(product['price'])}"
    
    def parse_accessibility_node(self, node, products):
        """Recursively traverse accessibility tree to find products"""
        # Heuristic: A product usually has a name, price, and maybe discount in its children
        # We look for leaf text nodes and aggregate them if they are close
        
        # This is a simplified traversal that collects potential product attributes from subtrees
        # Since the accessibility tree structure can vary, we treat "Generic" containers as potential items
        
        if not node:
            return

        role = node.get('role', '')
        name = node.get('name', '')
        children = node.get('children', [])
        
        # If this node looks like a product container (often 'generic' or 'group' or 'link')
        # We check its children for the required components
        if role in ['generic', 'group', 'link', 'button']:
             # Deep dive for text
             text_content = self.get_all_text(node)
             product = self.parse_product_text(text_content)
             if product:
                 products.append(product)
                 return # If we found a product, assume this subtree is handled

        for child in children:
            self.parse_accessibility_node(child, products)

    def get_all_text(self, node):
        """Collect all text from a node's subtree"""
        text = []
        if 'name' in node and node['name']:
            text.append(node['name'])
        
        for child in node.get('children', []):
            text.extend(self.get_all_text(child))
        return text

    def parse_product_text(self, text_list):
        """Parse a list of strings from a subtree to see if it makes a product"""
        # Join into lines to mimic the text-based parser structure
        full_text = "\n".join(text_list)
        
        # Must have price
        price_matches = re.findall(r'₹\s*([0-9,]+(?:\.\d+)?)', full_text)
        if not price_matches:
            return None
        
        clean_prices = [float(p.replace(',', '')) for p in price_matches]
        price = min(clean_prices) # Usually the selling price is the lower one
        mrp = max(clean_prices) if len(clean_prices) > 1 else price
        
        # Name heuristics
        name = None
        for line in text_list:
            if len(line) < 5 or '₹' in line or 'MINS' in line or 'OFF' in line:
                continue
            if line.lower() in ['add', 'customisable', 'out of stock']:
                continue
            name = line
            break
            
        if not name:
            return None

        # Discount
        discount = 0
        discount_match = re.search(r'(\d+)%\s*OFF', full_text)
        if discount_match:
            discount = int(discount_match.group(1))
        elif mrp > price:
             discount = round(((mrp - price) / mrp) * 100, 1)

        if price < 1 or price > 10000: # Sanity check
            return None

        return {
            'name': name[:200],
            'price': price,
            'mrp': mrp,
            'discount': discount,
            'timestamp': datetime.now().isoformat()
        }

    def parse_html_fallback(self, html_content):
        """Fallback: Extract products from HTML when accessibility fails"""
        products = []
        import re
        
        # Strip tags to get text
        text = re.sub(r'<[^>]+>', '\n', html_content)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            # Look for price
            if '₹' in line:
                price_match = re.search(r'₹\s*([0-9,]+)', line)
                if not price_match: 
                    continue
                    
                price = float(price_match.group(1).replace(',', ''))
                
                # Look backwards for Name
                name = None
                for j in range(1, 15):
                    if i - j < 0: break
                    prev_line = lines[i-j]
                    if len(prev_line) > 5 and '₹' not in prev_line and 'OFF' not in prev_line:
                        if prev_line.lower() not in ['add', 'customisable']:
                             name = prev_line
                             break
                
                if not name: continue
                
                # Look for Discount
                discount = 0
                for j in range(-5, 5):
                    if i + j < 0 or i + j >= len(lines): continue
                    context_line = lines[i+j]
                    disc_match = re.search(r'(\d+)%\s*OFF', context_line)
                    if disc_match:
                        discount = int(disc_match.group(1))
                        break
                
                products.append({
                    'name': name[:200],
                    'price': price,
                    'discount': discount,
                    'mrp': price, 
                    'timestamp': datetime.now().isoformat()
                })
                
        return products

    def search_and_scrape(self, page, search_query):
        """Search for products using accessibility snapshot"""
        print(f"\n{'='*60}")
        print(f"Searching: {search_query}")
        print('='*60)
        
        products = []
        
        try:
            # Navigate directly to search results
            url = f"https://www.swiggy.com/instamart/search?custom_back=true&query={search_query.replace(' ', '%20')}"
            print(f"Navigating to: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=45000)
            
            print("Waiting for results to load...")
            time.sleep(5)
            
            # Scroll aggressively to load products
            print("Scrolling to load products...")
            for i in range(5):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1)
            
            # Take screenshot
            screenshot_path = self.screenshots_dir / f'swiggy_search_{search_query.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            page.screenshot(path=str(screenshot_path))
            print(f"✓ Screenshot saved: {screenshot_path}")
            
            # Use Accessibility Snapshot
            print("Getting accessibility snapshot...")
            try:
                print(f"Page Object Type: {type(page)}")
                snapshot = page.accessibility.snapshot()
                
                # Parse Tree
                found_products = []
                self.parse_accessibility_node(snapshot, found_products)
                
            except Exception as e:
                print(f"⚠ Accessibility snapshot failed: {e}")
                print("Falling back to HTML parsing...")
                
                # Fallback: Parse HTML directly using regex (simplified)
                content = page.content()
                found_products = self.parse_html_fallback(content)

            # Filter and deduplicate
            seen_sigs = set()
            for p in found_products:
                p['search_query'] = search_query
                p['is_deal'] = self.is_deal(p['price'], p['discount'])
                
                sig = f"{p['name']}_{p['price']}"
                if sig not in seen_sigs:
                    seen_sigs.add(sig)
                    products.append(p)
            
            print(f"✓ Extracted {len(products)} products from accessibility tree")
            return products[0:CONFIG['max_products']]
            
        except Exception as e:
            print(f"✗ Error searching {search_query}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def is_deal(self, price, discount):
        """Check if product qualifies as a deal"""
        if price <= CONFIG['price_threshold']:
            return True
        if discount >= CONFIG['discount_threshold']:
            return True
        return False
    
    def check_price_change(self, product):
        """Check if this is a new deal or price drop"""
        product_key = self.get_product_key(product)
        
        if not product_key:
            print(f"⚠ No key for product: {product['name'][:50]}")
            return 'new'
        
        if product_key not in self.price_history:
            print(f"🆕 New product: {product['name'][:50]}")
            return 'new'
        
        old_data = self.price_history[product_key]
        old_price = old_data.get('price', 0)
        
        if old_price == 0:
            return 'new'
        
        price_drop_pct = ((old_price - product['price']) / old_price) * 100
        
        if price_drop_pct >= CONFIG['price_drop_threshold']:
            product['old_price'] = old_price
            product['price_drop_pct'] = round(price_drop_pct, 1)
            print(f"📉 Price drop: {product['name'][:50]} (₹{old_price} → ₹{product['price']})")
            return 'price_drop'
        
        if product['price'] >= old_price:
            print(f"✓ Same price: {product['name'][:50]} (₹{product['price']})")
            return 'same'
        
        print(f"→ Minor drop: {product['name'][:50]} (₹{old_price} → ₹{product['price']})")
        return 'minor_drop'
    
    def update_price_history(self, product):
        """Update price history for a product"""
        product_key = self.get_product_key(product)
        
        if product_key:
            self.price_history[product_key] = {
                'name': product['name'],
                'price': product['price'],
                'discount': product['discount'],
                'last_seen': product['timestamp']
            }
    
    def scrape_all_deals(self):
        """Scrape deals from multiple categories"""
        print("\n" + "="*60)
        print("SWIGGY INSTAMART PRICE TRACKER - STARTING")
        print("="*60)
        
        with sync_playwright() as p:
            # Stealth Browser Setup
            browser = p.chromium.launch(
                headless=True, # Run headless for automation
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='en-IN',
                timezone_id='Asia/Kolkata',
                permissions=['geolocation'],
                geolocation={'latitude': 12.9716, 'longitude': 77.5946},
                extra_http_headers={'Accept-Language': 'en-IN,en;q=0.9'}
            )
            
            page = context.new_page()
            
            # Hide automation
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)
            
            try:
                # Search for each query
                for search_query in CONFIG['search_queries']:
                    products = self.search_and_scrape(page, search_query)
                    self.deals.extend(products)
                    time.sleep(2)  # Rate limiting
                
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
            return
        
        print("\n" + "="*60)
        print("DEAL ANALYSIS")
        print("="*60)
        
        print(f"Total Deals Scraped: {len(self.deals)}")
        
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
        
        alert_worthy = self.new_deals + self.price_drops
        
        if not alert_worthy:
            print("\n✗ No new deals or price drops to alert")
            return {
                'total': len(self.deals),
                'new': 0,
                'price_drops': 0,
                'cheap': 0,
                'high_discount': 0,
                'alert_deals': []
            }
        
        cheap_deals = [d for d in alert_worthy if d['price'] <= CONFIG['price_threshold']]
        high_discount = [d for d in alert_worthy if d['discount'] >= CONFIG['discount_threshold']]
        
        print(f"New Deals: {len(self.new_deals)}")
        print(f"Price Drops: {len(self.price_drops)}")
        print(f"Alert-Worthy Deals: {len(alert_worthy)}")
        print(f"  - Cheap Deals (≤₹{CONFIG['price_threshold']}): {len(cheap_deals)}")
        print(f"  - High Discount (≥{CONFIG['discount_threshold']}%): {len(high_discount)}")
        
        # Sort by discount
        alert_worthy.sort(key=lambda x: x['discount'], reverse=True)
        
        if alert_worthy:
            print("\n🔥 NEW DEALS:")
            for i, deal in enumerate(alert_worthy[:10], 1):
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
            'alert_deals': alert_worthy[:10]
        }
    
    def send_summary_alert(self, analysis):
        """Send summary via Telegram"""
        if not analysis:
            print("No analysis data")
            return
        
        new_count = analysis.get('new', 0)
        price_drop_count = analysis.get('price_drops', 0)
        
        if new_count == 0 and price_drop_count == 0:
            message = f"""🛒 <b>Swiggy Instamart Check</b>
            
✓ No new deals or price drops found

All tracked products have the same prices as before.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            self.send_telegram_alert(message)
            print("✓ Sent 'no new deals' notification")
            return
        
        alert_deals = analysis.get('alert_deals', [])
        
        message = f"""🛒 <b>Swiggy Instamart Deals Alert</b>

📊 <b>Summary:</b>
• New Deals: {analysis['new']}
• Price Drops: {analysis['price_drops']}
• Cheap Deals (≤₹{CONFIG['price_threshold']}): {analysis['cheap']}
• High Discount (≥{CONFIG['discount_threshold']}%): {analysis['high_discount']}

🔥 <b>Top Deals:</b>
"""
        
        for i, deal in enumerate(alert_deals[:10], 1):
            change_marker = "🆕 NEW" if deal['change_type'] == 'new' else "📉 PRICE DROP"
            message += f"\n{change_marker}\n"
            message += f"{i}. {deal['name'][:80]}\n"
            message += f"   ₹{deal['price']:,} ({deal['discount']}% off)\n"
            
            if deal['change_type'] == 'price_drop':
                message += f"   Was: ₹{deal['old_price']:,} (dropped {deal['price_drop_pct']}%)\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_telegram_alert(message)
        print("✓ Sent alert with new deals and price drops")
    
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
            print("✓ No new deals - saved empty swiggy_deals_new.json")
    
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
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    tracker = SwiggyInstamartTracker()
    tracker.run()
