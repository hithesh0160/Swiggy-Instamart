#!/usr/bin/env python3
"""
Extract Swiggy deals from Playwright MCP snapshot
Analyzes products and finds highest discounts
"""

import re
import json
from datetime import datetime

# Sample snapshot data from the MCP response
SNAPSHOT_DATA = """
- generic [ref=e1684]: Cadbury Dairy Milk Chocolate Bar
- generic [ref=e1686]:
  - generic [ref=e1688]:
    - text: 20.2 g
  - generic [ref=e1693]: ₹ 20

- generic [ref=e1706]: Cadbury Dairy Milk Milkinis Chocolate Bar
- generic [ref=e1707]:
  - generic [ref=e1709]:
    - text: 17 g
  - generic [ref=e1714]: ₹ 20

- generic [ref=e1752]: Cadbury Dairy Milk Silk Chocolate Bar Valentine's Gift Pack
- generic [ref=e1754]:
  - generic [ref=e1756]: 60 g
  - generic [ref=e1757]: 5% OFF
  - generic [ref=e1759]:
    - generic [ref=e1760]: ₹ 96
    - generic [ref=e1761]: ₹ 102

- generic [ref=e1792]: 15% OFF
- generic [ref=e1794]:
  - generic [ref=e1795]: ₹ 113
  - generic [ref=e1796]: ₹ 133

- generic [ref=e1816]: 32% OFF
- generic [ref=e1818]:
  - generic [ref=e1819]: ₹ 120
  - generic [ref=e1820]: ₹ 178

- generic [ref=e1906]: 6% OFF
- generic [ref=e1908]:
  - generic [ref=e1909]: ₹ 138
  - generic [ref=e1910]: ₹ 147

- generic [ref=e1930]: 20% OFF
- generic [ref=e1932]:
  - generic [ref=e1933]: ₹ 36
  - generic [ref=e1934]: ₹ 45

- generic [ref=e2059]: 15% OFF
- generic [ref=e2061]:
  - generic [ref=e2062]: ₹ 34
  - generic [ref=e2063]: ₹ 40

- generic [ref=e2159]: 10% OFF
- generic [ref=e2161]:
  - generic [ref=e2162]: ₹ 202
  - generic [ref=e2163]: ₹ 225

- generic [ref=e2257]: 10% OFF
- generic [ref=e2259]:
  - generic [ref=e2260]: ₹ 159
  - generic [ref=e2261]: ₹ 177

- generic [ref=e2367]: 5% OFF
- generic [ref=e2369]:
  - generic [ref=e2370]: ₹ 203
  - generic [ref=e2371]: ₹ 214

- generic [ref=e2571]: 25% OFF
- generic [ref=e2573]:
  - generic [ref=e2574]: ₹ 160
  - generic [ref=e2575]: ₹ 214

- generic [ref=e2637]: 20% OFF
- generic [ref=e2639]:
  - generic [ref=e2640]: ₹ 360
  - generic [ref=e2641]: ₹ 450

- generic [ref=e2654]: 20% OFF
- generic [ref=e2656]:
  - generic [ref=e2657]: ₹ 839
  - generic [ref=e2658]: ₹ 1050

- generic [ref=e2671]: 25% OFF
- generic [ref=e2673]:
  - generic [ref=e2674]: ₹ 420
  - generic [ref=e2675]: ₹ 560

- generic [ref=e2870]: 30% OFF
- generic [ref=e2872]:
  - generic [ref=e2873]: ₹ 160
  - generic [ref=e2874]: ₹ 229

- generic [ref=e2894]: 5% OFF
- generic [ref=e2896]:
  - generic [ref=e2897]: ₹ 128
  - generic [ref=e2898]: ₹ 135

- generic [ref=e2918]: 19% OFF
- generic [ref=e2920]:
  - generic [ref=e2921]: ₹ 101
  - generic [ref=e2922]: ₹ 125

- generic [ref=e3134]: 25% OFF
- generic [ref=e3136]:
  - generic [ref=e3137]: ₹ 667
  - generic [ref=e3138]: ₹ 890

- generic [ref=e3205]: 56% OFF
- generic [ref=e3207]:
  - generic [ref=e3208]: ₹ 219
  - generic [ref=e3209]: ₹ 500

- generic [ref=e3238]: 21% OFF
- generic [ref=e3240]:
  - generic [ref=e3241]: ₹ 350
  - generic [ref=e3242]: ₹ 445

- generic [ref=e3289]: 10% OFF
- generic [ref=e3291]:
  - generic [ref=e3292]: ₹ 54
  - generic [ref=e3293]: ₹ 60

- generic [ref=e3392]: 8% OFF
- generic [ref=e3394]:
  - generic [ref=e3395]: ₹ 57
  - generic [ref=e3396]: ₹ 62

- generic [ref=e3418]: 10% OFF
- generic [ref=e3420]:
  - generic [ref=e3421]: ₹ 396
  - generic [ref=e3422]: ₹ 440

- generic [ref=e3445]: 20% OFF
- generic [ref=e3447]:
  - generic [ref=e3448]: ₹ 40
  - generic [ref=e3449]: ₹ 50

- generic [ref=e3470]: 2% OFF
- generic [ref=e3472]:
  - generic [ref=e3473]: ₹ 127
  - generic [ref=e3474]: ₹ 130

- generic [ref=e3499]: 27% OFF
- generic [ref=e3501]:
  - generic [ref=e3502]: ₹ 73
  - generic [ref=e3503]: ₹ 100

- generic [ref=e3523]: 10% OFF
- generic [ref=e3525]:
  - generic [ref=e3526]: ₹ 396
  - generic [ref=e3527]: ₹ 440
"""

