from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
CHECK_INTERVAL = 300  # Check every 5 minutes
PRICE_THRESHOLD = 50  # Alert for products under Rs 50
TEST_MODE = True  # Set to False to enable Telegram notifications

# Bangalore location URL
SWIGGY_URL = "https://www.swiggy.com/instamart"

class SwiggyPriceTracker:
    def __init__(self):
        self.tracked_products = {}
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome driver initialized successfully")
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            print("\nPlease ensure Chrome browser is installed")
            raise
    
    def fetch_products(self):
        """Scrape products from Swiggy Instamart"""
        try:
            print(f"Loading {SWIGGY_URL}...")
            self.driver.get(SWIGGY_URL)
            
            # Wait for location popup or products to load
            time.sleep(5)
            
            # Try to handle location popup if it appears
            try:
                # Look for location input or allow location button
                location_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    'input[placeholder*="location"], button[aria-label*="location"]')
                if location_elements:
                    print("Location popup detected, may need manual intervention")
            except:
                pass
            
            # Scroll to load more products
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract product data
            products = []
            
            # Try multiple selectors for product cards
            selectors = [
                '[data-testid="product-card"]',
                '.product-card',
                '[class*="ProductCard"]',
                '[class*="product"]'
            ]
            
            product_elements = []
            for selector in selectors:
                product_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if product_elements:
                    print(f"Found {len(product_elements)} products using selector: {selector}")
                    break
            
            if not product_elements:
                print("No products found. Page might need location setup.")
                # Save screenshot for debugging
                self.driver.save_screenshot('swiggy_debug.png')
                print("Screenshot saved as swiggy_debug.png")
                return []
            
            for element in product_elements[:50]:  # Limit to first 50 products
                try:
                    product = self.parse_product_element(element)
                    if product:
                        products.append(product)
                except Exception as e:
                    continue
            
            return products
            
        except Exception as e:
            print(f"Error fetching products: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def parse_product_element(self, element):
        """Extract product data from a product card element"""
        try:
            # Get product name
            name_selectors = ['h3', 'h4', '[class*="name"]', '[class*="title"]']
            name = None
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name:
                        break
                except:
                    continue
            
            if not name:
                return None
            
            # Get prices
            price_text = element.text
            
            # Extract current price (₹XX or Rs XX)
            import re
            price_matches = re.findall(r'₹\s*(\d+(?:\.\d+)?)|Rs\.?\s*(\d+(?:\.\d+)?)', price_text)
            
            if not price_matches:
                return None
            
            prices = []
            for match in price_matches:
                price_val = match[0] if match[0] else match[1]
                if price_val:
                    prices.append(float(price_val))
            
            if not prices:
                return None
            
            # First price is usually selling price, second is MRP
            current_price = min(prices)
            mrp = max(prices) if len(prices) > 1 else current_price
            
            # Generate a simple ID from name
            product_id = name.lower().replace(' ', '_')[:50]
            
            return {
                'id': product_id,
                'name': name,
                'price': current_price,
                'mrp': mrp
            }
            
        except Exception as e:
            return None
    
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
                    print(f"Alert sent for: {product_name}")
                else:
                    print(f"Failed to send alert: {response.text}")
                    
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
    
    def check_prices(self, products):
        """Check for price drops and send alerts"""
        if not products:
            print("No products to check")
            return
        
        print(f"\nAnalyzing {len(products)} products...")
        
        alert_count = 0
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
            print(f"No products found matching alert criteria (under ₹{PRICE_THRESHOLD} or >70% discount)")
        
        # Show sample products in test mode
        if TEST_MODE and products:
            print("\nSample products found:")
            for i, p in enumerate(products[:10]):
                discount = round(((p['mrp'] - p['price']) / p['mrp'] * 100), 1) if p['mrp'] > 0 else 0
                print(f"  {i+1}. {p['name'][:50]} - ₹{p['price']} (MRP: ₹{p['mrp']}, {discount}% off)")
    
    def run(self):
        """Main tracking loop"""
        print("Starting Swiggy Instamart Price Tracker (Selenium)...")
        print(f"Mode: {'TEST (Console Output)' if TEST_MODE else 'LIVE (Telegram Alerts)'}")
        print(f"Monitoring for products under ₹{PRICE_THRESHOLD}\n")
        
        try:
            iteration = 0
            while True:
                iteration += 1
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Check #{iteration}")
                
                products = self.fetch_products()
                self.check_prices(products)
                
                if TEST_MODE and iteration >= 1:
                    print("\nTest mode: Stopping after 1 check.")
                    break
                
                print(f"\nWaiting {CHECK_INTERVAL} seconds before next check...")
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nStopping tracker...")
        finally:
            self.driver.quit()
            print("Browser closed")

if __name__ == "__main__":
    tracker = SwiggyPriceTracker()
    tracker.run()
