"""
Test Script: Verify Shopping Cart API
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/cart"

def test_cart():
    print("=" * 60)
    print("TEST: Shopping Cart API")
    print("=" * 60)
    
    # 1. Clear Cart (Cleanup)
    print("\n1. Clearing Cart...")
    requests.delete(f"{BASE_URL}/", params={"user_id": 1})
    
    # 2. Get Cart (Should be empty)
    print("\n2. Get Cart (Empty)...")
    res = requests.get(f"{BASE_URL}/", params={"user_id": 1})
    data = res.json()
    print("Items:", len(data['items']))
    if len(data['items']) == 0:
        print("✓ Cart is empty")
    else:
        print("✗ Cart not empty!")

    # 3. Add Item
    print("\n3. Add Item (Product ID 1)...")
    # Assuming Product ID 1 exists (created by seed or previous steps? OR we just trust DB has something)
    # If DB empty, this FK might fail.
    # Let's hope Product 1 exists. If not, we might need to insert one.
    
    payload = {"product_id": 1, "quantity": 2}
    res = requests.post(f"{BASE_URL}/items", params={"user_id": 1}, json=payload)
    print("Result:", res.json())
    
    # 4. Get Cart (Should have 1 item)
    print("\n4. Get Cart (Verify)...")
    res = requests.get(f"{BASE_URL}/", params={"user_id": 1})
    data = res.json()
    items = data['items']
    print(f"Items count: {len(items)}")
    if len(items) > 0 and items[0]['product_id'] == 1 and items[0]['quantity'] == 2:
         print("✓ Item added correctly")
    else:
         print("✗ Item add failed or mismatch")
         print(data)
         
    # 5. Remove Item
    print("\n5. Remove Item...")
    if items:
        item_id = items[0]['id']
        requests.delete(f"{BASE_URL}/items/{item_id}", params={"user_id": 1})
        
        # Verify
        res = requests.get(f"{BASE_URL}/", params={"user_id": 1})
        if len(res.json()['items']) == 0:
            print("✓ Item removed successfully")
        else:
            print("✗ Item remove failed")

if __name__ == "__main__":
    test_cart()
