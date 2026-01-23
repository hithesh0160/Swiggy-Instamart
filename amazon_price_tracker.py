#!/usr/bin/env python3
"""
Amazon.in Price Tracker for GitHub Actions
Monitors Amazon deals and sends Telegram notifications
"""

import os
import json
import csv
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
from pathlib import Path

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SEARCH_QUERY = os.getenv('SEARCH_QUERY', '')

# Tracking configuration
CONFIG = {
    'price_threshold': 500,  # Alert for products under ₹500
    'discount_threshold': 50,  # Alert for >50% discount
    'price_drop_threshold': 20,  # Alert if price drops by >20%
    'max_products': 30,  # Reduced from 50 to save time
    'only_new_deals': True,  # Only alert on NEW deals or price drops
    'categories': [
        'electronics',
        'books',
        'home',
        'fashion',
        'grocery'
    ],
    'search_queries': [
        'lightning deals',
        'deals of the day',
        'today deals'
    ]
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
        """Load previous price history"""
        try:
            if Path('price_history.json').exists():
                with open('price_history.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
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
            time.sleep(3)
            
            # Scroll to load more products
            for i in range(3):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1)
            
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
        if price <= CONFIG['price_threshold']:
            return True
        if discount >= CONFIG['discount_threshold']:
            return True
        return False
    
    def check_price_change(self, product):
        """Check if this is a new deal or price drop"""
        product_key = product['asin'] if product['asin'] else product['name']
        
        if not product_key:
            return 'new'  # No way to track, treat as new
        
        # Check if we've seen this product before
        if product_key not in self.price_history:
            return 'new'  # New product
        
        old_data = self.price_history[product_key]
        old_price = old_data.get('price', 0)
        
        if old_price == 0:
            return 'new'
        
        # Check if price dropped significantly
        price_drop_pct = ((old_price - product['price']) / old_price) * 100
        
        if price_drop_pct >= CONFIG['price_drop_threshold']:
            product['old_price'] = old_price
            product['price_drop_pct'] = round(price_drop_pct, 1)
            return 'price_drop'
        
        # Same or higher price
        if product['price'] >= old_price:
            return 'same'
        
        # Small price drop (less than threshold)
        return 'minor_drop'
    
    def update_price_history(self, product):
        """Update price history for a product"""
        product_key = product['asin'] if product['asin'] else product['name']
        
        if product_key:
            self.price_history[product_key] = {
                'name': product['name'],
                'price': product['price'],
                'discount': product['discount'],
                'last_seen': product['timestamp']
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
        
        # Check each deal for price changes
        for deal in self.deals:
            change_type = self.check_price_change(deal)
            deal['change_type'] = change_type
            
            # Update price history
            self.update_price_history(deal)
            
            # Categorize
            if change_type == 'new':
                self.new_deals.append(deal)
            elif change_type == 'price_drop':
                self.price_drops.append(deal)
        
        # Save updated price history
        self.save_price_history()
        
        # Filter deals based on config
        if CONFIG['only_new_deals']:
            alert_worthy = self.new_deals + self.price_drops
        else:
            alert_worthy = self.deals
        
        # Further filter by thresholds
        cheap_deals = [d for d in alert_worthy if d['price'] <= CONFIG['price_threshold']]
        high_discount = [d for d in alert_worthy if d['discount'] >= CONFIG['discount_threshold']]
        
        print(f"Total Deals Scraped: {len(self.deals)}")
        print(f"New Deals: {len(self.new_deals)}")
        print(f"Price Drops: {len(self.price_drops)}")
        print(f"Cheap Deals (≤₹{CONFIG['price_threshold']}): {len(cheap_deals)}")
        print(f"High Discount (≥{CONFIG['discount_threshold']}%): {len(high_discount)}")
        
        # Combine and deduplicate alert-worthy deals
        alert_deals = list({d['name']: d for d in (cheap_deals + high_discount)}.values())
        
        # Sort by discount
        alert_deals.sort(key=lambda x: x['discount'], reverse=True)
        
        if alert_deals:
            print("\n🔥 ALERT-WORTHY DEALS:")
            for i, deal in enumerate(alert_deals[:10], 1):
                change_marker = "🆕" if deal['change_type'] == 'new' else "📉"
                print(f"{change_marker} {i}. {deal['name'][:60]}")
                print(f"   ₹{deal['price']} ({deal['discount']}% off)")
                if deal['change_type'] == 'price_drop':
                    print(f"   Price dropped from ₹{deal['old_price']} ({deal['price_drop_pct']}% drop)")
                if deal['link']:
                    print(f"   {deal['link']}")
                print()
        else:
            print("\n✗ No new deals or price drops found")
        
        return {
            'total': len(self.deals),
            'new': len(self.new_deals),
            'price_drops': len(self.price_drops),
            'cheap': len(cheap_deals),
            'high_discount': len(high_discount),
            'alert_deals': alert_deals[:10]
        }
    
    def send_summary_alert(self, analysis):
        """Send summary via Telegram"""
        if not analysis or not analysis.get('alert_deals'):
            print("No alert-worthy deals to send")
            return
        
        alert_deals = analysis['alert_deals']
        
        message = f"""🛒 <b>Amazon Deals Alert</b>

📊 <b>Summary:</b>
• New Deals: {analysis['new']}
• Price Drops: {analysis['price_drops']}
• Cheap Deals (≤₹{CONFIG['price_threshold']}): {analysis['cheap']}
• High Discount (≥{CONFIG['discount_threshold']}%): {analysis['high_discount']}

🔥 <b>Top Deals:</b>
"""
        
        for i, deal in enumerate(alert_deals[:5], 1):
            change_marker = "🆕 NEW" if deal['change_type'] == 'new' else "📉 PRICE DROP"
            message += f"\n{change_marker}\n"
            message += f"{i}. {deal['name'][:80]}\n"
            message += f"   ₹{deal['price']} ({deal['discount']}% off)\n"
            
            if deal['change_type'] == 'price_drop':
                message += f"   Was: ₹{deal['old_price']} (dropped {deal['price_drop_pct']}%)\n"
            
            if deal['link']:
                message += f"   <a href='{deal['link']}'>View Deal</a>\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_telegram_alert(message)
    
    def save_results(self):
        """Save results to files"""
        if not self.deals:
            print("No deals to save")
            return
        
        # Save all deals
        with open('amazon_deals.json', 'w', encoding='utf-8') as f:
            json.dump(self.deals, f, indent=2, ensure_ascii=False)
        print("✓ Saved all deals to amazon_deals.json")
        
        # Save only new deals and price drops
        new_and_drops = self.new_deals + self.price_drops
        if new_and_drops:
            with open('amazon_deals_new.json', 'w', encoding='utf-8') as f:
                json.dump(new_and_drops, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(new_and_drops)} new deals to amazon_deals_new.json")
        
        # Save price changes summary
        price_changes = {
            'timestamp': datetime.now().isoformat(),
            'new_deals': len(self.new_deals),
            'price_drops': len(self.price_drops),
            'deals': new_and_drops
        }
        with open('price_changes.json', 'w', encoding='utf-8') as f:
            json.dump(price_changes, f, indent=2, ensure_ascii=False)
        print("✓ Saved price changes to price_changes.json")
    
    def run(self):
        """Main execution"""
        try:
            # Scrape deals
            self.scrape_all_deals()
            
            # Analyze
            analysis = self.analyze_deals()
            
            # Save results
            self.save_results()
            
            # Send alerts
            if analysis and (analysis['new'] > 0 or analysis['price_drops'] > 0):
                self.send_summary_alert(analysis)
            else:
                print("\n✓ No new deals or price drops - No alert sent")
            
            print("\n" + "="*60)
            print("TRACKING COMPLETE")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    tracker = AmazonPriceTracker()
    tracker.run()
