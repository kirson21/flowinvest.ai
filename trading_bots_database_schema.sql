-- AI Trading Bot Constructor - Database Schema
-- Run this in Supabase SQL Editor

-- 1. Trading Bot Configurations Table
CREATE TABLE IF NOT EXISTS trading_bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    
    -- Bot Metadata
    bot_name VARCHAR(255) NOT NULL,
    description TEXT,
    ai_model VARCHAR(50) NOT NULL CHECK (ai_model IN ('grok-4', 'gpt-5')),
    
    -- Bot Configuration (JSON)
    bot_config JSONB NOT NULL,
    
    -- Strategy Information
    strategy_type VARCHAR(100) NOT NULL, -- 'Trend Following', 'Breakout', 'Scalping', 'Custom'
    is_predefined_strategy BOOLEAN DEFAULT false,
    
    -- Exchange Settings
    exchange VARCHAR(50) NOT NULL DEFAULT 'bybit',
    trading_mode VARCHAR(20) NOT NULL DEFAULT 'paper' CHECK (trading_mode IN ('paper', 'live')),
    
    -- Bot Status
    status VARCHAR(20) NOT NULL DEFAULT 'inactive' CHECK (status IN ('inactive', 'active', 'paused', 'error')),
    
    -- Risk Settings
    max_leverage INTEGER DEFAULT 10,
    max_concurrent_trades INTEGER DEFAULT 5,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE
);

-- 2. User Exchange API Keys (Encrypted)
CREATE TABLE IF NOT EXISTS user_exchange_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    
    -- Exchange Information
    exchange VARCHAR(50) NOT NULL,
    exchange_account_type VARCHAR(20) DEFAULT 'testnet' CHECK (exchange_account_type IN ('testnet', 'mainnet')),
    
    -- Encrypted API Credentials
    api_key_encrypted TEXT NOT NULL,
    api_secret_encrypted TEXT NOT NULL,
    passphrase_encrypted TEXT, -- For exchanges that require it
    
    -- Encryption Metadata
    encryption_key_id VARCHAR(100) NOT NULL, -- Reference to encryption key
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one active key per exchange per user
    UNIQUE(user_id, exchange, exchange_account_type)
);

-- 3. Trading Bot Executions/Trades
CREATE TABLE IF NOT EXISTS bot_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL REFERENCES trading_bots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    
    -- Exchange Trade Info
    exchange_order_id VARCHAR(255),
    exchange_trade_id VARCHAR(255),
    
    -- Trade Details
    symbol VARCHAR(50) NOT NULL, -- e.g., 'BTCUSDT'
    side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell', 'long', 'short')),
    order_type VARCHAR(20) NOT NULL, -- 'market', 'limit', 'stop'
    
    -- Quantities and Prices
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    filled_quantity DECIMAL(20, 8) DEFAULT 0,
    average_fill_price DECIMAL(20, 8),
    
    -- Risk Management
    leverage INTEGER DEFAULT 1,
    stop_loss_price DECIMAL(20, 8),
    take_profit_price DECIMAL(20, 8),
    
    -- Trade Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'filled', 'partially_filled', 'cancelled', 'rejected')),
    
    -- P&L Tracking
    realized_pnl DECIMAL(20, 8) DEFAULT 0,
    unrealized_pnl DECIMAL(20, 8) DEFAULT 0,
    
    -- Trading Mode
    is_paper_trade BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE
);

