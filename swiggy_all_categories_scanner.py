#!/usr/bin/env python3
"""
Swiggy All Categories Deal Scanner
Scans all product categories to find the best deals across Swiggy Instamart
Uses Playwright MCP for automation
"""

import json
import time
from datetime import datetime
from typing import List, Dict
from swiggy_deal_hunter_mcp import SwiggyDealHunter

# Comprehensive category list for Swiggy Instamart
CATEGORIES = {
    # Food & Beverages
    'food_beverages': [
        'chocolate', 'biscuits', 'cookies', 'chips', 'namkeen', 'snacks',
        'instant noodles', 'pasta', 'breakfast cereals', 'oats',
        'tea', 'coffee', 'cold drinks', 'juice', 'energy drinks',
        'milk', 'butter', 'cheese', 'yogurt', 'paneer',
        'rice', 'dal', 'atta', 'flour', 'sugar', 'salt',
        'cooking oil', 'ghee', 'spices', 'masala',
        'sauce', 'ketchup', 'jam', 'honey', 'peanut butter'
    ],
    
    # Personal Care
    'personal_care': [
        'shampoo', 'conditioner', 'soap', 'body wash', 'face wash',
        'toothpaste', 'toothbrush', 'mouthwash',
        'deodorant', 'perfume', 'talcum powder',
        'hair oil', 'hair gel', 'face cream', 'moisturizer',
        'sunscreen', 'lipstick', 'kajal', 'nail polish',
        'razor', 'shaving cream', 'aftershave',
        'sanitary pads', 'diapers', 'baby wipes'
    ],
    
    # Home & Kitchen
    'home_kitchen': [
        'detergent', 'fabric softener', 'dishwash liquid', 'floor cleaner',
        'toilet cleaner', 'glass cleaner', 'air freshener',
        'garbage bags', 'aluminium foil', 'cling wrap',
        'tissue paper', 'napkins', 'kitchen towel',
        'utensils', 'containers', 'bottles', 'lunch box',
        'cookware', 'pressure cooker', 'pan', 'kadai',
        'bedsheet', 'pillow', 'towel', 'curtains',
        'mop', 'broom', 'bucket', 'scrubber'
    ],
    
    # Electronics & Appliances
    'electronics': [
        'mobile accessories', 'charger', 'earphones', 'power bank',
        'smart watch', 'fitness band', 'bluetooth speaker',
        'led bulb', 'extension cord', 'adapter',
        'iron', 'kettle', 'mixer', 'blender',
        'fan', 'heater', 'air purifier',
        'batteries', 'torch', 'calculator'
    ],
    
    # Stationery & Office
    'stationery': [
        'notebook', 'pen', 'pencil', 'eraser', 'sharpener',
        'marker', 'highlighter', 'stapler', 'scissors',
        'glue', 'tape', 'paper', 'envelope',
        'file', 'folder', 'diary', 'calendar'
    ],
    
    # Baby Care
    'baby_care': [
        'baby food', 'baby oil', 'baby powder', 'baby lotion',
        'baby shampoo', 'baby soap', 'diapers', 'wipes',
        'feeding bottle', 'sipper', 'baby toys'
    ],
    
    # Pet Care
    'pet_care': [
        'dog food', 'cat food', 'pet treats', 'pet shampoo',
        'pet toys', 'pet accessories'
    ],
    
    # Health & Wellness
    'health_wellness': [
        'protein powder', 'vitamins', 'supplements',
        'health drinks', 'energy bars', 'dry fruits',
        'honey', 'apple cider vinegar', 'green tea',
        'face mask', 'hand sanitizer', 'antiseptic'
    ]
}

