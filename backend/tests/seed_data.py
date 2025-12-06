"""
Seed Data Script
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def seed():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                print("🌱 Seeding Database...")
                
                # 1. Cleaner: Optional - only if you want fresh start every time
                # cur.execute("TRUNCATE users, admins, products, stores, carts, orders CASCADE;")
                
                # 2. Users
                print("   -> Creating User...")
                cur.execute("""
                    INSERT INTO users (clerk_user_id, full_name, email, city)
                    VALUES ('user_test_123', 'Test User', 'user@example.com', 'Mumbai')
                    ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name
                    RETURNING id;
                """)
                user_id = cur.fetchone()[0]
                print(f"      User ID: {user_id}")

                # 3. Admins
                print("   -> Creating Admin...")
                cur.execute("""
                    INSERT INTO admins (admin_id, name, email, password_hash)
                    VALUES ('admin_test_1', 'Test Admin', 'admin@example.com', 'hashed_secret')
                    ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id;
                """)
                admin_id = cur.fetchone()[0]
                print(f"      Admin ID: {admin_id}")

                # 4. Stores
                print("   -> Creating Store...")
                cur.execute("""
                    INSERT INTO stores (admin_id, name, category, description)
                    VALUES (%s, 'Vyapar Tech Store', 'Electronics', 'Best gadgets in town')
                    ON CONFLICT DO NOTHING
                    RETURNING id;
                """, (admin_id,))
                store_row = cur.fetchone()
                if not store_row:
                    cur.execute("SELECT id FROM stores WHERE admin_id = %s", (admin_id,))
                    store_id = cur.fetchone()[0]
                else:
                    store_id = store_row[0]
                print(f"      Store ID: {store_id}")

                # 5. Products
                print("   -> Creating Products...")
                products = [
                    ('Apple iPhone 15', 79999.00, 10, 'Electronics', 'Latest Apple smartphone'),
                    ('Samsung Galaxy S24', 69999.00, 15, 'Electronics', 'Samsung flagship AI phone'),
                    ('Sony WH-1000XM5', 24999.00, 5, 'Accessories', 'Noise cancelling headphones'),
                    ('MacBook Air M2', 99999.00, 8, 'Computers', 'Lightweight powerful laptop'),
                    ('Logitech MX Master 3S', 8999.00, 20, 'Accessories', 'Ergonomic mouse')
                ]
                
                for title, price, stock, cat, desc in products:
                    cur.execute("""
                        INSERT INTO products (title, price, stock, category, store_id, description, image_url)
                        VALUES (%s, %s, %s, %s, %s, %s, 'https://placehold.co/400')
                        RETURNING id;
                    """, (title, price, stock, cat, store_id, desc))
                
                print(f"      Seeded {len(products)} products.")
                
                conn.commit()
                print("✅ Seed complete successfully!")
    except Exception as e:
        print(f"Seed Error: {e}")

if __name__ == "__main__":
    seed()
