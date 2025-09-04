-- ============================================================================
-- AI BOTS DATABASE SCHEMA
-- Creates tables for AI-generated bots with flexible JSON structure and chat history
-- ============================================================================

-- Drop existing objects if they exist (for clean recreation)
DROP TABLE IF EXISTS public.ai_bot_chat_history CASCADE;
DROP TABLE IF EXISTS public.user_ai_bots CASCADE;

-- Create user_ai_bots table (separate from user_bots for manual bots)
CREATE TABLE public.user_ai_bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- AI Model and Generation Info
    ai_model VARCHAR(50) NOT NULL, -- 'gpt-5', 'grok-4'
    generation_prompt TEXT NOT NULL, -- Original user prompt
    
    -- Flexible JSON Configuration (allows dynamic parameters)
    bot_config JSONB NOT NULL DEFAULT '{}', -- Main bot configuration
    strategy_config JSONB DEFAULT '{}', -- Strategy-specific settings
    risk_management JSONB DEFAULT '{}', -- Risk management parameters
    technical_indicators JSONB DEFAULT '{}', -- Technical indicator settings
    trading_rules JSONB DEFAULT '{}', -- Entry/exit rules
    
    -- Basic Trading Parameters (can be overridden in JSON)
    base_coin VARCHAR(10), -- e.g., 'BTC'
    quote_coin VARCHAR(10), -- e.g., 'USDT'
    exchange VARCHAR(50) DEFAULT 'binance',
    trade_type VARCHAR(20) DEFAULT 'spot', -- 'spot', 'futures'
    
    -- Status and Performance
    status VARCHAR(20) DEFAULT 'inactive', -- 'active', 'inactive', 'paused', 'error'
    is_active BOOLEAN DEFAULT false,
    
    -- Performance Metrics
    daily_pnl DECIMAL(10,4) DEFAULT 0,
    weekly_pnl DECIMAL(10,4) DEFAULT 0,
    monthly_pnl DECIMAL(10,4) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Metadata
    is_public BOOLEAN DEFAULT false,
    slug VARCHAR(255) UNIQUE,
    tags TEXT[] DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_active_at TIMESTAMP WITH TIME ZONE
);

-- Create chat history table (30-day retention)
CREATE TABLE public.ai_bot_chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL, -- Groups messages for one bot creation session
    
    -- Chat Message Data
    message_type VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    message_content TEXT NOT NULL,
    ai_model VARCHAR(50), -- Which model generated the response
    
    -- Context and Metadata
    bot_creation_stage VARCHAR(50), -- 'initial', 'clarification', 'refinement', 'final'
    context_data JSONB DEFAULT '{}', -- Additional context for the message
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Indexes for Performance
CREATE INDEX idx_user_ai_bots_user_id ON public.user_ai_bots(user_id);
CREATE INDEX idx_user_ai_bots_status ON public.user_ai_bots(status);
CREATE INDEX idx_user_ai_bots_is_active ON public.user_ai_bots(is_active);
CREATE INDEX idx_user_ai_bots_created_at ON public.user_ai_bots(created_at DESC);
CREATE INDEX idx_user_ai_bots_slug ON public.user_ai_bots(slug);

CREATE INDEX idx_ai_bot_chat_history_user_id ON public.ai_bot_chat_history(user_id);
CREATE INDEX idx_ai_bot_chat_history_session_id ON public.ai_bot_chat_history(session_id);
CREATE INDEX idx_ai_bot_chat_history_created_at ON public.ai_bot_chat_history(created_at DESC);

-- Row Level Security (RLS) Policies
ALTER TABLE public.user_ai_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_bot_chat_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_ai_bots
CREATE POLICY "Users can view their own AI bots" ON public.user_ai_bots
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own AI bots" ON public.user_ai_bots
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own AI bots" ON public.user_ai_bots
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own AI bots" ON public.user_ai_bots
    FOR DELETE USING (auth.uid() = user_id);

-- Public AI bots can be viewed by anyone
CREATE POLICY "Public AI bots are viewable by everyone" ON public.user_ai_bots
    FOR SELECT USING (is_public = true);