class MultiCategoryScanner:
    """Scan multiple categories for best deals"""
    
    def __init__(self):
        self.hunter = SwiggyDealHunter()
        self.all_deals = []
        self.category_results = {}
        self.scan_timestamp = datetime.now()
    
    def get_search_queries(self, max_per_category=5) -> List[tuple]:
        """Get list of (category, query) tuples to search"""
        queries = []
        for category, items in CATEGORIES.items():
            # Take top N items from each category
            for item in items[:max_per_category]:
                queries.append((category, item))
        return queries
    
    def scan_category(self, category: str, query: str, snapshot_yaml: str) -> Dict:
        """Scan a single category/query"""
        print(f"\n{'='*90}")
        print(f"Scanning: {category} > {query}")
        print(f"{'='*90}")
        
        # Parse products from snapshot
        products = self.hunter.parse_snapshot_yaml(snapshot_yaml)
        
        if not products:
            print(f"  ⚠ No products found for '{query}'")
            return None
        
        # Calculate metrics
        products = self.hunter.calculate_metrics(products)
        
        # Add category info to each product
        for product in products:
            product['category'] = category
            product['search_query'] = query
        
        # Categorize deals
        analysis = self.hunter.categorize_deals(products)
        
        print(f"  ✓ Found {analysis['total_products']} products")
        print(f"  ✓ Average discount: {analysis['average_discount']:.1f}%")
        print(f"  ✓ Max discount: {analysis['max_discount']}%")
        
        if analysis['pricing_errors']:
            print(f"  🚨 {len(analysis['pricing_errors'])} pricing errors!")
        if analysis['high_discounts']:
            print(f"  🔥 {len(analysis['high_discounts'])} high discounts!")
        
        return analysis
    
    def aggregate_results(self, category_results: Dict) -> Dict:
        """Aggregate results from all categories"""
        all_products = []
        
        for category, analysis in category_results.items():
            if analysis:
                all_products.extend(analysis['all_products'])
        
        # Sort by discount
        sorted_by_discount = sorted(all_products, key=lambda x: x.get('discount_percent', 0), reverse=True)
        sorted_by_savings = sorted(all_products, key=lambda x: x.get('savings', 0), reverse=True)
        sorted_by_value = sorted(all_products, key=lambda x: x.get('value_score', 0), reverse=True)
        
        # Categorize
        pricing_errors = [p for p in sorted_by_discount if p.get('discount_percent', 0) >= 70]
        high_discounts = [p for p in sorted_by_discount if 50 <= p.get('discount_percent', 0) < 70]
        good_deals = [p for p in sorted_by_discount if 30 <= p.get('discount_percent', 0) < 50]
        
        # Group by category
        by_category = {}
        for product in all_products:
            cat = product.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(product)
        
        return {
            'all_products': sorted_by_discount,
            'by_savings': sorted_by_savings,
            'by_value': sorted_by_value,
            'by_category': by_category,
            'pricing_errors': pricing_errors,
            'high_discounts': high_discounts,
            'good_deals': good_deals,
            'total_products': len(all_products),
            'total_categories': len(by_category),
            'average_discount': sum(p.get('discount_percent', 0) for p in all_products) / len(all_products) if all_products else 0,
            'total_savings': sum(p.get('savings', 0) for p in all_products),
            'scan_timestamp': self.scan_timestamp.isoformat()
        }
    
    def generate_master_report(self, aggregated: Dict) -> str:
        """Generate comprehensive report across all categories"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
{'='*90}
🎯 SWIGGY INSTAMART - MASTER DEAL REPORT (ALL CATEGORIES)
{'='*90}
Generated: {timestamp}
Total Products Scanned: {aggregated['total_products']}
Categories Covered: {aggregated['total_categories']}
Average Discount: {aggregated['average_discount']:.1f}%
Total Potential Savings: ₹{aggregated['total_savings']:,}
{'='*90}

"""
        
        # Pricing Errors
        if aggregated['pricing_errors']:
            report += f"\n🚨 PRICING ERRORS (70%+ OFF): {len(aggregated['pricing_errors'])}\n"
            report += "="*90 + "\n"
            for i, p in enumerate(aggregated['pricing_errors'][:20], 1):
                report += self._format_product(p, i) + "\n"
        
        # High Discounts
        if aggregated['high_discounts']:
            report += f"\n🔥 HIGH DISCOUNTS (50-69% OFF): {len(aggregated['high_discounts'])}\n"
            report += "="*90 + "\n"
            for i, p in enumerate(aggregated['high_discounts'][:30], 1):
                report += self._format_product(p, i) + "\n"
        
        # Good Deals
        if aggregated['good_deals']:
            report += f"\n⭐ GOOD DEALS (30-49% OFF): {len(aggregated['good_deals'])}\n"
            report += "="*90 + "\n"
            for i, p in enumerate(aggregated['good_deals'][:30], 1):
                report += self._format_product(p, i) + "\n"
        
        # Top Savings
        report += f"\n💰 TOP 30 BY SAVINGS AMOUNT\n"
        report += "="*90 + "\n"
        for i, p in enumerate(aggregated['by_savings'][:30], 1):
            report += self._format_product(p, i) + "\n"
        
        # Best Value
        report += f"\n🏆 TOP 30 BY VALUE SCORE\n"
        report += "="*90 + "\n"
        for i, p in enumerate(aggregated['by_value'][:30], 1):
            report += self._format_product(p, i) + "\n"
        
        # Category Breakdown
        report += f"\n📊 CATEGORY BREAKDOWN\n"
        report += "="*90 + "\n"
        for category, products in aggregated['by_category'].items():
            avg_discount = sum(p.get('discount_percent', 0) for p in products) / len(products) if products else 0
            total_savings = sum(p.get('savings', 0) for p in products)
            report += f"\n{category.upper().replace('_', ' ')}: {len(products)} products\n"
            report += f"  Average Discount: {avg_discount:.1f}%\n"
            report += f"  Total Savings: ₹{total_savings:,}\n"
            
            # Top 3 deals in this category
            top_3 = sorted(products, key=lambda x: x.get('discount_percent', 0), reverse=True)[:3]
            for i, p in enumerate(top_3, 1):
                report += f"  {i}. [{p.get('discount_percent', 0)}% OFF] {p.get('name', 'Unknown')[:50]}\n"
        
        report += "\n" + "="*90 + "\n"
        
        return report
    
    def _format_product(self, product: Dict, rank: int = None) -> str:
        """Format product for display"""
        name = product.get('name', 'Unknown')[:60]
        current = product.get('current_price', 0)
        original = product.get('original_price', current)
        discount = product.get('discount_percent', 0)
        savings = product.get('savings', 0)
        category = product.get('category', 'unknown')
        query = product.get('search_query', '')
        
        rank_str = f"#{rank:3d} " if rank else "     "
        
        return f"{rank_str}[{discount:2d}% OFF] ₹{current:5d} (was ₹{original:5d}) Save ₹{savings:4d} | {category:15s} | {query:15s}\n      {name}"
    
    def save_master_report(self, aggregated: Dict, report: str):
        """Save comprehensive report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON
        json_file = f"swiggy_all_categories_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(aggregated, f, indent=2, ensure_ascii=False)
        
        # Save text report
        txt_file = f"swiggy_all_categories_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return json_file, txt_file

def print_usage():
    """Print usage instructions"""
    print("""
{'='*90}
SWIGGY ALL CATEGORIES SCANNER - USAGE GUIDE
{'='*90}

