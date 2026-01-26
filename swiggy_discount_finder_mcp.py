#!/usr/bin/env python3
"""
Swiggy Discount Finder - Using Playwright MCP
Finds products with highest discounts and potential pricing errors
Run this through Kiro IDE with Playwright MCP configured
"""

import json
import re
from datetime import datetime

def extract_products_from_snapshot(snapshot_text):
    """Extract products from Playwright accessibility snapshot"""
    products = []
    
    # Parse the snapshot to find product information
    lines = snapshot_text.split('\n')
    
    current_product = {}
    in_product = False
    
    for i, line in enumerate(lines):
        # Look for delivery time indicator
        if 'Delivery in' in line and 'MINS' in line:
            if current_product and 'name' in current_product:
                products.append(current_product)
            current_product = {'delivery_time': line.strip()}
            in_product = True
        
        # Extract product name (usually after delivery time)
        elif in_product and 'generic' in line and ':' in line:
            text = line.split(':')[-1].strip()
            if text and len(text) > 5 and '₹' not in text and 'MINS' not in text:
                if 'name' not in current_product:
                    current_product['name'] = text
        
        # Extract size
        elif in_product and re.search(r'\d+\s*(g|ml|kg|ltr|L|pieces|Piece)', line):
            size_match = re.search(r'(\d+\s*(?:g|ml|kg|ltr|L|pieces|Piece))', line)
            if size_match:
                current_product['size'] = size_match.group(1)
        
        # Extract discount percentage
        elif in_product and 'OFF' in line:
            discount_match = re.search(r'(\d+)%\s*OFF', line)
            if discount_match:
                current_product['discount_percent'] = int(discount_match.group(1))
        
        # Extract prices
        elif in_product and '₹' in line:
            price_matches = re.findall(r'₹\s*(\d+)', line)
            if price_matches:
                prices = [int(p) for p in price_matches]
                if 'current_price' not in current_product:
                    current_product['current_price'] = prices[0]
                if len(prices) > 1 and 'original_price' not in current_product:
                    current_product['original_price'] = prices[1]
    
    # Add last product
    if current_product and 'name' in current_product:
        products.append(current_product)
    
    return products

def calculate_discounts(products):
    """Calculate discount percentages and savings"""
    for product in products:
        current = product.get('current_price', 0)
        original = product.get('original_price', current)
        
        if original > current:
            discount = round(((original - current) / original) * 100)
            product['discount_percent'] = discount
            product['savings'] = original - current
        else:
            product['discount_percent'] = product.get('discount_percent', 0)
            product['savings'] = 0
        
        product['original_price'] = original
    
    return products

def find_best_deals(products, min_discount=50):
    """Find products with high discounts (potential deals or errors)"""
    # Sort by discount percentage
    sorted_products = sorted(products, key=lambda x: x.get('discount_percent', 0), reverse=True)
    
    # Filter high discount products
    high_discounts = [p for p in sorted_products if p.get('discount_percent', 0) >= min_discount]
    
    return {
        'all_products': sorted_products,
        'high_discounts': high_discounts,
        'pricing_errors': [p for p in sorted_products if p.get('discount_percent', 0) >= 70],
        'total_products': len(sorted_products),
        'average_discount': sum(p.get('discount_percent', 0) for p in sorted_products) / len(sorted_products) if sorted_products else 0
    }

def format_product_report(product, rank=None):
    """Format a single product for display"""
    name = product.get('name', 'Unknown')[:60]
    current = product.get('current_price', 0)
    original = product.get('original_price', current)
    discount = product.get('discount_percent', 0)
    savings = product.get('savings', 0)
    size = product.get('size', 'N/A')
    
    rank_str = f"#{rank} " if rank else ""
    
    return f"""
{rank_str}{name}
  Size: {size}
  Price: ₹{current} (was ₹{original})
  Discount: {discount}% OFF
  Savings: ₹{savings}
"""

def generate_report(deals, search_query='chocolate'):
    """Generate a comprehensive discount report"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""
{'='*70}
SWIGGY INSTAMART DISCOUNT FINDER REPORT
{'='*70}
Search Query: {search_query}
Generated: {timestamp}
Total Products Found: {deals['total_products']}
Average Discount: {deals['average_discount']:.1f}%
{'='*70}

"""
    
    # Pricing Errors (70%+ discount)
    if deals['pricing_errors']:
        report += f"\n🚨 POTENTIAL PRICING ERRORS (70%+ OFF) - {len(deals['pricing_errors'])} found\n"
        report += "="*70 + "\n"
        for i, product in enumerate(deals['pricing_errors'][:10], 1):
            report += format_product_report(product, i)
    
    # High Discounts (50-69%)
    high_but_not_error = [p for p in deals['high_discounts'] 
                          if p.get('discount_percent', 0) < 70]
    if high_but_not_error:
        report += f"\n🔥 HIGH DISCOUNTS (50-69% OFF) - {len(high_but_not_error)} found\n"
        report += "="*70 + "\n"
        for i, product in enumerate(high_but_not_error[:10], 1):
            report += format_product_report(product, i)
    
    # Top 15 Deals Overall
    report += f"\n⭐ TOP 15 DEALS BY DISCOUNT\n"
    report += "="*70 + "\n"
    for i, product in enumerate(deals['all_products'][:15], 1):
        report += format_product_report(product, i)
    
    return report

# Example usage with MCP snapshot data
if __name__ == "__main__":
    print("Swiggy Discount Finder - MCP Version")
    print("="*70)
    print("\nThis script analyzes Playwright MCP snapshot data")
    print("to find products with high discounts and pricing errors.")
    print("\nUsage:")
    print("1. Use Playwright MCP to navigate to Swiggy search")
    print("2. Save snapshot to file")
    print("3. Pass snapshot text to extract_products_from_snapshot()")
    print("4. Use find_best_deals() to analyze")
    print("5. Generate report with generate_report()")
    print("\nExample:")
    print("  products = extract_products_from_snapshot(snapshot_text)")
    print("  products = calculate_discounts(products)")
    print("  deals = find_best_deals(products, min_discount=50)")
    print("  report = generate_report(deals)")
    print("  print(report)")
