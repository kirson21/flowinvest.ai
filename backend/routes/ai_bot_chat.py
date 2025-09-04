from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase_client import supabase_admin
from services.grok_service import GrokBotCreator

# Load environment variables
load_dotenv()

router = APIRouter()

# Initialize existing Grok service
grok_creator = GrokBotCreator()

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
    ai_model: str = 'grok-4'  # Default to Grok-4 (what's available)
    initial_prompt: Optional[str] = None

class ChatMessageRequest(BaseModel):
    user_id: str
    session_id: str
    message_content: str
    ai_model: str = 'grok-4'
    bot_creation_stage: Optional[str] = 'clarification'

class AiBotCreationRequest(BaseModel):
    user_id: str
    session_id: str
    ai_model: str
    bot_config: Dict[str, Any]
    strategy_config: Dict[str, Any] = {}
    risk_management: Dict[str, Any] = {}

# Conversational AI responses for chat flow
def generate_chat_response(message: str, ai_model: str, conversation_history: List[Dict] = []) -> tuple[str, bool, Dict]:
    """Generate contextual chat responses and detect when ready to create bot."""
    
    message_lower = message.lower()
    
    # Count how many questions have been asked
    question_count = len([msg for msg in conversation_history if msg.get('message_type') == 'assistant'])
    
    # If user mentions specific strategy details, try to create bot configuration
    strategy_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'scalping', 'momentum', 'conservative', 'aggressive', 'trading']
    if any(keyword in message_lower for keyword in strategy_keywords) and question_count >= 2:
        
        # Try to generate bot config using existing GrokBotCreator
        try:
            bot_config = grok_creator.generate_bot_config(message)
            
            # Format as conversation + JSON configuration
            response = f"""Perfect! Based on our conversation, I can now create your trading bot. Here's what I've designed for you:

**{bot_config.get('name', 'Custom Trading Bot')}**
- Strategy: {bot_config.get('strategy', 'Advanced').title()}
- Risk Level: {bot_config.get('risk_level', 'Medium').title()}
- Target: {bot_config.get('base_coin', 'BTC')}/{bot_config.get('quote_coin', 'USDT')}
- Profit Target: {bot_config.get('profit_target', 15)}%
- Stop Loss: {bot_config.get('stop_loss', 10)}%

```json
{{
  "ready_to_create": true,
  "bot_config": {bot_config_json},
  "strategy_config": {{
    "type": "{bot_config.get('strategy', 'mean_reversion')}",
    "indicators": {bot_config.get('advanced_settings', {}).get('technical_indicators', ['RSI', 'MACD'])},
    "max_positions": {bot_config.get('advanced_settings', {}).get('max_positions', 3)},
    "position_size": {bot_config.get('advanced_settings', {}).get('position_size', 20)}
  }},
  "risk_management": {{
    "stop_loss": {bot_config.get('stop_loss', 10)},
    "take_profit": {bot_config.get('profit_target', 15)},
    "max_positions": {bot_config.get('advanced_settings', {}).get('max_positions', 3)}
  }}
}}
```

Ready to create this bot for you! 🚀""".replace('{bot_config_json}', json.dumps({
                "name": bot_config.get('name'),
                "description": bot_config.get('description'),
                "base_coin": bot_config.get('base_coin'),
                "quote_coin": bot_config.get('quote_coin'),
                "exchange": bot_config.get('exchange'),
                "strategy": bot_config.get('strategy'),
                "trade_type": bot_config.get('trade_type'),
                "risk_level": bot_config.get('risk_level')
            }))
            
            # Extract the configuration for bot creation
            final_config = {
                "ready_to_create": True,
                "bot_config": {
                    "name": bot_config.get('name'),
                    "description": bot_config.get('description'),
                    "base_coin": bot_config.get('base_coin'),
                    "quote_coin": bot_config.get('quote_coin'),
                    "exchange": bot_config.get('exchange'),
                    "strategy": bot_config.get('strategy'),
                    "trade_type": bot_config.get('trade_type'),
                    "risk_level": bot_config.get('risk_level')
                },
                "strategy_config": {
                    "type": bot_config.get('strategy'),
                    "indicators": bot_config.get('advanced_settings', {}).get('technical_indicators', ['RSI', 'MACD']),
                    "max_positions": bot_config.get('advanced_settings', {}).get('max_positions', 3),
                    "position_size": bot_config.get('advanced_settings', {}).get('position_size', 20)
                },
                "risk_management": {
                    "stop_loss": bot_config.get('stop_loss', 10),
                    "take_profit": bot_config.get('profit_target', 15),
                    "max_positions": bot_config.get('advanced_settings', {}).get('max_positions', 3)
                }
            }
            
            return response, True, final_config
            
        except Exception as e:
            print(f"Error generating bot config: {e}")
    
    # Conversational flow - ask clarifying questions
    model_prefix = f"({ai_model.upper()}) " if ai_model == 'gpt-5' else ""
    
    if question_count == 0:
        return f"{model_prefix}Great! I'd love to help you create a trading bot. What cryptocurrency are you most interested in trading? Bitcoin, Ethereum, or something else?", False, {}
    elif question_count == 1:
        return f"{model_prefix}Perfect choice! Now, what's your risk tolerance? Are you comfortable with:\n\n• **Conservative** - Steady, lower-risk gains\n• **Moderate** - Balanced risk and reward\n• **Aggressive** - Higher risk for potentially bigger profits\n\nWhich approach fits your style?", False, {}
    elif question_count == 2:
        return f"{model_prefix}Excellent! One more thing - what trading style interests you most?\n\n• **Scalping** - Quick trades for small, frequent profits\n• **Swing Trading** - Medium-term positions over days/weeks\n• **Trend Following** - Riding long-term market trends\n\nWhat sounds most appealing?", False, {}
    else:
        # Generic helpful responses
        responses = [
            f"{model_prefix}That's a great point! Tell me more about your trading experience and what you're hoping to achieve.",
            f"{model_prefix}I understand. What's your typical trading timeframe - minutes, hours, or days?",
            f"{model_prefix}Interesting! Do you have any specific technical indicators you like to use?",
            f"{model_prefix}Good thinking. What about your position sizing - how much capital per trade?"
        ]
        return responses[hash(message) % len(responses)], False, {}