This tool scans ALL product categories on Swiggy Instamart to find the best deals.

CATEGORIES COVERED:
  • Food & Beverages (35 items)
  • Personal Care (24 items)
  • Home & Kitchen (28 items)
  • Electronics (18 items)
  • Stationery (17 items)
  • Baby Care (11 items)
  • Pet Care (6 items)
  • Health & Wellness (12 items)

WORKFLOW:
  1. For each category, search for top products
  2. Extract product data using Playwright MCP
  3. Calculate discounts and savings
  4. Aggregate results across all categories
  5. Generate master report

PLAYWRIGHT MCP WORKFLOW:
  For each search query:
    1. mcp_playwright_browser_navigate to search page
    2. mcp_playwright_browser_type to search
    3. mcp_playwright_browser_wait_for results
    4. mcp_playwright_browser_snapshot to get data
    5. Parse and analyze

EXAMPLE AUTOMATION:
  scanner = MultiCategoryScanner()
  queries = scanner.get_search_queries(max_per_category=5)
  
  for category, query in queries:
      # Navigate and search using MCP
      # Get snapshot
      analysis = scanner.scan_category(category, query, snapshot_yaml)
      scanner.category_results[f"{category}_{query}"] = analysis
  
  # Aggregate all results
  aggregated = scanner.aggregate_results(scanner.category_results)
  report = scanner.generate_master_report(aggregated)
  print(report)
  scanner.save_master_report(aggregated, report)

OUTPUT FILES:
  • swiggy_all_categories_YYYYMMDD_HHMMSS.json - Full data
  • swiggy_all_categories_YYYYMMDD_HHMMSS.txt - Formatted report

FEATURES:
  🚨 Finds pricing errors (70%+ discount)
  🔥 Identifies high discounts (50-69%)
  ⭐ Shows good deals (30-49%)
  💰 Sorts by maximum savings
  🏆 Calculates value scores
  📊 Category-wise breakdown
  📈 Aggregated statistics

ESTIMATED TIME:
  • 5 products per category × 8 categories = 40 searches
  • ~10 seconds per search = ~7 minutes total
  • Add buffer for page loads = ~10-15 minutes

TIPS:
  • Run during off-peak hours for better performance
  • Save snapshots for offline analysis
  • Monitor for rate limiting
  • Use headless mode for faster execution
""")

if __name__ == "__main__":
    print_usage()
    
    print("\n" + "="*90)
    print("QUICK START")
    print("="*90)
    print("\nTo scan all categories, ask Kiro to:")
    print("  1. 'Scan all Swiggy categories for deals'")
    print("  2. Or run this script with automation")
    print("\nManual mode:")
    print("  scanner = MultiCategoryScanner()")
    print("  # Then feed snapshots for each category")
