-- Fix user_purchases table for My Purchases functionality
-- This resolves HTTP 400 errors when loading/saving purchases

-- Create user_purchases table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_purchases (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    portfolio_id TEXT,
    purchase_id TEXT,
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    purchased_by UUID REFERENCES auth.users(id),
    -- Store the purchase data as JSON
    purchase_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_purchases ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own purchases" ON user_purchases;
DROP POLICY IF EXISTS "Users can insert own purchases" ON user_purchases;
DROP POLICY IF EXISTS "Users can update own purchases" ON user_purchases;
DROP POLICY IF EXISTS "Users can delete own purchases" ON user_purchases;

-- Create RLS policies for user_purchases
CREATE POLICY "Users can view own purchases" 
ON user_purchases FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own purchases" 
ON user_purchases FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own purchases" 
ON user_purchases FOR UPDATE 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own purchases" 
ON user_purchases FOR DELETE USING (auth.uid() = user_id);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_purchases TO authenticated;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_purchases_user_id ON user_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_user_purchases_portfolio_id ON user_purchases(portfolio_id);