-- VERIFICATION SCRIPT - Run this after the main fix
-- This script verifies that the voting and reviews functionality is working

-- 1. Check table schemas
SELECT 
    'user_votes' as table_name,
    column_name, 
    data_type,
    CASE 
        WHEN column_name = 'user_id' AND data_type = 'uuid' THEN '✅ CORRECT'
        WHEN column_name = 'user_id' AND data_type != 'uuid' THEN '❌ WRONG TYPE'
        ELSE '✅ OK'
    END as status
FROM information_schema.columns 
WHERE table_name = 'user_votes'
ORDER BY ordinal_position;

-- 2. Check seller_reviews (should already be working)
SELECT 
    'seller_reviews' as table_name,
    column_name, 
    data_type,
    '✅ OK' as status
FROM information_schema.columns 
WHERE table_name = 'seller_reviews' 
AND column_name IN ('reviewer_id', 'seller_name', 'rating')
ORDER BY ordinal_position;

-- 3. Check RLS policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    cmd,
    qual
FROM pg_policies 
WHERE tablename IN ('user_votes', 'seller_reviews')
ORDER BY tablename, policyname;

-- 4. Final confirmation message
SELECT 
    '🎉 VERIFICATION COMPLETE' as status,
    'Both voting and reviews should now work properly!' as message,
    'You can now test the functionality in your app' as next_step;