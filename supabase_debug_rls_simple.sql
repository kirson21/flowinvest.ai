-- Simple RLS disable script for debugging voting issues
-- This temporarily disables security to test if RLS is causing the API key errors

-- Disable RLS on user_votes table if it exists
ALTER TABLE user_votes DISABLE ROW LEVEL SECURITY;

-- Grant permissions to anon users for debugging
GRANT SELECT, INSERT, UPDATE, DELETE ON user_votes TO anon;

-- Disable RLS on seller_reviews table if it exists  
ALTER TABLE seller_reviews DISABLE ROW LEVEL SECURITY;

-- Grant permissions to anon users for debugging
GRANT SELECT, INSERT, UPDATE, DELETE ON seller_reviews TO anon;

-- Grant permissions on portfolios table for vote counts
GRANT SELECT ON portfolios TO anon;

-- Also grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON user_votes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON seller_reviews TO authenticated;

-- Display success message
SELECT 'RLS disabled for debugging - voting should now work' as status;