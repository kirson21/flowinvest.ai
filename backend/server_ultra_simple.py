"""
Ultra-simplified Flow Invest Backend
No Rust dependencies, no cryptography, just core functionality
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys
import uuid
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Flow Invest API - Simplified",
    description="AI-Powered Investment Platform (Simplified Version)",
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

# Try to import Supabase client, fallback to mock if not available
try:
    from ultra_simple_supabase import supabase, supabase_admin
    SUPABASE_AVAILABLE = bool(supabase)
except:
    supabase = None
    supabase_admin = None
    SUPABASE_AVAILABLE = False

try:
    from simple_exchange_service import SimpleExchangeKeysService
    exchange_service = SimpleExchangeKeysService()
except:
    exchange_service = None

# Pydantic models
class ExchangeKeysRequest(BaseModel):
    exchange: str
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    testnet: bool = True

class BotCreateRequest(BaseModel):
    name: str
    description: str
    strategy: str
    trading_pair: str
    leverage: Optional[float] = 1.0
    stop_loss: Optional[float] = None

# Mock current user for now
def get_current_user():
    return {"id": "demo-user", "email": "demo@example.com"}

# Health endpoints
@app.get("/")
async def root():
    return {
        "message": "Flow Invest API - Simplified Version",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "status": "healthy",
        "supabase_available": SUPABASE_AVAILABLE
    }

@app.get("/api/")
async def api_root():
    return {
        "message": "Flow Invest API - Simplified",
        "version": "1.0.0",
        "status": "healthy",
        "features": ["exchange_keys", "basic_trading_bots", "health_monitoring"]
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {
            "api": "running",
            "supabase": "connected" if SUPABASE_AVAILABLE else "unavailable",
            "exchange_service": "available" if exchange_service else "unavailable"
        }
    }

@app.get("/api/status")
async def get_status():
    return {
        "status": "ok",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "simplified": True
    }

# Exchange Keys Endpoints
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

@app.post("/api/exchange-keys/add")
async def add_exchange_keys(request: ExchangeKeysRequest, current_user: dict = Depends(get_current_user)):
    """Add exchange API keys"""
    if not exchange_service:
        return {"success": False, "error": "Exchange service not available"}
    
    result = exchange_service.store_api_keys(
        user_id=current_user["id"],
        exchange=request.exchange,
        api_key=request.api_key,
        api_secret=request.api_secret,
        passphrase=request.passphrase,
        testnet=request.testnet
    )
    
    return result

@app.get("/api/exchange-keys/")
async def get_user_exchange_keys(current_user: dict = Depends(get_current_user)):
    """Get user's exchange keys"""
    if not exchange_service:
        return {"success": False, "error": "Exchange service not available"}
    
    return exchange_service.get_user_keys(current_user["id"])

@app.post("/api/exchange-keys/test/{key_id}")
async def test_exchange_keys(key_id: str, current_user: dict = Depends(get_current_user)):
    """Test exchange API key connection"""
    if not exchange_service:
        return {"success": False, "error": "Exchange service not available"}
    
    return exchange_service.test_connection(current_user["id"], key_id)

@app.delete("/api/exchange-keys/{key_id}")
async def delete_exchange_keys(key_id: str, current_user: dict = Depends(get_current_user)):
    """Delete exchange API keys"""
    if not exchange_service:
        return {"success": False, "error": "Exchange service not available"}
    
    return exchange_service.delete_api_keys(current_user["id"], key_id)

# Trading Bots Endpoints
@app.get("/api/trading-bots/")
async def get_user_bots(current_user: dict = Depends(get_current_user)):
    """Get user trading bots"""
    if not SUPABASE_AVAILABLE:
        return {
            "success": True,
            "message": "Database not available, using mock data",
            "bots": []
        }
    
    try:
        result = supabase.table('user_trading_bots').select('*').eq('user_id', current_user["id"]).execute()
        return {"success": True, "bots": result.data or []}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/trading-bots/create")
async def create_bot(request: BotCreateRequest, current_user: dict = Depends(get_current_user)):
    """Create a new trading bot"""
    if not SUPABASE_AVAILABLE:
        return {"success": False, "error": "Database not available"}
    
    try:
        bot_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "name": request.name,
            "description": request.description,
            "strategy": request.strategy,
            "trading_pair": request.trading_pair,
            "leverage": request.leverage,
            "stop_loss": request.stop_loss,
            "status": "inactive",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('user_trading_bots').insert(bot_data).execute()
        
        if result.error:
            return {"success": False, "error": result.error}
        
        return {"success": True, "bot": result.data[0] if result.data else bot_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/trading-bots/strategy-templates")
async def get_strategy_templates():
    """Get available strategy templates"""
    return {
        "success": True,
        "templates": [
            {
                "id": "trend_following",
                "name": "Trend Following",
                "description": "Follow market trends with moving averages",
                "risk_level": "medium"
            },
            {
                "id": "scalping",
                "name": "Scalping", 
                "description": "Quick trades for small profits",
                "risk_level": "high"
            },
            {
                "id": "hodl",
                "name": "HODL Strategy",
                "description": "Buy and hold long-term",
                "risk_level": "low"
            }
        ]
    }

@app.post("/api/trading-bots/generate-bot")
async def generate_bot():
    """Generate bot configuration using AI (simplified)"""
    return {
        "success": False,
        "message": "AI bot generation requires OpenAI integration. For now, please use strategy templates."
    }

# Authentication endpoints (simplified)
@app.get("/api/auth/health")
async def auth_health():
    """Auth health check"""
    return {
        "success": True,
        "message": "Authentication service is healthy (simplified mode)",
        "supabase_connected": SUPABASE_AVAILABLE
    }

@app.post("/api/auth/admin/setup")
async def admin_setup():
    """Admin setup"""
    return {
        "success": True,
        "message": "Admin setup completed (simplified mode)",
        "supabase_available": SUPABASE_AVAILABLE
    }

# Error handlers
@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": str(exc)}

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "message": "The requested resource was not found"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))
    
    print(f"🚀 Starting Flow Invest API (Simplified) on port {port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Supabase Available: {SUPABASE_AVAILABLE}")
    
    uvicorn.run(
        "server_ultra_simple:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )