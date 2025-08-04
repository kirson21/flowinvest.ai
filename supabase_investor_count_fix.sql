-- Fix user_purchases table for proper investor counting
-- This ensures the table has all required fields for total investor calculations

-- Add any missing columns to existing user_purchases table
ALTER TABLE user_purchases 
ADD COLUMN IF NOT EXISTS portfolio_id TEXT,
ADD COLUMN IF NOT EXISTS purchased_by UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS purchase_data JSONB DEFAULT '{}'::jsonb;

-- Make sure we have proper indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_purchases_portfolio_id ON user_purchases(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_user_purchases_purchased_by ON user_purchases(purchased_by);

-- Update RLS policies to ensure they work properly
DROP POLICY IF EXISTS "Users can view own purchases" ON user_purchases;
DROP POLICY IF EXISTS "Users can insert own purchases" ON user_purchases;
DROP POLICY IF EXISTS "Users can update own purchases" ON user_purchases;
DROP POLICY IF EXISTS "Users can delete own purchases" ON user_purchases;

-- Create better RLS policies
CREATE POLICY "Users can view own purchases" 
ON user_purchases FOR SELECT 
USING (auth.uid() = user_id OR auth.uid() = purchased_by);

CREATE POLICY "Users can insert own purchases" 
ON user_purchases FOR INSERT 
WITH CHECK (auth.uid() = user_id OR auth.uid() = purchased_by);

CREATE POLICY "Users can update own purchases" 
ON user_purchases FOR UPDATE 
USING (auth.uid() = user_id OR auth.uid() = purchased_by) 
WITH CHECK (auth.uid() = user_id OR auth.uid() = purchased_by);

CREATE POLICY "Users can delete own purchases" 
ON user_purchases FOR DELETE 
USING (auth.uid() = user_id OR auth.uid() = purchased_by);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_purchases TO authenticated;

-- Test the table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user_purchases' 
ORDER BY ordinal_position;