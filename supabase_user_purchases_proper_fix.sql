-- PROPER FIX: Drop and recreate user_purchases table with correct structure
-- This will enable proper cross-device synchronization

-- Drop the broken table completely
DROP TABLE IF EXISTS user_purchases CASCADE;

-- Create user_purchases table with proper structure for cross-device sync
CREATE TABLE user_purchases (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    portfolio_id TEXT NOT NULL,
    purchase_id TEXT UNIQUE NOT NULL,
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    purchased_by UUID REFERENCES auth.users(id),
    -- Store the complete purchase data as JSONB for flexibility
    purchase_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_purchases ENABLE ROW LEVEL SECURITY;

-- Create proper RLS policies for cross-device access
CREATE POLICY "Users can view own purchases" 
ON user_purchases FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own purchases" 
ON user_purchases FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own purchases" 
ON user_purchases FOR UPDATE 
USING (auth.uid() = user_id) 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own purchases" 
ON user_purchases FOR DELETE 
USING (auth.uid() = user_id);

-- Grant all necessary permissions
GRANT ALL ON user_purchases TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Create indexes for performance
CREATE INDEX idx_user_purchases_user_id ON user_purchases(user_id);
CREATE INDEX idx_user_purchases_portfolio_id ON user_purchases(portfolio_id);
CREATE INDEX idx_user_purchases_purchased_at ON user_purchases(purchased_at);

-- Verify the table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user_purchases' 
ORDER BY ordinal_position;