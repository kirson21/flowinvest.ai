from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import webhook, auth, ai_bots
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
PORT = int(os.environ.get("PORT", 8001))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# Create FastAPI app
app = FastAPI(
    title="Flow Invest API",
    description="AI-Powered Investment Platform API",
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

# Include route modules
api_router.include_router(webhook.router, prefix="", tags=["webhook"])
api_router.include_router(auth.router, prefix="", tags=["auth"])
api_router.include_router(ai_bots.router, prefix="", tags=["ai_bots"])

# Mount API router
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Flow Invest API - AI-Powered Investment Platform",
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
    import os
    
    # Get port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8001))
    
    logger.info(f"Starting Flow Invest API on port {port}")
    logger.info(f"Environment: {ENVIRONMENT}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=ENVIRONMENT == "development",
        log_level="info"
    )