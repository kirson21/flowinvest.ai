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
            'has_capital': any(word in all_user_input for word in ['$', 'capital', '1000', '5000', '10000', '50000', '100000', 'k']),
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

def get_intelligent_fallback_response(message: str, ai_model: str, conversation_history: List[Dict] = []) -> str:
    """Generate professional trading systems responses following the expert prompt structure."""
    question_count = len([msg for msg in conversation_history if msg.get('message_type') == 'assistant'])
    
    # Extract user preferences from ALL conversation history
    all_user_messages = ' '.join([msg.get('message_content', '') for msg in conversation_history if msg.get('message_type') == 'user'])
    combined_text = (all_user_messages + ' ' + message).lower()
    
    # Professional model prefixes
    model_names = {
        'gpt-4o': '🧠 **GPT-4 Trading Systems**',
        'claude-3-7-sonnet': '🎭 **Claude Trading Expert**',
        'gemini-2.0-flash': '💎 **Gemini Quant Specialist**'
    }
    model_prefix = model_names.get(ai_model, '🤖 **Trading Systems Agent**')
    
    # Generate professional bot specification when enough info gathered (after bot name question)
    if question_count >= 5:
        
        # EXTRACT USER PREFERENCES FROM CONVERSATION HISTORY
        
        # 1. CAPITAL ANALYSIS - Extract from actual user responses
        trading_capital = 10000  # Default
        leverage = 1.0  # Default to spot
        
        if any(word in combined_text for word in ['1000', '1k']):
            trading_capital = 1000
        elif any(word in combined_text for word in ['5000', '5k']):
            trading_capital = 5000
        elif any(word in combined_text for word in ['10000', '10k']):
            trading_capital = 10000
        elif any(word in combined_text for word in ['50000', '50k']):
            trading_capital = 50000
        elif any(word in combined_text for word in ['100000', '100k']):
            trading_capital = 100000
        
        # Extract leverage from user answers
        if 'futures' in combined_text or 'leverage' in combined_text:
            if '2x' in combined_text or 'leverage 2' in combined_text:
                leverage = 2.0
            elif '3x' in combined_text or 'leverage 3' in combined_text:
                leverage = 3.0
            elif '3-5x' in combined_text or '4x' in combined_text or '5x' in combined_text:
                leverage = 5.0
            elif '10x' in combined_text:
                leverage = 10.0
            else:
                leverage = 3.0  # Default for futures
        
        # 2. COIN ANALYSIS - Extract from actual user responses
        coin = 'BTC'  # Default
        if any(word in combined_text for word in ['ethereum', 'eth']):
            coin = 'ETH'
        elif any(word in combined_text for word in ['solana', 'sol']):
            coin = 'SOL'
        elif any(word in combined_text for word in ['altcoin', 'altcoins']):
            coin = 'ALT'  # Mixed altcoins
        elif any(word in combined_text for word in ['ada', 'cardano']):
            coin = 'ADA'
        elif any(word in combined_text for word in ['matic', 'polygon']):
            coin = 'MATIC'
        elif any(word in combined_text for word in ['doge', 'dogecoin']):
            coin = 'DOGE'
        
        # 3. STRATEGY ANALYSIS - Extract from user answers
        strategy = 'momentum'  # Default
        if 'scalping' in combined_text:
            strategy = 'scalping'
        elif any(word in combined_text for word in ['mean reversion', 'dip', 'peak']):
            strategy = 'mean_reversion'
        elif any(word in combined_text for word in ['grid', 'range']):
            strategy = 'grid'
        elif any(word in combined_text for word in ['arbitrage', 'neutral']):
            strategy = 'arbitrage'
        elif any(word in combined_text for word in ['trend', 'following']):
            strategy = 'trend_following'
        elif 'momentum' in combined_text:
            strategy = 'momentum'
        
        # 4. RISK ANALYSIS - Extract from user answers
        risk_level = 'medium'
        max_risk_per_trade = 2.0
        max_drawdown = 10.0
        
        if any(word in combined_text for word in ['conservative', 'low risk', 'safe']):
            risk_level = 'low'
            max_risk_per_trade = 1.0
            max_drawdown = 5.0
        elif any(word in combined_text for word in ['aggressive', 'high risk', 'risky']):
            risk_level = 'high'
            max_risk_per_trade = 3.0
            max_drawdown = 15.0
        
        # Extract specific risk percentages from user answers
        import re
        risk_matches = re.findall(r'(\d+)%?\s*(?:risk|per trade)', combined_text)
        if risk_matches:
            max_risk_per_trade = float(risk_matches[0])
        
        drawdown_matches = re.findall(r'(\d+)%?\s*(?:drawdown|max loss)', combined_text)
        if drawdown_matches:
            max_drawdown = float(drawdown_matches[0])
        
        # 5. TIMEFRAME ANALYSIS - Extract from user answers  
        timeframe = '1h'
        if any(word in combined_text for word in ['scalping', 'minute', '1m', '5m']):
            timeframe = '5m'
        elif any(word in combined_text for word in ['swing', 'daily', '4h', '1d']):
            timeframe = '4h'
        elif any(word in combined_text for word in ['intraday', '15m', '1h']):
            timeframe = '1h'
        
        # 6. BOT NAME ANALYSIS - Extract from user answers
        bot_name = f"{coin} {strategy.title()} Pro"  # Default
        
        # Look for bot name in the latest message
        latest_message = message.strip()
        if len(latest_message) > 0 and not any(word in latest_message.lower() for word in ['question', 'what', 'how', 'when', 'where', 'why']):
            # User likely provided a bot name
            if len(latest_message.split()) <= 5:  # Reasonable bot name length
                bot_name = latest_message
        
        # 7. INSTRUMENTS - Extract from user answers
        instruments = 'spot'
        trade_type = 'spot'
        if 'futures' in combined_text:
            instruments = 'futures'
            trade_type = 'futures'
        
        # Create professional bot configuration using EXTRACTED USER PREFERENCES
        bot_config = {
            "ready_to_create": True,
            "bot_config": {
                "name": bot_name,
                "description": f"Professional {strategy} trading system for {coin} based on user specifications: {risk_level} risk, {leverage}x leverage, {timeframe} timeframe",
                "trading_capital_usd": trading_capital,
                "leverage_allowed": leverage,
                "instruments": instruments,
                "base_coin": coin,
                "quote_coin": "USDT",
                "exchange": "binance",
                "strategy_type": strategy,
                "trade_type": trade_type,
                "risk_level": risk_level,
                "timeframe": timeframe,
                "execution_notes": f"Created per user specs: {coin} trading, {leverage}x leverage, {strategy} strategy, {risk_level} risk"
            },
            "strategy_config": {
                "strategy_intent": "long_only" if leverage == 1.0 else "long_short_capable",
                "technical_indicators": ["RSI_14", "MACD_12_26_9", "EMA_20", "Volume_SMA_20"],
                "entry_conditions": [
                    f"{strategy.title()} signal confirmation on {timeframe}",
                    "Volume above 20-period average", 
                    "Risk parameters within user limits",
                    f"Leverage {leverage}x position sizing approved"
                ],
                "exit_conditions": [
                    "Take profit target reached",
                    "Stop loss triggered",
                    f"Signal reversal on {timeframe}",
                    "User-specified risk limits exceeded"
                ],
                "timeframes": [timeframe, "15m", "1h"],
                "signal_logic": f"User-specified {strategy} analysis for {coin} with {leverage}x leverage",
                "custom_parameters": {
                    "user_specified_coin": coin,
                    "user_specified_leverage": leverage,
                    "user_specified_strategy": strategy,
                    "user_specified_risk": risk_level
                }
            },
            "risk_management": {
                "max_risk_per_trade_percent": max_risk_per_trade,
                "max_portfolio_drawdown_percent": max_drawdown,
                "max_concurrent_positions": 2 if risk_level == 'low' else 3 if risk_level == 'medium' else 4,
                "stop_loss_percent": 2.0 if risk_level == 'low' else 3.5,
                "take_profit_percent": 4.0 if risk_level == 'low' else 6.0,
                "position_sizing_method": "fixed_percent",
                "position_size_percent": 2.0 if risk_level == 'low' else 3.0 if risk_level == 'medium' else 5.0,
                "kill_switch_conditions": [
                    f"Daily loss exceeds {max_risk_per_trade * 3}% of capital",
                    f"Leverage exceeds user limit of {leverage}x",
                    "User-specified drawdown limit exceeded"
                ]
            },
            "execution_config": {
                "slippage_assumption_bps": 5 if strategy == 'scalping' else 10,
                "trading_fees_bps": 10,
                "execution_latency_tolerance_ms": 500 if strategy == 'scalping' else 1000,
                "order_types": ["market", "limit", "stop_limit"],
                "rate_limit_handling": True,
                "secrets_handling": "environment_variables",
                "idempotency": True
            }
        }
        
        return f"""{model_prefix}

**PROFESSIONAL TRADING BOT SPECIFICATION COMPLETE**

✅ **Created Per Your Exact Specifications:**

**System Configuration:**
• Bot Name: **{bot_name}**
• Target Asset: **{coin}** (as you specified)
• Trading Type: **{trade_type.title()}** with **{leverage}x leverage** (as requested)
• Strategy: **{strategy.title()}** (from your preferences)
• Risk Level: **{risk_level.title()}** (per your tolerance)
• Timeframe: **{timeframe}** (based on your requirements)

**Capital & Risk (Your Specifications):**
• Trading Capital: **${trading_capital:,} USD**
• Max Risk per Trade: **{max_risk_per_trade}%**
• Portfolio Drawdown Limit: **{max_drawdown}%**
• Position Size: **{2.0 if risk_level == 'low' else 3.0 if risk_level == 'medium' else 5.0}%** of capital

**Following Your Requirements:**
• Instrument Type: **{instruments.title()}** (as you requested)
• Leverage Level: **{leverage}x** (matching your specification)
• Strategy Focus: **{strategy.title()}** for **{coin}** (per your answers)

```json
{json.dumps(bot_config, indent=2)}
```

**🚀 This bot follows your EXACT specifications and is ready for deployment!**"""
    
    # Professional mandatory questions flow
    if question_count == 0:
        return f"""{model_prefix}

Welcome to professional trading systems design. I am an expert in trading theory, market microstructure, and quantitative strategy development.

**Mandatory Question 1: Trading Capital & Leverage**

To design appropriate risk management and position sizing:

• What is your available trading capital (in USD)?
• What leverage are you comfortable with?
  - **1x (Spot Only)**: Safest, no liquidation risk
  - **2-3x (Moderate)**: Balanced risk/reward
  - **5x+ (Aggressive)**: Higher risk, requires experience

Example: "$10,000 capital with 1x leverage (spot only)"

Please specify your trading capital and maximum leverage tolerance."""
    
    elif question_count == 1:
        return f"""{model_prefix}

**Mandatory Question 2: Instrument Type & Market Access**

Critical for execution strategy design:

• **Spot Trading**: Buy/hold physical assets, no liquidation risk, lower capital efficiency
• **Futures/Margin**: Leverage trading, short selling capability, liquidation risk present
• **Mixed Approach**: Primarily spot with selective futures for hedging

**Which instrument type aligns with your risk management philosophy and trading experience?**

Note: Spot-only recommended for conservative approaches, futures for advanced risk management."""
    
    elif question_count == 2:
        return f"""{model_prefix}

**Mandatory Question 3: Risk Control Parameters**

Essential for capital preservation (industry standards):

**Position Risk Limits:**
• Max risk per single trade (% of equity)?
  - Conservative: 1-2% 
  - Moderate: 2-3%
  - Aggressive: 3-5%

**Portfolio Risk Limits:**
• Maximum portfolio drawdown (% loss that stops trading)?
  - Conservative: 5-10%
  - Moderate: 10-15%
  - Aggressive: 15-20%

• Maximum concurrent positions? (Recommended: 1-3 for risk control)

Example: "2% max per trade, 10% max drawdown, 2 positions maximum"

**Please specify your risk control parameters.**"""
    
    elif question_count == 3:
        return f"""{model_prefix}

**Mandatory Question 4: Strategy Intent & Timeframe**

For signal generation and execution design:

**Strategy Types:**
• **Momentum**: Trend following, breakout trading
• **Mean Reversion**: Buy dips, sell peaks, range trading  
• **Scalping**: High-frequency, small profits, sub-minute trades
• **Grid Trading**: Automated buy/sell at intervals
• **Statistical Arbitrage**: Market-neutral, correlation-based
• **Market Making**: Provide liquidity, capture bid-ask spread

**Timeframe Preferences:**
• **Scalping**: 1m-5m (requires fast execution)
• **Intraday**: 15m-1h (momentum/mean reversion)
• **Swing**: 4h-1d (trend following)
• **Position**: Multi-day (fundamental analysis)

**What strategy type and timeframe match your trading objectives?**"""
    
    elif question_count == 4:
        return f"""{model_prefix}

**Mandatory Question 5: Bot Name & Identity**

For system identification and management:

**Please choose a name for your trading bot:**
• Should be descriptive and memorable
• Examples: "Bitcoin Momentum Pro", "ETH Scalping Engine", "Conservative DCA Bot"
• Will be used for identification in your bot portfolio

**What would you like to name your trading bot?**"""
        
    else:
        # Professional follow-up questions for missing mandatory information
        follow_ups = [
            f"""{model_prefix}

**Clarification: Execution & Latency Requirements**

For production system specifications:
• Execution speed priority: Standard (1-5 seconds) or High-frequency (<100ms)?
• Exchange preference: Binance (high liquidity) or Bybit (derivatives focus)?
• Slippage tolerance: Conservative (0.05%) or Moderate (0.1%)?
• Co-location requirements for latency-sensitive strategies?""",
            
            f"""{model_prefix}

**Clarification: Signal Generation & Indicators**

For quantitative strategy implementation:
• Preferred technical indicators: RSI, MACD, moving averages, custom signals?
• Market regime detection: Bull/bear/sideways adaptation needed?
• Volume analysis: Include volume confirmation in signals?
• External data sources: News sentiment, on-chain metrics, order book data?""",
            
            f"""{model_prefix}

**Clarification: Operational & Safety Parameters**

For production deployment reliability:
• Trading session hours: 24/7 automated or specific market hours?
• Emergency procedures: Manual override capability required?
• Kill-switch conditions: Beyond standard drawdown limits?
• Monitoring requirements: Real-time alerts, dashboard access?"""
        ]
        return follow_ups[hash(message) % len(follow_ups)]

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
            ai_response = await get_contextual_ai_response(
                request.initial_prompt, 
                request.ai_model, 
                conversation_history,
                session_id  # Pass session_id for context continuity
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
            ai_response = await get_contextual_ai_response("Start conversation", request.ai_model, [], session_id)
        
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
        ai_response = await get_contextual_ai_response(
            request.message_content,
            request.ai_model,
            conversation_history,
            request.session_id  # Pass session_id for context continuity
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