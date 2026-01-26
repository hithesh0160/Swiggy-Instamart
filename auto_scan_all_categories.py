#!/usr/bin/env python3
"""
Automated All-Category Scanner
Uses Playwright MCP to automatically scan all Swiggy categories
Run this through Kiro with: "Scan all Swiggy categories for deals"
"""

import time
from datetime import datetime
from swiggy_all_categories_scanner import MultiCategoryScanner, CATEGORIES

def automated_scan_workflow():
    """
    Automated workflow for scanning all categories
    This is a guide for Kiro to execute using MCP tools
    """
    
    print("="*90)
    print("🤖 AUTOMATED ALL-CATEGORY SCAN WORKFLOW")
    print("="*90)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*90)
    
    scanner = MultiCategoryScanner()
    
    # Get all search queries (5 per category)
    queries = scanner.get_search_queries(max_per_category=5)
    
    print(f"\nTotal searches to perform: {len(queries)}")
    print(f"Estimated time: {len(queries) * 10 / 60:.1f} minutes")
    print("\n" + "="*90)
    
    print("\nAUTOMATED STEPS FOR EACH QUERY:")
    print("="*90)
    
    for i, (category, query) in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] {category} > {query}")
        print("-"*90)
        print("  Step 1: Navigate to search page")
        print("    → mcp_playwright_browser_navigate")
        print("    → URL: https://www.swiggy.com/instamart/search?custom_back=true")
        print()
        print("  Step 2: Clear and search")
        print(f"    → mcp_playwright_browser_type(text='{query}', submit=true)")
        print()
        print("  Step 3: Wait for results")
        print("    → mcp_playwright_browser_wait_for(time=5)")
        print()
        print("  Step 4: Dismiss popups (if any)")
        print("    → mcp_playwright_browser_click('Got it!' button)")
        print()
        print("  Step 5: Scroll to load more products")
        print("    → mcp_playwright_browser_evaluate(scroll script)")
        print()
        print("  Step 6: Get snapshot")
        print("    → mcp_playwright_browser_snapshot()")
        print()
        print("  Step 7: Parse and analyze")
        print("    → scanner.scan_category(category, query, snapshot_yaml)")
        print()
        print("  Step 8: Wait before next search")
        print("    → time.sleep(2)")
        print()
    
    print("\n" + "="*90)
    print("FINAL STEPS")
    print("="*90)
    print("  1. Aggregate all results")
    print("     → aggregated = scanner.aggregate_results(scanner.category_results)")
    print()
    print("  2. Generate master report")
    print("     → report = scanner.generate_master_report(aggregated)")
    print()
    print("  3. Save reports")
    print("     → scanner.save_master_report(aggregated, report)")
    print()
    print("  4. Display summary")
    print("     → print(report)")
    
    print("\n" + "="*90)
    print("EXPECTED OUTPUT")
    print("="*90)
    print("""
Files created:
  • swiggy_all_categories_YYYYMMDD_HHMMSS.json
  • swiggy_all_categories_YYYYMMDD_HHMMSS.txt

Report will include:
  🚨 All pricing errors (70%+ OFF)
  🔥 All high discounts (50-69% OFF)
  ⭐ All good deals (30-49% OFF)
  💰 Top 30 by savings amount
  🏆 Top 30 by value score
  📊 Category-wise breakdown
""")
    
    return queries

def generate_mcp_script():
    """Generate a script that can be executed step by step"""
    
    queries = []
    for category, items in CATEGORIES.items():
        for item in items[:5]:  # Top 5 per category
            queries.append((category, item))
    
    script = """
# Swiggy All-Category Scanner - MCP Execution Script
# Copy and execute these steps in Kiro

from swiggy_all_categories_scanner import MultiCategoryScanner

scanner = MultiCategoryScanner()
category_results = {}

# Search queries to execute:
"""
    
    for i, (category, query) in enumerate(queries, 1):
        script += f"""
# [{i}/{len(queries)}] {category} > {query}
# 1. Navigate: mcp_playwright_browser_navigate('https://www.swiggy.com/instamart/search?custom_back=true')
# 2. Search: mcp_playwright_browser_type(ref='<search_input_ref>', text='{query}', submit=True)
# 3. Wait: mcp_playwright_browser_wait_for(time=5)
# 4. Snapshot: snapshot = mcp_playwright_browser_snapshot()
# 5. Analyze:
analysis_{i} = scanner.scan_category('{category}', '{query}', snapshot_yaml)
category_results['{category}_{query}'] = analysis_{i}
"""
    
    script += """
# Aggregate and generate report
aggregated = scanner.aggregate_results(category_results)
report = scanner.generate_master_report(aggregated)
print(report)
json_file, txt_file = scanner.save_master_report(aggregated, report)
print(f"\\n✓ Reports saved: {json_file}, {txt_file}")
"""
    
    return script

def print_category_summary():
    """Print summary of all categories"""
    print("\n" + "="*90)
    print("CATEGORY SUMMARY")
    print("="*90)
    
    total_items = 0
    for category, items in CATEGORIES.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(items)} items)")
        print("-"*90)
        # Print first 10 items
        for i, item in enumerate(items[:10], 1):
            print(f"  {i:2d}. {item}")
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more")
        total_items += len(items)
    
    print("\n" + "="*90)
    print(f"TOTAL: {len(CATEGORIES)} categories, {total_items} items")
    print("="*90)

if __name__ == "__main__":
    print("\n" + "="*90)
    print("SWIGGY ALL-CATEGORY DEAL SCANNER")
    print("="*90)
    
    # Show category summary
    print_category_summary()
    
    # Show workflow
    print("\n")
    queries = automated_scan_workflow()
    
    # Generate execution script
    print("\n" + "="*90)
    print("GENERATING EXECUTION SCRIPT")
    print("="*90)
    
    script = generate_mcp_script()
    
    script_file = f"mcp_scan_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"\n✓ Execution script saved to: {script_file}")
    print("\nYou can:")
    print("  1. Ask Kiro to execute this workflow")
    print("  2. Run the script manually with MCP tools")
    print("  3. Execute step-by-step for better control")
    
    print("\n" + "="*90)
    print("QUICK START COMMAND FOR KIRO")
    print("="*90)
    print("""
Ask Kiro:
  "Scan all Swiggy Instamart categories for deals using Playwright MCP.
   Search 5 products per category, extract deals, and generate a master report
   showing pricing errors, high discounts, and best value products."
""")
