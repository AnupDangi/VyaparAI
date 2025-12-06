
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import uvicorn
import logging

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

# App Setup
app = FastAPI(title="VyaparAI Backend")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Helper ---
def get_db_connection():
    try:
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row, autocommit=True)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# --- Pydantic Models ---

class AdminSignupRequest(BaseModel):
    adminId: str
    fullName: str
    email: EmailStr
    password: str
    # Store details (for future phases, currently we just store admin)
    storeName: str
    description: str
    category: str
    address: str
    phone: str

class AdminLoginRequest(BaseModel):
    adminId: str
    password: str

class ClerkUserWebhook(BaseModel):
    # This matches the minimal data we need from Clerk
    data: dict
    type: str

class StoreSetupRequest(BaseModel):
    # For the separate store setup step if needed, currently part of signup
    name: str
    description: str
    category: str
    address: str
    phone: str

# --- Routes ---

@app.get("/")
def read_root():
    return {"message": "VyaparAI Backend is running 🚀"}

@app.post("/admin/signup")
def admin_signup(admin: AdminSignupRequest):
    """
    Registers a new admin and their store.
    """
    hashed_password = pwd_context.hash(admin.password)
    
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
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/admin/login")
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

            if not admin or not pwd_context.verify(creds.password, admin['password_hash']):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Fetch Store Name
            cur.execute("SELECT name FROM stores WHERE admin_id = %s", (admin['id'],))
            store = cur.fetchone()
            store_name = store['name'] if store else "Vyapar Store"

            return {
                "success": True, 
                "message": "Login successful", 
                "admin": {
                    "id": admin['id'],
                    "name": admin['name'],
                    "email": admin['email'],
                    "storeName": store_name
                }
            }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()

@app.post("/api/users/sync")
async def sync_user(request: Request):
    """
    Endpoint called explicitly by Frontend after Clerk Login,
    OR via Webhook (if configured).
    Receives user data and ensures it's in the DB.
    """
    try:
        payload = await request.json()
        
        # Determine format. If it's a Clerk Webhook, structure is { "data": { ... }, "type": "user.created" }
        # If it's a direct API call from frontend, expect flat { id, email, fullName... }
        
        user_data = {}
        
        if "type" in payload and "data" in payload:
            # It's a Webhook-like structure
            data = payload["data"]
            user_data = {
                "clerk_id": data.get("id"),
                "email": data.get("email_addresses", [{}])[0].get("email_address"),
                "name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
            }
        else:
            # Direct API call
            user_data = {
                "clerk_id": payload.get("clerkId"),
                "email": payload.get("email"),
                "name": payload.get("fullName"),
                "phone": payload.get("phone"),
                "address": payload.get("address"),
                "city": payload.get("city"),
                "pincode": payload.get("pincode")
            }

        if not user_data.get("clerk_id") or not user_data.get("email"):
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
                    user_data["clerk_id"], 
                    user_data["name"], 
                    user_data["email"],
                    user_data.get("phone"),
                    user_data.get("address"),
                    user_data.get("city"),
                    user_data.get("pincode")
                )
            )
            user = cur.fetchone()
            
        conn.close()
        return {"success": True, "user": user}

    except Exception as e:
        logger.error(f"User sync error: {e}")
        # Don't throw 500 if user exists, just return logic error if needed, but upsert handles existing.
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/clerk")
async def clerk_webhook(request: Request):
    """
    Dedicated endpoint for Clerk Webhooks.
    """
    return await sync_user(request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