-- RLS Policies for ai_bot_chat_history
CREATE POLICY "Users can view their own chat history" ON public.ai_bot_chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chat messages" ON public.ai_bot_chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own chat history" ON public.ai_bot_chat_history
    FOR DELETE USING (auth.uid() = user_id);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_ai_bots_updated_at
    BEFORE UPDATE ON public.user_ai_bots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up old chat history (30-day retention)
CREATE OR REPLACE FUNCTION cleanup_old_chat_history()
RETURNS void AS $$
BEGIN
    DELETE FROM public.ai_bot_chat_history 
    WHERE created_at < (now() - interval '30 days');
END;
$$ LANGUAGE plpgsql;

-- RPC Functions for API access

-- Get user's AI bots
CREATE OR REPLACE FUNCTION get_user_ai_bots(user_uuid UUID)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    name VARCHAR,
    description TEXT,
    ai_model VARCHAR,
    bot_config JSONB,
    strategy_config JSONB,
    risk_management JSONB,
    base_coin VARCHAR,
    quote_coin VARCHAR,
    exchange VARCHAR,
    status VARCHAR,
    is_active BOOLEAN,
    daily_pnl DECIMAL,
    weekly_pnl DECIMAL,
    monthly_pnl DECIMAL,
    total_trades INTEGER,
    successful_trades INTEGER,
    win_rate DECIMAL,
    slug VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        uab.id, uab.user_id, uab.name, uab.description, uab.ai_model,
        uab.bot_config, uab.strategy_config, uab.risk_management,
        uab.base_coin, uab.quote_coin, uab.exchange, uab.status, uab.is_active,
        uab.daily_pnl, uab.weekly_pnl, uab.monthly_pnl,
        uab.total_trades, uab.successful_trades, uab.win_rate,
        uab.slug, uab.created_at, uab.updated_at
    FROM public.user_ai_bots uab
    WHERE uab.user_id = user_uuid
    ORDER BY uab.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Save AI bot
CREATE OR REPLACE FUNCTION save_ai_bot(
    p_user_id UUID,
    p_name VARCHAR,
    p_description TEXT,
    p_ai_model VARCHAR,
    p_generation_prompt TEXT,
    p_bot_config JSONB,
    p_strategy_config JSONB DEFAULT '{}',
    p_risk_management JSONB DEFAULT '{}',
    p_base_coin VARCHAR DEFAULT NULL,
    p_quote_coin VARCHAR DEFAULT NULL,
    p_exchange VARCHAR DEFAULT 'binance'
)
RETURNS UUID AS $$
DECLARE
    new_bot_id UUID;
    bot_slug VARCHAR;
BEGIN
    -- Generate a unique slug
    bot_slug := lower(regexp_replace(p_name, '[^a-zA-Z0-9]+', '-', 'g'));
    bot_slug := trim(both '-' from bot_slug);
    
    -- Ensure slug is unique
    WHILE EXISTS (SELECT 1 FROM public.user_ai_bots WHERE slug = bot_slug) LOOP
        bot_slug := bot_slug || '-' || floor(random() * 1000)::text;
    END LOOP;
    
    -- Insert the new AI bot
    INSERT INTO public.user_ai_bots (
        user_id, name, description, ai_model, generation_prompt,
        bot_config, strategy_config, risk_management,
        base_coin, quote_coin, exchange, slug
    )
    VALUES (
        p_user_id, p_name, p_description, p_ai_model, p_generation_prompt,
        p_bot_config, p_strategy_config, p_risk_management,
        p_base_coin, p_quote_coin, p_exchange, bot_slug
    )
    RETURNING id INTO new_bot_id;
    
    RETURN new_bot_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get chat history for a session
