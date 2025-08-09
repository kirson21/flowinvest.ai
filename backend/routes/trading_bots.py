from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime
import uuid

from ..models.trading_bot import TradingBot, BotConfig, CreateBotRequest, BotResponse
from ..services.openai_service import OpenAIService
from ..services.bybit_service import BybitService
from ..services.encryption_service import EncryptionService
from ..services.bot_execution_service import BotExecutionService
from .auth import get_current_user

router = APIRouter(prefix="/api/trading-bots", tags=["Trading Bots"])

# Initialize services
openai_service = OpenAIService()
bybit_service = BybitService()
encryption_service = EncryptionService()
bot_execution_service = BotExecutionService()

@router.get("/strategy-templates", response_model=List[Dict[str, Any]])
async def get_strategy_templates(current_user: dict = Depends(get_current_user)):
    """Get all available predefined strategy templates"""
    try:
        from ..database import supabase
        
        response = supabase.table('strategy_templates').select('*').eq('is_active', True).execute()
        
        if response.data:
            return response.data
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategy templates: {str(e)}")

@router.post("/generate-bot", response_model=Dict[str, Any])
async def generate_bot_config(
    request: CreateBotRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI trading bot configuration using OpenAI GPT-5 or Grok-4"""
    try:
        # Validate AI model
        if request.ai_model not in ['gpt-5', 'grok-4']:
            raise HTTPException(status_code=400, detail="Invalid AI model. Use 'gpt-5' or 'grok-4'")
        
        # Generate bot configuration using AI
        if request.strategy_template_id:
            # Use predefined template
            bot_config = await _generate_from_template(request.strategy_template_id, request.customizations)
        else:
            # Generate custom strategy from natural language
            bot_config = await _generate_custom_strategy(
                request.strategy_description,
                request.ai_model,
                request.risk_preferences
            )
        
        # Validate generated configuration
        validated_config = await _validate_bot_config(bot_config)
        
        return {
            "success": True,
            "bot_config": validated_config,
            "ai_model": request.ai_model,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate bot configuration: {str(e)}")

@router.post("/create", response_model=BotResponse)
async def create_trading_bot(
    bot_data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create and save a new trading bot"""
    try:
        from ..database import supabase
        
        # Prepare bot data
        bot_record = {
            "user_id": current_user["id"],
            "bot_name": bot_data["bot_name"],
            "description": bot_data.get("description", ""),
            "ai_model": bot_data["ai_model"],
            "bot_config": json.dumps(bot_data["bot_config"]),
            "strategy_type": bot_data["bot_config"]["strategy"]["type"],
            "is_predefined_strategy": bot_data.get("is_predefined_strategy", False),
            "exchange": bot_data.get("exchange", "bybit"),
            "trading_mode": bot_data.get("trading_mode", "paper"),
            "max_leverage": bot_data["bot_config"]["riskManagement"].get("leverage", 10),
            "max_concurrent_trades": bot_data["bot_config"]["riskManagement"].get("maxConcurrentTrades", 5),
            "status": "inactive"
        }
        
        # Insert into database
        response = supabase.table('trading_bots').insert(bot_record).execute()
        
        if response.data:
            bot = response.data[0]
            
            # Log bot creation
            await _log_bot_activity(
                bot["id"], 
                current_user["id"], 
                "ai_generation", 
                f"Bot created using {bot_data['ai_model']}", 
                {"bot_config": bot_data["bot_config"]}
            )
            
            return BotResponse(**bot)
        else:
            raise HTTPException(status_code=500, detail="Failed to create bot")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trading bot: {str(e)}")

@router.get("/", response_model=List[BotResponse])
async def get_user_bots(current_user: dict = Depends(get_current_user)):
    """Get all trading bots for the current user"""
    try:
        from ..database import supabase
        
        response = supabase.table('trading_bots').select('*').eq('user_id', current_user["id"]).order('created_at', desc=True).execute()
        
        if response.data:
            return [BotResponse(**bot) for bot in response.data]
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bots: {str(e)}")

@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot_details(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific bot"""
    try:
        from ..database import supabase
        
        response = supabase.table('trading_bots').select('*').eq('id', bot_id).eq('user_id', current_user["id"]).single().execute()
        
        if response.data:
            return BotResponse(**response.data)
        else:
            raise HTTPException(status_code=404, detail="Bot not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bot details: {str(e)}")

@router.post("/{bot_id}/start")
async def start_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start a trading bot"""
    try:
        from ..database import supabase
        
        # Get bot details
        bot_response = supabase.table('trading_bots').select('*').eq('id', bot_id).eq('user_id', current_user["id"]).single().execute()
        
        if not bot_response.data:
            raise HTTPException(status_code=404, detail="Bot not found")
            
        bot = bot_response.data
        
        # Check if user has exchange keys configured
        keys_response = supabase.table('user_exchange_keys').select('*').eq('user_id', current_user["id"]).eq('exchange', bot['exchange']).eq('is_active', True).single().execute()
        
        if not keys_response.data:
            raise HTTPException(status_code=400, detail="Exchange API keys not configured")
        
        # Update bot status
        supabase.table('trading_bots').update({
            "status": "active",
            "last_active_at": datetime.utcnow().isoformat()
        }).eq('id', bot_id).execute()
        
        # Start bot execution service
        await bot_execution_service.start_bot(bot_id, bot, keys_response.data)
        
        # Log activity
        await _log_bot_activity(bot_id, current_user["id"], "config_change", "Bot started")
        
        return {"success": True, "message": "Bot started successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@router.post("/{bot_id}/stop")
async def stop_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stop a trading bot"""
    try:
        from ..database import supabase
        
        # Update bot status
        response = supabase.table('trading_bots').update({
            "status": "inactive"
        }).eq('id', bot_id).eq('user_id', current_user["id"]).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Stop bot execution service
        await bot_execution_service.stop_bot(bot_id)
        
        # Log activity
        await _log_bot_activity(bot_id, current_user["id"], "config_change", "Bot stopped")
        
        return {"success": True, "message": "Bot stopped successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")

@router.get("/{bot_id}/trades")
async def get_bot_trades(
    bot_id: str,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get trading history for a specific bot"""
    try:
        from ..database import supabase
        
        # Verify bot ownership
        bot_response = supabase.table('trading_bots').select('id').eq('id', bot_id).eq('user_id', current_user["id"]).single().execute()
        
        if not bot_response.data:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Get trades
        trades_response = supabase.table('bot_trades').select('*').eq('bot_id', bot_id).order('created_at', desc=True).limit(limit).execute()
        
        return {
            "success": True,
            "trades": trades_response.data or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bot trades: {str(e)}")

@router.get("/{bot_id}/performance")
async def get_bot_performance(
    bot_id: str,
    period: str = "daily",
    current_user: dict = Depends(get_current_user)
):
    """Get performance metrics for a specific bot"""
    try:
        from ..database import supabase
        
        # Verify bot ownership
        bot_response = supabase.table('trading_bots').select('id').eq('id', bot_id).eq('user_id', current_user["id"]).single().execute()
        
        if not bot_response.data:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Get performance data
        performance_response = supabase.table('bot_performance').select('*').eq('bot_id', bot_id).eq('period_type', period).order('period_start', desc=True).execute()
        
        return {
            "success": True,
            "performance": performance_response.data or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bot performance: {str(e)}")

@router.delete("/{bot_id}")
async def delete_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a trading bot"""
    try:
        from ..database import supabase
        
        # Stop bot if active
        await stop_bot(bot_id, current_user)
        
        # Delete bot (cascade will handle related records)
        response = supabase.table('trading_bots').delete().eq('id', bot_id).eq('user_id', current_user["id"]).execute()
        
        if response.data:
            return {"success": True, "message": "Bot deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Bot not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete bot: {str(e)}")

# Helper Functions
async def _generate_from_template(template_id: str, customizations: Dict[str, Any]) -> Dict[str, Any]:
    """Generate bot config from predefined template with customizations"""
    from ..database import supabase
    
    # Get template
    response = supabase.table('strategy_templates').select('*').eq('id', template_id).single().execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Strategy template not found")
    
    template = response.data
    base_config = template['strategy_config']
    
    # Apply customizations using AI if needed
    if customizations:
        customized_config = await openai_service.customize_strategy(base_config, customizations)
        return customized_config
    
    return base_config

async def _generate_custom_strategy(
    description: str, 
    ai_model: str, 
    risk_preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate custom strategy using AI based on natural language description"""
    
    # Use OpenAI service to generate strategy
    if ai_model == 'gpt-5':
        bot_config = await openai_service.generate_trading_strategy(description, risk_preferences)
    else:  # grok-4
        # For now, use OpenAI. Later can add Grok integration
        bot_config = await openai_service.generate_trading_strategy(description, risk_preferences)
    
    return bot_config

async def _validate_bot_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize bot configuration"""
    
    # Basic validation
    required_fields = ['botName', 'strategy', 'riskManagement', 'executionRules']
    for field in required_fields:
        if field not in config:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Risk validation
    risk_mgmt = config['riskManagement']
    
    # Limit maximum leverage
    if risk_mgmt.get('leverage', 1) > 20:
        raise HTTPException(status_code=400, detail="Maximum leverage exceeded (20x)")
    
    # Ensure stop loss exists
    if not risk_mgmt.get('stopLossPercent'):
        raise HTTPException(status_code=400, detail="Stop loss is required")
    
    # Limit concurrent trades
    if risk_mgmt.get('maxConcurrentTrades', 1) > 10:
        risk_mgmt['maxConcurrentTrades'] = 10
    
    return config

async def _log_bot_activity(
    bot_id: str, 
    user_id: str, 
    log_type: str, 
    message: str, 
    details: Dict[str, Any] = None
):
    """Log bot activity to database"""
    try:
        from ..database import supabase
        
        log_record = {
            "bot_id": bot_id,
            "user_id": user_id,
            "log_type": log_type,
            "log_level": "info",
            "message": message,
            "details": json.dumps(details) if details else None
        }
        
        supabase.table('bot_logs').insert(log_record).execute()
    except Exception as e:
        print(f"Failed to log bot activity: {e}")  # Log but don't fail the main operation