from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import logging

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routes (restored - using httpx-based supabase client)
from routes import auth, webhook, verification, ai_bots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
PORT = int(os.environ.get("PORT", 8001))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# Create FastAPI app
app = FastAPI(
    title="f01i.ai API",
    description="Future-Oriented Life & Investments AI Tools API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router
api_router = APIRouter()

# Basic health endpoints
@app.get("/")
async def root():
    return {
        "message": "f01i.ai API - Future-Oriented Life & Investments AI Tools",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "healthy"
    }

@app.get("/api/")
async def api_root():
    return {
        "message": "f01i.ai API - Future-Oriented Life & Investments AI Tools",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "healthy"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "services": {
            "api": "running",
            "supabase": "connected"
        }
    }

@app.get("/api/status")
async def get_status():
    return {"status": "ok", "environment": ENVIRONMENT}

# Include route modules (restored - using httpx-based supabase client)
api_router.include_router(auth.router)
api_router.include_router(webhook.router)
api_router.include_router(verification.router)
api_router.include_router(ai_bots.router)

# Include API router
app.include_router(api_router, prefix="/api")

# Error handlers
@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal error: {exc}")
    return {"error": "Internal server error", "message": str(exc)}

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "message": "The requested resource was not found"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))
    
    logger.info(f"Starting f01i.ai API on port {port}")
    logger.info(f"Environment: {ENVIRONMENT}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=ENVIRONMENT == "development",
        log_level="info"
    )