CREATE OR REPLACE FUNCTION get_chat_history(
    p_user_id UUID,
    p_session_id UUID
)
RETURNS TABLE (
    id UUID,
    message_type VARCHAR,
    message_content TEXT,
    ai_model VARCHAR,
    bot_creation_stage VARCHAR,
    context_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ch.id, ch.message_type, ch.message_content, ch.ai_model,
        ch.bot_creation_stage, ch.context_data, ch.created_at
    FROM public.ai_bot_chat_history ch
    WHERE ch.user_id = p_user_id AND ch.session_id = p_session_id
    ORDER BY ch.created_at ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Save chat message
CREATE OR REPLACE FUNCTION save_chat_message(
    p_user_id UUID,
    p_session_id UUID,
    p_message_type VARCHAR,
    p_message_content TEXT,
    p_ai_model VARCHAR DEFAULT NULL,
    p_bot_creation_stage VARCHAR DEFAULT 'initial',
    p_context_data JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    message_id UUID;
BEGIN
    INSERT INTO public.ai_bot_chat_history (
        user_id, session_id, message_type, message_content,
        ai_model, bot_creation_stage, context_data
    )
    VALUES (
        p_user_id, p_session_id, p_message_type, p_message_content,
        p_ai_model, p_bot_creation_stage, p_context_data
    )
    RETURNING id INTO message_id;
    
    RETURN message_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.user_ai_bots TO anon, authenticated;
GRANT ALL ON public.user_ai_bots TO authenticated;
GRANT ALL ON public.ai_bot_chat_history TO authenticated;

GRANT EXECUTE ON FUNCTION get_user_ai_bots(UUID) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION save_ai_bot(UUID, VARCHAR, TEXT, VARCHAR, TEXT, JSONB, JSONB, JSONB, VARCHAR, VARCHAR, VARCHAR) TO authenticated;
GRANT EXECUTE ON FUNCTION get_chat_history(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION save_chat_message(UUID, UUID, VARCHAR, TEXT, VARCHAR, VARCHAR, JSONB) TO authenticated;

-- Comments for documentation
COMMENT ON TABLE public.user_ai_bots IS 'AI-generated trading bots with flexible JSON configuration';
COMMENT ON TABLE public.ai_bot_chat_history IS 'Chat history for AI bot creation sessions (30-day retention)';
COMMENT ON COLUMN public.user_ai_bots.bot_config IS 'Main bot configuration in flexible JSON format';
COMMENT ON COLUMN public.user_ai_bots.strategy_config IS 'Strategy-specific settings allowing dynamic strategies';
COMMENT ON COLUMN public.user_ai_bots.risk_management IS 'Risk management parameters in JSON format';
COMMENT ON COLUMN public.ai_bot_chat_history.session_id IS 'Groups chat messages for one bot creation session';

-- Insert example AI bot configurations for reference
-- (These would be removed in production)
INSERT INTO public.user_ai_bots (
    user_id,
    name,
    description,
    ai_model,
    generation_prompt,
    bot_config,
    strategy_config,
    risk_management,
    base_coin,
    quote_coin,
    slug
) VALUES (
    'cd0e9717-f85d-4726-81e9-f260394ead58', -- Super admin user
    'AI Momentum Trader',
    'Advanced momentum trading bot that adapts to market conditions',
    'gpt-5',
    'Create a momentum trading bot for Bitcoin that can adapt its strategy based on market volatility',
    '{"trading_mode": "spot", "max_positions": 3, "position_size": 0.1}',
    '{"type": "momentum", "indicators": ["RSI", "MACD", "EMA"], "timeframes": ["1h", "4h"], "adaptation_rules": {"high_volatility": {"position_size": 0.05}, "low_volatility": {"position_size": 0.15}}}',
    '{"stop_loss": 2.5, "take_profit": 5.0, "max_drawdown": 10.0, "risk_per_trade": 1.0}',
    'BTC',
    'USDT',
    'ai-momentum-trader'
) ON CONFLICT (slug) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'AI Bots Database Schema created successfully!';
    RAISE NOTICE 'Tables created: user_ai_bots, ai_bot_chat_history';
    RAISE NOTICE 'Functions created: get_user_ai_bots, save_ai_bot, get_chat_history, save_chat_message';
    RAISE NOTICE 'Chat history retention: 30 days';
END $$;