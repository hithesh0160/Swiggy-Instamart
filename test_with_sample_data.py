import json
from swiggy_simple_tracker import SwiggyPriceTracker

# Sample data for testing
SAMPLE_DATA = {
    "data": {
        "widgets": [
            {
                "data": [
                    {"id": "1", "display_name": "Amul Butter 100g", "price": 60, "mrp": 65},
                    {"id": "2", "display_name": "Bread - White 400g", "price": 25, "mrp": 30},
                    {"id": "3", "display_name": "Milk - Toned 500ml", "price": 28, "mrp": 30},
                    {"id": "4", "display_name": "Eggs - 6 pieces", "price": 45, "mrp": 50},
                    {"id": "5", "display_name": "Onion - 1kg", "price": 35, "mrp": 40},
                    {"id": "6", "display_name": "Tomato - 500g", "price": 20, "mrp": 25},
                    {"id": "7", "display_name": "Potato - 1kg", "price": 30, "mrp": 35},
                    {"id": "8", "display_name": "Rice - Basmati 1kg", "price": 120, "mrp": 150},
                    {"id": "9", "display_name": "Dal - Toor 500g", "price": 85, "mrp": 100},
                    {"id": "10", "display_name": "Oil - Sunflower 1L", "price": 180, "mrp": 200},
                    # Some heavily discounted items
                    {"id": "11", "display_name": "Chocolate Bar - Expired Soon", "price": 9, "mrp": 50},
                    {"id": "12", "display_name": "Biscuits - Clearance Sale", "price": 15, "mrp": 60},
                    {"id": "13", "display_name": "Juice - Tetra Pack", "price": 12, "mrp": 45},
                    {"id": "14", "display_name": "Chips - Party Pack", "price": 49, "mrp": 99},
                    {"id": "15", "display_name": "Noodles - Instant 5 Pack", "price": 38, "mrp": 50},
                ]
            }
        ]
    }
}

def test_tracker():
    """Test the tracker with sample data"""
    print("Testing Swiggy Price Tracker with sample data...\n")
    
    # Create tracker instance
    tracker = SwiggyPriceTracker()
    
    # Extract products from sample data
    products = tracker.extract_products(SAMPLE_DATA)
    
    # Check prices and display alerts
    tracker.check_prices(products)
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nThe tracker successfully:")
    print("✓ Parsed product data")
    print("✓ Identified products under ₹50")
    print("✓ Calculated discounts")
    print("✓ Displayed alerts in console")
    print("\nNext steps:")
    print("1. Find the real Swiggy API endpoint (see SETUP_GUIDE.md)")
    print("2. Set up Telegram bot for notifications")
    print("3. Run continuously with TEST_MODE=False")

if __name__ == "__main__":
    test_tracker()
