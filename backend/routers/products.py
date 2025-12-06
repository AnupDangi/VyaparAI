from fastapi import APIRouter, HTTPException
from app.models.product import Product
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter()

def get_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

@router.get("/")
def get_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "price": r[2], "stock": r[3], "category": r[4], "description": r[5], "image": r[6]} for r in rows]

@router.post("/")
def create_product(product: Product):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (title, price, stock, category, description, image)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (product.title, product.price, product.stock, product.category, product.description, product.image))
    new_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": new_id, **product.dict()}

@router.put("/{product_id}")
def update_product(product_id: int, product: Product):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE products SET title=%s, price=%s, stock=%s, category=%s, description=%s, image=%s
        WHERE id=%s
    """, (product.title, product.price, product.stock, product.category, product.description, product.image, product_id))
    conn.commit()
    conn.close()
    return {"message": "Updated", "id": product_id}

@router.delete("/{product_id}")
def delete_product(product_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted"}
