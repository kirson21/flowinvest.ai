from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class TradingMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"

class BotStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"

class AIModel(str, Enum):
    GPT5 = "gpt-5"
    GROK4 = "grok-4"

class StrategyType(str, Enum):
    TREND_FOLLOWING = "Trend Following"
    BREAKOUT = "Breakout"
    SCALPING = "Scalping"
    MEAN_REVERSION = "Mean Reversion"
    GRID_TRADING = "Grid Trading"
    CUSTOM = "Custom"

class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"

class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
    LONG = "long"
    SHORT = "short"

class TradeStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

# Strategy Configuration Models
class TechnicalIndicator(BaseModel):
    name: str
    parameters: Dict[str, Any] = {}
    condition: str

class EntryConditions(BaseModel):
    indicators: List[TechnicalIndicator]
    additional_rules: Optional[List[str]] = []

class ExitConditions(BaseModel):
    take_profit: Dict[str, Any]
    stop_loss: Dict[str, Any]

class Strategy(BaseModel):
    type: StrategyType
    timeframes: List[str]
    entry_conditions: EntryConditions
    exit_conditions: ExitConditions

class RiskManagement(BaseModel):
    leverage: int = Field(ge=1, le=20)
    max_concurrent_trades: int = Field(ge=1, le=10)
    stop_loss_percent: float = Field(gt=0, le=10)
    take_profit_percent: float = Field(gt=0, le=50)
    position_size_percent: float = Field(gt=0, le=5)
    trailing_stop_percent: Optional[float] = Field(None, gt=0, le=10)

class ExecutionRules(BaseModel):
    order_type: OrderType
    time_in_force: str = "GTC"
    slippage: float = Field(ge=0, le=1)

class TradingFilters(BaseModel):
    min_volume: Optional[float] = None
    max_spread: Optional[float] = None
    allowed_assets: Optional[List[str]] = None

class BotConfig(BaseModel):
    bot_name: str = Field(min_length=1, max_length=255)
    description: str = ""
    strategy: Strategy
    risk_management: RiskManagement
    execution_rules: ExecutionRules
    filters: Optional[TradingFilters] = None
    generated_at: Optional[str] = None
    ai_model: Optional[str] = None
    risk_level: Optional[str] = None

    @validator('bot_name')
    def validate_bot_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Bot name cannot be empty')
        return v.strip()

# API Request Models
class CreateBotRequest(BaseModel):
    ai_model: AIModel
    strategy_template_id: Optional[str] = None
    strategy_description: Optional[str] = None
    customizations: Optional[Dict[str, Any]] = {}
    risk_preferences: Dict[str, Any] = {}

    @validator('risk_preferences')
    def validate_risk_preferences(cls, v):
        # Set defaults if not provided
        if 'risk_level' not in v:
            v['risk_level'] = 'medium'
        if 'max_leverage' not in v:
            v['max_leverage'] = 10
        if 'portfolio_percent_per_trade' not in v:
            v['portfolio_percent_per_trade'] = 2
        return v

class ExchangeKeysRequest(BaseModel):
    exchange: str = "bybit"
    api_key: str = Field(min_length=1)
    api_secret: str = Field(min_length=1)
    passphrase: Optional[str] = None
    exchange_account_type: str = Field(default="testnet", pattern="^(testnet|mainnet)$")

    @validator('api_key', 'api_secret')
    def validate_credentials(cls, v):
        if not v or v.strip() == "":
            raise ValueError('API credentials cannot be empty')
        return v.strip()

# Database Models
class TradingBot(BaseModel):
    id: str
    user_id: str
    bot_name: str
    description: str
    ai_model: str
    bot_config: Dict[str, Any]
    strategy_type: str
    is_predefined_strategy: bool = False
    exchange: str = "bybit"
    trading_mode: TradingMode = TradingMode.PAPER
    status: BotStatus = BotStatus.INACTIVE
    max_leverage: int = 10
    max_concurrent_trades: int = 5
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None

class BotTrade(BaseModel):
    id: str
    bot_id: str
    user_id: str
    exchange_order_id: Optional[str] = None
    exchange_trade_id: Optional[str] = None
    symbol: str
    side: TradeSide
    order_type: str
    quantity: float
    price: Optional[float] = None
    filled_quantity: float = 0
    average_fill_price: Optional[float] = None
    leverage: int = 1
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    status: TradeStatus = TradeStatus.PENDING
    realized_pnl: float = 0
    unrealized_pnl: float = 0
    is_paper_trade: bool = True
    created_at: datetime
    executed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

class BotLog(BaseModel):
    id: str
    bot_id: str
    user_id: str
    log_type: str
    log_level: str = "info"
    message: str
    details: Optional[Dict[str, Any]] = None
    exchange_response: Optional[Dict[str, Any]] = None
    trade_id: Optional[str] = None
    created_at: datetime

class BotPerformance(BaseModel):
    id: str
    bot_id: str
    user_id: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0
    total_pnl: float = 0
    total_volume: float = 0
    max_drawdown: float = 0
    sharpe_ratio: Optional[float] = None
    max_leverage_used: int = 1
    period_start: datetime
    period_end: datetime
    period_type: str = "daily"
    created_at: datetime

# Response Models
class BotResponse(BaseModel):
    id: str
    user_id: str
    bot_name: str
    description: str
    ai_model: str
    strategy_type: str
    exchange: str
    trading_mode: str
    status: str
    max_leverage: int
    max_concurrent_trades: int
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None

class TradeResponse(BaseModel):
    id: str
    bot_id: str
    symbol: str
    side: str
    quantity: float
    price: Optional[float]
    status: str
    realized_pnl: float
    is_paper_trade: bool
    created_at: datetime
    executed_at: Optional[datetime]

class PerformanceResponse(BaseModel):
    bot_id: str
    total_trades: int
    winning_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    period_start: datetime
    period_end: datetime

class MarketDataResponse(BaseModel):
    symbol: str
    price: float
    volume: float
    change_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime

# WebSocket Message Models
class WebSocketMessage(BaseModel):
    type: str
    bot_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TradingSignal(BaseModel):
    symbol: str
    action: str  # "long", "short"
    strength: float = Field(ge=0, le=1)
    price: float
    reason: str
    timestamp: datetime
    indicators: Optional[Dict[str, Any]] = None

class BotStatusUpdate(BaseModel):
    bot_id: str
    status: BotStatus
    message: str
    active_positions: int = 0
    total_pnl: float = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)