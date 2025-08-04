-- STEP 1: Find all existing policies on user_votes table
-- Run this first to see what policies exist

SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'user_votes'
ORDER BY policyname;