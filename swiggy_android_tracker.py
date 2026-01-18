from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
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

# Search categories to check
SEARCH_QUERIES = [
    "snacks",
    "biscuits",
    "chocolate",
    "bread",
    "milk",
    "vegetables",
    "fruits"
]

class SwiggyAndroidTracker:
    def __init__(self):
        self.tracked_products = {}
        self.driver = None
    
    def setup_driver(self):
        """Setup Appium driver for Android"""
        print("Setting up Appium connection...")
        
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.automation_name = "UiAutomator2"
        
        # Swiggy app package and activity
        options.app_package = "in.swiggy.android"
        options.app_activity = "in.swiggy.android.activities.HomeActivity"
        
        # Don't reset app to keep login session
        options.no_reset = True
        options.full_reset = False
        
        try:
            self.driver = webdriver.Remote(
                'http://localhost:4723',
                options=options
            )
            print("✓ Connected to Appium server")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Appium: {e}")
            print("\nMake sure:")
            print("1. Appium server is running (appium)")
            print("2. Android device/emulator is connected")
            print("3. USB debugging is enabled")
            print("4. Swiggy app is installed")
            return False
    
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
    
    def navigate_to_instamart(self):
        """Navigate to Instamart section"""
        try:
            print("Navigating to Instamart...")
            
            # Look for Instamart button/tab
            instamart_selectors = [
                '//android.widget.TextView[@text="Instamart"]',
                '//android.widget.TextView[contains(@text, "Instamart")]',
                '//*[contains(@content-desc, "Instamart")]'
            ]
            
            for selector in instamart_selectors:
                try:
                    element = self.driver.find_element(AppiumBy.XPATH, selector)
                    element.click()
                    print("✓ Clicked Instamart")
                    time.sleep(3)
                    return True
                except:
                    continue
            
            print("⚠ Could not find Instamart button, might already be there")
            return True
            
        except Exception as e:
            print(f"Error navigating to Instamart: {e}")
            return False
    
    def search_products(self, query):
        """Search for products"""
        try:
            print(f"\nSearching for: {query}")
            
            # Find search box
            search_selectors = [
                '//android.widget.EditText',
                '//*[@resource-id="in.swiggy.android:id/search_box"]',
                '//*[contains(@text, "Search")]',
                '//android.widget.TextView[contains(@text, "Search")]'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.driver.find_element(AppiumBy.XPATH, selector)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                print("  ✗ Could not find search box")
                return []
            
            # Click search box
            search_box.click()
            time.sleep(2)
            
            # Clear and type query
            search_box.clear()
            time.sleep(0.5)
            search_box.send_keys(query)
            time.sleep(2)
            
            # Press enter
            self.driver.press_keycode(66)  # Enter key
            time.sleep(4)
            
            # Scrape results
            products = self.scrape_current_screen()
            
            # Scroll and scrape more
            for i in range(3):
                self.scroll_down()
                time.sleep(1)
                more_products = self.scrape_current_screen()
                products.extend(more_products)
            
            # Remove duplicates
            seen = {}
            unique_products = []
            for p in products:
                key = f"{p['name']}_{p['price']}"
                if key not in seen:
                    seen[key] = True
                    unique_products.append(p)
            
            print(f"  ✓ Found {len(unique_products)} products")
            return unique_products
            
        except Exception as e:
            print(f"  Error searching: {e}")
            return []
    
    def scroll_down(self):
        """Scroll down the screen"""
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] // 2
            start_y = size['height'] * 0.8
            end_y = size['height'] * 0.2
            
            self.driver.swipe(start_x, start_y, start_x, end_y, 500)
        except:
            pass
    
    def scrape_current_screen(self):
        """Scrape products from current screen"""
        products = []
        
        try:
            # Get page source
            page_source = self.driver.page_source
            
            # Find all text elements
            text_elements = self.driver.find_elements(AppiumBy.XPATH, '//android.widget.TextView')
            
            # Group nearby elements as potential products
            all_texts = []
            for element in text_elements:
                try:
                    text = element.text
                    if text and len(text) > 0:
                        all_texts.append(text)
                except:
                    continue
            
            # Parse products from text
            i = 0
            while i < len(all_texts):
                text = all_texts[i]
                
                # Check if this line has a price
                prices = self.extract_price(text)
                
                if prices:
                    # Look back for product name
                    name = None
                    for j in range(max(0, i-3), i):
                        potential_name = all_texts[j]
                        if len(potential_name) > 5 and not self.extract_price(potential_name):
                            if potential_name.lower() not in ['add', 'added', 'buy', 'notify']:
                                name = potential_name
                                break
                    
                    if name:
                        current_price = min(prices)
                        mrp = max(prices) if len(prices) > 1 else current_price
                        
                        if 1 < current_price < 5000:
                            products.append({
                                'id': name.lower().replace(' ', '_')[:50],
                                'name': name[:100],
                                'price': current_price,
                                'mrp': mrp
                            })
                
                i += 1
            
            return products
            
        except Exception as e:
            print(f"  Error scraping screen: {e}")
            return []
    
    def check_prices(self, products):
        """Check for price drops and send alerts"""
        if not products:
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
            print("SAMPLE PRODUCTS:")
            print("="*70)
            for i, p in enumerate(products[:20]):
                discount = round(((p['mrp'] - p['price']) / p['mrp'] * 100), 1) if p['mrp'] > 0 else 0
                alert_marker = "🔥" if (p['price'] <= PRICE_THRESHOLD or discount >= 70) else "  "
                print(f"{alert_marker} {i+1:2d}. {p['name'][:45]:45s} ₹{p['price']:6.1f} (MRP: ₹{p['mrp']:6.1f}, {discount:5.1f}% off)")
            
            if cheap_products:
                print("\n" + "="*70)
                print(f"PRODUCTS UNDER ₹{PRICE_THRESHOLD}:")
                print("="*70)
                for name, price, mrp, discount in cheap_products[:10]:
                    print(f"🔥 {name[:50]:50s} ₹{price:6.1f} ({discount:.1f}% off)")
    
    def run(self):
        """Main tracking loop"""
        print("="*70)
        print("SWIGGY INSTAMART ANDROID TRACKER")
        print("="*70)
        print(f"Mode: {'TEST (Console)' if TEST_MODE else 'LIVE (Telegram)'}")
        print(f"Alert: Products under ₹{PRICE_THRESHOLD} or >70% discount")
        print("="*70)
        
        if not self.setup_driver():
            return
        
        try:
            # Navigate to Instamart
            self.navigate_to_instamart()
            
            iteration = 0
            
            while True:
                iteration += 1
                print(f"\n\n{'='*70}")
                print(f"CHECK #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                
                all_products = []
                
                # Search for each query
                for query in SEARCH_QUERIES:
                    products = self.search_products(query)
                    all_products.extend(products)
                
                # Remove duplicates
                seen = {}
                unique_products = []
                for p in all_products:
                    key = f"{p['name']}_{p['price']}"
                    if key not in seen:
                        seen[key] = True
                        unique_products.append(p)
                
                print(f"\n✓ Total unique products: {len(unique_products)}")
                
                if unique_products:
                    # Save to file
                    with open('scraped_products.json', 'w', encoding='utf-8') as f:
                        json.dump(unique_products, f, indent=2, ensure_ascii=False)
                    print(f"✓ Saved to scraped_products.json")
                    
                    # Check prices
                    self.check_prices(unique_products)
                
                if TEST_MODE and iteration >= 1:
                    print("\n" + "="*70)
                    print("TEST MODE: Stopping after 1 check")
                    print("Set TEST_MODE=False for continuous monitoring")
                    print("="*70)
                    break
                
                print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Stopping...")
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ Closed app connection")

if __name__ == "__main__":
    tracker = SwiggyAndroidTracker()
    tracker.run()
