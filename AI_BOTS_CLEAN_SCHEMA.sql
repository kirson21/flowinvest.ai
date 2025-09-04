-- AI BOTS DATABASE SCHEMA - CLEAN VERSION FOR SUPABASE
-- Execute this in your Supabase SQL Editor

-- Drop existing objects if they exist
DROP TABLE IF EXISTS public.ai_bot_chat_history CASCADE;
DROP TABLE IF EXISTS public.user_ai_bots CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_chat_history() CASCADE;
DROP FUNCTION IF EXISTS get_user_ai_bots(UUID) CASCADE;
DROP FUNCTION IF EXISTS save_ai_bot(UUID, VARCHAR, TEXT, VARCHAR, TEXT, JSONB, JSONB, JSONB, VARCHAR, VARCHAR, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_chat_history(UUID, UUID) CASCADE;
DROP FUNCTION IF EXISTS save_chat_message(UUID, UUID, VARCHAR, TEXT, VARCHAR, VARCHAR, JSONB) CASCADE;

-- Create user_ai_bots table
CREATE TABLE public.user_ai_bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    ai_model VARCHAR(50) NOT NULL,
    generation_prompt TEXT NOT NULL,
    bot_config JSONB NOT NULL DEFAULT '{}',
    strategy_config JSONB DEFAULT '{}',
    risk_management JSONB DEFAULT '{}',
    technical_indicators JSONB DEFAULT '{}',
    trading_rules JSONB DEFAULT '{}',
    base_coin VARCHAR(10),
    quote_coin VARCHAR(10),
    exchange VARCHAR(50) DEFAULT 'binance',
    trade_type VARCHAR(20) DEFAULT 'spot',
    status VARCHAR(20) DEFAULT 'inactive',
    is_active BOOLEAN DEFAULT false,
    daily_pnl DECIMAL(10,4) DEFAULT 0,
    weekly_pnl DECIMAL(10,4) DEFAULT 0,
    monthly_pnl DECIMAL(10,4) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    slug VARCHAR(255) UNIQUE,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_active_at TIMESTAMP WITH TIME ZONE
);

-- Create chat history table
CREATE TABLE public.ai_bot_chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    ai_model VARCHAR(50),
    bot_creation_stage VARCHAR(50),
    context_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create indexes
CREATE INDEX idx_user_ai_bots_user_id ON public.user_ai_bots(user_id);
CREATE INDEX idx_user_ai_bots_status ON public.user_ai_bots(status);
CREATE INDEX idx_user_ai_bots_is_active ON public.user_ai_bots(is_active);
CREATE INDEX idx_user_ai_bots_created_at ON public.user_ai_bots(created_at DESC);
CREATE INDEX idx_user_ai_bots_slug ON public.user_ai_bots(slug);
CREATE INDEX idx_ai_bot_chat_history_user_id ON public.ai_bot_chat_history(user_id);
CREATE INDEX idx_ai_bot_chat_history_session_id ON public.ai_bot_chat_history(session_id);
CREATE INDEX idx_ai_bot_chat_history_created_at ON public.ai_bot_chat_history(created_at DESC);

-- Enable RLS
ALTER TABLE public.user_ai_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_bot_chat_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_ai_bots
CREATE POLICY user_ai_bots_select_own ON public.user_ai_bots
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY user_ai_bots_insert_own ON public.user_ai_bots
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY user_ai_bots_update_own ON public.user_ai_bots
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY user_ai_bots_delete_own ON public.user_ai_bots
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY user_ai_bots_select_public ON public.user_ai_bots
    FOR SELECT USING (is_public = true);

-- RLS Policies for ai_bot_chat_history
CREATE POLICY chat_history_select_own ON public.ai_bot_chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY chat_history_insert_own ON public.ai_bot_chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY chat_history_delete_own ON public.ai_bot_chat_history
    FOR DELETE USING (auth.uid() = user_id);

-- Functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_ai_bots_updated_at
    BEFORE UPDATE ON public.user_ai_bots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION cleanup_old_chat_history()
RETURNS void AS $$
BEGIN
    DELETE FROM public.ai_bot_chat_history 
    WHERE created_at < (now() - interval '30 days');
END;
$$ LANGUAGE plpgsql;

-- RPC Functions
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
    bot_slug := lower(regexp_replace(p_name, '[^a-zA-Z0-9]+', '-', 'g'));
    bot_slug := trim(both '-' from bot_slug);
    
    WHILE EXISTS (SELECT 1 FROM public.user_ai_bots WHERE slug = bot_slug) LOOP
        bot_slug := bot_slug || '-' || floor(random() * 1000)::text;
    END LOOP;
    
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

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.user_ai_bots TO anon, authenticated;
GRANT ALL ON public.user_ai_bots TO authenticated;
GRANT ALL ON public.ai_bot_chat_history TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_ai_bots(UUID) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION save_ai_bot(UUID, VARCHAR, TEXT, VARCHAR, TEXT, JSONB, JSONB, JSONB, VARCHAR, VARCHAR, VARCHAR) TO authenticated;
GRANT EXECUTE ON FUNCTION get_chat_history(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION save_chat_message(UUID, UUID, VARCHAR, TEXT, VARCHAR, VARCHAR, JSONB) TO authenticated;