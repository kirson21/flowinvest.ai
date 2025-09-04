from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase_client import supabase_admin

# Load environment variables
load_dotenv()

router = APIRouter()

# AI Chat Models
class ChatMessage(BaseModel):
    message_type: str  # 'user', 'assistant', 'system'
    message_content: str
    ai_model: Optional[str] = None
    bot_creation_stage: Optional[str] = 'initial'
    context_data: Optional[Dict[str, Any]] = {}

class ChatSessionRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    ai_model: str = 'gpt-5'  # Default to GPT-5
    initial_prompt: Optional[str] = None

class ChatMessageRequest(BaseModel):
    user_id: str
    session_id: str
    message_content: str
    ai_model: str = 'gpt-5'
    bot_creation_stage: Optional[str] = 'clarification'

class AiBotCreationRequest(BaseModel):
    user_id: str
    session_id: str
    ai_model: str
    bot_config: Dict[str, Any]
    strategy_config: Dict[str, Any] = {}
    risk_management: Dict[str, Any] = {}

# Simple AI response simulation for now (until LLM integration is properly set up)
def get_mock_ai_response(message: str, ai_model: str = 'gpt-5') -> str:
    """Generate a mock AI response for testing purposes."""
    
    # If message contains strategy-related keywords, provide bot configuration
    strategy_keywords = ['create', 'bot', 'trading', 'bitcoin', 'strategy', 'momentum', 'scalping']
    if any(keyword in message.lower() for keyword in strategy_keywords):
        return '''Based on your requirements, I'll create a Bitcoin trading bot for you. Here's the configuration:

```json
{
  "ready_to_create": true,
  "bot_config": {
    "name": "Bitcoin Momentum Bot",
    "description": "AI-powered Bitcoin trading bot using momentum strategy",
    "base_coin": "BTC",
    "quote_coin": "USDT", 
    "exchange": "binance",
    "strategy": "momentum",
    "trade_type": "spot",
    "risk_level": "medium"
  },
  "strategy_config": {
    "type": "momentum",
    "indicators": ["RSI", "MACD", "EMA"],
    "timeframes": ["1h", "4h"],
    "entry_conditions": ["RSI < 30", "MACD bullish crossover"],
    "exit_conditions": ["RSI > 70", "Take profit reached"]
  },
  "risk_management": {
    "stop_loss": 2.0,
    "take_profit": 4.0,
    "max_positions": 2,
    "position_size": 0.1
  }
}
```

This bot is ready to be created! Click "Create Bot" when you're satisfied with the configuration.'''
    
    # Regular conversational responses
    responses = [
        "That's interesting! Could you tell me more about your risk tolerance? Are you comfortable with high-risk, high-reward strategies, or do you prefer more conservative approaches?",
        "Great! What's your preferred trading pair? Bitcoin/USDT, Ethereum/USDT, or something else?",
        "Perfect! What timeframe are you thinking for your trades? Quick scalping (minutes), swing trading (hours/days), or longer-term positions?",
        "Excellent choice! Do you have any specific technical indicators you'd like the bot to use? RSI, MACD, moving averages?",
        "That makes sense. What about position sizing? How much of your capital would you like the bot to use per trade?"
    ]
    
    # Return a contextual response based on model
    model_prefix = f"({ai_model.upper()}) " if ai_model == 'grok-4' else ""
    return model_prefix + responses[hash(message) % len(responses)]

