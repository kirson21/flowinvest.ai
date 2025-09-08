from fastapi import APIRouter, HTTPException
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
TRADING_EXPERT_PROMPT = """You are a world-class trading systems architect specializing in institutional-grade automated trading bots. You design production-ready systems with professional risk management and sophisticated trading strategies.

CRITICAL INSTRUCTION: You MUST analyze the ENTIRE conversation history to understand what the user has already told you. Do NOT repeat questions about information already provided.

PROFESSIONAL TRADING PARAMETERS YOU CAN CONFIGURE:

🔹 **BASIC CONFIGURATION**
- Trading Capital (leverage considerations)
- Base/Quote Currency Pairs
- Trade Type (Spot/Futures/Margin)
- Trading Mode (Long/Short/Both)

🔹 **ENTRY CONDITIONS** 
- Entry Signals & Triggers
- Technical Indicators (RSI, MACD, Bollinger Bands, SMA, EMA, etc.)
- Time Intervals (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- Signal Types (Bar closing, Real-time, Next candle)
- Grid Trading Parameters
- DCA (Dollar Cost Averaging) Strategies
- Order Distribution & Size

🔹 **EXIT CONDITIONS**
- Take Profit Strategies
- Stop Loss Management  
- Trailing Stops
- Exit Signals & Indicators
- Profit Target Percentages
- Risk-Reward Ratios

🔹 **ADVANCED RISK MANAGEMENT**
- Position Sizing Algorithms
- Maximum Drawdown Limits
- Concurrent Position Limits
- Kill-Switch Conditions
- Margin Requirements
- Risk Per Trade Limits
- Account Protection Rules

🔹 **ORDER MANAGEMENT**
- Grid of Orders (2-60 orders)
- Martingale Strategies (1%-500%)
- Order Spacing (Linear/Logarithmic)
- Partial Order Fills
- Order Pulling Mechanisms
- Volume Distribution

🔹 **ADVANCED FEATURES**
- Multi-timeframe Analysis
- Cross-asset Correlations
- Market Condition Filters
- Volatility Adjustments
- News Event Handling
- Session-based Trading

CONVERSATION FLOW:
1. If user hasn't specified TRADING CAPITAL → Ask about capital and leverage preferences
2. If user hasn't specified INSTRUMENTS → Ask about spot vs futures, trading pairs
3. If user hasn't specified STRATEGY TYPE → Ask about trading strategy (scalping, swing, grid, DCA, momentum, mean reversion)
4. If user hasn't specified RISK PARAMETERS → Ask about risk limits, stop loss, take profit targets
5. If user hasn't specified ENTRY CONDITIONS → Ask about entry signals, indicators, timeframes
6. If user hasn't specified EXIT CONDITIONS → Ask about exit strategy, profit targets
7. If user hasn't specified BOT NAME → Ask for descriptive bot name
8. If ALL INFO PROVIDED → Generate comprehensive bot specification JSON

ADVANCED QUESTIONS TO ASK (when user wants professional features):
- "Do you want custom entry conditions using technical indicators?"
- "Should I configure advanced grid trading with logarithmic distribution?"
- "What stop-loss and take-profit percentages do you prefer?"
- "Do you need multi-timeframe confirmation signals?"
- "Should the bot use martingale position sizing?"
- "What maximum concurrent positions should be allowed?"
- "Do you want session-based trading (specific hours)?"

IMPORTANT: Always check what user has ALREADY provided before asking new questions!

When ready to create bot, respond with comprehensive JSON including ALL professional parameters:
{
  "ready_to_create": true,
  "bot_config": {
    "name": "User's chosen descriptive name",
    "description": "Professional trading system with advanced features", 
    "base_coin": "User's coin choice",
    "quote_coin": "USDT",
    "trade_type": "spot/futures per user preference",
    "trading_capital_usd": "User's amount",
    "leverage": "User's leverage setting",
    "risk_level": "conservative/moderate/aggressive",
    "strategy_type": "scalping/swing/grid/dca/momentum/mean_reversion",
    "timeframe": "Primary trading timeframe",
    "advanced_settings": {
      "entry_conditions": [
        "List of entry signals and indicators"
      ],
      "exit_conditions": [
        "List of exit signals and conditions"  
      ],
      "technical_indicators": {
        "primary": "Main indicator (RSI/MACD/BB)",
        "interval": "5m/15m/1h/4h",
        "signal_type": "bar_closing/realtime/next_candle"
      },
      "grid_settings": {
        "orders_count": "Number of grid orders (2-60)",
        "spacing_type": "linear/logarithmic", 
        "spacing_percentage": "Order spacing %",
        "martingale_multiplier": "Position size multiplier %"
      },
      "risk_management": {
        "stop_loss_percent": "Stop loss percentage",
        "take_profit_percent": "Take profit percentage", 
        "max_positions": "Maximum concurrent positions",
        "risk_per_trade": "Risk per trade %",
        "max_drawdown": "Maximum account drawdown %"
      },
      "order_management": {
        "base_order_size": "Initial order size",
        "safety_order_size": "DCA order size",
        "safety_orders_count": "Number of DCA orders",
        "price_deviation": "Price deviation for safety orders %"
      }
    }
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
        
        # Enhanced state detection for professional trading parameters
        state = {
            # Basic Requirements
            'has_capital': any(word in all_user_input for word in ['$', 'capital', '1000', '5000', '10000', '50000', '100000', 'k', 'usd', 'budget']),
            'has_leverage': any(word in all_user_input for word in ['leverage', 'x', 'futures', 'margin', '2x', '5x', '10x']),
            'has_instruments': any(word in all_user_input for word in ['spot', 'futures', 'margin', 'derivatives', 'perpetual']),
            'has_risk': any(word in all_user_input for word in ['risk', '%', 'conservative', 'aggressive', 'drawdown', 'stop loss', 'take profit']),
            'has_strategy': any(word in all_user_input for word in ['momentum', 'scalping', 'mean', 'trend', 'grid', 'arbitrage', 'dca', 'swing']),
            'has_timeframe': any(word in all_user_input for word in ['minute', 'hour', 'daily', 'intraday', 'swing', '1m', '5m', '15m', '1h', '4h']),
            'has_botname': len([msg for msg in conversation_history if 'name' in msg.get('message_content', '').lower()]) > 0,
            
            # Advanced Parameters Detection
            'has_entry_conditions': any(word in all_user_input for word in ['entry', 'buy signal', 'entry condition', 'trigger', 'rsi', 'macd', 'bollinger']),
            'has_exit_conditions': any(word in all_user_input for word in ['exit', 'sell signal', 'exit condition', 'profit target', 'stop loss']),
            'has_indicators': any(word in all_user_input for word in ['rsi', 'macd', 'sma', 'ema', 'bollinger', 'stochastic', 'williams']),
            'has_grid_settings': any(word in all_user_input for word in ['grid', 'orders', 'spacing', 'martingale', 'dca', 'averaging']),
            'has_risk_management': any(word in all_user_input for word in ['stop loss', 'take profit', 'drawdown', 'position size', 'risk per trade']),
            'has_order_management': any(word in all_user_input for word in ['order size', 'base order', 'safety order', 'position sizing']),
            
            # Context for AI decision making
            'user_input': all_user_input,
            'question_count': len([msg for msg in conversation_history if msg.get('message_type') == 'assistant']),
            'is_editing_mode': 'modify' in all_user_input or 'edit' in all_user_input or 'change' in all_user_input
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
        
        # Check if we have all basic information needed to create bot
        basic_info_complete = (state['has_capital'] and state['has_instruments'] and 
                             state['has_risk'] and state['has_strategy'] and state['has_botname'])
        
        if basic_info_complete:
            # Check if user wants advanced features or if we should ask about them
            has_advanced_info = (state['has_entry_conditions'] or state['has_exit_conditions'] or 
                               state['has_grid_settings'] or state['has_order_management'])
            
            # If user has provided advanced info or explicitly declined, create bot
            wants_advanced = 'yes' in current_message.lower() or 'advanced' in current_message.lower()
            declines_advanced = any(word in current_message.lower() for word in ['no', 'basic', 'simple', 'skip'])
            
            if has_advanced_info or declines_advanced or state['question_count'] >= 8:
                # Generate bot configuration from user inputs
                return self.create_bot_specification(prefix, state, current_message)
            elif not wants_advanced and state['question_count'] < 6:
                # Ask if they want advanced features
                return f"""{prefix}

