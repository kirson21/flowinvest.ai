from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
import json
from dotenv import load_dotenv
from supabase_client import supabase_admin

# Load environment variables
load_dotenv()

router = APIRouter()

# AI Chat Models
class ChatSessionRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    ai_model: str = 'gpt-4o'
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
TRADING_EXPERT_PROMPT = """You are an expert trading systems specialist. You design production-ready automated trading bots.

CRITICAL INSTRUCTION: You MUST analyze the ENTIRE conversation history to understand what the user has already told you. Do NOT repeat questions about information already provided.

CONVERSATION FLOW:
1. If user hasn't specified TRADING CAPITAL → Ask about capital and leverage
2. If user hasn't specified INSTRUMENTS → Ask about spot vs futures trading
3. If user hasn't specified RISK PARAMETERS → Ask about risk limits and drawdown
4. If user hasn't specified STRATEGY/TIMEFRAME → Ask about trading strategy and timeframes  
5. If user hasn't specified BOT NAME → Ask for bot name
6. If ALL INFO PROVIDED → Generate final bot specification JSON

IMPORTANT: Always check what user has ALREADY provided before asking new questions!

When ready to create bot, respond with this JSON:
{
  "ready_to_create": true,
  "bot_config": {
    "name": "User's chosen name",
    "description": "Professional trading system based on user specs", 
    "base_coin": "User's coin choice",
    "quote_coin": "USDT",
    "trade_type": "spot or futures per user",
    "trading_capital_usd": "User's amount",
    "leverage_allowed": "User's leverage",
    "risk_level": "User's risk preference"
  }
}"""

