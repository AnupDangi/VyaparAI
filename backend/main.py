"""
VyaparAI Backend & Natural Language to SQL API
"""
import sys
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure 'routers' can be imported regardless of execution directory
# Ensure 'routers' can be imported regardless of execution directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add parent dir to allow 'from backend...' imports to work
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import existing routers
try:
    from routers import auth, products, bookings, customers, ocr, stats
except ImportError:
    # Try absolute import if running as package
    try:
        from backend.routers import auth, products, bookings, customers, ocr, stats
    except ImportError as e:
        print(f"Warning: Could not import routers: {e}")
        auth = products = bookings = customers = ocr = stats = None

# Import new NL2SQL router, Cart Router & Orders Router
try:
    from backend.routers.nl2sql import router as nl2sql_router
    from backend.routers.cart import router as cart_router
    from backend.routers.orders import router as orders_router
    from backend.routers.users import router as users_router
except ImportError:
    # Try relative import if running from backend dir
    try:
        from routers.nl2sql import router as nl2sql_router
        from routers.cart import router as cart_router
        from routers.orders import router as orders_router
        from routers.users import router as users_router
    except ImportError as e:
        print(f"Warning: Could not import new routers: {e}")
        nl2sql_router = None
        cart_router = None
        orders_router = None
        users_router = None

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App Setup
app = FastAPI(
    title="VyaparAI Backend & NL2SQL",
    description="Unified backend for E-commerce and Natural Language to SQL features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Setup
origins = [
    "http://localhost:8080", 
    "https://vyaparaishop.vercel.app",
    "https://vyaparai.onrender.com",
    # Allow all for development flexibility
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Existing Routers
if auth:
    app.include_router(auth.router, tags=["auth"])
    app.include_router(stats.router, prefix="/api/admin", tags=["admin_stats"])
    app.include_router(products.router, prefix="/api/products", tags=["products"])
    app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
    app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
    app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])

# Include Orders Router
if orders_router:
    app.include_router(orders_router, prefix="/api/orders", tags=["orders"])

# Include New NL2SQL Router
if nl2sql_router:
    app.include_router(nl2sql_router, prefix="/api/nl2sql", tags=["NL to SQL"])

# Include OCR Router
if ocr:
    app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])

# Include Cart Router
if cart_router:
    app.include_router(cart_router, prefix="/api/cart", tags=["cart"])

# Include Users Router
if users_router:
    app.include_router(users_router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {
        "message": "VyaparAI Backend is running 🚀",
        "description": "Natural Language to SQL API & E-commerce Backend",
        "endpoints": {
            "docs": "/docs",
            "nl_to_sql": "/api/nl-to-sql",
            "health": "/api/health"
        }
    }

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("VyaparAI Backend Starting...")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down VyaparAI Backend...")

if __name__ == "__main__":
    # Support running this file directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
