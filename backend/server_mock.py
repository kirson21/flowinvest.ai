from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
import random
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Pydantic models
class TradingBotGenerationRequest(BaseModel):
    ai_model: str  # 'gpt-5' or 'grok-4'
    strategy_description: str
    user_id: Optional[str] = None

class BotCreationRequest(BaseModel):
    bot_name: str
    description: str
    ai_model: str
    bot_config: Dict[str, Any]
    is_predefined_strategy: Optional[bool] = False
    trading_mode: Optional[str] = "paper"
    user_id: Optional[str] = None

# Mock AI responses
def get_mock_gpt5_response(prompt: str) -> Dict[str, Any]:
    """Mock GPT-5 response with realistic bot configuration"""
    
    # Analyze prompt for strategy type
    prompt_lower = prompt.lower()
    is_conservative = any(word in prompt_lower for word in ['conservative', 'safe', 'low risk', 'stable'])
    is_aggressive = any(word in prompt_lower for word in ['aggressive', 'high risk', 'risky', 'fast'])
    is_scalping = any(word in prompt_lower for word in ['scalp', 'quick', 'frequent', 'short'])
    
    # Determine base coin
    base_coin = 'BTC'
    if 'eth' in prompt_lower or 'ethereum' in prompt_lower:
        base_coin = 'ETH'
    elif 'sol' in prompt_lower or 'solana' in prompt_lower:
        base_coin = 'SOL'
    elif 'ada' in prompt_lower or 'cardano' in prompt_lower:
        base_coin = 'ADA'
    
    # Configure based on risk level
    if is_scalping:
        config = {
            "botName": f"{base_coin} Lightning Scalper Pro",
            "description": f"High-frequency scalping bot for {base_coin} targeting quick 1-3% gains with tight risk management",
            "strategy": {
                "type": "Scalping",
                "trendTypes": ["Bullish", "Bearish"],
                "entryConditions": {
                    "indicators": [
                        {"name": "RSI", "overbought": 80, "oversold": 20},
                        {"name": "EMA", "periods": [5, 15], "condition": "Fast EMA crossover for quick entries"}
                    ],
                    "gridOrders": {"levels": 3, "spacingPercent": 0.2}
                }
            },
            "riskManagement": {
                "leverage": 8,
                "maxConcurrentTrades": 5,
                "stopLossPercent": 1.5,
                "takeProfitPercent": 2.5,
                "avoidLiquidation": True
            }
        }
    elif is_conservative:
        config = {
            "botName": f"{base_coin} Steady Growth Guardian",
            "description": f"Conservative trend-following strategy for {base_coin} focusing on capital preservation and steady growth",
            "strategy": {
                "type": "Trend Following",
                "trendTypes": ["Bullish"],
                "entryConditions": {
                    "indicators": [
                        {"name": "RSI", "overbought": 70, "oversold": 30},
                        {"name": "EMA", "periods": [50, 200], "condition": "Long-term trend confirmation required"}
                    ],
                    "gridOrders": {"levels": 4, "spacingPercent": 1.0}
                }
            },
            "riskManagement": {
                "leverage": 2,
                "maxConcurrentTrades": 2,
                "stopLossPercent": 3,
                "takeProfitPercent": 8,
                "avoidLiquidation": True
            }
        }
    elif is_aggressive:
        config = {
            "botName": f"{base_coin} Momentum Beast",
            "description": f"Aggressive momentum trading bot for {base_coin} targeting high returns with calculated risk exposure",
            "strategy": {
                "type": "Momentum",
                "trendTypes": ["Bullish", "Bearish"],
                "entryConditions": {
                    "indicators": [
                        {"name": "RSI", "overbought": 75, "oversold": 25},
                        {"name": "MACD", "periods": [12, 26], "condition": "Strong momentum signals required"}
                    ],
                    "gridOrders": {"levels": 8, "spacingPercent": 0.8}
                }
            },
            "riskManagement": {
                "leverage": 15,
                "maxConcurrentTrades": 4,
                "stopLossPercent": 12,
                "takeProfitPercent": 25,
                "avoidLiquidation": True
            }
        }
    else:
        # Balanced default
        config = {
            "botName": f"{base_coin} Smart Breakout Trader",
            "description": f"Balanced breakout strategy for {base_coin} optimized for consistent profits with moderate risk",
            "strategy": {
                "type": "Breakout",
                "trendTypes": ["Bullish", "Bearish"],
                "entryConditions": {
                    "indicators": [
                        {"name": "RSI", "overbought": 70, "oversold": 30},
                        {"name": "Bollinger Bands", "periods": [20], "condition": "Breakout from bands with volume confirmation"}
                    ],
                    "gridOrders": {"levels": 5, "spacingPercent": 0.6}
                }
            },
            "riskManagement": {
                "leverage": 5,
                "maxConcurrentTrades": 3,
                "stopLossPercent": 6,
                "takeProfitPercent": 15,
                "avoidLiquidation": True
            }
        }
    
    # Add common fields
    config.update({
        "executionRules": {
            "orderType": "Limit",
            "timeInForce": "GTC"
        },
        "created_by_ai": True,
        "ai_model": "gpt-4o",
        "user_prompt": prompt,
        "is_predefined_strategy": False,
        "trading_mode": "paper"
    })
    
    return config