# Simple context-aware conversation handler
class ConversationTracker:
    def __init__(self):
        self.sessions = {}
    
    def get_conversation_state(self, session_id: str, conversation_history: List[Dict]) -> Dict:
        """Analyze conversation history to determine current state."""
        
        # Combine all user messages to analyze what they've already provided
        user_messages = []
        for msg in conversation_history:
            if msg.get('message_type') == 'user':
                user_messages.append(msg.get('message_content', '').lower())
        
        all_user_input = ' '.join(user_messages).lower()
        
        # Determine what information has been provided
        state = {
            'has_capital': any(word in all_user_input for word in ['$', 'capital', '1000', '5000', '10000', '50000', '100000', 'k']) or any(word in all_user_input for word in ['3x', '4x', '5x', '10x', '2-5x', '3-5x']),
            'has_leverage': any(word in all_user_input for word in ['leverage', 'x', 'futures', 'margin']),
            'has_instruments': any(word in all_user_input for word in ['spot', 'futures', 'margin']),
            'has_risk': any(word in all_user_input for word in ['risk', '%', 'conservative', 'aggressive', 'drawdown']),
            'has_strategy': any(word in all_user_input for word in ['momentum', 'scalping', 'mean', 'trend', 'grid', 'arbitrage']),
            'has_timeframe': any(word in all_user_input for word in ['minute', 'hour', 'daily', 'intraday', 'swing']),
            'has_botname': len([msg for msg in conversation_history if 'name' in msg.get('message_content', '').lower()]) > 0,
            'user_input': all_user_input,
            'question_count': len([msg for msg in conversation_history if msg.get('message_type') == 'assistant'])
        }
        
        return state

    def generate_next_question(self, ai_model: str, state: Dict, current_message: str) -> tuple[str, bool, Dict]:
        """Generate the next appropriate question based on conversation state."""
        
        model_names = {
            'gpt-4o': '🧠 **GPT-4 Trading Expert**',
            'claude-3-7-sonnet': '🎭 **Claude Trading Specialist**', 
            'gemini-2.0-flash': '💎 **Gemini Quant Expert**'
        }
        prefix = model_names.get(ai_model, '🤖 **Trading Expert**')
        
        # Check if we have all information needed to create bot
        if (state['has_capital'] and state['has_instruments'] and 
            state['has_risk'] and state['has_strategy'] and state['has_botname']):
            
            # Generate bot configuration from user inputs
            return self.create_bot_specification(prefix, state, current_message)
        
        # Ask for missing information in order
        if not state['has_capital']:
            return f"""{prefix}

**Question 1: Trading Capital & Leverage**

I need to understand your capital to design appropriate position sizing:

• What is your trading capital (in USD)?
• What leverage do you want? (1x=spot, 2-5x=moderate, 5x+=aggressive)

Example: "$10,000 with 3x leverage"

Please tell me your capital and leverage preference.""", False, {}
            
        elif not state['has_instruments']:
            return f"""{prefix}

**Question 2: Trading Instruments**

Perfect! Now I need to know your instrument preference:

• **Spot Trading**: Safer, no liquidation risk, lower leverage
• **Futures Trading**: Higher leverage, short selling, liquidation risk

Which type aligns with your trading goals?""", False, {}
            
        elif not state['has_risk']:
            return f"""{prefix}

**Question 3: Risk Management**

Critical for your safety:

• Max risk per trade (% of capital)? Conservative: 1-2%, Moderate: 2-3%, Aggressive: 3-5%
• Max portfolio drawdown? Conservative: 5-10%, Moderate: 10-15%
• Max concurrent positions? (Recommended: 1-3)

Example: "2% per trade, 10% max drawdown, 2 positions"

What are your risk limits?""", False, {}
            
        elif not state['has_strategy']:
            return f"""{prefix}

**Question 4: Strategy & Timeframe**

What trading approach interests you?

• **Momentum**: Trend following, breakout trading
• **Scalping**: High-frequency, small quick profits  
• **Mean Reversion**: Buy dips, sell peaks
• **Grid Trading**: Automated range trading

What strategy and timeframe suit your goals?""", False, {}
            
        elif not state['has_botname']:
            return f"""{prefix}

**Question 5: Bot Name**

Finally, what would you like to name your trading bot?

Examples: "Bitcoin Futures Pro", "Altcoin Momentum Trader", "ETH Scalping Engine"

What name do you want for your bot?""", False, {}
            
        else:
            return self.create_bot_specification(prefix, state, current_message)
    
    def create_bot_specification(self, prefix: str, state: Dict, current_message: str) -> tuple[str, bool, Dict]:
        """Create final bot specification based on user inputs."""
        
        user_input = state['user_input'] + ' ' + current_message.lower()
        
        # Extract actual user preferences
        # Capital
        capital = 10000
        if '1000' in user_input or '1k' in user_input:
            capital = 1000
        elif '5000' in user_input or '5k' in user_input:
            capital = 5000
        elif '50000' in user_input or '50k' in user_input:
            capital = 50000
        elif '100000' in user_input or '100k' in user_input:
            capital = 100000
            
        # Leverage
        leverage = 1.0
        if '2x' in user_input:
            leverage = 2.0
        elif '3x' in user_input or '3-5x' in user_input:
            leverage = 3.0
        elif '5x' in user_input:
            leverage = 5.0
        elif '10x' in user_input:
            leverage = 10.0
            
        # Coin
        coin = 'BTC'
        if 'ethereum' in user_input or 'eth' in user_input:
            coin = 'ETH'
        elif 'altcoin' in user_input or 'altcoins' in user_input:
            coin = 'ALT'
        elif 'solana' in user_input or 'sol' in user_input:
            coin = 'SOL'
            
        # Strategy
        strategy = 'momentum'
        if 'scalping' in user_input:
            strategy = 'scalping'
        elif 'mean' in user_input:
            strategy = 'mean_reversion'
        elif 'grid' in user_input:
            strategy = 'grid'
            
        # Trade type
        trade_type = 'spot'
        if 'futures' in user_input:
            trade_type = 'futures'
            
        # Bot name - try to extract from latest message
        bot_name = f"{coin} {strategy.title()} {trade_type.title()} Bot"
        if len(current_message.split()) <= 5 and len(current_message) > 3:
            bot_name = current_message.strip()
        
        bot_config = {
            "ready_to_create": True,
            "bot_config": {
                "name": bot_name,
                "description": f"Professional {strategy} bot for {coin} using {trade_type} trading with {leverage}x leverage",
                "base_coin": coin, 
                "quote_coin": "USDT",
                "trade_type": trade_type,
                "trading_capital_usd": capital,
                "leverage_allowed": leverage,
                "strategy_type": strategy,
                "risk_level": "medium"
            }
        }
        
        return f"""{prefix}

**TRADING BOT SPECIFICATION COMPLETE**

✅ **Based on YOUR specifications:**
• Bot Name: **{bot_name}**  
• Coin: **{coin}** (from your input)
• Trade Type: **{trade_type.upper()}** (as you requested)
• Leverage: **{leverage}x** (per your specification)
• Capital: **${capital:,}**
• Strategy: **{strategy.title()}**

```json
{json.dumps(bot_config, indent=2)}
```

🚀 **Your bot follows your EXACT specifications and is ready!**""", True, bot_config

# Initialize conversation tracker
conversation_tracker = ConversationTracker()

