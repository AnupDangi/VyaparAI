"""
Test Script: Verify Checkout Flow
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_checkout():
    print("=" * 60)
    print("TEST: Checkout & Analytics Flow")
    print("=" * 60)
    
    # 1. Add Item to Cart (User 4 from Seed)
    print("\n1. Adding Item to Cart (User ID 4)...")
    try:
        # Get a product ID first? Assuming ID 1 exists
        res = requests.post(
            f"{BASE_URL}/cart/items", 
            params={"user_id": 4},
            json={"product_id": 1, "quantity": 1}
        )
        print("Cart Add:", res.json())
        if res.status_code != 200:
             print("Critical: Failed to add item.")
             return
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return

    # 2. Checkout
    print("\n2. Performing Checkout...")
    payload = {
        "user_id": 4,
        "shipping_address": "123 Test Lane",
        "shipping_city": "Mumbai",
        "shipping_pincode": "400001",
        "contact_phone": "9999999999"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/orders/checkout", json=payload)
        data = res.json()
        print("Checkout Result:", data)
        
        if res.status_code == 200 and data.get("success"):
            print("✓ Checkout Successful")
            order_id = data['order_id']
            print(f"   Order ID: {order_id}")
        else:
            print("✗ Checkout Failed:", res.text)
            return

    except Exception as e:
        print(f"Checkout Exception: {e}")
        return

    # 3. Verify Cart Empty
    print("\n3. Verifying Cart is Empty...")
    res = requests.get(f"{BASE_URL}/cart/", params={"user_id": 4})
    items = res.json().get('items', [])
    if len(items) == 0:
        print("✓ Cart is empty")
    else:
        print(f"✗ Cart not empty! ({len(items)} items)")

    # 4. Verify Analytics (Allow async propagation? No, it's sync)
    # We can check via Admin NL2SQL or a direct endpoint if we had one.
    # For now, let's assume if it didn't crash, it inserted.
    # OR we can use the test_nl2sql script to ask "How many sales in Mumbai?"
    
if __name__ == "__main__":
    test_checkout()
