-- Flow Invest Supabase Database Schema
-- Created for comprehensive user management, trading bots, portfolios, and real-time features

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE bot_status AS ENUM ('active', 'inactive', 'paused', 'error');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high');
CREATE TYPE trade_type AS ENUM ('long', 'short');
CREATE TYPE portfolio_type AS ENUM ('manual', 'ai_generated', 'prebuilt');
CREATE TYPE exchange_type AS ENUM ('binance', 'bybit', 'kraken');

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    country TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- User settings and preferences
CREATE TABLE public.user_settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    language VARCHAR(10) DEFAULT 'en' NOT NULL,
    theme VARCHAR(20) DEFAULT 'light' NOT NULL,
    notifications_enabled BOOLEAN DEFAULT true,
    email_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id)
);

-- Encrypted API keys storage
CREATE TABLE public.api_keys (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    exchange exchange_type NOT NULL,
    name TEXT NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    api_secret_encrypted TEXT NOT NULL,
    passphrase_encrypted TEXT,
    is_testnet BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Trading bots table
CREATE TABLE public.bots (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    strategy TEXT NOT NULL,
    risk_level risk_level DEFAULT 'medium',
    trade_type trade_type DEFAULT 'long',
    base_coin VARCHAR(20) NOT NULL,
    quote_coin VARCHAR(20) NOT NULL,
    exchange exchange_type NOT NULL,
    api_key_id UUID REFERENCES public.api_keys(id) ON DELETE SET NULL,
    status bot_status DEFAULT 'inactive',
    is_prebuilt BOOLEAN DEFAULT false,
    
    -- Configuration settings
    deposit_amount DECIMAL(20, 8),
    trading_mode VARCHAR(50) DEFAULT 'simple',
    profit_target DECIMAL(10, 4),
    stop_loss DECIMAL(10, 4),
    
    -- Advanced settings (stored as JSONB for flexibility)
    advanced_settings JSONB DEFAULT '{}',
    
    -- Performance metrics
    daily_pnl DECIMAL(10, 4) DEFAULT 0,
    weekly_pnl DECIMAL(10, 4) DEFAULT 0,
    monthly_pnl DECIMAL(10, 4) DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    last_executed_at TIMESTAMP WITH TIME ZONE
);

-- Portfolios table
CREATE TABLE public.portfolios (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    portfolio_type portfolio_type DEFAULT 'manual',
    risk_level risk_level DEFAULT 'medium',
    total_value DECIMAL(20, 8) DEFAULT 0,
    
    -- Performance metrics
    daily_return DECIMAL(10, 4) DEFAULT 0,
    weekly_return DECIMAL(10, 4) DEFAULT 0,
    monthly_return DECIMAL(10, 4) DEFAULT 0,
    yearly_return DECIMAL(10, 4) DEFAULT 0,
    
    -- Portfolio configuration
    auto_rebalance BOOLEAN DEFAULT false,
    rebalance_frequency VARCHAR(20),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Portfolio assets (holdings)
CREATE TABLE public.portfolio_assets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name TEXT,
    quantity DECIMAL(20, 8) NOT NULL,
    avg_price DECIMAL(20, 8),
    current_price DECIMAL(20, 8),
    allocation_percentage DECIMAL(5, 2),
    value DECIMAL(20, 8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- News feed entries (enhanced from existing system)
CREATE TABLE public.news_feed (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    sentiment INTEGER CHECK (sentiment >= 0 AND sentiment <= 100),
    source TEXT,
    original_language VARCHAR(10) DEFAULT 'en',
    content_hash TEXT UNIQUE, -- To prevent duplicates
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Translations table (for multi-language support)
CREATE TABLE public.translations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    news_feed_id UUID REFERENCES public.news_feed(id) ON DELETE CASCADE NOT NULL,
    language VARCHAR(10) NOT NULL,
    title_translated TEXT NOT NULL,
    summary_translated TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(news_feed_id, language)
);

-- Bot trading history
CREATE TABLE public.bot_trades (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    bot_id UUID REFERENCES public.bots(id) ON DELETE CASCADE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- 'buy' or 'sell'
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    fee DECIMAL(20, 8) DEFAULT 0,
    pnl DECIMAL(20, 8),
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- User sessions and activity logs
CREATE TABLE public.user_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_bots_user_id ON public.bots(user_id);
CREATE INDEX idx_bots_status ON public.bots(status);
CREATE INDEX idx_portfolios_user_id ON public.portfolios(user_id);
CREATE INDEX idx_portfolio_assets_portfolio_id ON public.portfolio_assets(portfolio_id);
CREATE INDEX idx_news_feed_published_at ON public.news_feed(published_at DESC);
CREATE INDEX idx_translations_news_feed_id ON public.translations(news_feed_id);
CREATE INDEX idx_bot_trades_bot_id ON public.bot_trades(bot_id);
CREATE INDEX idx_bot_trades_executed_at ON public.bot_trades(executed_at DESC);
CREATE INDEX idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX idx_api_keys_user_id ON public.api_keys(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bot_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies

-- Users can only see their own profile
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- User settings policies
CREATE POLICY "Users can view own settings" ON public.user_settings
    FOR ALL USING (auth.uid() = user_id);

-- API keys policies (highly restricted)
CREATE POLICY "Users can manage own API keys" ON public.api_keys
    FOR ALL USING (auth.uid() = user_id);

-- Bots policies
CREATE POLICY "Users can view own bots and prebuilt bots" ON public.bots
    FOR SELECT USING (auth.uid() = user_id OR is_prebuilt = true);

CREATE POLICY "Users can manage own bots" ON public.bots
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bots" ON public.bots
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own bots" ON public.bots
    FOR DELETE USING (auth.uid() = user_id);

-- Portfolios policies
CREATE POLICY "Users can manage own portfolios" ON public.portfolios
    FOR ALL USING (auth.uid() = user_id);

-- Portfolio assets policies
CREATE POLICY "Users can manage portfolio assets" ON public.portfolio_assets
    FOR ALL USING (
        auth.uid() = (SELECT user_id FROM public.portfolios WHERE id = portfolio_id)
    );

-- Bot trades policies
CREATE POLICY "Users can view own bot trades" ON public.bot_trades
    FOR SELECT USING (
        auth.uid() = (SELECT user_id FROM public.bots WHERE id = bot_id)
    );

-- User sessions policies
CREATE POLICY "Users can view own sessions" ON public.user_sessions
    FOR ALL USING (auth.uid() = user_id);

-- News feed is public (no RLS needed)
-- Translations are public (no RLS needed)

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON public.user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON public.api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bots_updated_at BEFORE UPDATE ON public.bots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON public.portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolio_assets_updated_at BEFORE UPDATE ON public.portfolio_assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample prebuilt bots (FlowInvest.ai bots)
INSERT INTO public.bots (
    name, description, strategy, risk_level, trade_type, 
    base_coin, quote_coin, exchange, is_prebuilt, status,
    daily_pnl, weekly_pnl, monthly_pnl, win_rate
) VALUES 
(
    'AI Trend Master Pro',
    'Advanced trend-following algorithm with machine learning capabilities and smart risk management',
    'Trend Following',
    'medium',
    'long',
    'BTC',
    'USDT',
    'binance',
    true,
    'active',
    2.34,
    12.78,
    45.67,
    68.5
),
(
    'Quantum Scalping Engine',
    'High-frequency trading bot optimized for quick profits with AI-powered entry and exit signals',
    'Scalping',
    'high',
    'long',
    'ETH',
    'USDT',
    'bybit',
    true,
    'active',
    4.12,
    18.45,
    47.89,
    72.3
),
(
    'Shield Conservative Growth',
    'Low-risk strategy focused on steady gains with advanced portfolio protection mechanisms',
    'Conservative Growth',
    'low',
    'long',
    'BTC',
    'USD',
    'kraken',
    true,
    'active',
    0.89,
    4.23,
    18.56,
    78.9
),
(
    'DeFi Yield Maximizer',
    'Smart contract integration for optimized DeFi yield farming with automated rebalancing',
    'DeFi Yield',
    'medium',
    'long',
    'Multi-Asset',
    'USDT',
    'binance',
    true,
    'active',
    1.95,
    8.74,
    32.15,
    74.2
);

-- Create a function to handle user creation (triggered by Supabase Auth)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    
    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;