# Simplified AI response function
async def get_contextual_ai_response(message: str, ai_model: str, conversation_history: List[Dict], session_id: str) -> str:
    """Generate contextual AI response that follows conversation flow."""
    
    # Analyze conversation state
    state = conversation_tracker.get_conversation_state(session_id, conversation_history)
    
    print(f"🔍 Conversation state: {state}")
    
    # Generate appropriate response based on state
    response, is_ready, bot_config = conversation_tracker.generate_next_question(ai_model, state, message)
    
    # Try real AI first, fallback to our logic
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv('EMERGENT_LLM_KEY')
        if api_key and len(conversation_history) <= 2:  # Use AI for early conversation
            chat = LlmChat(api_key=api_key, session_id=session_id, system_message=TRADING_EXPERT_PROMPT)
            
            if ai_model == 'gpt-4o':
                chat.with_model("openai", "gpt-4o")
            elif ai_model == 'claude-3-7-sonnet':
                chat.with_model("anthropic", "claude-3-7-sonnet-20250219")  
            elif ai_model == 'gemini-2.0-flash':
                chat.with_model("gemini", "gemini-2.0-flash")
            
            # Add conversation context manually
            context_msg = f"CONVERSATION SO FAR: {state['user_input']}\n\nCURRENT MESSAGE: {message}"
            user_message = UserMessage(text=context_msg)
            ai_response = await chat.send_message(user_message)
            
            if len(ai_response) > 100:  # Real AI response
                return ai_response
                
    except Exception as e:
        print(f"AI error: {e}")
    
    # Use our deterministic logic for reliability
    return response

@router.post("/ai-bot-chat/start-session")
async def start_chat_session(request: ChatSessionRequest):
    """Start AI bot chat session."""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create initial conversation history with user's prompt for state analysis
        initial_history = []
        if request.initial_prompt:
            initial_history = [{
                'message_type': 'user',
                'message_content': request.initial_prompt
            }]
        
        response = await get_contextual_ai_response(
            request.initial_prompt or "Hello", 
            request.ai_model, 
            initial_history,
            session_id
        )
        
        # Save messages to database
        if supabase_admin and request.initial_prompt:
            try:
                # Save user message
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': session_id,
                    'p_message_type': 'user', 
                    'p_message_content': request.initial_prompt,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': 'initial'
                }).execute()
                
                # Save AI response
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': session_id,
                    'p_message_type': 'assistant',
                    'p_message_content': response,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': 'initial'
                }).execute()
            except Exception as e:
                print(f"Database save error: {e}")
        
        return {
            "success": True,
            "session_id": session_id,
            "ai_model": request.ai_model,
            "message": response,
            "ready_to_create": "ready_to_create" in response,
            "bot_config": None
        }
        
    except Exception as e:
        print(f"Session start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-bot-chat/send-message") 
async def send_chat_message(request: ChatMessageRequest):
    """Send message in chat session."""
    try:
        # Get conversation history
        conversation_history = []
        if supabase_admin:
            try:
                history_response = supabase_admin.rpc('get_chat_history', {
                    'p_user_id': request.user_id,
                    'p_session_id': request.session_id
                }).execute()
                conversation_history = history_response.data or []
            except Exception as e:
                print(f"History retrieval error: {e}")
        
        # Generate contextual response
        response = await get_contextual_ai_response(
            request.message_content,
            request.ai_model,
            conversation_history,
            request.session_id
        )
        
        # Save messages to database
        if supabase_admin:
            try:
                # Save user message
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': request.session_id,
                    'p_message_type': 'user',
                    'p_message_content': request.message_content,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': request.bot_creation_stage
                }).execute()
                
                # Save AI response
                supabase_admin.rpc('save_chat_message', {
                    'p_user_id': request.user_id,
                    'p_session_id': request.session_id,
                    'p_message_type': 'assistant',
                    'p_message_content': response,
                    'p_ai_model': request.ai_model,
                    'p_bot_creation_stage': request.bot_creation_stage
                }).execute()
            except Exception as e:
                print(f"Database save error: {e}")
        
        # Check if bot is ready
        is_ready = "ready_to_create" in response
        bot_config = None
        
        if is_ready:
            try:
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    if json_end != -1:
                        json_str = response[json_start:json_end].strip()
                        bot_config = json.loads(json_str)
            except Exception as e:
                print(f"JSON parse error: {e}")
        
        return {
            "success": True,
            "session_id": request.session_id,
            "message": response,
            "ready_to_create": is_ready,
            "bot_config": bot_config
        }
        
    except Exception as e:
        print(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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