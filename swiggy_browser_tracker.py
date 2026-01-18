from playwright.sync_api import sync_playwright
import time
import requests
import json
from datetime import datetime
import re

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
CHECK_INTERVAL = 300  # Check every 5 minutes
PRICE_THRESHOLD = 50  # Alert for products under Rs 50
TEST_MODE = True  # Set to False to enable Telegram notifications

SWIGGY_URL = "https://www.swiggy.com/instamart/city/bangalore"

class SwiggyPriceTracker:
    def __init__(self):
        self.tracked_products = {}
    
    def send_alert(self, product_name, price, original_price, discount_pct):
        """Send alert via Telegram or print to console"""
        message = f"""🔥 PRICE ALERT! 🔥
        
Product: {product_name}
Current Price: ₹{price}
Original Price: ₹{original_price}
Discount: {discount_pct}%

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if TEST_MODE:
            print("\n" + "="*60)
            print(message)
            print("="*60 + "\n")
        else:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': message
                }
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    print(f"✓ Alert sent for: {product_name}")
                else:
                    print(f"✗ Failed to send alert")
                    
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
    
    def extract_price(self, text):
        """Extract price from text"""
        # Match ₹XX or Rs XX
        matches = re.findall(r'₹\s*(\d+(?:\.\d+)?)|Rs\.?\s*(\d+(?:\.\d+)?)', text)
        prices = []
        for match in matches:
            price_val = match[0] if match[0] else match[1]
            if price_val:
                prices.append(float(price_val))
        return prices
    
    def scrape_products(self, page):
        """Scrape products from the current page"""
        products = []
        
        try:
            # Wait for products to load
            print("Waiting for products to load...")
            page.wait_for_selector('[class*="product"], [class*="Product"], [data-testid*="product"]', timeout=10000)
            
            # Scroll to load more products
            print("Scrolling to load more products...")
            for i in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            # Get all product elements - try multiple selectors
            selectors = [
                '[data-testid*="product"]',
                '[class*="ProductCard"]',
                '[class*="product-card"]',
                'div[class*="product"]',
            ]
            
            product_elements = []
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements and len(elements) > 5:  # Need reasonable number of products
                        product_elements = elements
                        print(f"✓ Found {len(elements)} products using selector: {selector}")
                        break
                except:
                    continue
            
            if not product_elements:
                print("❌ No products found. Saving screenshot for debugging...")
                page.screenshot(path="swiggy_debug.png")
                print("Screenshot saved as swiggy_debug.png")
                return []
            
            # Extract data from each product
            for i, element in enumerate(product_elements[:50]):  # Limit to 50 products
                try:
                    # Get all text from the element
                    text = element.inner_text()
                    
                    # Extract product name (usually first line or largest text)
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if not lines:
                        continue
                    
                    # First non-price line is usually the name
                    name = None
                    for line in lines:
                        if not re.search(r'₹|Rs\.?|\d+%', line):
                            name = line
                            break
                    
                    if not name:
                        name = lines[0]
                    
                    # Extract prices
                    prices = self.extract_price(text)
                    
                    if not prices or not name:
                        continue
                    
                    # First price is usually selling price, second is MRP
                    current_price = min(prices)
                    mrp = max(prices) if len(prices) > 1 else current_price
                    
                    # Skip if price is too high (likely parsing error)
                    if current_price > 10000:
                        continue
                    
                    product = {
                        'id': f"{name.lower().replace(' ', '_')[:50]}_{i}",
                        'name': name[:100],
                        'price': current_price,
                        'mrp': mrp
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    continue
            
            # Remove duplicates based on name
            seen = set()
            unique_products = []
            for p in products:
                if p['name'] not in seen:
                    seen.add(p['name'])
                    unique_products.append(p)
            
            return unique_products
            
        except Exception as e:
            print(f"Error scraping products: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def check_prices(self, products):
        """Check for price drops and send alerts"""
        if not products:
            print("No products to analyze")
            return
        
        print(f"\nAnalyzing {len(products)} products...")
        
        alert_count = 0
        cheap_products = []
        
        for product in products:
            product_id = product['id']
            name = product['name']
            price = product['price']
            mrp = product['mrp']
            
            # Calculate discount
            if mrp > 0 and price > 0:
                discount_pct = round(((mrp - price) / mrp) * 100, 2)
            else:
                discount_pct = 0
            
            # Track cheap products for display
            if price <= PRICE_THRESHOLD:
                cheap_products.append((name, price, mrp, discount_pct))
            
            # Alert conditions
            should_alert = False
            
            if 0 < price <= PRICE_THRESHOLD:
                should_alert = True
            
            if discount_pct >= 70:
                should_alert = True
            
            if should_alert:
                if product_id not in self.tracked_products or self.tracked_products[product_id] != price:
                    self.send_alert(name, price, mrp, discount_pct)
                    self.tracked_products[product_id] = price
                    alert_count += 1
        
        if alert_count == 0:
            print(f"✗ No products found matching alert criteria (under ₹{PRICE_THRESHOLD} or >70% discount)")
        else:
            print(f"✓ Found {alert_count} products matching alert criteria!")
        
        # Show sample products
        if products:
            print("\n" + "="*70)
            print("SAMPLE PRODUCTS (First 20):")
            print("="*70)
            for i, p in enumerate(products[:20]):
                discount = round(((p['mrp'] - p['price']) / p['mrp'] * 100), 1) if p['mrp'] > 0 else 0
                alert_marker = "🔥" if (p['price'] <= PRICE_THRESHOLD or discount >= 70) else "  "
                print(f"{alert_marker} {i+1:2d}. {p['name'][:45]:45s} ₹{p['price']:6.1f} (MRP: ₹{p['mrp']:6.1f}, {discount:5.1f}% off)")
            
            if cheap_products:
                print("\n" + "="*70)
                print(f"PRODUCTS UNDER ₹{PRICE_THRESHOLD}:")
                print("="*70)
                for name, price, mrp, discount in cheap_products[:15]:
                    print(f"🔥 {name[:50]:50s} ₹{price:6.1f} ({discount:.1f}% off)")
    
    def setup_location(self, page):
        """Handle location setup"""
        print("\n" + "="*70)
        print("LOCATION SETUP")
        print("="*70)
        print("Please set your location to Bangalore in the browser window.")
        print("The script will wait for 30 seconds for you to:")
        print("1. Enter 'Bangalore' in the location field")
        print("2. Select your specific area")
        print("3. Wait for products to load")
        print("\nWaiting...")
        
        time.sleep(30)
        print("✓ Continuing with scraping...")
    
    def run(self):
        """Main tracking loop"""
        print("="*70)
        print("SWIGGY INSTAMART PRICE TRACKER (Browser-Based)")
        print("="*70)
        print(f"Mode: {'TEST (Console Output)' if TEST_MODE else 'LIVE (Telegram Alerts)'}")
        print(f"Alert Threshold: Products under ₹{PRICE_THRESHOLD} or >70% discount")
        print("="*70)
        
        with sync_playwright() as p:
            print("\nLaunching browser...")
            browser = p.chromium.launch(headless=False)  # Set to True to hide browser
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                iteration = 0
                location_set = False
                
                while True:
                    iteration += 1
                    print(f"\n\n{'='*70}")
                    print(f"CHECK #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*70)
                    
                    # Navigate to Swiggy
                    print(f"Loading {SWIGGY_URL}...")
                    page.goto(SWIGGY_URL, wait_until="domcontentloaded")
                    time.sleep(5)
                    
                    # Handle location setup on first run
                    if not location_set:
                        self.setup_location(page)
                        location_set = True
                    
                    # Scrape products
                    products = self.scrape_products(page)
                    
                    if products:
                        # Save products to file
                        with open('scraped_products.json', 'w', encoding='utf-8') as f:
                            json.dump(products, f, indent=2, ensure_ascii=False)
                        print(f"✓ Saved {len(products)} products to scraped_products.json")
                        
                        # Check prices
                        self.check_prices(products)
                    else:
                        print("❌ No products found. Check screenshot: swiggy_debug.png")
                    
                    if TEST_MODE and iteration >= 1:
                        print("\n" + "="*70)
                        print("TEST MODE: Stopping after 1 check")
                        print("Set TEST_MODE=False for continuous monitoring")
                        print("="*70)
                        break
                    
                    print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds before next check...")
                    time.sleep(CHECK_INTERVAL)
                    
            except KeyboardInterrupt:
                print("\n\n⏹ Stopping tracker...")
            finally:
                browser.close()
                print("Browser closed")

if __name__ == "__main__":
    tracker = SwiggyPriceTracker()
    tracker.run()
