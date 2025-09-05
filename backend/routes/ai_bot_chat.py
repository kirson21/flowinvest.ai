from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
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
    ai_model: str = 'gpt-4o'  # Default to GPT-4o
    initial_prompt: Optional[str] = None

class ChatMessageRequest(BaseModel):
    user_id: str
    session_id: str
    message_content: str
    ai_model: str = 'gpt-4o'
    bot_creation_stage: Optional[str] = 'clarification'

class AiBotCreationRequest(BaseModel):
    user_id: str
    session_id: str
    ai_model: str
    bot_config: Dict[str, Any]
    strategy_config: Dict[str, Any] = {}
    risk_management: Dict[str, Any] = {}

# Professional Trading Agent System Prompt
AI_BOT_CREATION_PROMPT = """You are an expert trading systems agent (Futures & Spot). You are a domain specialist: you know trading theory, market microstructure, order types, execution, risk management and quantitative strategy design at an expert level. You never drift into unrelated topics. Your mission: design, specify, backtest, and deliver production-ready automated trading bot specifications that strictly obey user-specified strategy constraints and risk rules.

Important constraints for the agent:
Always ask the user any missing, essential questions needed to produce a complete and safe design (see mandatory question list below).
Produce the final result only in valid JSON (see JSON schema below). If you need to explain, put the explanation inside the JSON fields (e.g., "notes": "...") — do not output plain text outside JSON.
Prioritize capital preservation and strict risk controls. No aggressive defaults without explicit user consent.
When proposing code or integrations, assume execution will run in production: include secrets handling, idempotency, rate-limit handling, and kill-switches.

Mandatory questions to always ask the user (if missing):
- Trading capital (USD or asset) and allowed leverage (if any).
- Allowed instruments: spot or margin/futures? 
- Risk limits: max risk per trade (% of equity), max portfolio drawdown (%), maximum concurrent positions.
- Target timeframe: intraday / swing / multi-day / minute / hourly / daily.
- Strategy intent: long-only, short-capable (spot short via borrowing?), market-making, liquidity-taking, grid, mean-reversion, momentum, statistical arbitrage, etc.
- Slippage & fee assumptions (if unknown, agent must use conservative defaults and document them).
- Execution latency tolerance (ms) and whether colocated infrastructure is required.
- Any custom indicators, signals, or existing model to reuse?

If the user is a newbie or does not know exactly how to answer, the Agent can offer his own options and supplement the strategy based on the description and wishes of the user.

JSON Schema for final bot specification:
```json
{
  "ready_to_create": true,
  "bot_config": {
    "name": "Descriptive Bot Name",
    "description": "Detailed technical description",
    "trading_capital_usd": 10000,
    "leverage_allowed": 1.0,
    "instruments": "spot",
    "base_coin": "BTC",
    "quote_coin": "USDT", 
    "exchange": "binance",
    "strategy_type": "momentum",
    "trade_type": "spot",
    "risk_level": "medium",
    "timeframe": "1h",
    "execution_notes": "Production considerations and assumptions"
  },
  "strategy_config": {
    "strategy_intent": "long_only",
    "technical_indicators": ["RSI", "MACD", "EMA"],
    "entry_conditions": ["Detailed entry logic"],
    "exit_conditions": ["Detailed exit logic"], 
    "timeframes": ["1h", "4h"],
    "signal_logic": "Specific signal generation rules",
    "custom_parameters": {}
  },
  "risk_management": {
    "max_risk_per_trade_percent": 2.0,
    "max_portfolio_drawdown_percent": 10.0,
    "max_concurrent_positions": 3,
    "stop_loss_percent": 2.0,
    "take_profit_percent": 4.0,
    "position_sizing_method": "fixed_percent",
    "position_size_percent": 5.0,
    "kill_switch_conditions": ["Emergency stop conditions"]
  },
  "execution_config": {
    "slippage_assumption_bps": 5,
    "trading_fees_bps": 10,
    "execution_latency_tolerance_ms": 1000,
    "order_types": ["market", "limit"],
    "rate_limit_handling": true,
    "secrets_handling": "environment_variables",
    "idempotency": true
  }
}
```

Begin by greeting the user professionally and asking about their trading capital and preferred instruments (spot vs futures) as these are fundamental to bot design."""

