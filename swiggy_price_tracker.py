import requests
import time
import json
from datetime import datetime
import re

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
CHECK_INTERVAL = 300  # Check every 5 minutes
PRICE_THRESHOLD = 50  # Alert for products under Rs 50
TEST_MODE = True  # Set to False to enable Telegram notifications

# Swiggy Instamart configuration (Bangalore)
LATITUDE = "12.9716"
LONGITUDE = "77.5946"

class SwiggyPriceTracker:
    def __init__(self):
        self.tracked_products = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://www.swiggy.com',
            'Referer': 'https://www.swiggy.com/instamart',
        })
    
    def fetch_products(self):
        """Fetch products from Swiggy Instamart using their listing API"""
        try:
            # Try the main listing endpoint
            url = f"https://www.swiggy.com/api/instamart/home?clientId=INSTAMART-APP&pageNumber=0"
            
            params = {
                'lat': LATITUDE,
                'lng': LONGITUDE,
            }
            
            print(f"Fetching from: {url}")
            response = self.session.get(url, params=params, timeout=15)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response length: {len(response.text)} bytes")
            
            if response.status_code == 200:
                data = response.json()
                # Save response for debugging
                with open('swiggy_response.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("Response saved to swiggy_response.json")
                return data
            else:
                print(f"API Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"Error fetching products: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def send_telegram_alert(self, product_name, price, original_price, discount_pct):
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
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    print(f"Alert sent for: {product_name}")
                else:
                    print(f"Failed to send alert: {response.text}")
                    
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
    
    def check_prices(self, data):
        """Check for price drops and send alerts"""
        if not data:
            return
        
        products = self.extract_products(data)
        
        print(f"Found {len(products)} products to analyze")
        
        alert_count = 0
        for product in products:
            product_id = product.get('id')
            name = product.get('name', 'Unknown')
            price = product.get('price', 0)
            original_price = product.get('mrp', price)
            
            # Calculate discount percentage
            if original_price > 0 and price > 0:
                discount_pct = round(((original_price - price) / original_price) * 100, 2)
            else:
                discount_pct = 0
            
            # Alert conditions
            should_alert = False
            
            # Condition 1: Price under threshold
            if 0 < price <= PRICE_THRESHOLD:
                should_alert = True
            
            # Condition 2: Discount over 70%
            if discount_pct >= 70:
                should_alert = True
            
            # Check if this is a new alert (not already tracked at this price)
            if should_alert:
                if product_id not in self.tracked_products or self.tracked_products[product_id] != price:
                    self.send_telegram_alert(name, price, original_price, discount_pct)
                    self.tracked_products[product_id] = price
                    alert_count += 1
        
        if alert_count == 0:
            print(f"No products found matching alert criteria (under ₹{PRICE_THRESHOLD} or >70% discount)")
    
    def extract_products(self, data):
        """Extract product information from API response"""
        products = []
        
        try:
            print("Parsing API response structure...")
            
            # Navigate through Swiggy's response structure
            if isinstance(data, dict):
                # Check for common Swiggy response patterns
                if 'data' in data:
                    widgets = data['data'].get('widgets', [])
                    print(f"Found {len(widgets)} widgets")
                    
                    for widget in widgets:
                        widget_data = widget.get('data', {})
                        
                        # Check for product grids
                        if isinstance(widget_data, list):
                            for item in widget_data:
                                product = self.parse_product(item)
                                if product:
                                    products.append(product)
                        
                        # Check for variations data
                        if 'variations' in widget_data:
                            for variation in widget_data['variations']:
                                product = self.parse_product(variation)
                                if product:
                                    products.append(product)
                        
                        # Check for items array
                        if 'items' in widget_data:
                            for item in widget_data['items']:
                                product = self.parse_product(item)
                                if product:
                                    products.append(product)
            
            print(f"Extracted {len(products)} products")
            
            # Show sample products
            if products and TEST_MODE:
                print("\nSample products found:")
                for i, p in enumerate(products[:5]):
                    print(f"  {i+1}. {p['name'][:50]} - ₹{p['price']} (MRP: ₹{p['mrp']})")
            
        except Exception as e:
            print(f"Error extracting products: {e}")
            import traceback
            traceback.print_exc()
        
        return products
    
    def parse_product(self, item):
        """Parse individual product data"""
        try:
            # Handle different response structures
            product_id = item.get('id') or item.get('product_id') or item.get('sku_id', '')
            name = item.get('display_name') or item.get('name') or item.get('product_name', 'Unknown')
            
            # Price extraction - try multiple fields
            price = 0
            mrp = 0
            
            # Try direct price fields
            if 'price' in item:
                price = float(item['price'])
            elif 'selling_price' in item:
                price = float(item['selling_price'])
            elif 'offer_price' in item:
                price = float(item['offer_price'])
            
            # Try MRP fields
            if 'mrp' in item:
                mrp = float(item['mrp'])
            elif 'list_price' in item:
                mrp = float(item['list_price'])
            elif 'original_price' in item:
                mrp = float(item['original_price'])
            
            # If no MRP, use price as MRP
            if mrp == 0:
                mrp = price
            
            if product_id and name and price > 0:
                return {
                    'id': str(product_id),
                    'name': name,
                    'price': price,
                    'mrp': mrp
                }
        except Exception as e:
            pass
        
        return None
    
    def run(self):
        """Main tracking loop"""
        print("Starting Swiggy Instamart Price Tracker...")
        print(f"Mode: {'TEST (Console Output)' if TEST_MODE else 'LIVE (Telegram Alerts)'}")
        print(f"Monitoring for products under ₹{PRICE_THRESHOLD}")
        print(f"Checking every {CHECK_INTERVAL} seconds\n")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Check #{iteration} - Fetching products...")
                data = self.fetch_products()
                
                if data:
                    print(f"Response received. Parsing products...")
                    self.check_prices(data)
                else:
                    print("No data received from API")
                
                if TEST_MODE and iteration >= 1:
                    print("\nTest mode: Stopping after 1 check. Set TEST_MODE=False for continuous monitoring.")
                    break
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\nStopping tracker...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    tracker = SwiggyPriceTracker()
    tracker.run()
