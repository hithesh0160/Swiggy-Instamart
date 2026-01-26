#!/usr/bin/env python3
"""
Swiggy Instamart Price Tracker - Complete MCP Implementation
Uses Playwright MCP server for browser automation
Monitors Swiggy Instamart deals and sends Telegram notifications

IMPORTANT: This script is designed to be executed by an AI assistant that has access
to MCP tools. The AI assistant will make the actual MCP tool calls using call_mcp_tool().

To run this:
1. Ask the AI assistant: "Run swiggy_instamart_tracker_mcp.py using Playwright MCP"
2. The AI will execute the script and make MCP tool calls on your behalf
3. Results will be saved to swiggy_deals.json and Telegram alerts will be sent

Alternatively, you can manually replace self.call_mcp_tool() calls with actual
MCP tool invocations if you have direct access to the MCP server.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import re
import sys
from typing import List, Dict, Optional

# Import the deal hunter for parsing
from swiggy_deal_hunter_mcp import SwiggyDealHunter

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
    ],
    'mcp_server': 'user-playwright',  # MCP server name
    'base_url': 'https://www.swiggy.com/instamart/search?custom_back=true',
    'wait_timeout': 30000,  # 30 seconds
    'scroll_attempts': 5,  # Number of scroll attempts to load more products
}

class SwiggyInstamartTrackerMCP:
    """Complete Swiggy Instamart tracker using Playwright MCP"""
    
    def __init__(self):
        self.deals = []
        self.price_history = self.load_price_history()
        self.new_deals = []
        self.price_drops = []
        self.screenshots_dir = Path('screenshots')
        self.screenshots_dir.mkdir(exist_ok=True)
        self.hunter = SwiggyDealHunter()
        self.current_tab_id = None
    
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
            import requests
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
        normalized_name = self.normalize_name(product.get('name', ''))
        price = int(product.get('current_price', product.get('price', 0)))
        return f"name_{normalized_name[:100]}_{price}"
    
    def call_mcp_tool(self, tool_name: str, **kwargs):
        """
        Call MCP tool with error handling.
        This will be executed by the AI assistant making actual MCP calls.
        """
        # This method is a placeholder - the AI assistant will make actual calls
        # For now, we'll structure the code to show what needs to be called
        print(f"[MCP] Would call: {tool_name} with {kwargs}")
        
        # Return None to indicate this needs actual MCP execution
        # The AI assistant will replace these with real calls
        return None
    
    def navigate_to_search_page(self):
        """Navigate to Swiggy Instamart search page using MCP"""
        print("\n" + "="*60)
        print("Navigating to Swiggy Instamart...")
        print("="*60)
        
        try:
            # Check existing tabs
            tabs_result = self.call_mcp_tool('browser_tabs', action='list')
            
            # Navigate to search page (MCP will handle tab management)
            navigate_result = self.call_mcp_tool('browser_navigate', url=CONFIG['base_url'])
            
            if navigate_result:
                print(f"✓ Navigated to: {CONFIG['base_url']}")
                # Wait for page to load
                self.call_mcp_tool('browser_wait_for', time=3)
                return True
            else:
                print("✗ Failed to navigate")
                return False
                
        except Exception as e:
            print(f"✗ Error navigating: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search_and_get_snapshot(self, search_query: str) -> Optional[str]:
        """Search for products and get accessibility snapshot"""
        print(f"\n{'='*60}")
        print(f"Searching: {search_query}")
        print('='*60)
        
        try:
            # Strategy 1: Try direct URL navigation with query (simpler and more reliable)
            search_url = f"{CONFIG['base_url']}&query={search_query.replace(' ', '%20')}"
            print(f"Navigating to: {search_url}")
            navigate_result = self.call_mcp_tool('browser_navigate', url=search_url)
            
            if navigate_result:
                print("✓ Navigated to search URL")
                # Wait for results to load
                self.call_mcp_tool('browser_wait_for', time=5)
            else:
                # Strategy 2: Get snapshot and find search input
                print("Trying to find search input...")
                snapshot_result = self.call_mcp_tool('browser_snapshot')
                
                if snapshot_result:
                    # Parse snapshot to find search input
                    snapshot_text = snapshot_result.get('snapshot', '') if isinstance(snapshot_result, dict) else str(snapshot_result)
                    
                    # Find search input ref from snapshot
                    search_input_ref = None
                    for line in snapshot_text.split('\n'):
                        if ('input' in line.lower() or 'search' in line.lower()) and 'ref=' in line:
                            # Extract ref from line like: "- input [ref=e1234]:"
                            ref_match = re.search(r'\[ref=([^\]]+)\]', line)
                            if ref_match:
                                search_input_ref = ref_match.group(1)
                                break
                    
                    if search_input_ref:
                        print(f"✓ Found search input: {search_input_ref}")
                        # Type in search box
                        type_result = self.call_mcp_tool(
                            'browser_type',
                            ref=search_input_ref,
                            text=search_query,
                            submit=True  # Submit automatically
                        )
                        
                        if type_result:
                            print(f"✓ Typed and submitted search query")
                            self.call_mcp_tool('browser_wait_for', time=5)
            
            # Scroll to load more products (using evaluate to scroll)
            print("Scrolling to load more products...")
            for i in range(CONFIG['scroll_attempts']):
                # Use browser_evaluate to scroll
                scroll_function = "() => { window.scrollTo(0, document.body.scrollHeight); }"
                self.call_mcp_tool('browser_evaluate', function=scroll_function)
                self.call_mcp_tool('browser_wait_for', time=1)
            
            # Take screenshot
            screenshot_filename = f'swiggy_search_{search_query.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            screenshot_result = self.call_mcp_tool(
                'browser_take_screenshot',
                filename=screenshot_filename,
                type='png',
                fullPage=True
            )
            if screenshot_result:
                print(f"✓ Screenshot saved: {screenshot_filename}")
            
            # Get final snapshot with products
            print("Getting product snapshot...")
            snapshot_result = self.call_mcp_tool('browser_snapshot')
            
            if snapshot_result:
                # Extract snapshot text from result
                if isinstance(snapshot_result, dict):
                    snapshot_text = snapshot_result.get('snapshot', '')
                    if not snapshot_text:
                        # Try other possible keys
                        snapshot_text = snapshot_result.get('content', '')
                        if not snapshot_text:
                            snapshot_text = str(snapshot_result)
                else:
                    snapshot_text = str(snapshot_result)
                
                print(f"✓ Got snapshot ({len(snapshot_text)} chars)")
                return snapshot_text
            else:
                print("✗ Failed to get snapshot")
                return None
                
        except Exception as e:
            print(f"✗ Error searching {search_query}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_products_from_snapshot(self, snapshot_text: str, search_query: str) -> List[Dict]:
        """Parse products from MCP snapshot"""
        if not snapshot_text:
            return []
        
        # Use the deal hunter to parse snapshot
        products = self.hunter.parse_snapshot_yaml(snapshot_text)
        
        if not products:
            print("  ⚠ No products found in snapshot")
            return []
        
        # Calculate metrics
        products = self.hunter.calculate_metrics(products)
        
        # Add metadata
        for product in products:
            product['search_query'] = search_query
            product['timestamp'] = datetime.now().isoformat()
            product['is_deal'] = self.is_deal(
                product.get('current_price', product.get('price', 0)),
                product.get('discount_percent', product.get('discount', 0))
            )
            # Normalize price field
            if 'current_price' in product:
                product['price'] = product['current_price']
            if 'original_price' in product:
                product['mrp'] = product['original_price']
        
        print(f"  ✓ Parsed {len(products)} products")
        return products
    
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
            print(f"⚠ No key for product: {product.get('name', 'Unknown')[:50]}")
            return 'new'
        
        if product_key not in self.price_history:
            print(f"🆕 New product: {product.get('name', 'Unknown')[:50]}")
            return 'new'
        
        old_data = self.price_history[product_key]
        old_price = old_data.get('price', 0)
        
        if old_price == 0:
            return 'new'
        
        current_price = product.get('price', product.get('current_price', 0))
        price_drop_pct = ((old_price - current_price) / old_price) * 100
        
        if price_drop_pct >= CONFIG['price_drop_threshold']:
            product['old_price'] = old_price
            product['price_drop_pct'] = round(price_drop_pct, 1)
            print(f"📉 Price drop: {product.get('name', 'Unknown')[:50]} (₹{old_price} → ₹{current_price})")
            return 'price_drop'
        
        if current_price >= old_price:
            print(f"✓ Same price: {product.get('name', 'Unknown')[:50]} (₹{current_price})")
            return 'same'
        
        print(f"→ Minor drop: {product.get('name', 'Unknown')[:50]} (₹{old_price} → ₹{current_price})")
        return 'minor_drop'
    
    def update_price_history(self, product):
        """Update price history for a product"""
        product_key = self.get_product_key(product)
        
        if product_key:
            current_price = product.get('price', product.get('current_price', 0))
            discount = product.get('discount', product.get('discount_percent', 0))
            
            self.price_history[product_key] = {
                'name': product.get('name', 'Unknown'),
                'price': current_price,
                'discount': discount,
                'last_seen': product.get('timestamp', datetime.now().isoformat())
            }
    
    def scrape_all_deals(self):
        """Scrape deals from multiple categories using MCP"""
        print("\n" + "="*60)
        print("SWIGGY INSTAMART PRICE TRACKER - MCP VERSION")
        print("="*60)
        
        # Navigate to search page
        if not self.navigate_to_search_page():
            print("✗ Failed to navigate to search page")
            return
        
        # Search for each query
        for search_query in CONFIG['search_queries']:
            try:
                # Get snapshot
                snapshot_text = self.search_and_get_snapshot(search_query)
                
                if snapshot_text:
                    # Parse products
                    products = self.parse_products_from_snapshot(snapshot_text, search_query)
                    self.deals.extend(products)
                    
                    print(f"✓ Found {len(products)} products for '{search_query}'")
                else:
                    print(f"✗ No snapshot for '{search_query}'")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"✗ Error processing '{search_query}': {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Remove duplicates
        seen = set()
        unique_deals = []
        for deal in self.deals:
            key = f"{deal.get('name', '')}_{deal.get('price', deal.get('current_price', 0))}"
            if key not in seen:
                seen.add(key)
                unique_deals.append(deal)
        
        self.deals = unique_deals
        print(f"\n✓ Total unique deals found: {len(self.deals)}")
    
    def analyze_deals(self):
        """Analyze and categorize deals"""
        if not self.deals:
            print("No deals to analyze")
            return None
        
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
        
        cheap_deals = [d for d in alert_worthy if d.get('price', d.get('current_price', 0)) <= CONFIG['price_threshold']]
        high_discount = [d for d in alert_worthy if d.get('discount', d.get('discount_percent', 0)) >= CONFIG['discount_threshold']]
        
        print(f"New Deals: {len(self.new_deals)}")
        print(f"Price Drops: {len(self.price_drops)}")
        print(f"Alert-Worthy Deals: {len(alert_worthy)}")
        print(f"  - Cheap Deals (≤₹{CONFIG['price_threshold']}): {len(cheap_deals)}")
        print(f"  - High Discount (≥{CONFIG['discount_threshold']}%): {len(high_discount)}")
        
        # Sort by discount
        alert_worthy.sort(key=lambda x: x.get('discount', x.get('discount_percent', 0)), reverse=True)
        
        if alert_worthy:
            print("\n🔥 NEW DEALS:")
            for i, deal in enumerate(alert_worthy[:10], 1):
                change_marker = "🆕" if deal['change_type'] == 'new' else "📉"
                name = deal.get('name', 'Unknown')[:60]
                price = deal.get('price', deal.get('current_price', 0))
                discount = deal.get('discount', deal.get('discount_percent', 0))
                print(f"{change_marker} {i}. {name}")
                print(f"   ₹{price} ({discount}% off)")
                if deal['change_type'] == 'price_drop':
                    print(f"   Price dropped from ₹{deal.get('old_price', 0)} ({deal.get('price_drop_pct', 0)}% drop)")
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
            name = deal.get('name', 'Unknown')[:80]
            price = deal.get('price', deal.get('current_price', 0))
            discount = deal.get('discount', deal.get('discount_percent', 0))
            
            message += f"\n{change_marker}\n"
            message += f"{i}. {name}\n"
            message += f"   ₹{price:,} ({discount}% off)\n"
            
            if deal['change_type'] == 'price_drop':
                message += f"   Was: ₹{deal.get('old_price', 0):,} (dropped {deal.get('price_drop_pct', 0)}%)\n"
        
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
    tracker = SwiggyInstamartTrackerMCP()
    tracker.run()
