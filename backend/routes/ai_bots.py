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

# Import subscription limit checking
class LimitCheckRequest(BaseModel):
    resource_type: str  # 'ai_bots', 'manual_bots', 'marketplace_products'
    current_count: Optional[int] = 0

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
        
        # CRITICAL: Check subscription limits before creating bot
        user_id = bot_data.get('user_id')
        if user_id:
            # Special case: Super Admin UUID bypasses all limits
            if user_id == "cd0e9717-f85d-4726-81e9-f260394ead58":
                print(f"Super Admin detected - bypassing subscription limits for user {user_id}")
            else:
                # Determine bot type - AI bots vs manual bots
                ai_model = bot_data.get('ai_model', '').lower()
                is_ai_bot = bool(ai_model and ai_model != 'manual')
                resource_type = 'ai_bots' if is_ai_bot else 'manual_bots'
                
                # Count current user bots of this type
                try:
                    if supabase:
                        print(f"Checking existing bots for user {user_id}, resource_type: {resource_type}")
                        existing_response = supabase.table('user_bots')\
                            .select('strategy,description,name')\
                            .eq('user_id', user_id)\
                            .execute()
                        
                        print(f"Existing bots query status: {existing_response.status_code}")
                        print(f"Existing bots data: {existing_response.data}")
                        
                        if existing_response.data:
                            current_count = 0
                            for bot in existing_response.data:
                                # Determine if existing bot is AI-generated or manual
                                # AI bots typically have strategy field or AI-related keywords in description/name
                                bot_strategy = (bot.get('strategy') or '').lower()
                                bot_description = (bot.get('description') or '').lower()
                                bot_name = (bot.get('name') or '').lower()
                                
                                # Check if this is an AI bot based on strategy or AI keywords
                                existing_is_ai = (
                                    bot_strategy in ['momentum', 'steady_growth', 'scalping', 'swing', 'ai_generated'] or
                                    'ai' in bot_description or 'grok' in bot_description or 
                                    'generated' in bot_description or 'algorithm' in bot_description
                                )
                                
                                print(f"Bot: {bot_name}, strategy: {bot_strategy}, is_ai: {existing_is_ai}")
                                
                                if resource_type == 'ai_bots' and existing_is_ai:
                                    current_count += 1
                                elif resource_type == 'manual_bots' and not existing_is_ai:
                                    current_count += 1
                        else:
                            current_count = 0
                        
                        print(f"Current {resource_type} count for user {user_id}: {current_count}")
                        
                        # Call subscription limit checking
                        # Import here to avoid circular imports
                        import sys
                        import os
                        sys.path.append(os.path.dirname(__file__))
                        
                        # Use the supabase admin directly for subscription checking
                        from supabase_client import supabase_admin
                        
                        if supabase_admin:
                            print(f"Checking subscription for user {user_id}")
                            # Check user's subscription
                            sub_response = supabase_admin.table('subscriptions')\
                                .select('*')\
                                .eq('user_id', user_id)\
                                .execute()
                            
                            print(f"Subscription query status: {sub_response.status_code}")
                            print(f"Subscription data: {sub_response.data}")
                            
                            # Default to free plan limits
                            limits = {
                                "ai_bots": 1,
                                "manual_bots": 2,
                                "marketplace_products": 1
                            }
                            
                            if sub_response.data and len(sub_response.data) > 0:
                                subscription = sub_response.data[0]
                                plan_type = subscription.get('plan_type', 'free')
                                print(f"User has subscription with plan_type: {plan_type}")
                                
                                if plan_type == 'super_admin':
                                    # Super admin has no limits - skip limit checking
                                    print("Super admin plan detected - skipping limits")
                                    pass  # Continue with bot creation
                                elif plan_type == 'premium':
                                    # Premium plan limits
                                    limits = {
                                        "ai_bots": 10,
                                        "manual_bots": 20,
                                        "marketplace_products": 10
                                    }
                                    print(f"Premium plan limits applied: {limits}")
                                # else: use free plan limits (already set above)
                            else:
                                print("No subscription found - using free plan limits")
                            
                            # Check if user has reached the limit (skip for super admin)
                            if sub_response.data and len(sub_response.data) > 0:
                                subscription = sub_response.data[0]
                                if subscription.get('plan_type') != 'super_admin':
                                    limit = limits.get(resource_type, 1)
                                    print(f"Checking limit: current_count={current_count}, limit={limit}")
                                    
                                    if current_count >= limit:
                                        error_msg = f"Subscription limit reached. {subscription.get('plan_type', 'Free').title()} plan allows {limit} {resource_type.replace('_', ' ')}. Current: {current_count}"
                                        print(f"LIMIT EXCEEDED: {error_msg}")
                                        raise HTTPException(status_code=403, detail=error_msg)
                                    else:
                                        print(f"Limit check passed: {current_count} < {limit}")
                            else:
                                # No subscription found - apply free limits
                                limit = limits.get(resource_type, 1)
                                print(f"No subscription - checking free limit: current_count={current_count}, limit={limit}")
                                if current_count >= limit:
                                    error_msg = f"Subscription limit reached. Free plan allows {limit} {resource_type.replace('_', ' ')}. Current: {current_count}"
                                    print(f"FREE LIMIT EXCEEDED: {error_msg}")
                                    raise HTTPException(status_code=403, detail=error_msg)
                                else:
                                    print(f"Free limit check passed: {current_count} < {limit}")
                            
                except HTTPException:
                    raise  # Re-raise HTTP exceptions
                except Exception as e:
                    print(f"Warning: Could not check subscription limits: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue with bot creation if limit checking fails (graceful fallback)
        
        # Prepare bot data for Supabase storage (match actual schema)
        supabase_data = {
            "name": bot_data['bot_name'],
            "description": bot_data['description'],
            "strategy": "ai_generated" if bot_data['ai_model'] != 'manual' else "manual",
            "config": bot_data['bot_config'],  # Use 'config' instead of 'bot_config'
            "trading_mode": bot_data.get('trading_mode', 'paper'),
            "status": "inactive",
            "is_prebuilt": False,
            "user_id": bot_data.get('user_id'),
            "daily_pnl": 0.0,
            "weekly_pnl": 0.0,
            "monthly_pnl": 0.0,
            "win_rate": 0.0,
            "total_trades": 0,
            "successful_trades": 0,
            "is_active": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to Supabase
        bot_id = str(uuid.uuid4())
        try:
            if supabase:
                response = supabase.table('user_bots').insert(supabase_data).execute()
                if response.data and len(response.data) > 0:
                    bot_id = response.data[0].get('id', bot_id)
                    print(f"Bot successfully saved to database with ID: {bot_id}")
                else:
                    print(f"Bot creation failed - no data returned from Supabase")
                    raise HTTPException(status_code=500, detail="Failed to create bot - database error")
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            # Don't continue with graceful fallback for bot creation - this should fail
            raise HTTPException(status_code=500, detail=f"Failed to create bot: {str(e)}")
        
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

# Bot management endpoints (restored with Supabase storage)
@router.get("/bots/user/{user_id}")
async def get_user_bots(user_id: str):
    """Get all bots for a specific user"""
    try:
        if not supabase:
            return {"success": True, "bots": [], "total": 0}
            
        response = supabase.table('user_bots').select('*').eq('user_id', user_id).execute()
        bots = response.data if response.data else []
        
        return {
            "success": True,
            "bots": bots,
            "total": len(bots)
        }
        
    except Exception as e:
        print(f"Error fetching user bots: {e}")
        return {"success": True, "bots": [], "total": 0}

@router.post("/bots/{bot_id}/activate")
async def activate_bot(bot_id: str):
    """Activate a trading bot"""
    try:
        if not supabase:
            return {"success": True, "message": f"Bot {bot_id} activated (mock)"}
            
        response = supabase.table('user_bots').update({
            'status': 'active',
            'is_active': True
        }).eq('id', bot_id).execute()
        
        return {"success": True, "message": f"Bot {bot_id} activated successfully"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to activate bot: {str(e)}"}

@router.post("/bots/{bot_id}/deactivate")
async def deactivate_bot(bot_id: str):
    """Deactivate a trading bot"""
    try:
        if not supabase:
            return {"success": True, "message": f"Bot {bot_id} deactivated (mock)"}
            
        response = supabase.table('user_bots').update({
            'status': 'inactive',
            'is_active': False
        }).eq('id', bot_id).execute()
        
        return {"success": True, "message": f"Bot {bot_id} deactivated successfully"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to deactivate bot: {str(e)}"}

@router.delete("/bots/{bot_id}")
async def delete_bot(bot_id: str):
    """Delete a trading bot"""
    try:
        if not supabase:
            return {"success": True, "message": f"Bot {bot_id} deleted (mock)"}
            
        response = supabase.table('user_bots').delete().eq('id', bot_id).execute()
        return {"success": True, "message": f"Bot {bot_id} deleted successfully"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to delete bot: {str(e)}"}

@router.get("/bots/{bot_id}")
async def get_bot_details(bot_id: str):
    """Get detailed information about a specific bot"""
    try:
        if not supabase:
            return {
                "success": True,
                "bot": {"id": bot_id, "name": "Mock Bot", "description": "Mock bot", "status": "inactive"}
            }
            
        response = supabase.table('user_bots').select('*').eq('id', bot_id).execute()
        
        if response.data and len(response.data) > 0:
            return {"success": True, "bot": response.data[0]}
        else:
            raise HTTPException(status_code=404, detail="Bot not found")
            
    except Exception as e:
        return {"success": False, "message": f"Failed to get bot details: {str(e)}"}