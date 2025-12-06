"""
Cart Router - Shopping Cart Management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import psycopg
from backend.config.setup_schema import DATABASE_URL
import os

router = APIRouter()

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    title: str
    price: float
    image_url: Optional[str] = None
    total_item_price: float

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total_cart_price: float

def get_db_connection():
    return psycopg.connect(DATABASE_URL)

@router.get("/", response_model=CartResponse)
def get_cart(user_id: int = 1, clerk_id: Optional[str] = None): # Optional clerk_id overrides user_id
    """Get current user's cart"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            target_user_id = user_id
            
            # Resolve user if clerk_id provided
            if clerk_id:
                cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_id,))
                row = cur.fetchone()
                if row:
                    target_user_id = row[0]
            
            # Get or create cart
            cur.execute("SELECT id FROM carts WHERE user_id = %s", (target_user_id,))
            cart_row = cur.fetchone()
            
            if not cart_row:
                cur.execute(
                    "INSERT INTO carts (user_id) VALUES (%s) RETURNING id", 
                    (target_user_id,)
                )
                conn.commit()
                cart_id = cur.fetchone()[0]
            else:
                cart_id = cart_row[0]
            
            # Get items
            cur.execute("""
                SELECT ci.id, ci.product_id, ci.quantity, 
                       p.title, p.price, p.image_url
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = %s
            """, (cart_id,))
            
            items = []
            total_cart = 0.0
            
            for row in cur.fetchall():
                item_id, prod_id, qty, title, price, img = row
                price = float(price)
                item_total = price * qty
                total_cart += item_total
                
                items.append({
                    "id": item_id,
                    "product_id": prod_id,
                    "quantity": qty,
                    "title": title,
                    "price": price,
                    "image_url": img,
                    "total_item_price": item_total
                })
                
            return {
                "id": cart_id,
                "user_id": target_user_id,
                "items": items,
                "total_cart_price": total_cart
            }
    finally:
        conn.close()

@router.post("/items")
def add_item_to_cart(item: CartItemAdd, user_id: int = 1, clerk_id: Optional[str] = None):
    """Add item to cart. Resolves user from clerk_id if provided."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            target_user_id = user_id
            
            # Resolve user if clerk_id provided
            if clerk_id:
                cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_id,))
                row = cur.fetchone()
                if row:
                    target_user_id = row[0]
                else:
                    raise HTTPException(status_code=404, detail="User not found")

            # Ensure cart exists for target_user_id
            cur.execute("SELECT id FROM carts WHERE user_id = %s", (target_user_id,))
            cart_row = cur.fetchone()
            if not cart_row:
                cur.execute(
                    "INSERT INTO carts (user_id) VALUES (%s) RETURNING id", 
                    (target_user_id,)
                )
                cart_id = cur.fetchone()[0]
            else:
                cart_id = cart_row[0]
                
            # Upsert item
            cur.execute("""
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (cart_id, product_id) 
                DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity
                RETURNING id
            """, (cart_id, item.product_id, item.quantity))
            
            item_id = cur.fetchone()[0]
            conn.commit()
            return {"message": "Item added to cart", "cart_id": cart_id, "item_id": item_id}
    finally:
        conn.close()

@router.put("/items")
def update_item_quantity(item: CartItemAdd, user_id: int = 1, clerk_id: Optional[str] = None):
    """Set absolute quantity for an item"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            target_user_id = user_id
            
            if clerk_id:
                cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_id,))
                row = cur.fetchone()
                if row:
                    target_user_id = row[0]
                else:
                    raise HTTPException(status_code=404, detail="User not found")

            # Ensure cart exists
            cur.execute("SELECT id FROM carts WHERE user_id = %s", (target_user_id,))
            cart_row = cur.fetchone()
            if not cart_row:
                cur.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (target_user_id,))
                cart_id = cur.fetchone()[0]
            else:
                cart_id = cart_row[0]
                
            # Upsert item with SET quantity
            cur.execute("""
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (cart_id, product_id) 
                DO UPDATE SET quantity = EXCLUDED.quantity
                RETURNING id
            """, (cart_id, item.product_id, item.quantity))
            
            item_id = cur.fetchone()[0]
            conn.commit()
            return {"message": "Cart updated", "cart_id": cart_id, "item_id": item_id}
    finally:
        conn.close()

@router.delete("/items/{item_id}")
def remove_item(item_id: int, user_id: int = 1, clerk_id: Optional[str] = None):
    """Remove item from cart"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            target_user_id = user_id
            if clerk_id:
                cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_id,))
                row = cur.fetchone()
                if row:
                    target_user_id = row[0]

            # Verify ownership via join
            cur.execute("""
                DELETE FROM cart_items 
                WHERE id = %s AND cart_id IN (SELECT id FROM carts WHERE user_id = %s)
            """, (item_id, target_user_id))
            conn.commit()
            return {"message": "Item removed"}
    finally:
        conn.close()

@router.delete("/")
def clear_cart(user_id: int = 1, clerk_id: Optional[str] = None):
    """Clear all items"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            target_user_id = user_id
            if clerk_id:
                cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_id,))
                row = cur.fetchone()
                if row:
                    target_user_id = row[0]

            cur.execute("""
                DELETE FROM cart_items 
                WHERE cart_id IN (SELECT id FROM carts WHERE user_id = %s)
            """, (target_user_id,))
            conn.commit()
            return {"message": "Cart cleared"}
    finally:
        conn.close()
