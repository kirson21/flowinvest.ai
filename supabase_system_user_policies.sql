-- Fix RLS policies to allow system user for pre-built bots

-- Drop existing policies to recreate them
DROP POLICY IF EXISTS "Users can view own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can insert own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can update own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can delete own bots" ON user_bots;

-- Create updated RLS policies that allow system user for pre-built bots
CREATE POLICY "Users can view own bots" 
ON user_bots
FOR SELECT
USING (
  auth.uid() = user_id 
  OR is_prebuilt = true 
  OR user_id = '00000000-0000-0000-0000-000000000000'
);

CREATE POLICY "Users can insert own bots" 
ON user_bots
FOR INSERT
WITH CHECK (
  auth.uid() = user_id 
  OR user_id = '00000000-0000-0000-0000-000000000000'
);

CREATE POLICY "Users can update own bots" 
ON user_bots
FOR UPDATE
USING (
  auth.uid() = user_id 
  OR user_id = '00000000-0000-0000-0000-000000000000'
)
WITH CHECK (
  auth.uid() = user_id 
  OR user_id = '00000000-0000-0000-0000-000000000000'
);

CREATE POLICY "Users can delete own bots" 
ON user_bots
FOR DELETE
USING (
  auth.uid() = user_id 
  OR user_id = '00000000-0000-0000-0000-000000000000'
);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_bots TO authenticated;