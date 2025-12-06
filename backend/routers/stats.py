from fastapi import APIRouter, HTTPException
from config.db import get_db_connection
from datetime import date
import arrow

router = APIRouter()

@router.get("/stats")
def get_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Total Users
            cur.execute("SELECT COUNT(*) as count FROM users")
            total_users = cur.fetchone()['count']

            # Total Revenue (sum of all orders)
            cur.execute("SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders")
            total_revenue = cur.fetchone()['revenue']

            # Orders Today
            cur.execute("SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) = %s", (date.today(),))
            orders_today = cur.fetchone()['count']

            # Low Stock Items (< 10)
            cur.execute("SELECT COUNT(*) as count FROM products WHERE stock < 10")
            low_stock = cur.fetchone()['count']

            return {
                "totalUsers": total_users,
                "totalRevenue": total_revenue,
                "ordersToday": orders_today,
                "lowStockItems": low_stock
            }
    except Exception as e:
        print(f"Stats Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")
    finally:
        conn.close()

@router.get("/categories/performance")
def get_category_performance():
    # For now, we simulate "Revenue" based on products inventory value or mock it, 
    # since we may not have enough order data. 
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get category counts
            cur.execute("""
                SELECT category as name, COUNT(*) as product_count, COALESCE(SUM(price * stock), 0) as potential_revenue 
                FROM products 
                GROUP BY category
            """)
            rows = cur.fetchall()
            
            performance = []
            for r in rows:
                performance.append({
                    "name": r['name'] or "Uncategorized",
                    "revenue": r['potential_revenue'], 
                    "orders": int(r['product_count']), 
                    "growth": 0 # Placeholder
                })
            return performance
    finally:
        conn.close()

@router.get("/activity")
def get_recent_activity():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Union Orders, Products, Users
            # We fetch top 5 recent events
            query = """
                SELECT 'order' as type, 'New order #' || id::text as action, created_at FROM orders
                UNION ALL
                SELECT 'user' as type, 'User registered: ' || full_name as action, created_at FROM users
                UNION ALL
                SELECT 'alert' as type, 'Low stock: ' || title as action, created_at FROM products WHERE stock < 10
                ORDER BY created_at DESC
                LIMIT 10
            """
            cur.execute(query)
            rows = cur.fetchall()
            
            activity = []
            for r in rows:
                # Calculate relative time using arrow or similar logic if needed, 
                # but for simplicity return string or format it in frontend. 
                # Let's return raw timestamp and 'time' string for frontend friendliness if possible.
                # Actually, frontend expects "2 min ago". We can compute it or just return timestamp.
                # Let's compute a simple string here or return timestamp.
                # Pydantic usually handles datetime serialization.
                dt = r['created_at']
                time_str = arrow.get(dt).humanize() if dt else "just now"
                
                activity.append({
                    "action": r['action'],
                    "time": time_str,
                    "type": r['type']
                })
            return activity
    except Exception as e:
        print(f"Activity Error: {e}")
        # Return empty list on error
        return []
    finally:
        conn.close()
