from fastapi import APIRouter, HTTPException
from config.db import get_db_connection
from schemas import UserSyncRequest
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/sync")
def sync_user(payload: UserSyncRequest):
    """
    Endpoint called explicitly by Frontend after Clerk Login.
    Receives user data and ensures it's in the DB.
    """
    logger.info(f"Syncing user: {payload.email}")
    conn = None
    try:
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
                    phone = COALESCE(users.phone, EXCLUDED.phone),
                    updated_at = NOW()
                RETURNING id, full_name, email
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
            conn.commit()
            logger.info(f"User synced successfully: {user['id']}")
            return {"success": True, "user": user}

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"User sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
