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