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
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# AI Bot Creation Prompt Template
AI_BOT_CREATION_PROMPT = """
You are an expert AI trading bot creator. Your role is to help users create sophisticated trading bots by asking clarifying questions and gathering detailed requirements.

IMPORTANT GUIDELINES:
1. Ask ONE specific question at a time
2. Be conversational and friendly
3. Focus on gathering essential information for bot creation
4. After collecting enough information, provide a complete bot configuration
5. Always consider risk management and trading safety

INFORMATION TO GATHER (ask about these one by one):
1. Trading Strategy Type (scalping, momentum, mean reversion, swing trading, etc.)
2. Target Cryptocurrency/Trading Pair
3. Exchange preference
4. Risk tolerance (low, medium, high)
5. Trading capital/position size
6. Time horizon (minutes, hours, days)
7. Technical indicators preference
8. Stop-loss and take-profit preferences
9. Any specific market conditions or requirements

When you have gathered sufficient information, respond with a JSON configuration in this exact format:
```json
{
  "ready_to_create": true,
  "bot_config": {
    "name": "Bot Name",
    "description": "Detailed description",
    "base_coin": "BTC",
    "quote_coin": "USDT", 
    "exchange": "binance",
    "strategy": "momentum",
    "trade_type": "spot",
    "risk_level": "medium"
  },
  "strategy_config": {
    "type": "momentum",
    "indicators": ["RSI", "MACD"],
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

Start by greeting the user and asking about their trading strategy preference.
"""

# Initialize LLM Chat
def get_llm_chat(session_id: str, ai_model: str = 'gpt-5'):
    """Initialize LLM chat with proper model selection."""
    try:
        api_key = os.getenv('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=AI_BOT_CREATION_PROMPT
        )
        
        # Set the appropriate model based on user choice
        if ai_model.lower() == 'gpt-5':
            chat.with_model("openai", "gpt-5")
        elif ai_model.lower() == 'grok-4':
            # Note: Grok might be mapped to a different provider
            # Check available models and update accordingly
            chat.with_model("openai", "gpt-4o")  # Fallback for now
        else:
            # Default to GPT-5
            chat.with_model("openai", "gpt-5")
            
        return chat
    except Exception as e:
        print(f"Error initializing LLM chat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize AI model: {str(e)}")

@router.post("/ai-bot-chat/start-session")
async def start_chat_session(request: ChatSessionRequest):
    """Start a new AI bot creation chat session."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize LLM chat
        chat = get_llm_chat(session_id, request.ai_model)
        
        # Create initial system message
        if request.initial_prompt:
            user_message = UserMessage(text=request.initial_prompt)
            ai_response = await chat.send_message(user_message)
            
            # Save initial user message to database
            if supabase_admin:
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': session_id,
                    'p_message_type': 'user',
                    'p_message_content': request.initial_prompt,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': 'initial',
                    'p_context_data': {}
                }).execute()
                
                # Save AI response to database
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': session_id,
                    'p_message_type': 'assistant',
                    'p_message_content': ai_response,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': 'initial',
                    'p_context_data': {}
                }).execute()
        else:
            # Send greeting message
            greeting = "Hello! I'm here to help you create a powerful AI trading bot. Let's start by understanding what kind of trading strategy you'd like to implement. Are you interested in:\n\n1. **Scalping** - Quick, small profits from minor price movements\n2. **Momentum Trading** - Following strong price trends\n3. **Mean Reversion** - Trading when prices return to average\n4. **Swing Trading** - Capturing medium-term price swings\n5. **Something else** - Tell me your specific strategy idea\n\nWhich approach interests you most?"
            ai_response = greeting
            
            # Save greeting to database
            if supabase_admin:
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': session_id,
                    'p_message_type': 'assistant',
                    'p_message_content': greeting,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': 'initial',
                    'p_context_data': {}
                }).execute()
        
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
        # Initialize LLM chat with existing session
        chat = get_llm_chat(request.session_id, request.ai_model)
        
        # Send user message to AI
        user_message = UserMessage(text=request.message_content)
        ai_response = await chat.send_message(user_message)
        
        # Save user message to database
        if supabase_admin:
            supabase_admin.rpc('save_chat_message', {
                'p_user_id': request.user_id,
                'p_session_id': request.session_id,
                'p_message_type': 'user',
                'p_message_content': request.message_content,
                'p_ai_model': request.ai_model,
                'p_bot_creation_stage': request.bot_creation_stage,
                'p_context_data': {}
            }).execute()
            
            # Save AI response to database
            supabase_admin.rpc('save_chat_message', {
                'p_user_id': request.user_id,
                'p_session_id': request.session_id,
                'p_message_type': 'assistant',
                'p_message_content': ai_response,
                'p_ai_model': request.ai_model,
                'p_bot_creation_stage': request.bot_creation_stage,
                'p_context_data': {}
            }).execute()
        
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
        if not emergent_key:
            return {"status": "error", "message": "EMERGENT_LLM_KEY not configured"}
        
        return {
            "status": "healthy",
            "ai_models_available": ["gpt-5", "grok-4"],
            "database_available": supabase_admin is not None,
            "message": "AI Bot Chat service is running"
        }
    except Exception as e:
        return {"status": "error", "message": f"Health check failed: {str(e)}"}