from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from config.db import get_db_connection
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# Cloudinary Configuration
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)

router = APIRouter()

@router.get("/")
def get_products(store_id: Optional[int] = None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if store_id:
                cur.execute("SELECT * FROM products WHERE store_id = %s ORDER BY id DESC", (store_id,))
            else:
                cur.execute("SELECT * FROM products ORDER BY id DESC")
            rows = cur.fetchall()
            return rows
    finally:
        conn.close()

@router.get("/{product_id}")
def get_product(product_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cur.fetchone()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return product
    finally:
        conn.close()

@router.post("/")
async def create_product(
    title: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    store_id: int = Form(...),
    image: UploadFile = File(...)
):
    # Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(image.file)
        image_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO products (title, price, stock, category, description, image_url, store_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, title, image_url
            """, (title, price, stock, category, description, image_url, store_id))
            new_product = cur.fetchone()
            return {"success": True, "product": new_product}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.put("/{product_id}")
async def update_product(
    product_id: int,
    title: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if product exists
            cur.execute("SELECT image_url FROM products WHERE id = %s", (product_id,))
            product = cur.fetchone()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            image_url = product['image_url']

            # If new image is uploaded, process it
            if image:
                try:
                    upload_result = cloudinary.uploader.upload(image.file)
                    image_url = upload_result.get("secure_url")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

            cur.execute("""
                UPDATE products 
                SET title=%s, price=%s, stock=%s, category=%s, description=%s, image_url=%s
                WHERE id=%s
                RETURNING *
            """, (title, price, stock, category, description, image_url, product_id))
            updated_product = cur.fetchone()
            
            return {"success": True, "product": updated_product}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/{product_id}")
def delete_product(product_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Check if product is in any orders (order_items)
            cur.execute("SELECT COUNT(*) as count FROM order_items WHERE product_id = %s", (product_id,))
            if cur.fetchone()['count'] > 0:
                raise HTTPException(status_code=400, detail="Cannot delete product that has been ordered. Try archiving it instead.")
            
            # 2. Check bookings
            cur.execute("SELECT COUNT(*) as count FROM bookings WHERE product_id = %s", (product_id,))
            if cur.fetchone()['count'] > 0:
                 raise HTTPException(status_code=400, detail="Cannot delete product with existing bookings.")

            # 3. Clean up Cart Items (Safe to delete)
            cur.execute("DELETE FROM cart_items WHERE product_id = %s", (product_id,))

            # 4. Delete Product
            cur.execute("DELETE FROM products WHERE id=%s RETURNING id", (product_id,))
            deleted = cur.fetchone()
            
            if not deleted:
                raise HTTPException(status_code=404, detail="Product not found")
            
            conn.commit()
            return {"success": True, "message": "Product deleted"}
    except HTTPException as he:
        conn.rollback()
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
