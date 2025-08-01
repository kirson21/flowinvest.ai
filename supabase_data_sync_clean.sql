-- Cross-Device Data Synchronization Database Schema
-- This schema enables user data to sync across all devices

-- Table: user_bots (for trading bots synchronization)
CREATE TABLE IF NOT EXISTS user_bots (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Bot Configuration
    name VARCHAR(255) NOT NULL,
    description TEXT,
    strategy VARCHAR(100) NOT NULL,
    exchange VARCHAR(100) NOT NULL,
    trading_pair VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    
    -- Performance Metrics
    daily_pnl DECIMAL(10,4) DEFAULT 0,
    weekly_pnl DECIMAL(10,4) DEFAULT 0,
    monthly_pnl DECIMAL(10,4) DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Bot Status
    is_active BOOLEAN DEFAULT FALSE,
    is_prebuilt BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'inactive',
    
    -- Advanced Settings (stored as JSONB for flexibility)
    advanced_settings JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: user_purchases (for marketplace purchases synchronization)
CREATE TABLE IF NOT EXISTS user_purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Purchase Details
    product_id VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    
    -- Purchase Information
    purchase_price DECIMAL(10,2) NOT NULL,
    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Product Data (stored as JSONB)
    product_data JSONB NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'refunded', 'expired'))
);

-- Table: user_accounts (for account balance synchronization)
CREATE TABLE IF NOT EXISTS user_accounts (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Account Balance
    balance DECIMAL(15,2) DEFAULT 0.00,
    
    -- Currency
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: user_votes (for voting history synchronization)
CREATE TABLE IF NOT EXISTS user_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Vote Details
    product_id VARCHAR(255) NOT NULL,
    vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('upvote', 'downvote')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate votes
    UNIQUE(user_id, product_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_bots_user_id ON user_bots(user_id);
CREATE INDEX IF NOT EXISTS idx_user_bots_created_at ON user_bots(created_at);
CREATE INDEX IF NOT EXISTS idx_user_purchases_user_id ON user_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_user_purchases_purchased_at ON user_purchases(purchased_at);
CREATE INDEX IF NOT EXISTS idx_user_votes_user_id ON user_votes(user_id);

-- RLS Policies
ALTER TABLE user_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_accounts ENABLE ROW LEVEL SECURITY;  
ALTER TABLE user_votes ENABLE ROW LEVEL SECURITY;

-- User Bots Policies
CREATE POLICY "Users can view own bots" ON user_bots
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own bots" ON user_bots
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bots" ON user_bots
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own bots" ON user_bots
    FOR DELETE USING (auth.uid() = user_id);

-- Super admin can manage all bots
CREATE POLICY "Super admin can manage all bots" ON user_bots
    FOR ALL USING (auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58');

-- User Purchases Policies
CREATE POLICY "Users can view own purchases" ON user_purchases
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own purchases" ON user_purchases
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Super admin can view all purchases
CREATE POLICY "Super admin can view all purchases" ON user_purchases
    FOR SELECT USING (auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58');

-- User Accounts Policies
CREATE POLICY "Users can view own account" ON user_accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own account" ON user_accounts
    FOR ALL USING (auth.uid() = user_id);

-- Super admin can view all accounts
CREATE POLICY "Super admin can view all accounts" ON user_accounts
    FOR SELECT USING (auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58');

-- User Votes Policies
CREATE POLICY "Users can view own votes" ON user_votes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own votes" ON user_votes
    FOR ALL USING (auth.uid() = user_id);

-- Functions for automatic timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamps
CREATE TRIGGER update_user_bots_updated_at BEFORE UPDATE ON user_bots 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_accounts_updated_at BEFORE UPDATE ON user_accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Initialize user account on first login (optional)
CREATE OR REPLACE FUNCTION init_user_account()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_accounts (user_id, balance) 
    VALUES (NEW.id, 0.00)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to create account on user creation
CREATE TRIGGER init_user_account_trigger
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION init_user_account();