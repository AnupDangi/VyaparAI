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
def get_products():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM products ORDER BY id DESC")
            rows = cur.fetchall()
            # Convert to list of dicts (psycopg dict_row already gives dict-like objects)
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
                INSERT INTO products (title, price, stock, category, description, image_url)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, title, image_url
            """, (title, price, stock, category, description, image_url))
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
            cur.execute("DELETE FROM products WHERE id=%s RETURNING id", (product_id,))
            deleted = cur.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="Product not found")
            return {"success": True, "message": "Product deleted"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