def extract_deals_from_snapshot():
    """Extract product deals from snapshot data"""
    products = []
    
    # Find all discount patterns
    discount_pattern = r'(\d+)%\s*OFF.*?₹\s*(\d+).*?₹\s*(\d+)'
    
    matches = re.finditer(discount_pattern, SNAPSHOT_DATA, re.DOTALL)
    
    for match in matches:
        discount_percent = int(match.group(1))
        current_price = int(match.group(2))
        original_price = int(match.group(3))
        
        # Calculate savings
        savings = original_price - current_price
        
        # Verify discount calculation
        calculated_discount = round(((original_price - current_price) / original_price) * 100)
        
        products.append({
            'discount_percent': discount_percent,
            'current_price': current_price,
            'original_price': original_price,
            'savings': savings,
            'calculated_discount': calculated_discount
        })
    
    return products

def analyze_deals(products):
    """Analyze and categorize deals"""
    # Sort by discount percentage
    sorted_products = sorted(products, key=lambda x: x['discount_percent'], reverse=True)
    
    # Categorize
    pricing_errors = [p for p in sorted_products if p['discount_percent'] >= 70]
    high_discounts = [p for p in sorted_products if 50 <= p['discount_percent'] < 70]
    good_deals = [p for p in sorted_products if 20 <= p['discount_percent'] < 50]
    
    return {
        'all_products': sorted_products,
        'pricing_errors': pricing_errors,
        'high_discounts': high_discounts,
        'good_deals': good_deals,
        'total_products': len(sorted_products),
        'average_discount': sum(p['discount_percent'] for p in sorted_products) / len(sorted_products) if sorted_products else 0,
        'total_savings': sum(p['savings'] for p in sorted_products)
    }

def print_report(analysis):
    """Print formatted report"""
    print("\n" + "="*70)
    print("SWIGGY CHOCOLATE DEALS - DISCOUNT ANALYSIS")
    print("="*70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Products Analyzed: {analysis['total_products']}")
    print(f"Average Discount: {analysis['average_discount']:.1f}%")
    print(f"Total Potential Savings: ₹{analysis['total_savings']}")
    print("="*70)
    
    # Pricing Errors
    if analysis['pricing_errors']:
        print(f"\n🚨 POTENTIAL PRICING ERRORS (70%+ OFF): {len(analysis['pricing_errors'])}")
        print("-"*70)
        for i, p in enumerate(analysis['pricing_errors'], 1):
            print(f"{i}. {p['discount_percent']}% OFF - ₹{p['current_price']} (was ₹{p['original_price']}) - Save ₹{p['savings']}")
    
    # High Discounts
    if analysis['high_discounts']:
        print(f"\n🔥 HIGH DISCOUNTS (50-69% OFF): {len(analysis['high_discounts'])}")
        print("-"*70)
        for i, p in enumerate(analysis['high_discounts'], 1):
            print(f"{i}. {p['discount_percent']}% OFF - ₹{p['current_price']} (was ₹{p['original_price']}) - Save ₹{p['savings']}")
    
    # Good Deals
    if analysis['good_deals']:
        print(f"\n⭐ GOOD DEALS (20-49% OFF): {len(analysis['good_deals'])}")
        print("-"*70)
        for i, p in enumerate(analysis['good_deals'][:10], 1):
            print(f"{i}. {p['discount_percent']}% OFF - ₹{p['current_price']} (was ₹{p['original_price']}) - Save ₹{p['savings']}")
    
    # Top 5 by savings amount
    print(f"\n💰 TOP 5 BY SAVINGS AMOUNT")
    print("-"*70)
    top_savings = sorted(analysis['all_products'], key=lambda x: x['savings'], reverse=True)[:5]
    for i, p in enumerate(top_savings, 1):
        print(f"{i}. Save ₹{p['savings']} - {p['discount_percent']}% OFF - ₹{p['current_price']} (was ₹{p['original_price']})")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    print("Extracting deals from Swiggy snapshot...")
    products = extract_deals_from_snapshot()
    
    print(f"Found {len(products)} products with discounts")
    
    analysis = analyze_deals(products)
    print_report(analysis)
    
    # Save to JSON
    output_file = f"swiggy_deals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n✓ Full analysis saved to: {output_file}")
