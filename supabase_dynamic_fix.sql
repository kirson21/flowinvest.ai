-- STEP 2: DYNAMIC POLICY DROPPER
-- This script will automatically drop ALL policies on user_votes table

DO $$
DECLARE
    policy_record RECORD;
BEGIN
    -- Loop through all policies on user_votes table and drop them
    FOR policy_record IN 
        SELECT policyname 
        FROM pg_policies 
        WHERE tablename = 'user_votes'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON user_votes', policy_record.policyname);
        RAISE NOTICE 'Dropped policy: %', policy_record.policyname;
    END LOOP;
    
    -- Also disable RLS temporarily
    ALTER TABLE user_votes DISABLE ROW LEVEL SECURITY;
    RAISE NOTICE 'Disabled RLS on user_votes';
    
END $$;

-- Now drop foreign key constraint
ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_user_id_fkey;

-- Convert the column type
ALTER TABLE user_votes ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

-- Recreate foreign key constraint
ALTER TABLE user_votes ADD CONSTRAINT user_votes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Re-enable RLS
ALTER TABLE user_votes ENABLE ROW LEVEL SECURITY;

-- Create new clean policies
CREATE POLICY "allow_read_all_votes" ON user_votes FOR SELECT TO authenticated USING (true);
CREATE POLICY "allow_insert_own_votes" ON user_votes FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "allow_update_own_votes" ON user_votes FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "allow_delete_own_votes" ON user_votes FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Force schema reload
NOTIFY pgrst, 'reload schema';

-- Verify the fix
SELECT 'SUCCESS: user_id column type fixed' as status, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_votes' AND column_name = 'user_id';