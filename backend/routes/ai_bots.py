from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.grok_service import GrokBotCreator
from supabase_client import supabase
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

# Initialize Grok service
grok_creator = GrokBotCreator()

# Pydantic models
class BotCreationRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None

class BotCreationResponse(BaseModel):
    success: bool
    bot_config: Dict[str, Any]
    bot_id: str
    message: str

class BotListResponse(BaseModel):
    success: bool
    bots: list
    total: int

@router.post("/bots/create-with-ai", response_model=BotCreationResponse)
async def create_bot_with_ai(request: BotCreationRequest):
    """Create a trading bot using Grok 4 AI"""
    try:
        # Validate input
        if not request.prompt or len(request.prompt.strip()) < 10:
            raise HTTPException(status_code=400, detail="Prompt must be at least 10 characters long")
        
        # Generate bot configuration using Grok 4
        bot_config = grok_creator.generate_bot_config(request.prompt, request.user_id)
        
        # Validate the generated configuration
        if not grok_creator.validate_bot_config(bot_config):
            raise HTTPException(status_code=400, detail="Generated configuration failed validation")
        
        # Prepare bot data for Supabase
        bot_data = {
            "name": bot_config["name"],
            "description": bot_config["description"],
            "strategy": bot_config["strategy"],
            "risk_level": bot_config["risk_level"],
            "trade_type": bot_config["trade_type"],
            "base_coin": bot_config["base_coin"],
            "quote_coin": bot_config["quote_coin"],
            "exchange": bot_config["exchange"],
            "status": "inactive",
            "is_prebuilt": False,
            "deposit_amount": bot_config.get("deposit_amount", 0),
            "trading_mode": bot_config.get("trading_mode", "simple"),
            "profit_target": bot_config.get("profit_target", 0),
            "stop_loss": bot_config.get("stop_loss", 0),
            "advanced_settings": bot_config.get("advanced_settings", {}),
            "daily_pnl": 0,
            "weekly_pnl": 0,
            "monthly_pnl": 0,
            "win_rate": 0,
            "total_trades": 0,
            "successful_trades": 0,
            "user_id": request.user_id
        }
        
        # Save to Supabase if user_id is provided
        bot_id = str(uuid.uuid4())
        if request.user_id:
            try:
                # Save to Supabase
                response = supabase.table('user_bots').insert(bot_data).execute()
                if response.data:
                    bot_id = response.data[0]['id']
                    bot_config['id'] = bot_id
            except Exception as e:
                print(f"Error saving to Supabase: {e}")
                # Continue without saving if Supabase fails
                pass
        
        return BotCreationResponse(
            success=True,
            bot_config=bot_config,
            bot_id=bot_id,
            message="Bot created successfully with AI"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/bots/user/{user_id}", response_model=BotListResponse)
async def get_user_bots(user_id: str, include_prebuilt: bool = True):
    """Get all bots for a specific user"""
    try:
        # Get bots from Supabase
        if include_prebuilt:
            response = supabase.table('user_bots').select('*').or_(f'user_id.eq.{user_id},is_prebuilt.eq.true').order('created_at', desc=True).execute()
        else:
            response = supabase.table('user_bots').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        bots = response.data or []
        
        return BotListResponse(
            success=True,
            bots=bots,
            total=len(bots)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bots: {str(e)}")

@router.put("/bots/{bot_id}/activate")
async def activate_bot(bot_id: str, user_id: str):
    """Activate a bot (mock implementation for now)"""
    try:
        # Update bot status in Supabase
        response = supabase.table('user_bots').update({
            'status': 'active',
            'last_executed_at': datetime.utcnow().isoformat()
        }).eq('id', bot_id).eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Bot not found or unauthorized")
        
        return {"success": True, "message": "Bot activated successfully", "status": "active"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating bot: {str(e)}")

@router.put("/bots/{bot_id}/deactivate")
async def deactivate_bot(bot_id: str, user_id: str):
    """Deactivate a bot"""
    try:
        # Update bot status in Supabase
        response = supabase.table('user_bots').update({
            'status': 'inactive'
        }).eq('id', bot_id).eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Bot not found or unauthorized")
        
        return {"success": True, "message": "Bot deactivated successfully", "status": "inactive"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating bot: {str(e)}")

@router.delete("/bots/{bot_id}")
async def delete_bot(bot_id: str, user_id: str):
    """Delete a bot"""
    try:
        # Delete from Supabase
        response = supabase.table('user_bots').delete().eq('id', bot_id).eq('user_id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Bot not found or unauthorized")
        
        return {"success": True, "message": "Bot deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting bot: {str(e)}")

@router.get("/bots/{bot_id}")
async def get_bot_details(bot_id: str, user_id: Optional[str] = None):
    """Get detailed information about a specific bot"""
    try:
        query = supabase.table('bots').select('*').eq('id', bot_id)
        
        # If user_id provided, ensure user owns the bot or it's prebuilt
        if user_id:
            query = query.or_(f'user_id.eq.{user_id},is_prebuilt.eq.true')
        
        response = query.execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        return {"success": True, "bot": response.data[0]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bot details: {str(e)}")

# Test endpoint for Grok service
@router.post("/bots/test-grok")
async def test_grok_service(request: BotCreationRequest):
    """Test the Grok service without saving to database"""
    try:
        bot_config = grok_creator.generate_bot_config(request.prompt)
        return {
            "success": True,
            "config": bot_config,
            "message": "Grok service test successful"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grok service error: {str(e)}")