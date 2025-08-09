from fastapi import FastAPI, APIRouter, HTTPException
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
PORT = int(os.environ.get("PORT", 8001))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

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

# Basic health endpoints
@app.get("/")
async def root():
    return {
        "message": "Flow Invest API - AI-Powered Investment Platform",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "healthy",
        "deployment": "minimal"
    }

@app.get("/api/")
async def api_root():
    return {
        "message": "Flow Invest API - AI-Powered Investment Platform",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "status": "healthy",
        "deployment": "minimal"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "deployment": "minimal",
        "services": {
            "api": "running",
            "database": "minimal_mode"
        }
    }

@app.get("/api/status")
async def get_status():
    return {"status": "ok", "environment": ENVIRONMENT, "deployment": "minimal"}

# Exchange keys endpoint (minimal implementation)
@app.get("/api/exchange-keys/supported-exchanges")
async def get_supported_exchanges():
    """Get list of supported exchanges"""
    return {
        "success": True,
        "exchanges": [
            {
                "id": "bybit",
                "name": "Bybit",
                "logo": "/logos/bybit.png",
                "supports_testnet": True,
                "supports_futures": True,
                "supports_spot": True
            }
        ]
    }

# Trading bots placeholder endpoints
@app.get("/api/trading-bots/")
async def get_user_bots():
    """Get user trading bots - minimal implementation"""
    return {
        "success": True,
        "message": "Trading bot system is in minimal deployment mode",
        "bots": []
    }

@app.post("/api/trading-bots/generate-bot")
async def generate_bot():
    """Generate bot - minimal implementation"""
    return {
        "success": False,
        "message": "Bot generation requires full deployment with OpenAI integration"
    }

# Auth endpoints
@app.get("/api/auth/health")
async def auth_health():
    """Auth health check"""
    return {
        "success": True,
        "message": "Authentication service is in minimal mode",
        "database_connected": False
    }

@app.post("/api/auth/admin/setup")
async def admin_setup():
    """Admin setup"""
    return {
        "success": True,
        "message": "Admin setup is in minimal mode - full database required for complete functionality"
    }

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
    
    logger.info(f"Starting Flow Invest API (Minimal Mode) on port {port}")
    logger.info(f"Environment: {ENVIRONMENT}")
    
    uvicorn.run(
        "server_minimal:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )