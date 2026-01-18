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
                    
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
    
    def extract_price(self, text):
        """Extract price from text"""
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
            print("  Scrolling to load products...")
            for i in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
            
            # Get all div elements
            all_elements = page.query_selector_all('div')
            print(f"  Analyzing {len(all_elements)} elements...")
            
            product_count = 0
            for element in all_elements:
                try:
                    text = element.inner_text()
                    
                    # Skip if too short or too long
                    if len(text) < 10 or len(text) > 500:
                        continue
                    
                    # Must contain a price
                    prices = self.extract_price(text)
                    if not prices:
                        continue
                    
                    # Extract lines
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
                        if line.lower() in ['add', 'added', 'buy', 'cart', 'notify', 'notify me', 'out of stock']:
                            continue
                        name = line
                        break
                    
                    if not name:
                        continue
                    
                    # Get prices
                    current_price = min(prices)
                    mrp = max(prices) if len(prices) > 1 else current_price
                    
                    # Sanity checks
                    if current_price > 5000 or current_price < 1:
                        continue
                    
                    product = {
                        'id': f"{name.lower().replace(' ', '_')[:50]}_{product_count}",
                        'name': name[:100],
                        'price': current_price,
                        'mrp': mrp
                    }
                    
                    products.append(product)
                    product_count += 1
                    
                    if product_count > 100:
                        break
                    
                except:
                    continue
            
            # Remove duplicates
            seen = {}
            unique_products = []
            for p in products:
                key = f"{p['name']}_{p['price']}"
                if key not in seen:
                    seen[key] = True
                    unique_products.append(p)
            
            print(f"  ✓ Found {len(unique_products)} unique products")
            return unique_products
            
        except Exception as e:
            print(f"  Error scraping: {e}")
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
            
            discount_pct = round(((mrp - price) / mrp) * 100, 2) if mrp > 0 else 0
            
            if price <= PRICE_THRESHOLD:
                cheap_products.append((name, price, mrp, discount_pct))
            
            should_alert = (0 < price <= PRICE_THRESHOLD) or (discount_pct >= 70)
            
            if should_alert:
                if product_id not in self.tracked_products or self.tracked_products[product_id] != price:
                    self.send_alert(name, price, mrp, discount_pct)
                    self.tracked_products[product_id] = price
                    alert_count += 1
        
        if alert_count == 0:
            print(f"✗ No products matching alert criteria")
        else:
            print(f"✓ Found {alert_count} products matching alert criteria!")
        
        # Display results
        if products:
            print("\n" + "="*70)
            print("ALL PRODUCTS FOUND:")
            print("="*70)
            for i, p in enumerate(products[:30]):
                discount = round(((p['mrp'] - p['price']) / p['mrp'] * 100), 1) if p['mrp'] > 0 else 0
                alert_marker = "🔥" if (p['price'] <= PRICE_THRESHOLD or discount >= 70) else "  "
                print(f"{alert_marker} {i+1:2d}. {p['name'][:45]:45s} ₹{p['price']:6.1f} (MRP: ₹{p['mrp']:6.1f}, {discount:5.1f}% off)")
            
            if cheap_products:
                print("\n" + "="*70)
                print(f"PRODUCTS UNDER ₹{PRICE_THRESHOLD}:")
                print("="*70)
                for name, price, mrp, discount in cheap_products:
                    print(f"🔥 {name[:50]:50s} ₹{price:6.1f} ({discount:.1f}% off)")
    
    def run(self):
        """Main tracking loop"""
        print("="*70)
        print("SWIGGY INSTAMART PRICE TRACKER - MANUAL MODE")
        print("="*70)
        print(f"Mode: {'TEST (Console)' if TEST_MODE else 'LIVE (Telegram)'}")
        print(f"Alert: Products under ₹{PRICE_THRESHOLD} or >70% discount")
        print("="*70)
        
        with sync_playwright() as p:
            print("\nLaunching browser...")
            
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                print("\nOpening Swiggy Instamart Bangalore...")
                page.goto("https://www.swiggy.com/instamart/city/bangalore", wait_until="domcontentloaded")
                time.sleep(3)
                
                print("\n" + "="*70)
                print("MANUAL SETUP")
                print("="*70)
                print("A browser window has opened with Bangalore location.")
                print("\nPlease do the following:")
                print("1. Browse to ANY category or search for products")
                print("2. Scroll to see products on the page")
                print("3. Come back here and press ENTER")
                print("\nThe script will scrape whatever products are visible!")
                print("="*70)
                
                input("\nPress ENTER when products are visible...")
                
                iteration = 0
                
                while True:
                    iteration += 1
                    print(f"\n\n{'='*70}")
                    print(f"CHECK #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*70)
                    
                    # Scrape current page
                    products = self.scrape_products(page)
                    
                    if products:
                        # Save to file
                        with open('scraped_products.json', 'w', encoding='utf-8') as f:
                            json.dump(products, f, indent=2, ensure_ascii=False)
                        print(f"✓ Saved to scraped_products.json")
                        
                        # Check prices
                        self.check_prices(products)
                    else:
                        print("❌ No products found")
                        page.screenshot(path="debug.png")
                        print("Screenshot saved as debug.png")
                    
                    if TEST_MODE and iteration >= 1:
                        print("\n" + "="*70)
                        print("TEST MODE: Stopping after 1 check")
                        print("\nTo run continuously:")
                        print("- Set TEST_MODE=False in the script")
                        print("- The browser will stay open")
                        print("- You can browse different categories")
                        print("- It will re-scrape every 5 minutes")
                        print("="*70)
                        break
                    
                    print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds...")
                    print("(You can browse to different categories in the browser)")
                    time.sleep(CHECK_INTERVAL)
                    
            except KeyboardInterrupt:
                print("\n\n⏹ Stopping...")
            finally:
                print("\nClosing browser...")
                browser.close()

if __name__ == "__main__":
    tracker = SwiggyPriceTracker()
    tracker.run()
