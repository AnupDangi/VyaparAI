import requests
import psycopg
from backend.config.setup_schema import DATABASE_URL

BASE_URL = "http://localhost:8000/api"

def get_db_connection():
    return psycopg.connect(DATABASE_URL)

def reproduce_issue():
    print("reproducing issue...")
    
    # 1. Reset Data for Clean Slate
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Clear carts
        cur.execute("TRUNCATE carts CASCADE")
        # Ensure User 1 exists (for the hardcoded cart API)
        cur.execute("INSERT INTO users (id, full_name, email, clerk_user_id) VALUES (1, 'Test User', 'test@example.com', 'user_123') ON CONFLICT (id) DO NOTHING")
        # Ensure a Real Clerk User exists (simulating the logged in user)
        # The logs showed Clerk ID: user_36SiosOTZLn1emln0Wxev8KnPsB mapping to ID=1.
        # So actually, if ID=1 is the logged in user, it *should* work if the backend works as I think.
        
        # Let's check what ID the clerk user maps to in the real DB.
        # But wait, looking at the code again:
        # cart.py: def add_item_to_cart(item: CartItemAdd, user_id: int = 1):  <-- Hardcoded default!
        # orders.py: Resolves user_id from Clerk ID.
        pass
    conn.commit()
    conn.close()

    # 2. Add Item to Cart (calls /api/cart/items)
    # This uses the default user_id=1 from the function signature if auth middleware doesn't override it.
    # FIX TEST: Pass clerk_id to match the Checkout user.
    print("Adding item to cart...")
    res = requests.post(f"{BASE_URL}/cart/items?clerk_id=user_123", json={"product_id": 1, "quantity": 2})
    print(f"Add Item: {res.status_code} {res.json()}")

    # 3. Checkout (calls /api/orders/checkout)
    # This sends a Clerk ID. 
    # If the Clerk ID resolves to User ID 1, it SHOULD work.
    # If the logic is correct, why did it fail?
    
    # Let's try with a specific Clerk ID known to NOT be ID 1 (if possible) or just ID 1.
    # The log said: "User resolved: ID=1". So the user *is* ID 1.
    # And `cart.py` uses `user_id=1` by default.
    # So both should be pointing to Cart for User 1.
    
    # Wait, check `orders.py` line 67: `WHERE ci.cart_id = %s`.
    # And `cart.py` line 45: `SELECT id FROM carts WHERE user_id = %s`.
    
    # Is it possible `cart.py` is creating a cart, but `orders.py` is finding a DIFFERENT cart?
    # Or `cart_items` are not being saved?
    
    payload = {
        "clerk_id": "user_123", # Maps to ID 1 in my seed above
        "shipping_address": "123 Test St"
    }
    print("Checking out...")
    res = requests.post(f"{BASE_URL}/orders/checkout", json=payload)
    print(f"Checkout: {res.status_code} {res.json()}")

if __name__ == "__main__":
    reproduce_issue()
