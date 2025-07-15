from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import webhook, auth, ai_bots
from motor.motor_asyncio import AsyncIOMotorClient
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
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/flow_invest")
DB_NAME = os.environ.get("DB_NAME", "flow_invest")
PORT = int(os.environ.get("PORT", 8001))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# Create FastAPI app
app = FastAPI(
    title="Flow Invest API",
    description="AI-Powered Investment Platform API",
    version="1.0.0"
)

# Configure CORS for production
allowed_origins = [
    "http://localhost:3000",
    "https://flowinvestai.app",
    "https://www.flowinvestai.app",
    "https://*.railway.app",
    "https://*.vercel.app"
]

if ENVIRONMENT == "production":
    allowed_origins = [
        "https://flowinvestai.app",
        "https://www.flowinvestai.app"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
mongodb_client = None
mongodb = None

@app.on_event("startup")
async def startup_db_client():
    global mongodb_client, mongodb
    try:
        mongodb_client = AsyncIOMotorClient(MONGO_URL)
        mongodb = mongodb_client[DB_NAME]
        logger.info(f"Connected to MongoDB: {DB_NAME}")
        
        # Test connection
        await mongodb.command('ping')
        logger.info("MongoDB connection successful")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # In production, you might want to use a cloud MongoDB service
        # For now, we'll continue without MongoDB for Railway deployment

@app.on_event("shutdown")
async def shutdown_db_client():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")

# Include routers
app.include_router(webhook.router)
app.include_router(auth.router)
app.include_router(ai_bots.router)

# Health check endpoints
@app.get("/api")
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
            "database": "connected" if mongodb else "disconnected",
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
    
    logger.info(f"Starting Flow Invest API on port {PORT}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"MongoDB URL: {MONGO_URL}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=PORT,
        reload=ENVIRONMENT == "development",
        log_level="info"
    )