-- Comprehensive fix for all remaining Supabase issues

-- Fix user_notifications table RLS policies (table already exists but needs proper policies)
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to recreate them properly
DROP POLICY IF EXISTS "Users can view own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can insert own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can delete own notifications" ON user_notifications;

-- Create proper RLS policies for user_notifications
CREATE POLICY "Users can view own notifications" 
ON user_notifications FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own notifications" 
ON user_notifications FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" 
ON user_notifications FOR UPDATE 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own notifications" 
ON user_notifications FOR DELETE USING (auth.uid() = user_id);

-- Add missing columns to user_profiles if they don't exist
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS seller_verification_status VARCHAR(50) DEFAULT 'unverified',
ADD COLUMN IF NOT EXISTS social_links JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS specialties TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS experience TEXT;

-- Fix user_profiles RLS policies
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

-- Fix user_accounts RLS policies
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

-- Grant all necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_notifications TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_accounts TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON portfolios TO authenticated;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id_read ON user_notifications(user_id, read);
CREATE INDEX IF NOT EXISTS idx_user_profiles_verification_status ON user_profiles(seller_verification_status);
CREATE INDEX IF NOT EXISTS idx_user_profiles_social_links ON user_profiles USING GIN (social_links);

-- Ensure portfolios table has proper structure for live marketplace
ALTER TABLE portfolios 
ADD COLUMN IF NOT EXISTS votes JSONB DEFAULT '{"upvotes": 0, "downvotes": 0, "totalVotes": 0}'::jsonb,
ADD COLUMN IF NOT EXISTS rating DECIMAL(3,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS total_reviews INTEGER DEFAULT 0;