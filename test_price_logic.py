#!/usr/bin/env python3
"""
Test script to verify price change detection logic
"""

import json

# Simulate price history
price_history = {
    "PROD001": {
        "name": "Test Product 1",
        "price": 1000.0,
        "discount": 50,
        "last_seen": "2026-01-23T09:00:00"
    },
    "PROD002": {
        "name": "Test Product 2",
        "price": 500.0,
        "discount": 30,
        "last_seen": "2026-01-23T09:00:00"
    }
}

# Simulate current products
current_products = [
    {
        "asin": "PROD001",
        "name": "Test Product 1",
        "price": 1000.0,  # Same price
        "discount": 50
    },
    {
        "asin": "PROD002",
        "name": "Test Product 2",
        "price": 350.0,  # Price dropped 30%
        "discount": 50
    },
    {
        "asin": "PROD003",
        "name": "Test Product 3",  # New product
        "price": 200.0,
        "discount": 70
    }
]

def check_price_change(product, history):
    """Check if this is a new deal or price drop"""
    product_key = product['asin']
    
    if product_key not in history:
        return 'new'
    
    old_data = history[product_key]
    old_price = old_data.get('price', 0)
    
    if old_price == 0:
        return 'new'
    
    # Check if price dropped significantly (>20%)
    price_drop_pct = ((old_price - product['price']) / old_price) * 100
    
    if price_drop_pct >= 20:
        product['old_price'] = old_price
        product['price_drop_pct'] = round(price_drop_pct, 1)
        return 'price_drop'
    
    # Same or higher price
    if product['price'] >= old_price:
        return 'same'
    
    # Small price drop (less than threshold)
    return 'minor_drop'

# Test
print("Testing Price Change Detection Logic")
print("=" * 60)

new_deals = []
price_drops = []
same_price = []

for product in current_products:
    change_type = check_price_change(product, price_history)
    product['change_type'] = change_type
    
    print(f"\nProduct: {product['name']}")
    print(f"  ASIN: {product['asin']}")
    print(f"  Current Price: ₹{product['price']}")
    print(f"  Change Type: {change_type}")
    
    if change_type == 'new':
        new_deals.append(product)
        print(f"  ✅ Will ALERT - New product")
    elif change_type == 'price_drop':
        price_drops.append(product)
        print(f"  ✅ Will ALERT - Price dropped from ₹{product['old_price']} ({product['price_drop_pct']}%)")
    elif change_type == 'same':
        same_price.append(product)
        print(f"  ❌ No alert - Same price as before")
    else:
        print(f"  ❌ No alert - Minor price change")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"New Deals: {len(new_deals)}")
print(f"Price Drops: {len(price_drops)}")
print(f"Same Price (no alert): {len(same_price)}")
print(f"\nTotal products that will trigger alerts: {len(new_deals) + len(price_drops)}")

if len(new_deals) + len(price_drops) == 0:
    print("\n✓ No new deals or price drops - Will send 'No new deals' message")
else:
    print("\n✓ Will send alert with new deals and price drops only")