def get_mock_grok_response(prompt: str) -> Dict[str, Any]:
    """Mock Grok-4 response with different JSON structure"""
    
    prompt_lower = prompt.lower()
    is_conservative = any(word in prompt_lower for word in ['conservative', 'safe', 'low risk', 'stable'])
    is_aggressive = any(word in prompt_lower for word in ['aggressive', 'high risk', 'risky', 'fast'])
    is_scalping = any(word in prompt_lower for word in ['scalp', 'quick', 'frequent', 'short'])
    
    # Determine base coin
    base_coin = 'BTC'
    if 'eth' in prompt_lower or 'ethereum' in prompt_lower:
        base_coin = 'ETH'
    elif 'sol' in prompt_lower or 'solana' in prompt_lower:
        base_coin = 'SOL'
    
    # Configure based on strategy
    if is_scalping:
        strategy = 'scalping'
        risk_level = 'high'
        profit_target = 3
        stop_loss = 2
        name = f"{base_coin} Lightning Scalper"
        description = f"High-frequency scalping bot for {base_coin} targeting quick 2-4% gains"
    elif is_conservative:
        strategy = 'trend_following'
        risk_level = 'low'
        profit_target = 10
        stop_loss = 4
        name = f"{base_coin} Steady Growth Bot"
        description = f"Conservative trend-following strategy for {base_coin} with focus on capital preservation"
    elif is_aggressive:
        strategy = 'momentum'
        risk_level = 'high'
        profit_target = 25
        stop_loss = 15
        name = f"{base_coin} Momentum Hunter"
        description = f"Aggressive momentum trading bot for {base_coin} targeting high returns"
    else:
        strategy = 'mean_reversion'
        risk_level = 'medium'
        profit_target = 15
        stop_loss = 8
        name = f"{base_coin} Smart Trader Pro"
        description = f"Balanced mean-reversion strategy for {base_coin} optimized for consistent profits"
    
    return {
        "name": name,
        "description": description,
        "strategy": strategy,
        "risk_level": risk_level,
        "trade_type": "spot",
        "base_coin": base_coin,
        "quote_coin": "USDT",
        "exchange": "binance",
        "deposit_amount": 1000,
        "trading_mode": "simple",
        "profit_target": profit_target,
        "stop_loss": stop_loss,
        "advanced_settings": {
            "max_positions": random.randint(2, 5),
            "position_size": random.randint(20, 40),
            "rebalance_frequency": random.choice(["hourly", "daily", "weekly"]),
            "technical_indicators": ["RSI", "MACD", "Moving Average", "Bollinger Bands"][:random.randint(2, 4)]
        },
        "created_by_ai": True,
        "ai_model": "grok-2-1212",
        "user_prompt": prompt,
        "is_prebuilt": False,
        "status": "inactive"
    }

# Basic health endpoints
@app.get("/")
async def root():
    return {
        "message": "f01i.ai API - Future-Oriented Life & Investments AI Tools",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "status": "healthy"
    }

@app.get("/api/")
async def api_root():
    return {
        "message": "f01i.ai API - Future-Oriented Life & Investments AI Tools",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "status": "healthy"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "services": {
            "api": "running",
            "ai_models": "mock_enabled"
        }
    }

@app.get("/api/status")
async def get_status():
    return {"status": "ok", "environment": os.getenv("ENVIRONMENT", "production")}

# AI Trading Bot Routes (Mock Implementation)
@app.post("/api/trading-bots/generate-bot")
async def generate_trading_bot(request: TradingBotGenerationRequest):
    """Generate trading bot configuration using mock AI responses"""
    try:
        # Validate input
        if not request.strategy_description or len(request.strategy_description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Strategy description must be at least 10 characters long")
        
        if request.ai_model not in ['gpt-5', 'grok-4']:
            raise HTTPException(status_code=400, detail="AI model must be either 'gpt-5' or 'grok-4'")
        
        # Generate bot configuration using mock responses
        if request.ai_model == 'gpt-5':
            bot_config = get_mock_gpt5_response(request.strategy_description)
        else:  # grok-4
            bot_config = get_mock_grok_response(request.strategy_description)
        
        # Add model information to response
        bot_config['ai_model'] = request.ai_model
        
        return {
            "success": True,
            "bot_config": bot_config,
            "ai_model": request.ai_model,
            "message": f"Bot configuration generated successfully using {request.ai_model.upper()} (Mock)"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/trading-bots/create")
async def create_trading_bot(request: BotCreationRequest):
    """Create and save a trading bot from generated configuration (mock storage)"""
    try:
        # Generate a unique bot ID
        bot_id = str(uuid.uuid4())
        
        # Mock successful creation
        return {
            "success": True,
            "bot_id": bot_id,
            "message": f"Trading bot '{request.bot_name}' created successfully using {request.ai_model.upper()} (Mock)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bot: {str(e)}")

# Legacy endpoint for backward compatibility
@app.post("/api/bots/create-with-ai")
async def create_bot_with_ai_legacy(request: dict):
    """Legacy endpoint for backward compatibility (mock)"""
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Use Grok mock by default for legacy endpoint
        bot_config = get_mock_grok_response(prompt)
        bot_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "bot_config": bot_config,
            "bot_id": bot_id,
            "message": "Bot created successfully with AI (Mock)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("server_mock:app", host="0.0.0.0", port=port)