-- 4. Bot Activity Logs
CREATE TABLE IF NOT EXISTS bot_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL REFERENCES trading_bots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    
    -- Log Details
    log_type VARCHAR(50) NOT NULL, -- 'signal', 'trade', 'error', 'config_change', 'ai_generation'
    log_level VARCHAR(20) NOT NULL DEFAULT 'info' CHECK (log_level IN ('debug', 'info', 'warning', 'error')),
    
    -- Log Content
    message TEXT NOT NULL,
    details JSONB, -- Additional structured data
    
    -- Context
    exchange_response JSONB, -- Store exchange API responses
    trade_id UUID REFERENCES bot_trades(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. AI Strategy Templates (Predefined Strategies)
CREATE TABLE IF NOT EXISTS strategy_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Template Info
    template_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    
    -- Strategy Configuration
    strategy_config JSONB NOT NULL,
    
    -- Usage Stats
    usage_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Bot Performance Metrics
CREATE TABLE IF NOT EXISTS bot_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL REFERENCES trading_bots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    
    -- Performance Metrics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0, -- Percentage
    
    -- Financial Metrics
    total_pnl DECIMAL(20, 8) DEFAULT 0,
    total_volume DECIMAL(20, 8) DEFAULT 0,
    max_drawdown DECIMAL(20, 8) DEFAULT 0,
    
    -- Risk Metrics
    sharpe_ratio DECIMAL(10, 4),
    max_leverage_used INTEGER DEFAULT 1,
    
    -- Time Period
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Update Frequency (daily, weekly, monthly)
    period_type VARCHAR(20) NOT NULL DEFAULT 'daily',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique performance records per bot per period
    UNIQUE(bot_id, period_start, period_end, period_type)
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_trading_bots_user_id ON trading_bots(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_bots_status ON trading_bots(status);
CREATE INDEX IF NOT EXISTS idx_bot_trades_bot_id ON bot_trades(bot_id);
CREATE INDEX IF NOT EXISTS idx_bot_trades_symbol ON bot_trades(symbol);
CREATE INDEX IF NOT EXISTS idx_bot_trades_created_at ON bot_trades(created_at);
CREATE INDEX IF NOT EXISTS idx_bot_logs_bot_id ON bot_logs(bot_id);
CREATE INDEX IF NOT EXISTS idx_bot_logs_log_type ON bot_logs(log_type);
CREATE INDEX IF NOT EXISTS idx_bot_performance_bot_id ON bot_performance(bot_id);

-- Enable RLS on all tables
ALTER TABLE trading_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_exchange_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_performance ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Trading Bots
CREATE POLICY "Users can view own bots" ON trading_bots
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own bots" ON trading_bots
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bots" ON trading_bots
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own bots" ON trading_bots
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for Exchange Keys (Most Secure)
CREATE POLICY "Users can view own exchange keys" ON user_exchange_keys
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own exchange keys" ON user_exchange_keys
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own exchange keys" ON user_exchange_keys
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own exchange keys" ON user_exchange_keys
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for Bot Trades
CREATE POLICY "Users can view own bot trades" ON bot_trades
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can create bot trades" ON bot_trades
    FOR INSERT WITH CHECK (true); -- Backend creates trades

CREATE POLICY "System can update bot trades" ON bot_trades
    FOR UPDATE USING (true); -- Backend updates trades

-- RLS Policies for Bot Logs
CREATE POLICY "Users can view own bot logs" ON bot_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can create bot logs" ON bot_logs
    FOR INSERT WITH CHECK (true); -- Backend creates logs

-- RLS Policies for Strategy Templates (Public Read)
CREATE POLICY "Everyone can view strategy templates" ON strategy_templates
    FOR SELECT USING (is_active = true);

-- RLS Policies for Bot Performance
CREATE POLICY "Users can view own bot performance" ON bot_performance
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can manage bot performance" ON bot_performance
    FOR ALL USING (true); -- Backend manages performance metrics

-- Insert Predefined Strategy Templates
INSERT INTO strategy_templates (template_name, description, risk_level, strategy_config) VALUES
('Low-Risk Trend Follower', 'Trades only top-100 market cap assets. Leverage 2-3x. Enters in overbought/oversold zones with grid orders. No more than 2 concurrent trades.', 'low', 
'{"botName": "Low-Risk Trend Follower", "description": "Trades only top-100 market cap assets. Leverage 2-3x. Enters in overbought/oversold zones with grid orders. No more than 2 concurrent trades.", "strategy": {"type": "Trend Following", "trendTypes": ["Bullish", "Bearish"], "entryConditions": {"indicators": [{"name": "RSI", "overbought": 70, "oversold": 30}, {"name": "EMA", "periods": [20, 50], "condition": "EMA20 > EMA50 for long, EMA20 < EMA50 for short"}], "gridOrders": {"levels": 5, "spacingPercent": 0.5}}}, "riskManagement": {"leverage": 3, "maxConcurrentTrades": 2, "stopLossPercent": 2, "takeProfitPercent": 5, "avoidLiquidation": true}, "executionRules": {"orderType": "Limit", "timeInForce": "GTC"}}'::jsonb),

('Mid-Risk Breakout Trader', 'Trades strong breakouts with 5x leverage, trailing stop loss, and volume confirmation.', 'medium',
'{"botName": "Mid-Risk Breakout Trader", "description": "Trades strong breakouts with 5x leverage, trailing stop loss, and volume confirmation.", "strategy": {"type": "Breakout", "breakoutDetection": {"timeframes": ["15m", "1h"], "confirmationIndicators": [{"name": "Volume", "condition": "Volume > 150% of 20-period average"}, {"name": "Bollinger Bands", "condition": "Price closes above upper band for long, below lower band for short"}]}}, "riskManagement": {"leverage": 5, "maxConcurrentTrades": 4, "stopLossPercent": 3, "trailingStopPercent": 2, "takeProfitPercent": 7}, "executionRules": {"orderType": "Market", "timeInForce": "GTC"}}'::jsonb),

('High-Risk Scalper', 'Fast scalping with 10x leverage, small TP/SL targets.', 'high',
'{"botName": "High-Risk Scalper", "description": "Fast scalping with 10x leverage, small TP/SL targets.", "strategy": {"type": "Scalping", "timeframes": ["1m", "5m"], "entryConditions": {"indicators": [{"name": "EMA", "period": 9, "condition": "Price crosses EMA9"}, {"name": "VWAP", "condition": "Above VWAP for long, below for short"}]}}, "riskManagement": {"leverage": 10, "maxConcurrentTrades": 6, "stopLossPercent": 1, "takeProfitPercent": 1.5}, "executionRules": {"orderType": "Market", "timeInForce": "IOC"}}'::jsonb);