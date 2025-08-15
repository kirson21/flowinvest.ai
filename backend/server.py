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

# Import routes (using httpx-based supabase client - no Rust dependencies)
from routes import auth, webhook, verification, ai_bots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
PORT = int(os.environ.get("PORT", 8001))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# Create FastAPI app
app = FastAPI(
    title="f01i.ai API",
    description="Future-Oriented Life & Investments AI Tools API",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# CORS middleware - configured for production
allowed_origins = [
    "https://f01i.ai",
    "https://app.f01i.ai", 
    "https://flowinvestaiapp-kirsons-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001"
]

if ENVIRONMENT == "development":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
            "supabase": "connected" if os.getenv("SUPABASE_URL") else "not_configured"
        }
    }

@app.get("/api/status")
async def get_status():
    return {"status": "ok", "environment": ENVIRONMENT}

# Include route modules (using httpx-based supabase client - no Rust dependencies)
try:
    api_router.include_router(auth.router)
    logger.info("Auth routes loaded successfully")
except Exception as e:
    logger.warning(f"Auth routes failed to load: {e}")

try:
    api_router.include_router(webhook.router)
    logger.info("Webhook routes loaded successfully")
except Exception as e:
    logger.warning(f"Webhook routes failed to load: {e}")

try:
    api_router.include_router(verification.router)
    logger.info("Verification routes loaded successfully")
except Exception as e:
    logger.warning(f"Verification routes failed to load: {e}")

try:
    api_router.include_router(ai_bots.router)
    logger.info("AI bots routes loaded successfully")
except Exception as e:
    logger.warning(f"AI bots routes failed to load: {e}")

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