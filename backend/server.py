# CGI compatibility for Python 3.13+
import cgi_compat

from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import logging
import time

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routes (using httpx-based supabase client - no Rust dependencies)
from routes import auth, webhook, verification, ai_bots, crypto_simple
# Crypto payments temporarily disabled due to pydantic v2 conflicts
# from routes import crypto_payments

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
PORT = int(os.environ.get("PORT", 8001))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# Create FastAPI app
app = FastAPI(
    title="f01i.ai API",
    description="Future-Oriented Life & Investments AI Tools API with Crypto Payment Integration",
    version="1.1.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    print(f"\n🌐 INCOMING REQUEST:")
    print(f"   Method: {request.method}")
    print(f"   URL: {request.url}")
    print(f"   Path: {request.url.path}")
    print(f"   Query: {request.url.query}")
    print(f"   Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    print(f"📤 RESPONSE:")
    print(f"   Status: {response.status_code}")
    print(f"   Process time: {process_time:.4f}s")
    print("=" * 60)
    
    return response

# CORS middleware - configured for production
allowed_origins = [
    "https://f01i.ai",
    "https://f01i.app",  # User's actual frontend domain
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
        "version": "1.1.0",
        "environment": ENVIRONMENT,
        "status": "healthy",
        "features": ["balance_system", "subscriptions", "crypto_payments"]
    }

@app.get("/api/")
async def api_root():
    return {
        "message": "f01i.ai API - Future-Oriented Life & Investments AI Tools",
        "version": "1.1.0",
        "environment": ENVIRONMENT,
        "status": "healthy",
        "features": ["balance_system", "subscriptions", "crypto_payments"]
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.1.0",
        "environment": ENVIRONMENT,
        "services": {
            "api": "running",
            "supabase": "connected" if os.getenv("SUPABASE_URL") else "not_configured",
            "crypto_payments": "available" if os.getenv("CAPITALIST_USERNAME") else "not_configured"
        }
    }

@app.get("/api/status")
async def get_status():
    return {"status": "ok", "environment": ENVIRONMENT}

# Include route modules (using httpx-based supabase client - no Rust dependencies)
try:
    print("=== LOADING AUTH ROUTES ===")
    api_router.include_router(auth.router)
    print(f"✅ Auth routes loaded successfully - {len(auth.router.routes)} routes added")
    for route in auth.router.routes:
        print(f"   {route.methods} {route.path}")
    logger.info("Auth routes loaded successfully")
except Exception as e:
    print(f"❌ Auth routes failed to load: {e}")
    import traceback
    print("Full traceback:")
    traceback.print_exc()
    logger.warning(f"Auth routes failed to load: {e}")

try:
    print("=== LOADING WEBHOOK ROUTES ===")
    api_router.include_router(webhook.router)
    print(f"✅ Webhook routes loaded successfully")
    logger.info("Webhook routes loaded successfully")
except Exception as e:
    print(f"❌ Webhook routes failed to load: {e}")
    logger.warning(f"Webhook routes failed to load: {e}")

try:
    print("=== LOADING VERIFICATION ROUTES ===")
    api_router.include_router(verification.router)
    print(f"✅ Verification routes loaded successfully")
    logger.info("Verification routes loaded successfully")
except Exception as e:
    print(f"❌ Verification routes failed to load: {e}")
    logger.warning(f"Verification routes failed to load: {e}")

try:
    print("=== LOADING AI BOTS ROUTES ===")
    api_router.include_router(ai_bots.router)
    print(f"✅ AI bots routes loaded successfully")
    logger.info("AI bots routes loaded successfully")
except Exception as e:
    print(f"❌ AI bots routes failed to load: {e}")
    logger.warning(f"AI bots routes failed to load: {e}")

try:
    print("=== LOADING CRYPTO PAYMENTS ROUTES ===")
    api_router.include_router(crypto_simple.router)
    print(f"✅ Crypto payments routes loaded successfully")
    logger.info("Crypto payments routes loaded successfully")
except Exception as e:
    print(f"❌ Crypto payments routes failed to load: {e}")
    logger.warning(f"Crypto payments routes failed to load: {e}")

print("=== ROUTE LOADING COMPLETE ===")
print(f"Total API routes loaded: {len(api_router.routes)}")

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