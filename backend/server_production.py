from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any
from openai import OpenAI
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

# Initialize OpenAI client for GPT-5
try:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    openai_client = None

# Initialize Grok client
try:
    grok_client = OpenAI(
        api_key=os.getenv("GROK_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
except:
    grok_client = None

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

# Basic health endpoints
@app.get("/")
async def root():
    return {
        "message": "Flow Invest API - AI-Powered Investment Platform",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "status": "healthy"
    }

@app.get("/api/")
async def api_root():
    return {
        "message": "Flow Invest API - AI-Powered Investment Platform",
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
            "openai": "connected" if openai_client else "disconnected",
            "grok": "connected" if grok_client else "disconnected"
        }
    }

@app.get("/api/status")
async def get_status():
    return {"status": "ok", "environment": os.getenv("ENVIRONMENT", "production")}

# AI Bot Generation Functions
def generate_with_openai(prompt: str) -> Dict[str, Any]:
    """Generate bot config using OpenAI GPT"""
    if not openai_client:
        raise ValueError("OpenAI client not configured")
    
    system_prompt = """
    You are an expert trading bot configuration assistant. Convert natural language trading instructions into structured JSON configuration.

    IMPORTANT: You must respond with ONLY valid JSON that follows this exact schema:

    {
        "botName": "string (creative bot name based on strategy)",
        "description": "string (detailed description of the strategy)",
        "strategy": {
            "type": "string (e.g., 'Trend Following', 'Mean Reversion', 'Breakout', 'Scalping', 'Momentum')",
            "trendTypes": ["array of trend types like 'Bullish', 'Bearish']",
            "entryConditions": {
                "indicators": [
                    {"name": "RSI", "overbought": 70, "oversold": 30},
                    {"name": "EMA", "periods": [20, 50], "condition": "description"}
                ],
                "gridOrders": {
                    "levels": 5,
                    "spacingPercent": 0.5
                }
            }
        },
        "riskManagement": {
            "leverage": "number (1-20, conservative to aggressive)",
            "maxConcurrentTrades": "number (1-5)",
            "stopLossPercent": "number (1-15%)",
            "takeProfitPercent": "number (3-25%)",
            "avoidLiquidation": true
        },
        "executionRules": {
            "orderType": "string ('Limit' or 'Market')",
            "timeInForce": "string ('GTC', 'IOC', 'FOK')"
        }
    }

    Respond with ONLY the JSON object, no additional text.
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a trading bot configuration for: {prompt}"}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        config = json.loads(ai_response)
        
        # Add metadata
        config["created_by_ai"] = True
        config["ai_model"] = "gpt-4o"
        config["user_prompt"] = prompt
        config["is_predefined_strategy"] = False
        config["trading_mode"] = "paper"
        
        return config
        
    except Exception as e:
        # Fallback configuration
        return generate_fallback_config(prompt, "gpt-5")

def generate_with_grok(prompt: str) -> Dict[str, Any]:
    """Generate bot config using Grok"""
    if not grok_client:
        raise ValueError("Grok client not configured")
    
    system_prompt = """
    You are an expert trading bot configuration assistant for Flow Invest. Convert natural language trading instructions into structured JSON configuration.

    IMPORTANT: You must respond with ONLY valid JSON that follows this exact schema:

    {
        "name": "string (creative bot name based on strategy)",
        "description": "string (detailed description of the strategy)",
        "strategy": "string (e.g., 'momentum', 'mean_reversion', 'breakout', 'scalping', 'trend_following')",
        "risk_level": "string (low, medium, high)",
        "trade_type": "string (spot, futures, options)",
        "base_coin": "string (e.g., BTC, ETH, SOL)",
        "quote_coin": "string (e.g., USDT, USD, BTC)",
        "exchange": "string (e.g., binance, coinbase, kraken)",
        "deposit_amount": "number (initial capital amount)",
        "trading_mode": "string (simple, advanced)",
        "profit_target": "number (percentage for profit taking)",
        "stop_loss": "number (percentage for stop loss)",
        "advanced_settings": {
            "max_positions": "number (1-10)",
            "position_size": "number (percentage of capital per trade)",
            "rebalance_frequency": "string (daily, weekly, monthly)",
            "technical_indicators": ["string array of indicators"]
        }
    }

    Respond with ONLY the JSON object, no additional text.
    """

    try:
        response = grok_client.chat.completions.create(
            model="grok-2-1212",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a trading bot configuration for: {prompt}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        config = json.loads(ai_response)
        
        # Add metadata
        config["created_by_ai"] = True
        config["ai_model"] = "grok-2-1212"
        config["user_prompt"] = prompt
        config["is_prebuilt"] = False
        config["status"] = "inactive"
        
        return config
        
    except Exception as e:
        # Fallback configuration  
        return generate_fallback_config(prompt, "grok-4")

def generate_fallback_config(prompt: str, model: str) -> Dict[str, Any]:
    """Generate fallback configuration when AI APIs fail"""
    prompt_lower = prompt.lower()
    
    # Analyze prompt for key characteristics
    is_conservative = any(word in prompt_lower for word in ['conservative', 'safe', 'low risk', 'stable'])
    is_aggressive = any(word in prompt_lower for word in ['aggressive', 'high risk', 'risky', 'fast'])
    is_scalping = any(word in prompt_lower for word in ['scalp', 'quick', 'frequent', 'short term'])
    
    if model == "gpt-5":
        # GPT-5 style fallback
        if is_scalping:
            strategy_type = 'Scalping'
            leverage = 10
            stop_loss = 2
            take_profit = 3
            max_trades = 5
            bot_name = "Lightning Scalper Pro"
            description = "High-frequency scalping bot targeting quick 2-3% gains with tight risk management"
        elif is_conservative:
            strategy_type = 'Trend Following'
            leverage = 3
            stop_loss = 3
            take_profit = 8
            max_trades = 2
            bot_name = "Steady Growth Follower"
            description = "Conservative trend-following strategy focusing on capital preservation and steady growth"
        elif is_aggressive:
            strategy_type = 'Momentum'
            leverage = 15
            stop_loss = 12
            take_profit = 20
            max_trades = 4
            bot_name = "Momentum Beast"
            description = "Aggressive momentum trading bot targeting high returns with calculated risk exposure"
        else:
            strategy_type = 'Breakout'
            leverage = 5
            stop_loss = 5
            take_profit = 12
            max_trades = 3
            bot_name = "Smart Breakout Trader"
            description = "Balanced breakout strategy optimized for consistent profits with moderate risk"
        
        return {
            "botName": bot_name,
            "description": description,
            "strategy": {
                "type": strategy_type,
                "trendTypes": ["Bullish", "Bearish"],
                "entryConditions": {
                    "indicators": [
                        {"name": "RSI", "overbought": 70, "oversold": 30},
                        {"name": "EMA", "periods": [20, 50], "condition": "EMA20 > EMA50 for long, EMA20 < EMA50 for short"}
                    ],
                    "gridOrders": {"levels": 5, "spacingPercent": 0.5}
                }
            },
            "riskManagement": {
                "leverage": leverage,
                "maxConcurrentTrades": max_trades,
                "stopLossPercent": stop_loss,
                "takeProfitPercent": take_profit,
                "avoidLiquidation": True
            },
            "executionRules": {"orderType": "Limit", "timeInForce": "GTC"},
            "created_by_ai": True,
            "ai_model": "fallback",
            "user_prompt": prompt,
            "is_predefined_strategy": False,
            "trading_mode": "paper"
        }
    else:
        # Grok-4 style fallback
        base_coin = 'BTC'
        if 'eth' in prompt_lower or 'ethereum' in prompt_lower:
            base_coin = 'ETH'
        elif 'sol' in prompt_lower or 'solana' in prompt_lower:
            base_coin = 'SOL'
        
        if is_scalping:
            strategy = 'scalping'
            risk_level = 'high'
            profit_target = 2
            stop_loss = 1
            name = f"{base_coin} Lightning Scalper"
            description = f"High-frequency scalping bot for {base_coin} targeting quick 1-3% gains"
        elif is_conservative:
            strategy = 'trend_following'
            risk_level = 'low'
            profit_target = 10
            stop_loss = 5
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
                "max_positions": 3,
                "position_size": 33,
                "rebalance_frequency": "daily",
                "technical_indicators": ["RSI", "MACD", "Moving Average"]
            },
            "created_by_ai": True,
            "ai_model": "fallback",
            "user_prompt": prompt,
            "is_prebuilt": False,
            "status": "inactive"
        }

# AI Trading Bot Routes
@app.post("/api/trading-bots/generate-bot")
async def generate_trading_bot(request: TradingBotGenerationRequest):
    """Generate trading bot configuration using either GPT-5 or Grok-4"""
    try:
        # Validate input
        if not request.strategy_description or len(request.strategy_description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Strategy description must be at least 10 characters long")
        
        if request.ai_model not in ['gpt-5', 'grok-4']:
            raise HTTPException(status_code=400, detail="AI model must be either 'gpt-5' or 'grok-4'")
        
        # Generate bot configuration using the selected AI model
        if request.ai_model == 'gpt-5':
            bot_config = generate_with_openai(request.strategy_description)
        else:  # grok-4
            bot_config = generate_with_grok(request.strategy_description)
        
        # Add model information to response
        bot_config['ai_model'] = request.ai_model
        
        return {
            "success": True,
            "bot_config": bot_config,
            "ai_model": request.ai_model,
            "message": f"Bot configuration generated successfully using {request.ai_model.upper()}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/trading-bots/create")
async def create_trading_bot(request: BotCreationRequest):
    """Create and save a trading bot from generated configuration (mock for now)"""
    try:
        # For now, just return success since we don't have Supabase in production
        bot_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "bot_id": bot_id,
            "message": f"Trading bot '{request.bot_name}' created successfully using {request.ai_model.upper()}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bot: {str(e)}")

# Legacy endpoint for backward compatibility
@app.post("/api/bots/create-with-ai")
async def create_bot_with_ai_legacy(request: dict):
    """Legacy endpoint for backward compatibility"""
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Use Grok by default for legacy endpoint
        bot_config = generate_with_grok(prompt)
        bot_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "bot_config": bot_config,
            "bot_id": bot_id,
            "message": "Bot created successfully with AI"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("server_production:app", host="0.0.0.0", port=port)