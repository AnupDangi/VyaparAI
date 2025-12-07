"""
Orders Router - Order Management and Checkout
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import psycopg
from backend.config.setup_schema import DATABASE_URL
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class OrderCheckout(BaseModel):
    clerk_id: str
    shipping_address: Optional[str] = "Default Address"
    shipping_city: Optional[str] = "Default City"
    shipping_pincode: Optional[str] = "000000"
    contact_phone: Optional[str] = "0000000000"

def get_db_connection():
    return psycopg.connect(DATABASE_URL)

@router.post("/checkout")
def checkout_cart(data: OrderCheckout):
    """
    Checkout Process:
    1. Resolve User
    2. Get Cart & Items
    3. Validate Stock
    4. Create Order
    5. Move Items & Update Analytics
    6. Clear Cart
    """
    logger.info(f"Checkout request received for Clerk ID: {data.clerk_id}")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 0. Resolve User
            cur.execute("SELECT id, full_name, city, phone FROM users WHERE clerk_user_id = %s", (data.clerk_id,))
            user_row = cur.fetchone()
            if not user_row:
                logger.error(f"User not found for Clerk ID: {data.clerk_id}")
                raise HTTPException(status_code=404, detail="User not found. Please refresh or relogin.")
            
            user_id, u_name, u_city, u_phone = user_row
            logger.info(f"User resolved: ID={user_id}, Name={u_name}")
            
            # Use provided phone or fallback to user profile
            final_phone = data.contact_phone if data.contact_phone != "0000000000" else (u_phone or "")

            # 1. Get Cart
            cur.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
            cart_row = cur.fetchone()
            if not cart_row:
                logger.error(f"No active cart found for User ID: {user_id}")
                raise HTTPException(status_code=400, detail="No active cart found")
            cart_id = cart_row[0]
            logger.info(f"Cart found: {cart_id}")

            # 2. Get Cart Items
            cur.execute("""
                SELECT ci.product_id, ci.quantity, p.price, p.stock, p.title, 
                       p.category, p.store_id
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = %s
            """, (cart_id,))
            items = cur.fetchall()
            
            if not items:
                logger.warning(f"Cart {cart_id} is empty")
                raise HTTPException(status_code=400, detail="Cart is empty")

            total_amount = 0
            order_items_data = []

            # 3. Validate Stock & Calculate Total
            for item in items:
                pid, qty, price, stock, title, cat, sid = item
                if qty > stock:
                    logger.warning(f"Insufficient stock for {title}: {qty} > {stock}")
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for {title}")
                
                line_total = float(price) * qty
                total_amount += line_total
                order_items_data.append({
                    "product_id": pid,
                    "quantity": qty,
                    "price": float(price),
                    "title": title,
                    "category": cat,
                    "store_id": sid
                })

            # 4. Create Order
            # Prefer provided shipping data
            
            cur.execute("""
                INSERT INTO orders (
                    user_id, total_amount, status, payment_status, 
                    user_name, shipping_address, shipping_city, shipping_pincode, contact_phone
                ) VALUES (%s, %s, 'Pending', 'Paid', %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_id, total_amount, 
                u_name or "Guest", data.shipping_address, data.shipping_city, 
                data.shipping_pincode, final_phone
            ))
            order_id = cur.fetchone()[0]
            logger.info(f"Order created: {order_id}")

            # 5. Process Items (Order Items + Fact Sales + Stock)
            for item in order_items_data:
                # Add to order_items
                cur.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price_at_time)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item['product_id'], item['quantity'], item['price']))

                # Update Stock
                cur.execute("""
                    UPDATE products SET stock = stock - %s WHERE id = %s
                """, (item['quantity'], item['product_id']))

                # Populate FACT_SALES (Denormalized)
                cur.execute("""
                    INSERT INTO fact_sales (
                        order_id, user_id, product_id, store_id,
                        quantity, price_at_time, total_amount,
                        order_status, payment_status,
                        user_city, product_category, product_title
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending', 'Paid', %s, %s, %s)
                """, (
                    order_id, user_id, item['product_id'], item['store_id'],
                    item['quantity'], item['price'], (item['price'] * item['quantity']),
                    data.shipping_city, item['category'], item['title']
                ))

            # 6. Clear Cart
            cur.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart_id,))

            conn.commit()
            logger.info(f"Checkout completed successfully for Order {order_id}")
            return {
                "success": True, 
                "order_id": order_id, 
                "message": "Checkout successful"
            }
            
    except HTTPException as e:
        conn.rollback()
        logger.error(f"HTTP Exception during checkout: {e.detail}")
        raise e
    except Exception as e:
        conn.rollback()
        logger.error(f"Checkout Critical Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/{user_ident}")
def get_user_orders(user_ident: str):
    """Get orders for a user (by internal ID or Clerk ID)"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Resolve ID if Clerk ID is passed
            if user_ident.startswith("user_"):
                cur.execute("SELECT id FROM users WHERE clerk_user_id = %s", (user_ident,))
                row = cur.fetchone()
                if not row:
                    return [] # User not found or no orders yet
                user_id = row[0]
            else:
                # Assume it's an internal ID
                try:
                    user_id = int(user_ident)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid User ID format")

            cur.execute("""
                SELECT id, total_amount, status, created_at 
                FROM orders WHERE user_id = %s ORDER BY created_at DESC
            """, (user_id,))
            orders = []
            for row in cur.fetchall():
                oid, total, status, date = row
                # Get items
                cur.execute("""
                    SELECT oi.quantity, p.title, p.image_url, oi.price_at_time
                    FROM order_items oi JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = %s
                """, (oid,))
                # Return items with images and price
                items = [{"quantity": r[0], "title": r[1], "image_url": r[2], "price": float(r[3])} for r in cur.fetchall()]
                
                orders.append({
                    "id": oid,
                    "total": float(total),
                    "status": status,
                    "date": str(date),
                    "items": items
                })
            return orders
    finally:
        conn.close()
