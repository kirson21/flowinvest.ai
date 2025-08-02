-- Fix Supabase RLS policies for user_bots table to allow authenticated users to manage their own bots

-- Enable RLS on user_bots table (if not already enabled)
ALTER TABLE user_bots ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to prevent conflicts)
DROP POLICY IF EXISTS "Users can view own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can insert own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can update own bots" ON user_bots;
DROP POLICY IF EXISTS "Users can delete own bots" ON user_bots;

-- Create RLS policies for user_bots table

-- Policy: Allow users to view their own bots + prebuilt bots
CREATE POLICY "Users can view own bots" 
ON user_bots
FOR SELECT
USING (auth.uid() = user_id OR is_prebuilt = true);

-- Policy: Allow users to insert their own bots
CREATE POLICY "Users can insert own bots" 
ON user_bots
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Allow users to update their own bots
CREATE POLICY "Users can update own bots" 
ON user_bots
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Policy: Allow users to delete their own bots
CREATE POLICY "Users can delete own bots" 
ON user_bots
FOR DELETE
USING (auth.uid() = user_id);

-- Ensure authenticated role has necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_bots TO authenticated;

-- Also create policies for other data sync tables to prevent similar issues

-- user_purchases table
ALTER TABLE user_purchases ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own purchases" ON user_purchases;
DROP POLICY IF EXISTS "Users can insert own purchases" ON user_purchases;

CREATE POLICY "Users can view own purchases" 
ON user_purchases
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own purchases" 
ON user_purchases
FOR INSERT
WITH CHECK (auth.uid() = user_id);

GRANT SELECT, INSERT ON user_purchases TO authenticated;

-- user_accounts table
ALTER TABLE user_accounts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own account" ON user_accounts;
DROP POLICY IF EXISTS "Users can upsert own account" ON user_accounts;

CREATE POLICY "Users can view own account" 
ON user_accounts
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can upsert own account" 
ON user_accounts
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

GRANT SELECT, INSERT, UPDATE ON user_accounts TO authenticated;

-- user_votes table
ALTER TABLE user_votes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own votes" ON user_votes;

CREATE POLICY "Users can manage own votes" 
ON user_votes
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON user_votes TO authenticated;