-- Fix existing user_purchases table structure
-- This adds missing columns and fixes the schema

-- Add missing columns to existing user_purchases table
ALTER TABLE user_purchases 
ADD COLUMN IF NOT EXISTS portfolio_id TEXT,
ADD COLUMN IF NOT EXISTS purchase_id TEXT,
ADD COLUMN IF NOT EXISTS purchased_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS purchased_by UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS purchase_data JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Make sure user_id column exists and is correct type
ALTER TABLE user_purchases 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Enable RLS if not already enabled
ALTER TABLE user_purchases ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to recreate them
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