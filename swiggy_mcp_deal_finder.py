#!/usr/bin/env python3
"""
Swiggy Deal Finder - Complete MCP Workflow
Automated deal hunting with Playwright MCP tools
"""

import sys
import os

# Import the deal hunter
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Main workflow guide"""
    
    print("="*90)
    print("🎯 SWIGGY DEAL FINDER - PLAYWRIGHT MCP WORKFLOW")
    print("="*90)
    print("\nThis tool finds the best deals and pricing errors on Swiggy Instamart")
    print("using Playwright MCP browser automation.")
    print("\n" + "="*90)
    print("WORKFLOW STEPS")
    print("="*90)
    
    print("\n[STEP 1] Navigate to Swiggy Instamart")
    print("  Command: mcp_playwright_browser_navigate")
    print("  URL: https://www.swiggy.com/instamart/search?custom_back=true")
    
    print("\n[STEP 2] Search for products")
    print("  Command: mcp_playwright_browser_type")
    print("  Parameters:")
    print("    - ref: (search input ref from snapshot)")
    print("    - text: 'chocolate' (or any product)")
    print("    - submit: true")
    
    print("\n[STEP 3] Wait for results")
    print("  Command: mcp_playwright_browser_wait_for")
    print("  Parameters: time=5")
    
    print("\n[STEP 4] Dismiss popups")
    print("  Command: mcp_playwright_browser_click")
    print("  Target: 'Got it!' button (if present)")
    
    print("\n[STEP 5] Get product snapshot")
    print("  Command: mcp_playwright_browser_snapshot")
    print("  Save output for analysis")
    
    print("\n[STEP 6] Analyze deals")
    print("  Run: python swiggy_deal_hunter_mcp.py")
    print("  Or use the SwiggyDealHunter class directly")
    
    print("\n[STEP 7] Take screenshot")
    print("  Command: mcp_playwright_browser_take_screenshot")
    print("  Filename: swiggy_deals_<timestamp>.png")
    
    print("\n" + "="*90)
    print("EXAMPLE RESULTS FROM CHOCOLATE SEARCH")
    print("="*90)
    print("""
Total Products: 26
Average Discount: 17.3%
Total Savings: ₹1,493

🔥 HIGH DISCOUNTS (50-69% OFF): 1 product
  #1 [56% OFF] ₹219 (was ₹500) Save ₹281
     Cadbury Studio Brownie Aux Noix Signature Pralines

⭐ GOOD DEALS (30-49% OFF): 11 products
  #1 [32% OFF] ₹120 (was ₹178) Save ₹58
  #2 [30% OFF] ₹160 (was ₹229) Save ₹69
  #3 [27% OFF] ₹73 (was ₹100) Save ₹27
  ...

💰 TOP SAVINGS:
  #1 Save ₹281 - 56% OFF - Cadbury Studio Brownie
  #2 Save ₹223 - 25% OFF - Cadbury Studio Assorted
  #3 Save ₹211 - 20% OFF - Cadbury Dairy Milk Silk Pralines
""")
    
    print("\n" + "="*90)
    print("FEATURES")
    print("="*90)
    print("  🚨 Detects pricing errors (70%+ discount)")
    print("  🔥 Finds high discounts (50-69%)")
    print("  ⭐ Shows good deals (30-49%)")
    print("  💰 Sorts by maximum savings")
    print("  🏆 Calculates value score")
    print("  📊 Generates JSON reports")
    print("  📸 Takes verification screenshots")
    
    print("\n" + "="*90)
    print("FILES CREATED")
    print("="*90)
    print("  1. swiggy_deal_hunter_mcp.py - Main analysis class")
    print("  2. extract_swiggy_deals.py - Quick extraction script")
    print("  3. swiggy_discount_finder_mcp.py - Helper functions")
    print("  4. test_swiggy_frames.py - Original Playwright test")
    
    print("\n" + "="*90)
    print("QUICK START")
    print("="*90)
    print("""
Ask Kiro to:
1. "Navigate to Swiggy and search for chocolate"
2. "Get the page snapshot"
3. "Run the deal analysis"

Or manually:
1. Open browser with MCP
2. Navigate and search
3. Get snapshot YAML
4. Run: python extract_swiggy_deals.py
""")
    
    print("\n" + "="*90)
    print("CONFIGURATION")
    print("="*90)
    print("MCP Config (.kiro/settings/mcp.json):")
    print("""{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--browser",
        "chromium"
      ]
    }
  }
}""")
    
    print("\n" + "="*90)
    print("✅ SETUP COMPLETE")
    print("="*90)
    print("\nYou're ready to hunt for deals!")
    print("Try searching for: chocolate, snacks, electronics, home-kitchen")
    print("\n")

if __name__ == "__main__":
    main()
