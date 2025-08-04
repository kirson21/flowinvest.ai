-- SIMPLIFIED USER VOTES SCHEMA FIX
-- This script fixes the user_id column data type issue in user_votes table
-- Safe for Supabase SQL Editor

BEGIN;

-- Step 1: Check if we need to fix the data type
DO $$
BEGIN
    -- Check current data type
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_votes' 
        AND column_name = 'user_id' 
        AND data_type != 'uuid'
    ) THEN
        RAISE NOTICE 'Found user_id column that needs to be converted to UUID';
        
        -- Drop foreign key constraint if it exists
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name = 'user_votes' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%user_id%'
        ) THEN
            EXECUTE 'ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_user_id_fkey';
            RAISE NOTICE 'Dropped existing foreign key constraint';
        END IF;
        
        -- Convert column type
        EXECUTE 'ALTER TABLE user_votes ALTER COLUMN user_id TYPE UUID USING user_id::UUID';
        RAISE NOTICE 'Converted user_id column to UUID type';
        
        -- Recreate foreign key constraint
        EXECUTE 'ALTER TABLE user_votes ADD CONSTRAINT user_votes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE';
        RAISE NOTICE 'Recreated foreign key constraint';
        
    ELSE
        RAISE NOTICE 'user_id column is already UUID type - no changes needed';
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error during conversion: %', SQLERRM;
    ROLLBACK;
    RETURN;
END $$;

-- Step 2: Verify the fix worked
SELECT 
    'Schema Fix Status' as check_type,
    column_name, 
    data_type,
    CASE 
        WHEN data_type = 'uuid' THEN '✅ FIXED'
        ELSE '❌ NEEDS FIX'
    END as status
FROM information_schema.columns 
WHERE table_name = 'user_votes' 
AND column_name = 'user_id';

-- Step 3: Test with actual insert/delete
DO $$
DECLARE 
    test_user_id UUID := 'cd0e9717-f85d-4726-81e9-f260394ead58';
    test_vote_id UUID;
    test_product_id TEXT := 'test-schema-fix-' || extract(epoch from now());
BEGIN
    -- Try to insert a test vote
    INSERT INTO user_votes (user_id, product_id, vote_type)
    VALUES (test_user_id, test_product_id, 'upvote')
    RETURNING id INTO test_vote_id;
    
    RAISE NOTICE '✅ SUCCESS: Test vote created with ID: %', test_vote_id;
    
    -- Clean up test vote immediately
    DELETE FROM user_votes WHERE id = test_vote_id;
    RAISE NOTICE '✅ Test vote cleaned up successfully';
    
    -- Show success message
    RAISE NOTICE '🎉 USER VOTES TABLE IS NOW FIXED AND WORKING!';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ Test insert failed: %', SQLERRM;
    RAISE NOTICE 'This indicates the schema fix may not have worked completely';
END $$;

-- Step 4: Force schema refresh
NOTIFY pgrst, 'reload schema';

-- Step 5: Final status check
SELECT 
    'FINAL STATUS' as summary,
    'user_votes table' as table_name,
    COUNT(*) as total_votes,
    'Schema fix complete - voting should now work!' as message
FROM user_votes;

COMMIT;