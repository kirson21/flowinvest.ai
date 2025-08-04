-- FINAL FIX: Drop policies, fix column type, recreate policies
-- This handles the RLS policy dependency issue

-- Step 1: Drop ALL existing RLS policies that reference user_id
DROP POLICY IF EXISTS "Users can view own votes" ON user_votes;
DROP POLICY IF EXISTS "Users can manage their own votes" ON user_votes;
DROP POLICY IF EXISTS "Users can view all votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to read votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to insert votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to update their votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to delete their votes" ON user_votes;
DROP POLICY IF EXISTS "Allow users to insert their own votes" ON user_votes;
DROP POLICY IF EXISTS "Allow users to update their own votes" ON user_votes;
DROP POLICY IF EXISTS "Allow users to delete their own votes" ON user_votes;
DROP POLICY IF EXISTS "Allow authenticated users to read all votes" ON user_votes;

-- Step 2: Drop foreign key constraint if it exists
ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_user_id_fkey;

-- Step 3: Now we can safely convert the column type
ALTER TABLE user_votes ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

-- Step 4: Recreate foreign key constraint
ALTER TABLE user_votes ADD CONSTRAINT user_votes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Step 5: Recreate RLS policies with correct UUID handling
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

-- Step 6: Force schema reload
NOTIFY pgrst, 'reload schema';

-- Step 7: Verification
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_votes' AND column_name = 'user_id';