# Initialize LLM integration
async def get_ai_response(message: str, ai_model: str, conversation_history: List[Dict] = []) -> str:
    """Generate AI response using Emergent Universal Key."""
    try:
        # Try to use emergentintegrations if available
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            api_key = os.getenv('EMERGENT_LLM_KEY')
            if not api_key:
                raise ValueError("EMERGENT_LLM_KEY not found")
            
            # Create session ID for this conversation
            session_id = f"bot_creation_{datetime.now().timestamp()}"
            
            # Initialize LLM chat
            chat = LlmChat(
                api_key=api_key,
                session_id=session_id,
                system_message=AI_BOT_CREATION_PROMPT
            )
            
            # Configure model based on user choice
            if ai_model.lower().startswith('gpt') or ai_model.lower() == 'openai':
                chat.with_model("openai", "gpt-4o")
            elif ai_model.lower().startswith('claude') or ai_model.lower() == 'anthropic':
                chat.with_model("anthropic", "claude-3-7-sonnet-20250219")
            elif ai_model.lower().startswith('gemini') or ai_model.lower() == 'google':
                chat.with_model("gemini", "gemini-2.0-flash")
            else:
                # Default to GPT-4o
                chat.with_model("openai", "gpt-4o")
            
            # Send message and get response
            user_message = UserMessage(text=message)
            response = await chat.send_message(user_message)
            
            return response
            
        except ImportError:
            # Fallback if emergentintegrations not available
            print("Emergentintegrations not available, using intelligent fallback")
            return get_intelligent_fallback_response(message, ai_model, conversation_history)
            
    except Exception as e:
        print(f"AI response generation error: {e}")
        return get_intelligent_fallback_response(message, ai_model, conversation_history)

def get_intelligent_fallback_response(message: str, ai_model: str, conversation_history: List[Dict] = []) -> str:
    """Generate intelligent fallback responses when AI service unavailable."""
    message_lower = message.lower()
    question_count = len([msg for msg in conversation_history if msg.get('message_type') == 'assistant'])
    
    # Model-specific prefixes
    model_names = {
        'gpt-4o': '🧠 GPT-4',
        'claude-3-7-sonnet': '🎭 Claude',
        'gemini-2.0-flash': '💎 Gemini'
    }
    model_prefix = model_names.get(ai_model, '🤖 AI')
    
    # If user mentions enough details, generate bot config
    if question_count >= 2 and any(word in message_lower for word in ['bitcoin', 'btc', 'ethereum', 'momentum', 'scalping', 'conservative', 'aggressive']):
        
        # Extract details from conversation
        coin = 'BTC'
        if 'ethereum' in message_lower or 'eth' in message_lower:
            coin = 'ETH'
        elif 'solana' in message_lower or 'sol' in message_lower:
            coin = 'SOL'
            
        strategy = 'momentum'
        risk_level = 'medium'
        
        if 'scalping' in message_lower:
            strategy = 'scalping'
            risk_level = 'high'
        elif 'conservative' in message_lower:
            strategy = 'trend_following'
            risk_level = 'low'
        elif 'aggressive' in message_lower:
            strategy = 'momentum'
            risk_level = 'high'
        
        bot_config = {
            "ready_to_create": True,
            "bot_config": {
                "name": f"{coin} {strategy.title()} Bot",
                "description": f"{model_prefix} generated {strategy} trading bot for {coin}",
                "base_coin": coin,
                "quote_coin": "USDT",
                "exchange": "binance",
                "strategy": strategy,
                "trade_type": "spot",
                "risk_level": risk_level
            },
            "strategy_config": {
                "type": strategy,
                "indicators": ["RSI", "MACD", "EMA"],
                "timeframes": ["1h", "4h"],
                "entry_conditions": [f"{strategy.title()} signal detected", "Volume confirmation"],
                "exit_conditions": ["Profit target reached", "Stop loss triggered"]
            },
            "risk_management": {
                "stop_loss": 2.0 if risk_level == 'low' else 5.0,
                "take_profit": 4.0 if risk_level == 'low' else 8.0,
                "max_positions": 2 if risk_level == 'low' else 4,
                "position_size": 0.05 if risk_level == 'low' else 0.1
            }
        }
        
        return f"""{model_prefix} Perfect! Based on our conversation, I have everything needed to create your trading bot:

**{bot_config['bot_config']['name']}**
• Strategy: {strategy.title()}
• Crypto: {coin}/USDT
• Risk Level: {risk_level.title()}
• Stop Loss: {bot_config['risk_management']['stop_loss']}%
• Take Profit: {bot_config['risk_management']['take_profit']}%

```json
{json.dumps(bot_config, indent=2)}
```

🚀 Your bot configuration is ready! This will be a powerful {strategy} trading bot optimized for {coin} trading."""
    
    # Progressive conversation questions
    if question_count == 0:
        return f"{model_prefix} Hello! I'm excited to help you create a personalized trading bot. Let's start with the fundamentals:\n\n**What cryptocurrency interests you most?**\n• Bitcoin (BTC)\n• Ethereum (ETH) \n• Solana (SOL)\n• Other?\n\nTell me your preference!"
    
    elif question_count == 1:
        return f"{model_prefix} Great choice! Now, what's your trading style preference?\n\n**Risk & Strategy:**\n• **Conservative** - Steady, safe profits with lower risk\n• **Moderate** - Balanced risk/reward approach\n• **Aggressive** - Higher risk for potentially bigger gains\n\nWhich approach fits your personality?"
    
    elif question_count == 2:
        return f"{model_prefix} Perfect! One more key question:\n\n**What trading strategy appeals to you?**\n• **Scalping** - Quick trades, small profits, very active\n• **Swing Trading** - Medium-term positions (days/weeks)\n• **Trend Following** - Ride long-term market movements\n• **Mean Reversion** - Buy dips, sell peaks\n\nWhat sounds most interesting to you?"
    
    else:
        # Generic helpful responses
        responses = [
            f"{model_prefix} That's valuable insight! Could you tell me more about your trading experience level?",
            f"{model_prefix} Interesting! What's your typical investment timeline - short-term or long-term?",
            f"{model_prefix} Good point! Do you have any specific technical indicators you prefer?",
            f"{model_prefix} I understand. What about your comfort with automated trading - any concerns?"
        ]
        return responses[hash(message) % len(responses)]

