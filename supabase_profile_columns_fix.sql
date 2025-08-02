-- Add missing columns to existing Supabase tables

-- Add seller_verification_status column to user_profiles table
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS seller_verification_status VARCHAR(50) DEFAULT 'unverified',
ADD COLUMN IF NOT EXISTS social_links JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS specialties TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS experience TEXT;

-- Update RLS policies for user_profiles to allow all operations
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;

CREATE POLICY "Users can view own profile" 
ON user_profiles FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" 
ON user_profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" 
ON user_profiles FOR UPDATE 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Update RLS policies for user_accounts to allow all operations
DROP POLICY IF EXISTS "Users can view own account" ON user_accounts;
DROP POLICY IF EXISTS "Users can insert own account" ON user_accounts;
DROP POLICY IF EXISTS "Users can update own account" ON user_accounts;

CREATE POLICY "Users can view own account" 
ON user_accounts FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own account" 
ON user_accounts FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own account" 
ON user_accounts FOR UPDATE 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_verification_status ON user_profiles(seller_verification_status);
CREATE INDEX IF NOT EXISTS idx_user_profiles_social_links ON user_profiles USING GIN (social_links);

-- Make sure all permissions are granted
GRANT SELECT, INSERT, UPDATE, DELETE ON user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_accounts TO authenticated;