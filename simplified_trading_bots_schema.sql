-- Simplified Trading Bots Database Schema
-- API keys stored securely in Supabase without additional encryption

-- Exchange API Keys Table
CREATE TABLE IF NOT EXISTS exchange_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    exchange VARCHAR(50) NOT NULL,
    api_key TEXT NOT NULL,
    api_secret TEXT NOT NULL,
    passphrase TEXT,
    testnet BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_exchange_api_keys_user_id ON exchange_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_exchange_api_keys_active ON exchange_api_keys(user_id, is_active);

-- RLS Policies for exchange_api_keys
ALTER TABLE exchange_api_keys ENABLE ROW LEVEL SECURITY;

-- Users can only see their own API keys
CREATE POLICY "Users can view their own API keys" ON exchange_api_keys
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own API keys  
CREATE POLICY "Users can insert their own API keys" ON exchange_api_keys
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own API keys
CREATE POLICY "Users can update their own API keys" ON exchange_api_keys
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own API keys
CREATE POLICY "Users can delete their own API keys" ON exchange_api_keys
    FOR DELETE USING (auth.uid() = user_id);

-- Trading Bots Table (simplified)
CREATE TABLE IF NOT EXISTS user_trading_bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    strategy VARCHAR(100) NOT NULL,
    trading_pair VARCHAR(20) NOT NULL,
    leverage DECIMAL(5,2) DEFAULT 1.0,
    stop_loss DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'inactive',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_trading_bots_user_id ON user_trading_bots(user_id);

-- RLS Policies for trading bots
ALTER TABLE user_trading_bots ENABLE ROW LEVEL SECURITY;

-- Users can only see their own bots
CREATE POLICY "Users can view their own bots" ON user_trading_bots
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own bots
CREATE POLICY "Users can insert their own bots" ON user_trading_bots
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own bots
CREATE POLICY "Users can update their own bots" ON user_trading_bots
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own bots  
CREATE POLICY "Users can delete their own bots" ON user_trading_bots
    FOR DELETE USING (auth.uid() = user_id);

-- Bot Trading Logs (simplified)
CREATE TABLE IF NOT EXISTS bot_trading_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID REFERENCES user_trading_bots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    trading_pair VARCHAR(20),
    amount DECIMAL(20,8),
    price DECIMAL(20,8),
    result TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for logs
CREATE INDEX IF NOT EXISTS idx_bot_trading_logs_bot_id ON bot_trading_logs(bot_id);
CREATE INDEX IF NOT EXISTS idx_bot_trading_logs_user_id ON bot_trading_logs(user_id);

-- RLS Policies for bot logs
ALTER TABLE bot_trading_logs ENABLE ROW LEVEL SECURITY;

-- Users can only see their own bot logs
CREATE POLICY "Users can view their own bot logs" ON bot_trading_logs
    FOR SELECT USING (auth.uid() = user_id);

-- System can insert bot logs
CREATE POLICY "System can insert bot logs" ON bot_trading_logs
    FOR INSERT WITH CHECK (true);

-- Update triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers
DROP TRIGGER IF EXISTS update_exchange_api_keys_updated_at ON exchange_api_keys;
CREATE TRIGGER update_exchange_api_keys_updated_at
    BEFORE UPDATE ON exchange_api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_trading_bots_updated_at ON user_trading_bots;
CREATE TRIGGER update_user_trading_bots_updated_at
    BEFORE UPDATE ON user_trading_bots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();