@router.post("/ai-bot-chat/start-session") 
async def start_chat_session(request: ChatSessionRequest):
    """Start a new AI bot creation chat session."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history (should be empty for new session)
        conversation_history = []
        
        # Generate AI response
        if request.initial_prompt:
            ai_response = await get_ai_response(
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
                        'p_context_data': {}
                    }).execute()
                except Exception as e:
                    print(f"Database save error: {e}")
        else:
            # Send greeting message
            ai_response = await get_ai_response("Start conversation", request.ai_model, [])
        
        # Check if response has bot config
        is_ready = "ready_to_create" in ai_response
        bot_config = None
        if is_ready:
            try:
                if "```json" in ai_response:
                    json_start = ai_response.find("```json") + 7
                    json_end = ai_response.find("```", json_start)
                    if json_end != -1:
                        json_str = ai_response[json_start:json_end].strip()
                        bot_config = json.loads(json_str)
            except:
                is_ready = False
        
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
        
        # Generate AI response with context
        ai_response = await get_ai_response(
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
                    'p_context_data': {}
                }).execute()
            except Exception as e:
                print(f"Database save error: {e}")
        
        # Check if bot configuration is ready
        is_ready = False
        bot_config = None
        
        try:
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                if json_end != -1:
                    json_str = ai_response[json_start:json_end].strip()
                    config_data = json.loads(json_str)
                    if config_data.get("ready_to_create", False):
                        bot_config = config_data
                        is_ready = True
        except Exception as json_error:
            print(f"No valid JSON configuration found: {json_error}")
        
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
            "message": f"AI trading bot '{bot_config.get('name', 'Unnamed Bot')}' created successfully using {request.ai_model}!"
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
        # Check Universal Key
        emergent_key = os.getenv('EMERGENT_LLM_KEY')
        
        ai_models_available = ["gpt-4o", "claude-3-7-sonnet", "gemini-2.0-flash"]
        
        # Try to import emergentintegrations
        integration_status = "unavailable"
        try:
            from emergentintegrations.llm.chat import LlmChat
            integration_status = "available"
        except ImportError:
            integration_status = "fallback_mode"
        
        return {
            "status": "healthy",
            "ai_models_available": ai_models_available,
            "database_available": supabase_admin is not None,
            "universal_key_configured": bool(emergent_key),
            "integration_status": integration_status,
            "message": f"AI Bot Chat service running with Emergent Universal Key ({integration_status})"
        }
    except Exception as e:
        return {"status": "error", "message": f"Health check failed: {str(e)}"}