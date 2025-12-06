from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Auth Schemas ---
class AdminSignupRequest(BaseModel):
    adminId: str
    fullName: str
    email: EmailStr
    password: str
    storeName: str
    description: str
    category: str
    address: str
    phone: str

class AdminLoginRequest(BaseModel):
    adminId: str
    password: str

class ClerkUserWebhook(BaseModel):
    data: dict
    type: str

class UserSyncRequest(BaseModel):
    clerkId: str
    email: str
    fullName: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None

# --- Product Schemas ---
class ProductBase(BaseModel):
    title: str
    price: float
    stock: int = 0
    category: Optional[str] = None
    description: Optional[str] = None
    # image will be handled via UploadFile in the route, but for response/DB it's a string URL using Cloudinary
    image_url: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None

# --- Booking Schemas ---
class BookingCreate(BaseModel):
    customer_phone: str
    product_id: int
    quantity: int

class BookingResponse(BaseModel):
    id: int
    customer_phone: str
    product_id: int
    quantity: int
    total_price: float
    status: str
    booking_time: datetime

# --- Customer/Chat Schemas ---
class ChatMessage(BaseModel):
    id: int
    name: str
    lastMsg: str
