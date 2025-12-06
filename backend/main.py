from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, products, bookings, customers
import uvicorn
import logging

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App Setup
app = FastAPI(title="VyaparAI Backend")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])

@app.get("/")
def read_root():
    return {"message": "VyaparAI Backend is running 🚀"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
