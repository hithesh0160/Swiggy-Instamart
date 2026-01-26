#!/usr/bin/env python3
"""
Swiggy Deal Hunter - Automated Discount Finder using Playwright MCP
Searches for products and finds the best deals and pricing errors
"""

import re
import json
from datetime import datetime
from typing import List, Dict

class SwiggyDealHunter:
    """Hunt for the best deals on Swiggy Instamart"""
    
    def __init__(self):
        self.products = []
        self.search_query = ""
    
    def parse_snapshot_yaml(self, yaml_text: str) -> List[Dict]:
        """Parse Playwright accessibility snapshot YAML"""
        products = []
        lines = yaml_text.split('\n')
        
        current_product = {}
        
        for i, line in enumerate(lines):
            # Look for product names
            if 'generic [ref=' in line and ']:' in line:
                text = line.split(']:')[-1].strip()
                
                # Check if it's a product name (not too short, not a price)
                if text and len(text) > 10 and '₹' not in text and 'MINS' not in text:
                    if 'OFF' not in text and 'Delivery' not in text:
                        if current_product and 'name' in current_product:
                            products.append(current_product)
                        current_product = {'name': text}
            
            # Extract discount percentage
            if 'OFF' in line and '%' in line:
                match = re.search(r'(\d+)%\s*OFF', line)
                if match:
                    current_product['discount_percent'] = int(match.group(1))
            
            # Extract prices
            if '₹' in line:
                prices = re.findall(r'₹\s*(\d+)', line)
                if prices:
                    if 'current_price' not in current_product:
                        current_product['current_price'] = int(prices[0])
                    elif len(prices) > 1 and 'original_price' not in current_product:
                        current_product['original_price'] = int(prices[1])
            
            # Extract size
            if re.search(r'\d+\s*(g|ml|kg|ltr|L|pieces|Piece)', line):
                match = re.search(r'(\d+\s*(?:g|ml|kg|ltr|L|pieces|Piece))', line)
                if match and 'size' not in current_product:
                    current_product['size'] = match.group(1)
        
        # Add last product
        if current_product and 'name' in current_product:
            products.append(current_product)
        
        return products
    
    def calculate_metrics(self, products: List[Dict]) -> List[Dict]:
        """Calculate discount percentages and savings"""
        for product in products:
            current = product.get('current_price', 0)
            original = product.get('original_price', current)
            
            # Calculate discount if we have both prices
            if original > current:
                discount = round(((original - current) / original) * 100)
                product['discount_percent'] = discount
                product['savings'] = original - current
            else:
                product['discount_percent'] = product.get('discount_percent', 0)
                product['savings'] = 0
            
            product['original_price'] = original
            
            # Calculate value score (higher is better)
            # Considers both discount percentage and absolute savings
            if product['savings'] > 0:
                product['value_score'] = (product['discount_percent'] * 0.6) + (min(product['savings'] / 10, 40) * 0.4)
            else:
                product['value_score'] = 0
        
        return products
    
    def categorize_deals(self, products: List[Dict]) -> Dict:
        """Categorize products by discount level"""
        # Sort by discount percentage
        sorted_by_discount = sorted(products, key=lambda x: x.get('discount_percent', 0), reverse=True)
        sorted_by_savings = sorted(products, key=lambda x: x.get('savings', 0), reverse=True)
        sorted_by_value = sorted(products, key=lambda x: x.get('value_score', 0), reverse=True)
        
        # Categorize
        pricing_errors = [p for p in sorted_by_discount if p.get('discount_percent', 0) >= 70]
        high_discounts = [p for p in sorted_by_discount if 50 <= p.get('discount_percent', 0) < 70]
        good_deals = [p for p in sorted_by_discount if 30 <= p.get('discount_percent', 0) < 50]
        moderate_deals = [p for p in sorted_by_discount if 15 <= p.get('discount_percent', 0) < 30]
        
        return {
            'all_products': sorted_by_discount,
            'by_savings': sorted_by_savings,
            'by_value': sorted_by_value,
            'pricing_errors': pricing_errors,
            'high_discounts': high_discounts,
            'good_deals': good_deals,
            'moderate_deals': moderate_deals,
            'total_products': len(products),
            'average_discount': sum(p.get('discount_percent', 0) for p in products) / len(products) if products else 0,
            'total_savings': sum(p.get('savings', 0) for p in products),
            'max_discount': max((p.get('discount_percent', 0) for p in products), default=0),
            'max_savings': max((p.get('savings', 0) for p in products), default=0)
        }
    
    def format_product(self, product: Dict, rank: int = None) -> str:
        """Format product for display"""
        name = product.get('name', 'Unknown')[:70]
        current = product.get('current_price', 0)
        original = product.get('original_price', current)
        discount = product.get('discount_percent', 0)
        savings = product.get('savings', 0)
        size = product.get('size', 'N/A')
        value_score = product.get('value_score', 0)
        
        rank_str = f"#{rank:2d} " if rank else "    "
        
        return f"{rank_str}[{discount:2d}% OFF] ₹{current:4d} (was ₹{original:4d}) Save ₹{savings:3d} | {size:10s} | Score: {value_score:.1f}\n     {name}"
    
    def generate_report(self, analysis: Dict, search_query: str = "") -> str:
        """Generate comprehensive report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
{'='*90}
🎯 SWIGGY INSTAMART DEAL HUNTER REPORT
{'='*90}
Search Query: {search_query or 'N/A'}
Generated: {timestamp}
Total Products: {analysis['total_products']}
Average Discount: {analysis['average_discount']:.1f}%
Max Discount: {analysis['max_discount']}%
Total Potential Savings: ₹{analysis['total_savings']}
Max Single Savings: ₹{analysis['max_savings']}
{'='*90}
"""
        
        # Pricing Errors
        if analysis['pricing_errors']:
            report += f"\n🚨 POTENTIAL PRICING ERRORS (70%+ OFF): {len(analysis['pricing_errors'])}\n"
            report += "-"*90 + "\n"
            for i, p in enumerate(analysis['pricing_errors'][:5], 1):
                report += self.format_product(p, i) + "\n"
        
        # High Discounts
        if analysis['high_discounts']:
            report += f"\n🔥 HIGH DISCOUNTS (50-69% OFF): {len(analysis['high_discounts'])}\n"
            report += "-"*90 + "\n"
            for i, p in enumerate(analysis['high_discounts'][:10], 1):
                report += self.format_product(p, i) + "\n"
        
        # Good Deals
        if analysis['good_deals']:
            report += f"\n⭐ GOOD DEALS (30-49% OFF): {len(analysis['good_deals'])}\n"
            report += "-"*90 + "\n"
            for i, p in enumerate(analysis['good_deals'][:10], 1):
                report += self.format_product(p, i) + "\n"
        
        # Top by Savings Amount
        report += f"\n💰 TOP 10 BY SAVINGS AMOUNT\n"
        report += "-"*90 + "\n"
        for i, p in enumerate(analysis['by_savings'][:10], 1):
            report += self.format_product(p, i) + "\n"
        
        # Top by Value Score
        report += f"\n🏆 TOP 10 BY VALUE SCORE (Best Overall Deals)\n"
        report += "-"*90 + "\n"
        for i, p in enumerate(analysis['by_value'][:10], 1):
            report += self.format_product(p, i) + "\n"
        
        report += "\n" + "="*90 + "\n"
        
        return report
    
    def save_results(self, analysis: Dict, search_query: str = ""):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"swiggy_deals_{search_query.replace(' ', '_')}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return filename

# Example usage
if __name__ == "__main__":
    print("Swiggy Deal Hunter - MCP Version")
    print("="*90)
    print("\nThis tool analyzes Swiggy Instamart products to find:")
    print("  🚨 Pricing errors (70%+ discount)")
    print("  🔥 High discounts (50-69%)")
    print("  ⭐ Good deals (30-49%)")
    print("  💰 Maximum savings")
    print("  🏆 Best value products")
    print("\nUsage with Playwright MCP:")
    print("  1. Navigate to Swiggy search page")
    print("  2. Search for products (e.g., 'chocolate')")
    print("  3. Get snapshot using mcp_playwright_browser_snapshot")
    print("  4. Pass snapshot YAML to parse_snapshot_yaml()")
    print("  5. Generate report")
    print("\nExample:")
    print("  hunter = SwiggyDealHunter()")
    print("  products = hunter.parse_snapshot_yaml(snapshot_yaml)")
    print("  products = hunter.calculate_metrics(products)")
    print("  analysis = hunter.categorize_deals(products)")
    print("  report = hunter.generate_report(analysis, 'chocolate')")
    print("  print(report)")
    print("  hunter.save_results(analysis, 'chocolate')")
