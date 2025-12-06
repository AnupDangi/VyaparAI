from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, bookings, customers

app = FastAPI(title="Kirana Admin API", version="1.0")

# Allow React frontend
                               
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])

@app.get("/")
def home():
    return {"message": "Kirana Backend Live - Python + FastAPI + Neon DB"}