@router.post("/ai-bot-chat/start-session")
async def start_chat_session(request: ChatSessionRequest):
    """Start a new AI bot creation chat session."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate AI response
        if request.initial_prompt:
            ai_response = get_mock_ai_response(request.initial_prompt, request.ai_model)
            
            # Save initial user message to database
            if supabase_admin:
                try:
                    supabase_admin.rpc('save_chat_message', {
                        'p_user_id': request.user_id,
                        'p_session_id': session_id,
                        'p_message_type': 'user',
                        'p_message_content': request.initial_prompt,
                        'p_ai_model': request.ai_model,
                        'p_bot_creation_stage': 'initial',
                        'p_context_data': {}
                    }).execute()
                except Exception as e:
                    print(f"Database save error: {e}")
                
                # Save AI response to database
                try:
                    supabase_admin.rpc('save_chat_message', {
                        'p_user_id': request.user_id,
                        'p_session_id': session_id,
                        'p_message_type': 'assistant',
                        'p_message_content': ai_response,
                        'p_ai_model': request.ai_model,
                        'p_bot_creation_stage': 'initial',
                        'p_context_data': {}
                    }).execute()
                except Exception as e:
                    print(f"Database save error: {e}")
        else:
            # Send greeting message
            greeting = f"Hello! I'm your AI trading bot assistant powered by {request.ai_model.upper()}. Let's create a powerful trading bot together!\n\nTo get started, tell me:\n\n1. What cryptocurrency would you like to trade?\n2. What's your trading experience level?\n3. Are you looking for quick profits or steady growth?\n\nWhat's your trading strategy idea?"
            ai_response = greeting
            
            # Save greeting to database
            if supabase_admin:
                try:
                    supabase_admin.rpc('save_chat_message', {
                        'p_user_id': request.user_id,
                        'p_session_id': session_id,
                        'p_message_type': 'assistant',
                        'p_message_content': greeting,
                        'p_ai_model': request.ai_model,
                        'p_bot_creation_stage': 'initial',
                        'p_context_data': {}
                    }).execute()
                except Exception as e:
                    print(f"Database save error: {e}")
        
        return {
            "success": True,
            "session_id": session_id,
            "ai_model": request.ai_model,
            "message": ai_response,
            "stage": "initial"
        }
        
    except Exception as e:
        print(f"Error starting chat session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat session: {str(e)}")

@router.post("/ai-bot-chat/send-message")
async def send_chat_message(request: ChatMessageRequest):
    """Send a message in an existing chat session and get AI response."""
    try:
        # Generate AI response
        ai_response = get_mock_ai_response(request.message_content, request.ai_model)
        
        # Save user message to database
        if supabase_admin:
            try:
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': request.session_id,
                    'p_message_type': 'user',
                    'p_message_content': request.message_content,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': request.bot_creation_stage,
                    'p_context_data': {}
                }).execute()
            except Exception as e:
                print(f"Database save error: {e}")
            
            # Save AI response to database
            try:
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': request.session_id,
                    'p_message_type': 'assistant',
                    'p_message_content': ai_response,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': request.bot_creation_stage,
                    'p_context_data': {}
                }).execute()
            except Exception as e:
                print(f"Database save error: {e}")
        
        # Check if the response contains a bot configuration
        bot_config = None
        is_ready_to_create = False
        
        try:
            # Try to extract JSON from the response
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                if json_end != -1:
                    json_str = ai_response[json_start:json_end].strip()
                    config_data = json.loads(json_str)
                    if config_data.get("ready_to_create", False):
                        bot_config = config_data
                        is_ready_to_create = True
        except Exception as json_error:
            print(f"No valid JSON configuration found: {json_error}")
        
        return {
            "success": True,
            "session_id": request.session_id,
            "message": ai_response,
            "stage": request.bot_creation_stage,
            "ready_to_create": is_ready_to_create,
            "bot_config": bot_config
        }
        
    except Exception as e:
        print(f"Error sending chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/ai-bot-chat/history/{session_id}")
async def get_chat_history(session_id: str, user_id: str):
    """Get chat history for a session."""
    try:
        if not supabase_admin:
            return {"success": False, "messages": [], "message": "Database not available"}
        
        response = supabase_admin.rpc('get_chat_history', {
            'p_user_id': user_id,
            'p_session_id': session_id
        }).execute()
        
        messages = response.data if response.data else []
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages
        }
        
    except Exception as e:
        print(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.post("/ai-bot-chat/create-bot")
async def create_ai_bot(request: AiBotCreationRequest):
    """Create an AI bot from chat session configuration."""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Extract bot configuration
        bot_config = request.bot_config.get('bot_config', {})
        strategy_config = request.strategy_config or request.bot_config.get('strategy_config', {})
        risk_management = request.risk_management or request.bot_config.get('risk_management', {})
        
        # Get the original prompt from chat history
        chat_response = supabase_admin.rpc('get_chat_history', {
            'p_user_id': request.user_id,
            'p_session_id': request.session_id
        }).execute()
        
        generation_prompt = ""
        if chat_response.data:
            # Find the first user message as the generation prompt
            user_messages = [msg for msg in chat_response.data if msg.get('message_type') == 'user']
            if user_messages:
                generation_prompt = user_messages[0].get('message_content', '')
        
        # Save AI bot to database
        bot_response = supabase_admin.rpc('save_ai_bot', {
            'p_user_id': request.user_id,
            'p_name': bot_config.get('name', 'AI Generated Bot'),
            'p_description': bot_config.get('description', 'AI-powered trading bot'),
            'p_ai_model': request.ai_model,
            'p_generation_prompt': generation_prompt,
            'p_bot_config': json.dumps(request.bot_config),
            'p_strategy_config': json.dumps(strategy_config),
            'p_risk_management': json.dumps(risk_management),
            'p_base_coin': bot_config.get('base_coin'),
            'p_quote_coin': bot_config.get('quote_coin'),
            'p_exchange': bot_config.get('exchange', 'binance')
        }).execute()
        
        if not bot_response.data:
            raise HTTPException(status_code=500, detail="Failed to save AI bot to database")
        
        bot_id = bot_response.data
        
        return {
            "success": True,
            "bot_id": bot_id,
            "message": f"AI trading bot '{bot_config.get('name', 'Unnamed Bot')}' created successfully!"
        }
        
    except Exception as e:
        print(f"Error creating AI bot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create AI bot: {str(e)}")

@router.get("/ai-bots/user/{user_id}")
async def get_user_ai_bots(user_id: str):
    """Get all AI bots for a user."""
    try:
        if not supabase_admin:
            return {"success": True, "bots": [], "total": 0}
        
        response = supabase_admin.rpc('get_user_ai_bots', {
            'user_uuid': user_id
        }).execute()
        
        bots = response.data if response.data else []
        
        return {
            "success": True,
            "bots": bots,
            "total": len(bots)
        }
        
    except Exception as e:
        print(f"Error getting user AI bots: {e}")
        return {"success": True, "bots": [], "total": 0}

@router.delete("/ai-bot-chat/cleanup-old-sessions")
async def cleanup_old_chat_sessions():
    """Clean up chat sessions older than 30 days."""
    try:
        if supabase_admin:
            supabase_admin.rpc('cleanup_old_chat_history').execute()
        
        return {"success": True, "message": "Old chat sessions cleaned up"}
        
    except Exception as e:
        print(f"Error cleaning up old chat sessions: {e}")
        return {"success": False, "message": f"Failed to cleanup: {str(e)}"}

# Health check endpoint
@router.get("/ai-bot-chat/health")
async def health_check():
    """Health check for AI bot chat service."""
    try:
        # Check if environment variables are set
        emergent_key = os.getenv('EMERGENT_LLM_KEY')
        
        return {
            "status": "healthy",
            "ai_models_available": ["gpt-5", "grok-4"],
            "database_available": supabase_admin is not None,
            "llm_integration": "mock" if not emergent_key else "configured",
            "message": "AI Bot Chat service is running (using mock responses for now)"
        }
    except Exception as e:
        return {"status": "error", "message": f"Health check failed: {str(e)}"}