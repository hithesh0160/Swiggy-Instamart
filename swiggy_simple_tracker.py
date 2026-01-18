import requests
import time
import json
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
CHECK_INTERVAL = 300  # Check every 5 minutes
PRICE_THRESHOLD = 50  # Alert for products under Rs 50
TEST_MODE = True  # Set to False to enable Telegram notifications

# Bangalore coordinates
LATITUDE = 12.9716
LONGITUDE = 77.5946

class SwiggyPriceTracker:
    def __init__(self):
        self.tracked_products = {}
        self.session = requests.Session()
        
        # Headers that mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.swiggy.com',
            'Referer': 'https://www.swiggy.com/instamart',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        })
    
    def fetch_products(self):
        """Fetch products from Swiggy Instamart API"""
        try:
            # Try different API endpoints
            endpoints = [
                f"https://www.swiggy.com/api/instamart/home?lat={LATITUDE}&lng={LONGITUDE}&pageNumber=0",
                f"https://www.swiggy.com/dapi/instamart/home?lat={LATITUDE}&lng={LONGITUDE}",
                f"https://www.swiggy.com/mapi/instamart/home?lat={LATITUDE}&lng={LONGITUDE}",
            ]
            
            for url in endpoints:
                print(f"\nTrying endpoint: {url}")
                try:
                    response = self.session.get(url, timeout=15)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Save for debugging
                        with open('swiggy_response.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print("✓ Response saved to swiggy_response.json")
                        
                        return data
                    
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
                    continue
            
            print("\n❌ All endpoints failed. Swiggy may require authentication or location setup.")
            print("Alternative: You can manually save product data to 'swiggy_response.json' and the script will parse it.")
            return None
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
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
                    print(f"✓ Alert sent for: {product_name}")
                else:
                    print(f"✗ Failed to send alert")
                    
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
    
    def extract_products(self, data):
        """Extract products from Swiggy API response"""
        products = []
        
        try:
            if not data:
                return products
            
            print("\nParsing response structure...")
            
            # Navigate through nested structure
            def find_products(obj, depth=0):
                if depth > 10:  # Prevent infinite recursion
                    return
                
                if isinstance(obj, dict):
                    # Check if this looks like a product
                    if 'display_name' in obj or 'product_name' in obj:
                        product = self.parse_product(obj)
                        if product:
                            products.append(product)
                    
                    # Recurse through dict values
                    for value in obj.values():
                        find_products(value, depth + 1)
                
                elif isinstance(obj, list):
                    # Recurse through list items
                    for item in obj:
                        find_products(item, depth + 1)
            
            find_products(data)
            print(f"✓ Extracted {len(products)} products")
            
        except Exception as e:
            print(f"Error extracting products: {e}")
        
        return products
    
    def parse_product(self, item):
        """Parse individual product"""
        try:
            # Extract name
            name = (item.get('display_name') or 
                   item.get('name') or 
                   item.get('product_name') or 
                   item.get('title', '')).strip()
            
            if not name or len(name) < 3:
                return None
            
            # Extract prices
            price = 0
            mrp = 0
            
            # Try various price fields
            price_fields = ['price', 'selling_price', 'offer_price', 'effective_price']
            for field in price_fields:
                if field in item and item[field]:
                    try:
                        price = float(item[field])
                        if price > 0:
                            break
                    except:
                        pass
            
            # Try MRP fields
            mrp_fields = ['mrp', 'list_price', 'original_price', 'marked_price']
            for field in mrp_fields:
                if field in item and item[field]:
                    try:
                        mrp = float(item[field])
                        if mrp > 0:
                            break
                    except:
                        pass
            
            # If no MRP, use price
            if mrp == 0:
                mrp = price
            
            # Need valid price
            if price <= 0:
                return None
            
            product_id = str(item.get('id', item.get('sku_id', name.lower().replace(' ', '_')[:50])))
            
            return {
                'id': product_id,
                'name': name,
                'price': price,
                'mrp': mrp
            }
            
        except Exception as e:
            return None
    
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
        
        # Show sample products in test mode
        if TEST_MODE and products:
            print("\n" + "="*70)
            print("SAMPLE PRODUCTS (First 15):")
            print("="*70)
            for i, p in enumerate(products[:15]):
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
        print("SWIGGY INSTAMART PRICE TRACKER")
        print("="*70)
        print(f"Mode: {'TEST (Console Output)' if TEST_MODE else 'LIVE (Telegram Alerts)'}")
        print(f"Location: Bangalore ({LATITUDE}, {LONGITUDE})")
        print(f"Alert Threshold: Products under ₹{PRICE_THRESHOLD} or >70% discount")
        print("="*70)
        
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"\n\n{'='*70}")
                print(f"CHECK #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                
                data = self.fetch_products()
                
                if data:
                    products = self.extract_products(data)
                    self.check_prices(products)
                else:
                    print("\n⚠ No data received. Check if:")
                    print("  1. You have internet connection")
                    print("  2. Swiggy Instamart is available in your location")
                    print("  3. The API endpoints haven't changed")
                
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
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(60)

if __name__ == "__main__":
    tracker = SwiggyPriceTracker()
    tracker.run()
