from fastapi import APIRouter, HTTPException, Depends, Request
from config.db import get_db_connection
from schemas import AdminSignupRequest, AdminLoginRequest, UserSyncRequest
from passlib.context import CryptContext
import logging

router = APIRouter()
pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

@router.post("/admin/signup")
def admin_signup(admin: AdminSignupRequest):
    """
    Registers a new admin and their store.
    """
    hashed_password = pass_context.hash(admin.password)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if admin exists
            cur.execute("SELECT id FROM admins WHERE admin_id = %s OR email = %s", (admin.adminId, admin.email))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Admin ID or Email already exists")
            
            # Insert new admin
            cur.execute(
                """
                INSERT INTO admins (admin_id, name, email, password_hash)
                VALUES (%s, %s, %s, %s)
                RETURNING id, admin_id, name, email
                """,
                (admin.adminId, admin.fullName, admin.email, hashed_password)
            )
            new_admin = cur.fetchone()
            admin_db_id = new_admin['id']
            
            # Insert store details
            cur.execute(
                """
                INSERT INTO stores (admin_id, name, description, category, address, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    admin_db_id, 
                    admin.storeName, 
                    admin.description, 
                    admin.category, 
                    admin.address, 
                    admin.phone
                )
            )
            
            return {"success": True, "message": "Admin and Store registered successfully", "admin": new_admin}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/admin/login")
def admin_login(creds: AdminLoginRequest):
    """
    Verifies admin credentials.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Find admin by ID usage
            cur.execute("SELECT * FROM admins WHERE admin_id = %s", (creds.adminId,))
            admin = cur.fetchone()
            
            if not admin:
                # Try email 
                cur.execute("SELECT * FROM admins WHERE email = %s", (creds.adminId,))
                admin = cur.fetchone()

            if not admin or not pass_context.verify(creds.password, admin['password_hash']):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Fetch Store Name and ID
            cur.execute("SELECT id, name FROM stores WHERE admin_id = %s", (admin['id'],))
            store = cur.fetchone()
            store_name = store['name'] if store else "Vyapar Store"
            store_id = store['id'] if store else None

            return {
                "success": True, 
                "message": "Login successful", 
                "admin": {
                    "id": admin['id'],
                    "name": admin['name'],
                    "email": admin['email'],
                    "storeName": store_name,
                    "storeId": store_id
                }
            }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()

@router.post("/api/users/sync")
def sync_user(payload: UserSyncRequest):
    """
    Endpoint called explicitly by Frontend after Clerk Login.
    Receives user data and ensures it's in the DB.
    """
    try:
        if not payload.clerkId or not payload.email:
             raise HTTPException(status_code=400, detail="Missing required user fields")

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (clerk_user_id, full_name, email, phone, address, city, pincode)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (clerk_user_id) 
                DO UPDATE SET 
                    email = EXCLUDED.email,
                    full_name = EXCLUDED.full_name,
                    updated_at = NOW()
                RETURNING *
                """,
                (
                    payload.clerkId, 
                    payload.fullName, 
                    payload.email,
                    payload.phone,
                    payload.address,
                    payload.city,
                    payload.pincode
                )
            )
            user = cur.fetchone()
            
        conn.close()
        return {"success": True, "user": user}

    except Exception as e:
        logger.error(f"User sync error: {e}")
        # Don't throw 500 if user exists, just return logic error if needed, but upsert handles existing.
        raise HTTPException(status_code=500, detail=str(e))
