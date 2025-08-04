-- Fix for User Votes Table Data Type Issue
-- This script fixes the critical data type mismatch in user_votes table
-- Root cause: user_id column is character varying but needs to be UUID type

-- ==================================================
-- CRITICAL FIX: USER VOTES TABLE DATA TYPE
-- ==================================================

-- Step 1: Check current data and constraints
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default 
FROM information_schema.columns 
WHERE table_name = 'user_votes' 
AND column_name = 'user_id';

-- Step 2: First, let's see if there's any existing data
SELECT COUNT(*) as current_vote_count FROM user_votes;

-- Step 3: Drop existing foreign key constraints (if any)
-- We need to identify and drop foreign key constraints first
SELECT 
    conname as constraint_name,
    conrelid::regclass as table_name,
    confrelid::regclass as referenced_table
FROM pg_constraint 
WHERE contype = 'f' 
AND conrelid = 'user_votes'::regclass;

-- Drop the foreign key constraint if it exists
-- (Replace 'constraint_name' with actual constraint name from above query)
-- ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_user_id_fkey;

-- Step 4: Convert the column type from CHARACTER VARYING to UUID
-- This will only work if existing data is valid UUID format
ALTER TABLE user_votes 
ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

-- Step 5: Recreate the foreign key constraint to reference auth.users
-- This assumes the referenced table uses UUID for user IDs
ALTER TABLE user_votes 
ADD CONSTRAINT user_votes_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Step 6: Verify the change
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default 
FROM information_schema.columns 
WHERE table_name = 'user_votes' 
AND column_name = 'user_id';

-- Step 7: Test with a sample insert (will be cleaned up)
-- Replace 'cd0e9717-f85d-4726-81e9-f260394ead58' with actual user ID
DO $$
DECLARE 
    test_user_id UUID := 'cd0e9717-f85d-4726-81e9-f260394ead58';
    test_vote_id UUID;
BEGIN
    -- Try to insert a test vote
    INSERT INTO user_votes (user_id, product_id, vote_type)
    VALUES (test_user_id, 'test-product-schema-fix', 'upvote')
    RETURNING id INTO test_vote_id;
    
    RAISE NOTICE 'Test vote created with ID: %', test_vote_id;
    
    -- Clean up test vote
    DELETE FROM user_votes WHERE id = test_vote_id;
    
    RAISE NOTICE 'Test vote cleaned up successfully';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Test failed: %', SQLERRM;
END $$;

-- ==================================================
-- REFRESH SCHEMA AND VERIFY
-- ==================================================

-- Force PostgREST to reload the schema
NOTIFY pgrst, 'reload schema';

-- Final verification
SELECT 'user_votes schema fixed' as status, 
       COUNT(*) as row_count 
FROM user_votes;

COMMENT ON TABLE user_votes IS 'User votes for products - FIXED: user_id now properly typed as UUID';

-- Show the final table structure
\d user_votes;