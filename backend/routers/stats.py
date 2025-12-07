from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from config.db import get_db_connection
from datetime import date
import arrow

router = APIRouter()

@router.get("/stats")
def get_stats(store_id: Optional[int] = Query(None)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Total Users (Global is fine, but maybe unique customers for store?)
            if store_id:
                # Count unique users who bought from this store
                cur.execute("SELECT COUNT(DISTINCT user_id) as count FROM fact_sales WHERE store_id = %s", (store_id,))
                total_users = cur.fetchone()['count']
            else:
                cur.execute("SELECT COUNT(*) as count FROM users")
                total_users = cur.fetchone()['count']

            # 2. Total Revenue
            if store_id:
                cur.execute("SELECT COALESCE(SUM(total_amount), 0) as revenue FROM fact_sales WHERE store_id = %s", (store_id,))
            else:
                cur.execute("SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders")
            total_revenue = cur.fetchone()['revenue']

            # 3. Orders Today
            if store_id:
                 cur.execute("SELECT COUNT(DISTINCT order_id) as count FROM fact_sales WHERE store_id = %s AND DATE(sale_date) = %s", (store_id, date.today()))
            else:
                cur.execute("SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) = %s", (date.today(),))
            orders_today = cur.fetchone()['count']

            # 4. Low Stock Items (< 10)
            if store_id:
                cur.execute("SELECT COUNT(*) as count FROM products WHERE stock < 10 AND store_id = %s", (store_id,))
            else:
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
def get_category_performance(store_id: Optional[int] = Query(None)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get category counts
            if store_id:
                 cur.execute("""
                    SELECT category as name, COUNT(*) as product_count, COALESCE(SUM(price * stock), 0) as potential_revenue 
                    FROM products 
                    WHERE store_id = %s
                    GROUP BY category
                """, (store_id,))
            else:
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
def get_recent_activity(store_id: Optional[int] = Query(None)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if store_id:
                # Store specific activity
                query = """
                    SELECT 'order' as type, 'New order including ' || product_title as action, sale_date as created_at 
                    FROM fact_sales WHERE store_id = %s
                    UNION ALL
                    SELECT 'alert' as type, 'Low stock: ' || title as action, created_at FROM products WHERE stock < 10 AND store_id = %s
                    ORDER BY created_at DESC
                    LIMIT 10
                """
                cur.execute(query, (store_id, store_id))
            else:
                # Global activity
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
        return []
    finally:
        conn.close()
