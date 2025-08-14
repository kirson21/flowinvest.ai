from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.grok_service import GrokBotCreator
from supabase_client import supabase
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

# Initialize Grok service only (no OpenAI to avoid Rust dependencies)
grok_creator = GrokBotCreator()

# Pydantic models
class BotCreationRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None

class TradingBotGenerationRequest(BaseModel):
    ai_model: str  # Only 'grok-4' supported now
    strategy_description: str
    risk_preferences: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class BotCreationResponse(BaseModel):
    success: bool
    bot_config: Dict[str, Any]
    bot_id: str
    message: str

@router.post("/trading-bots/generate-bot")
async def generate_trading_bot(request: TradingBotGenerationRequest):
    """Generate trading bot configuration using Grok-4 only (no OpenAI to avoid Rust)"""
    try:
        # Validate input
        if not request.strategy_description or len(request.strategy_description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Strategy description must be at least 10 characters long")
        
        # Only support Grok-4 to avoid OpenAI/Rust dependencies
        if request.ai_model == 'gpt-5':
            raise HTTPException(status_code=400, detail="GPT-5 temporarily unavailable due to deployment constraints. Please use Grok-4.")
        
        if request.ai_model not in ['grok-4']:
            raise HTTPException(status_code=400, detail="Only 'grok-4' model is currently supported")
        
        # Generate bot configuration using Grok only
        bot_config = grok_creator.generate_bot_config(request.strategy_description, request.user_id)
        
        # Validate the generated configuration
        if not grok_creator.validate_bot_config(bot_config):
            raise HTTPException(status_code=400, detail="Generated configuration failed validation")
        
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

@router.post("/trading-bots/create")
async def create_trading_bot(bot_data: Dict[str, Any]):
    """Create and save a trading bot from generated configuration (with Supabase storage)"""
    try:
        # Validate required fields
        required_fields = ['bot_name', 'description', 'ai_model', 'bot_config']
        for field in required_fields:
            if field not in bot_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Prepare bot data for Supabase storage
        supabase_data = {
            "name": bot_data['bot_name'],
            "description": bot_data['description'],
            "ai_model": bot_data['ai_model'],
            "bot_config": bot_data['bot_config'],
            "is_predefined_strategy": bot_data.get('is_predefined_strategy', False),
            "trading_mode": bot_data.get('trading_mode', 'paper'),
            "status": "inactive",
            "is_prebuilt": False,
            "user_id": bot_data.get('user_id'),
            "daily_pnl": 0,
            "weekly_pnl": 0,
            "monthly_pnl": 0,
            "win_rate": 0,
            "total_trades": 0,
            "successful_trades": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to Supabase
        bot_id = str(uuid.uuid4())
        try:
            if supabase:
                response = supabase.table('user_bots').insert(supabase_data).execute()
                if response.data:
                    bot_id = response.data[0].get('id', bot_id)
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            # Continue without saving if Supabase fails
            pass
        
        return {
            "success": True,
            "bot_id": bot_id,
            "message": f"Trading bot '{bot_data['bot_name']}' created successfully using {bot_data['ai_model'].upper()}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bot: {str(e)}")

# Legacy endpoint for backward compatibility
@router.post("/bots/create-with-ai", response_model=BotCreationResponse)
async def create_bot_with_ai(request: BotCreationRequest):
    """Legacy endpoint - create bot with Grok only"""
    try:
        if not request.prompt or len(request.prompt.strip()) < 10:
            raise HTTPException(status_code=400, detail="Prompt must be at least 10 characters long")
        
        # Generate bot using Grok
        bot_config = grok_creator.generate_bot_config(request.prompt, request.user_id)
        
        if not grok_creator.validate_bot_config(bot_config):
            raise HTTPException(status_code=400, detail="Generated bot configuration is invalid")
        
        bot_id = str(uuid.uuid4())
        
        return BotCreationResponse(
            success=True,
            bot_config=bot_config,
            bot_id=bot_id,
            message="Bot created successfully with Grok-4"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Mock endpoints (no database operations)
@router.get("/bots/user/{user_id}")
async def get_user_bots(user_id: str):
    """Get user bots (mock response)"""
    return {
        "success": True,
        "bots": [],
        "message": "Mock response - no bots stored"
    }

@router.post("/bots/{bot_id}/activate")
async def activate_bot(bot_id: str):
    """Activate bot (mock)"""
    return {
        "success": True,
        "message": f"Bot {bot_id} activated (mock)"
    }

@router.post("/bots/{bot_id}/deactivate")
async def deactivate_bot(bot_id: str):
    """Deactivate bot (mock)"""
    return {
        "success": True,
        "message": f"Bot {bot_id} deactivated (mock)"
    }

@router.delete("/bots/{bot_id}")
async def delete_bot(bot_id: str):
    """Delete bot (mock)"""
    return {
        "success": True,
        "message": f"Bot {bot_id} deleted (mock)"
    }

@router.get("/bots/{bot_id}")
async def get_bot_details(bot_id: str):
    """Get bot details (mock)"""
    return {
        "success": True,
        "bot": {
            "id": bot_id,
            "name": "Mock Bot",
            "description": "Mock bot for testing",
            "status": "inactive"
        }
    }