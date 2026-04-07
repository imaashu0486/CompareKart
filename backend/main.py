"""
CompareKart FastAPI Backend
Production-ready API for product price comparison across multiple e-commerce platforms.
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from database import init_db
from mongo_db import init_mongo_indexes, close_mongo
from routes.product_routes import router as product_router
from routes.auth_routes import router as auth_router
from routes.mobile_product_routes import router as mobile_product_router
from routes.mobile_auth_routes import router as mobile_auth_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifecycle.
    Initialize database on startup.
    """
    # Startup
    logger.info("Initializing CompareKart backend...")
    init_db()
    await init_mongo_indexes()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    await close_mongo()
    logger.info("Shutting down CompareKart backend...")


# Create FastAPI app
app = FastAPI(
    title="CompareKart API",
    description="Real-time product price comparison across Amazon, Flipkart, Croma, and eBay",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Status and timestamp
    """
    return {
        "status": "healthy",
        "service": "CompareKart API",
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API documentation.
    
    Returns:
        Welcome message and API information
    """
    return {
        "message": "Welcome to CompareKart API",
        "description": "Real-time product price comparison",
        "documentation": "/docs",
        "version": "1.0.0",
    }


# Include routers
app.include_router(product_router)
app.include_router(auth_router)
app.include_router(mobile_product_router)
app.include_router(mobile_auth_router)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with standardized response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


# Catch-all exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "Internal server error",
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn
    import asyncio
    import sys
    
    logger.info("Starting CompareKart API server...")
    logger.info("Server will be available at http://0.0.0.0:8000")
    logger.info("API documentation: http://localhost:8000/docs")
    
    # Create server config with Windows-specific settings
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
    server = uvicorn.Server(config)
    
    try:
        # Run the server
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)

