-- Fix for voting and reviews functionality
-- This script ensures proper RLS policies for user_votes and seller_reviews tables

-- ==================================================
-- USER VOTES TABLE FIXES
-- ==================================================

-- Drop existing policies to start fresh
DROP POLICY IF EXISTS "Users can manage their own votes" ON user_votes;
DROP POLICY IF EXISTS "Users can view all votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to read votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to insert votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to update their votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to delete their votes" ON user_votes;

-- Enable RLS
ALTER TABLE user_votes ENABLE ROW LEVEL SECURITY;

-- Create comprehensive policies for user_votes
CREATE POLICY "Allow authenticated users to read all votes" ON user_votes
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY "Allow users to insert their own votes" ON user_votes
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to update their own votes" ON user_votes
    FOR UPDATE TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to delete their own votes" ON user_votes
    FOR DELETE TO authenticated
    USING (auth.uid() = user_id);

-- ==================================================
-- SELLER REVIEWS TABLE FIXES
-- ==================================================

-- Drop existing policies to start fresh
DROP POLICY IF EXISTS "Users can manage their own reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Users can view all reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Allow authenticated users to read reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Allow authenticated users to insert reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Allow authenticated users to update their reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Allow authenticated users to delete their reviews" ON seller_reviews;

-- Enable RLS
ALTER TABLE seller_reviews ENABLE ROW LEVEL SECURITY;

-- Create comprehensive policies for seller_reviews
CREATE POLICY "Allow authenticated users to read all reviews" ON seller_reviews
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY "Allow users to insert their own reviews" ON seller_reviews
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = reviewer_id);

CREATE POLICY "Allow users to update their own reviews" ON seller_reviews
    FOR UPDATE TO authenticated
    USING (auth.uid() = reviewer_id)
    WITH CHECK (auth.uid() = reviewer_id);

CREATE POLICY "Allow users to delete their own reviews" ON seller_reviews
    FOR DELETE TO authenticated
    USING (auth.uid() = reviewer_id);

-- ==================================================
-- GRANT PERMISSIONS (Extra safety)
-- ==================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO authenticated;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_votes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON seller_reviews TO authenticated;

-- ==================================================
-- REFRESH SCHEMA CACHE
-- ==================================================

-- Force PostgREST to reload the schema
NOTIFY pgrst, 'reload schema';

-- Check if tables are accessible
SELECT 'user_votes table accessible' as status, count(*) as row_count FROM user_votes;
SELECT 'seller_reviews table accessible' as status, count(*) as row_count FROM seller_reviews;