-- Emergency fix for RLS policies - Make them less restrictive
-- Run this if portfolio creation still fails after debugging

-- Temporarily disable RLS on all tables to test if that's the issue
ALTER TABLE portfolios DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_notifications DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_accounts DISABLE ROW LEVEL SECURITY;

-- Alternative: Make RLS policies more permissive (if you prefer to keep RLS enabled)
-- Uncomment these lines if you want to keep RLS but make it more permissive:

-- DROP POLICY IF EXISTS "Users can insert own portfolios" ON portfolios;
-- CREATE POLICY "Allow all authenticated users to insert portfolios" 
-- ON portfolios FOR INSERT TO authenticated WITH CHECK (true);

-- DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
-- CREATE POLICY "Allow all authenticated users to view profiles" 
-- ON user_profiles FOR SELECT TO authenticated USING (true);

-- DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
-- CREATE POLICY "Allow all authenticated users to insert profiles" 
-- ON user_profiles FOR INSERT TO authenticated WITH CHECK (true);

-- DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
-- CREATE POLICY "Allow all authenticated users to update profiles" 
-- ON user_profiles FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

GRANT ALL ON portfolios TO authenticated;
GRANT ALL ON user_notifications TO authenticated;
GRANT ALL ON user_profiles TO authenticated;
GRANT ALL ON user_accounts TO authenticated;