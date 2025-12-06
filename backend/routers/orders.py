from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from config.db import get_db_connection
import arrow

router = APIRouter()

class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderSchema(BaseModel):
    items: List[OrderItemSchema]
    total_amount: float
    clerk_id: str
    shipping_address: Optional[str] = ""

@router.post("/")
def create_order(order: OrderSchema):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Get User ID from Clerk ID
            cur.execute("SELECT id FROM users WHERE clerk_id = %s", (order.clerk_id,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user_id = user['id']

            # 2. Insert Order
            cur.execute("""
                INSERT INTO orders (user_id, total_amount, status, payment_status, created_at, updated_at)
                VALUES (%s, %s, 'Pending', 'Pending', NOW(), NOW())
                RETURNING id
            """, (user_id, order.total_amount))
            order_id = cur.fetchone()['id']

            # 3. Insert Items and Update Stock
            for item in order.items:
                # Check stock first (Optimistic)
                cur.execute("SELECT stock FROM products WHERE id = %s", (item.product_id,))
                product = cur.fetchone()
                if not product or product['stock'] < item.quantity:
                    conn.rollback()
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")

                cur.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item.product_id, item.quantity, item.price))

                # Update Stock
                cur.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (item.quantity, item.product_id))

            conn.commit()
            return {"success": True, "orderId": order_id, "message": "Order placed successfully"}
    except HTTPException as e:
        conn.rollback()
        raise e
    except Exception as e:
        conn.rollback()
        print(f"Order Creation Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")
    finally:
        conn.close()

@router.get("/{clerk_id}")
def get_user_orders(clerk_id: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get User ID
            cur.execute("SELECT id FROM users WHERE clerk_id = %s", (clerk_id,))
            user = cur.fetchone()
            if not user:
                # If user not found yet (maybe sync issue), return empty
                return []
            
            user_id = user['id']

            # Get Orders
            cur.execute("""
                SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC
            """, (user_id,))
            orders = cur.fetchall()

            # Helper to get items for an order
            orders_with_items = []
            for o in orders:
                cur.execute("""
                    SELECT oi.*, p.title, p.image_url 
                    FROM order_items oi 
                    JOIN products p ON oi.product_id = p.id 
                    WHERE oi.order_id = %s
                """, (o['id'],))
                items = cur.fetchall()
                orders_with_items.append({
                    "id": o['id'],
                    "total": o['total_amount'],
                    "status": o['status'],
                    "date": o['created_at'], # Frontend likes string? Pydantic handles datetime
                    "items": items
                })

            return orders_with_items
    finally:
        conn.close()