@router.post("/ai-bot-chat/start-session")
async def start_chat_session(request: ChatSessionRequest):
    """Start a new AI bot creation chat session."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history to provide context
        conversation_history = []
        
        # Generate AI response using existing service
        if request.initial_prompt:
            ai_response, is_ready, bot_config = generate_chat_response(
                request.initial_prompt, 
                request.ai_model, 
                conversation_history
            )
            
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
                        'p_context_data': bot_config if is_ready else {}
                    }).execute()
                except Exception as e:
                    print(f"Database save error: {e}")
        else:
            # Send greeting message
            greeting = f"Hello! I'm your AI trading bot assistant powered by {request.ai_model.upper()}. I'll help you create a personalized trading bot through a friendly conversation.\n\nLet's start with the basics - what cryptocurrency would you like your bot to trade?"
            ai_response = greeting
            is_ready = False
            bot_config = {}
            
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
            "stage": "initial",
            "ready_to_create": is_ready,
            "bot_config": bot_config if is_ready else None
        }
        
    except Exception as e:
        print(f"Error starting chat session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat session: {str(e)}")

@router.post("/ai-bot-chat/send-message")
async def send_chat_message(request: ChatMessageRequest):
    """Send a message in an existing chat session and get AI response."""
    try:
        # Get conversation history for context
        conversation_history = []
        if supabase_admin:
            try:
                history_response = supabase_admin.rpc('get_chat_history', {
                    'p_user_id': request.user_id,
                    'p_session_id': request.session_id
                }).execute()
                if history_response.data:
                    conversation_history = history_response.data
            except Exception as e:
                print(f"Error getting conversation history: {e}")
        
        # Generate AI response using existing service with context
        ai_response, is_ready, bot_config = generate_chat_response(
            request.message_content, 
            request.ai_model,
            conversation_history
        )
        
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
                    'p_context_data': bot_config if is_ready else {}
                }).execute()
            except Exception as e:
                print(f"Database save error: {e}")
        
        return {
            "success": True,
            "session_id": request.session_id,
            "message": ai_response,
            "stage": request.bot_creation_stage,
            "ready_to_create": is_ready,
            "bot_config": bot_config if is_ready else None
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
        # Check if existing environment variables are set
        grok_key = os.getenv('GROK_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        ai_models_available = []
        if grok_key:
            ai_models_available.append("grok-4")
        if openai_key:
            ai_models_available.append("gpt-5")
        
        # Fallback if no keys
        if not ai_models_available:
            ai_models_available = ["grok-4", "gpt-5"]  # Will use smart fallback
        
        return {
            "status": "healthy",
            "ai_models_available": ai_models_available,
            "database_available": supabase_admin is not None,
            "grok_service": "available" if grok_key else "using_fallback",
            "openai_service": "available" if openai_key else "not_configured",
            "message": "AI Bot Chat service is running using existing GrokBotCreator service"
        }
    except Exception as e:
        return {"status": "error", "message": f"Health check failed: {str(e)}"}