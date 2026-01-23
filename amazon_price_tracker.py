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
    'max_products': 50,  # Max products to track per run
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
        'today deals',
        'clearance sale'
    ]
}

class AmazonPriceTracker:
    def __init__(self):
        self.deals = []
        self.screenshots_dir = Path('screenshots')
        self.screenshots_dir.mkdir(exist_ok=True)
        
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
        
        # Filter deals
        cheap_deals = [d for d in self.deals if d['price'] <= CONFIG['price_threshold']]
        high_discount = [d for d in self.deals if d['discount'] >= CONFIG['discount_threshold']]
        
        print(f"Total Deals: {len(self.deals)}")
        print(f"Cheap Deals (≤₹{CONFIG['price_threshold']}): {len(cheap_deals)}")
        print(f"High Discount (≥{CONFIG['discount_threshold']}%): {len(high_discount)}")
        
        # Top deals
        top_deals = sorted(self.deals, key=lambda x: x['discount'], reverse=True)[:10]
        
        print("\n🔥 TOP 10 DEALS:")
        for i, deal in enumerate(top_deals, 1):
            print(f"{i}. {deal['name'][:60]}")
            print(f"   ₹{deal['price']} ({deal['discount']}% off)")
            if deal['link']:
                print(f"   {deal['link']}")
            print()
        
        return {
            'total': len(self.deals),
            'cheap': len(cheap_deals),
            'high_discount': len(high_discount),
            'top_deals': top_deals
        }
    
    def send_summary_alert(self, analysis):
        """Send summary via Telegram"""
        if not analysis:
            return
        
        message = f"""🛒 <b>Amazon Deals Update</b>

📊 <b>Summary:</b>
• Total Deals: {analysis['total']}
• Cheap Deals (≤₹{CONFIG['price_threshold']}): {analysis['cheap']}
• High Discount (≥{CONFIG['discount_threshold']}%): {analysis['high_discount']}

🔥 <b>Top 5 Deals:</b>
"""
        
        for i, deal in enumerate(analysis['top_deals'][:5], 1):
            message += f"\n{i}. {deal['name'][:80]}\n"
            message += f"   ₹{deal['price']} ({deal['discount']}% off)\n"
            if deal['link']:
                message += f"   <a href='{deal['link']}'>View Deal</a>\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_telegram_alert(message)
    
    def save_results(self):
        """Save results to files"""
        if not self.deals:
            print("No deals to save")
            return
        
        # Save JSON
        with open('amazon_deals.json', 'w', encoding='utf-8') as f:
            json.dump(self.deals, f, indent=2, ensure_ascii=False)
        print("✓ Saved to amazon_deals.json")
        
        # Save CSV
        if self.deals:
            keys = ['name', 'price', 'discount', 'category', 'link', 'rating', 'timestamp']
            with open('amazon_deals.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for deal in self.deals:
                    row = {k: deal.get(k, '') for k in keys}
                    writer.writerow(row)
            print("✓ Saved to amazon_deals.csv")
    
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
            if analysis and (analysis['cheap'] > 0 or analysis['high_discount'] > 0):
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
    tracker = AmazonPriceTracker()
    tracker.run()
