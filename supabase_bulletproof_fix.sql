-- BULLETPROOF USER VOTES FIX
-- Simple script without complex quotes or procedures

-- Step 1: Drop foreign key constraint if it exists
ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_user_id_fkey;

-- Step 2: Convert user_id column to UUID type
ALTER TABLE user_votes ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

-- Step 3: Recreate foreign key constraint
ALTER TABLE user_votes ADD CONSTRAINT user_votes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Step 4: Force schema reload
NOTIFY pgrst, 'reload schema';

-- Step 5: Quick verification
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_votes' AND column_name = 'user_id';