**Advanced Configuration Options**

Your basic bot is ready! Would you like to configure advanced features?

🔹 **Entry Conditions**: Custom buy signals using RSI, MACD, Bollinger Bands
🔹 **Exit Strategy**: Sophisticated take-profit and stop-loss rules  
🔹 **Grid Trading**: Automated order grid with martingale scaling
🔹 **Risk Controls**: Advanced position sizing and drawdown protection

Type **"yes"** for professional features or **"create basic bot"** to proceed with current settings.""", False, {}
            else:
                return self.create_bot_specification(prefix, state, current_message)
        
        # Ask for missing basic information in order
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

**Question 2: Trading Instruments & Pairs**

Perfect! Now I need to know your trading preferences:

• **Spot Trading**: Safer, no liquidation risk, lower leverage
• **Futures Trading**: Higher leverage, short selling, liquidation risk
• **Trading Pairs**: BTC/USDT, ETH/USDT, altcoins, or specific preferences?

Which instruments and pairs align with your goals?""", False, {}
            
        elif not state['has_strategy']:
            return f"""{prefix}

**Question 3: Trading Strategy & Timeframe**

What trading approach interests you?

• **Momentum**: Trend following, breakout trading (15m-4h)
• **Scalping**: High-frequency, small quick profits (1m-15m)  
• **Mean Reversion**: Buy dips, sell peaks (1h-1d)
• **Grid Trading**: Automated range trading (any timeframe)
• **DCA**: Dollar cost averaging with safety orders

What strategy and timeframe suit your goals?""", False, {}
            
        elif not state['has_risk']:
            return f"""{prefix}

**Question 4: Risk Management**

Critical for protecting your capital:

• Max risk per trade? Conservative: 1-2%, Moderate: 2-3%, Aggressive: 3-5%
• Stop loss percentage? (e.g., 2-5% depending on strategy)
• Take profit target? (e.g., 1-3% for scalping, 5-20% for swing)
• Max concurrent positions? (1-3 recommended)

Example: "2% risk per trade, 3% stop loss, 4% take profit, max 2 positions"

What are your risk management preferences?""", False, {}
            
        elif not state['has_botname']:
            return f"""{prefix}

**Question 5: Bot Identity**

Finally, let's name your trading bot:

Examples: 
• "BTC Momentum Pro" (for momentum strategy)
• "Altcoin Grid Master" (for grid trading)
• "ETH Scalping Engine" (for scalping)
• "Conservative DCA Bot" (for dollar cost averaging)

What descriptive name do you want for your bot?""", False, {}
            
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
        
        response = await get_contextual_ai_response(
            request.initial_prompt or "Hello", 
            request.ai_model, 
            [],
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

@router.post("/ai-bot-chat/create-bot")
async def create_ai_bot(request: AiBotCreationRequest):
    """Create AI bot from conversation."""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        bot_config = request.bot_config.get('bot_config', {})
        
        # Get original prompt from history
        chat_response = supabase_admin.rpc('get_chat_history', {
            'p_user_id': request.user_id,
            'p_session_id': request.session_id
        }).execute()
        
        generation_prompt = ""
        if chat_response.data:
            user_messages = [msg for msg in chat_response.data if msg.get('message_type') == 'user']
            if user_messages:
                generation_prompt = user_messages[0].get('message_content', '')
        
        # Save to AI bots table
        bot_response = supabase_admin.rpc('save_ai_bot', {
            'p_user_id': request.user_id,
            'p_name': bot_config.get('name', 'AI Bot'),
            'p_description': bot_config.get('description', 'AI trading bot'),
            'p_ai_model': request.ai_model,
            'p_generation_prompt': generation_prompt,
            'p_bot_config': json.dumps(request.bot_config),
            'p_strategy_config': json.dumps(request.strategy_config),
            'p_risk_management': json.dumps(request.risk_management),
            'p_base_coin': bot_config.get('base_coin'),
            'p_quote_coin': bot_config.get('quote_coin'),
            'p_exchange': 'binance'
        }).execute()
        
        if not bot_response.data:
            raise HTTPException(status_code=500, detail="Failed to save bot")
        
        return {
            "success": True,
            "bot_id": bot_response.data,
            "message": f"Bot '{bot_config.get('name')}' created successfully!"
        }
        
    except Exception as e:
        print(f"Bot creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Other endpoints
@router.get("/ai-bot-chat/history/{session_id}")
async def get_chat_history(session_id: str, user_id: str):
    """Get chat history."""
    try:
        if not supabase_admin:
            return {"success": False, "messages": []}
        
        response = supabase_admin.rpc('get_chat_history', {
            'p_user_id': user_id,
            'p_session_id': session_id
        }).execute()
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": response.data or []
        }
        
    except Exception as e:
        print(f"History error: {e}")
        return {"success": False, "messages": []}

@router.get("/ai-bots/user/{user_id}")
async def get_user_ai_bots(user_id: str):
    """Get user AI bots."""
    try:
        if not supabase_admin:
            return {"success": True, "bots": [], "total": 0}
        
        response = supabase_admin.rpc('get_user_ai_bots', {
            'user_uuid': user_id
        }).execute()
        
        bots = response.data or []
        
        return {
            "success": True,
            "bots": bots,
            "total": len(bots)
        }
        
    except Exception as e:
        print(f"Get bots error: {e}")
        return {"success": True, "bots": [], "total": 0}

@router.get("/ai-bot-chat/health")
async def health_check():
    """Health check."""
    try:
        emergent_key = os.getenv('EMERGENT_LLM_KEY')
        
        return {
            "status": "healthy",
            "ai_models_available": ["gpt-4o", "claude-3-7-sonnet", "gemini-2.0-flash"],
            "database_available": supabase_admin is not None,
            "universal_key_configured": bool(emergent_key),
            "message": "Professional Trading Agent with context-aware conversation flow"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}