-- Correct RLS policies: Pre-built bots belong to super admin but are visible to all users

-- Drop existing policies to recreate them
DROP POLICY IF EXISTS "Users can view own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can insert own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can update own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can delete own bots" ON user_bots;

-- Create correct RLS policies
CREATE POLICY "Users can view own bots" 
ON user_bots
FOR SELECT
USING (
  auth.uid() = user_id 
  OR is_prebuilt = true
);

CREATE POLICY "Users can insert own bots" 
ON user_bots
FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bots" 
ON user_bots
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own bots" 
ON user_bots
FOR DELETE
USING (auth.uid() = user_id);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_bots TO authenticated;