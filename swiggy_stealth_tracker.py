#!/usr/bin/env python3
"""
Swiggy Instamart Price Tracker with Stealth Mode
Bypasses bot detection to scrape deals
"""

import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
from pathlib import Path
import re

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

CONFIG = {
    'price_threshold': 50,
    'discount_threshold': 70,
    'price_drop_threshold': 20,
    'max_products': 50,
    'only_new_deals': True,
    'search_queries': [
        'chocolate',
        'biscuits',
        'snacks',
        'bread',
        'chips',
        'cookies',
        'namkeen',
        'instant noodles'
    ]
}

class SwiggyStealthTracker:
    def __init__(self):
        self.deals = []
        self.price_history = self.load_price_history()
        self.new_deals = []
        self.price_drops = []
        self.screenshots_dir = Path('screenshots')
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def load_price_history(self):
        try:
            if Path('swiggy_price_history.json').exists():
                with open('swiggy_price_history.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load price history: {e}")
        return {}
    
    def save_price_history(self):
        try:
            with open('swiggy_price_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.price_history, f, indent=2, ensure_ascii=False)
            print("✓ Price history saved")
        except Exception as e:
            print(f"Error saving price history: {e}")
    
    def send_telegram_alert(self, message):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("Telegram not configured, skipping notification")
            return
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✓ Telegram notification sent")
            else:
                print(f"✗ Telegram error: {response.status_code}")
        except Exception as e:
            print(f"Error sending Telegram: {e}")
    
    def extract_price(self, text):
        matches = re.findall(r'₹\s*([0-9,]+(?:\.\d+)?)', text)
        if matches:
            try:
                return float(matches[0].replace(',', ''))
            except:
                pass
        return None
    
    def normalize_name(self, name):
        normalized = ' '.join(name.lower().split())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def get_product_key(self, product):
        normalized_name = self.normalize_name(product['name'])
        return f"name_{normalized_name[:100]}_{int(product['price'])}"
    
    def scrape_search_results(self, page, search_query):
        """Scrape products from search results"""
        print(f"\n{'='*60}")
        print(f"Searching: {search_query}")
        print('='*60)
        
        products = []
        
        try:
            # Find search input
            search_input = page.query_selector('input')
            if not search_input:
                print("✗ Search input not found")
                return []
            
            print(f"Typing '{search_query}'...")
            search_input.click()
            time.sleep(0.5)
            search_input.fill('')  # Clear first
            time.sleep(0.3)
            
            # Type slowly (human-like)
            for char in search_query:
                search_input.type(char)
                time.sleep(0.08)
            
            print("Waiting for results...")
            time.sleep(4)
            
            # Scroll to load more
            for i in range(3):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1)
            
            # Screenshot
            screenshot_path = self.screenshots_dir / f'swiggy_{search_query.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            page.screenshot(path=str(screenshot_path))
            print(f"✓ Screenshot: {screenshot_path}")
            
            # Extract products
            all_divs = page.query_selector_all('div')
            
            for div in all_divs:
                try:
                    text = div.inner_text()
                    
                    if len(text) < 10 or len(text) > 500:
                        continue
                    
                    price = self.extract_price(text)
                    if not price or price < 1 or price > 5000:
                        continue
                    
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if len(lines) < 2:
                        continue
                    
                    # Find product name
                    name = None
                    for line in lines:
                        if re.search(r'₹|Rs\.?|\d+%\s*(off|OFF)', line):
                            continue
                        if len(line) < 5:
                            continue
                        if line.lower() in ['add', 'added', 'buy', 'cart', 'notify']:
                            continue
                        name = line
                        break
                    
                    if not name:
                        continue
                    
                    # Extract MRP
                    all_prices = re.findall(r'₹\s*([0-9,]+(?:\.\d+)?)', text)
                    prices = [float(p.replace(',', '')) for p in all_prices if p]
                    
                    mrp = max(prices) if len(prices) > 1 else price
                    discount = round(((mrp - price) / mrp) * 100, 1) if mrp > price else 0
                    
                    product = {
                        'name': name[:200],
                        'price': price,
                        'mrp': mrp,
                        'discount': discount,
                        'search_query': search_query,
                        'timestamp': datetime.now().isoformat(),
                        'is_deal': price <= CONFIG['price_threshold'] or discount >= CONFIG['discount_threshold']
                    }
                    
                    products.append(product)
                    
                except:
                    continue
            
            print(f"✓ Extracted {len(products)} products")
            return products
            
        except Exception as e:
            print(f"✗ Error searching {search_query}: {e}")
            return []
    
    def check_price_change(self, product):
        product_key = self.get_product_key(product)
        
        if not product_key:
            return 'new'
        
        if product_key not in self.price_history:
            print(f"🆕 New: {product['name'][:50]}")
            return 'new'
        
        old_price = self.price_history[product_key].get('price', 0)
        if old_price == 0:
            return 'new'
        
        price_drop_pct = ((old_price - product['price']) / old_price) * 100
        
        if price_drop_pct >= CONFIG['price_drop_threshold']:
            product['old_price'] = old_price
            product['price_drop_pct'] = round(price_drop_pct, 1)
            print(f"📉 Drop: {product['name'][:50]} (₹{old_price} → ₹{product['price']})")
            return 'price_drop'
        
        if product['price'] >= old_price:
            return 'same'
        
        return 'minor_drop'
    
    def update_price_history(self, product):
        product_key = self.get_product_key(product)
        if product_key:
            self.price_history[product_key] = {
                'name': product['name'],
                'price': product['price'],
                'discount': product['discount'],
                'last_seen': product['timestamp']
            }
    
    def scrape_all_deals(self):
        print("\n" + "="*60)
        print("SWIGGY INSTAMART STEALTH TRACKER - STARTING")
        print("="*60)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,  # Set to False for debugging
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
                window.navigator.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en', 'hi']});
            """)
            
            try:
                print("\nOpening search page...")
                page.goto("https://www.swiggy.com/instamart/search?custom_back=true", 
                         wait_until='domcontentloaded', timeout=60000)
                time.sleep(5)
                
                # Screenshot initial page
                screenshot_path = self.screenshots_dir / f'swiggy_main_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                page.screenshot(path=str(screenshot_path))
                print(f"✓ Main page screenshot: {screenshot_path}")
                
                # Search for each query
                for search_query in CONFIG['search_queries']:
                    products = self.scrape_search_results(page, search_query)
                    self.deals.extend(products)
                    time.sleep(2)
                
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
        if not self.deals:
            print("No deals to analyze")
            return None
        
        print("\n" + "="*60)
        print("DEAL ANALYSIS")
        print("="*60)
        
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
            print("\n✗ No new deals or price drops")
            return {'total': len(self.deals), 'new': 0, 'price_drops': 0, 'alert_deals': []}
        
        cheap_deals = [d for d in alert_worthy if d['price'] <= CONFIG['price_threshold']]
        high_discount = [d for d in alert_worthy if d['discount'] >= CONFIG['discount_threshold']]
        
        print(f"New Deals: {len(self.new_deals)}")
        print(f"Price Drops: {len(self.price_drops)}")
        print(f"Cheap (≤₹{CONFIG['price_threshold']}): {len(cheap_deals)}")
        print(f"High Discount (≥{CONFIG['discount_threshold']}%): {len(high_discount)}")
        
        alert_worthy.sort(key=lambda x: x['discount'], reverse=True)
        
        return {
            'total': len(self.deals),
            'new': len(self.new_deals),
            'price_drops': len(self.price_drops),
            'cheap': len(cheap_deals),
            'high_discount': len(high_discount),
            'alert_deals': alert_worthy[:15]
        }
    
    def send_summary_alert(self, analysis):
        if not analysis:
            return
        
        if analysis['new'] == 0 and analysis['price_drops'] == 0:
            message = f"""🛒 <b>Swiggy Instamart Check</b>

✓ No new deals or price drops found

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            self.send_telegram_alert(message)
            return
        
        alert_deals = analysis['alert_deals']
        
        message = f"""🛒 <b>Swiggy Instamart Deals</b>

📊 <b>Summary:</b>
• New Deals: {analysis['new']}
• Price Drops: {analysis['price_drops']}
• Cheap (≤₹{CONFIG['price_threshold']}): {analysis['cheap']}
• High Discount (≥{CONFIG['discount_threshold']}%): {analysis['high_discount']}

🔥 <b>Top Deals:</b>
"""
        
        for i, deal in enumerate(alert_deals[:10], 1):
            marker = "🆕" if deal['change_type'] == 'new' else "📉"
            message += f"\n{marker} {i}. {deal['name'][:70]}\n"
            message += f"   ₹{deal['price']} ({deal['discount']}% off)\n"
            
            if deal['change_type'] == 'price_drop':
                message += f"   Was: ₹{deal['old_price']} (↓{deal['price_drop_pct']}%)\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_telegram_alert(message)
    
    def save_results(self):
        if not self.deals:
            return
        
        with open('swiggy_deals.json', 'w', encoding='utf-8') as f:
            json.dump(self.deals, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(self.deals)} deals to swiggy_deals.json")
        
        new_and_drops = self.new_deals + self.price_drops
        with open('swiggy_deals_new.json', 'w', encoding='utf-8') as f:
            json.dump(new_and_drops, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(new_and_drops)} new/changed deals")
    
    def run(self):
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
    tracker = SwiggyStealthTracker()
    tracker.run()
