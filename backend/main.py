"""
Main FastAPI Application
Natural Language to SQL System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Natural Language to SQL API",
    description="Production-ready NL→SQL pipeline that converts natural language questions into executable SQL queries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["NL to SQL"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Natural Language to SQL API",
        "version": "1.0.0",
        "description": "Convert natural language questions to SQL queries",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "nl_to_sql": "/api/nl-to-sql",
            "schema": "/api/schema",
            "initialize": "/api/initialize"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 60)
    print("Natural Language to SQL API Starting...")
    print("=" * 60)
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("Shutting down Natural Language to SQL API...")


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
