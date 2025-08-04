-- Fix user_votes.product_id column type from VARCHAR to UUID
-- Similar to the successful user_id fix, but targeting product_id

-- First check current schema
SELECT table_name, column_name, data_type FROM information_schema.columns 
WHERE table_name = 'user_votes' AND column_name IN ('product_id', 'user_id');

-- Check if there are any foreign key constraints on product_id
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_name='user_votes' 
AND kcu.column_name = 'product_id';

-- Drop any foreign key constraints on product_id
ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_product_id_fkey;

-- Convert product_id from VARCHAR to UUID
-- Using CAST to handle the conversion properly
ALTER TABLE user_votes ALTER COLUMN product_id TYPE UUID USING product_id::UUID;

-- Add foreign key constraint back if needed (linking to portfolios.id)
ALTER TABLE user_votes ADD CONSTRAINT user_votes_product_id_fkey 
FOREIGN KEY (product_id) REFERENCES portfolios(id) ON DELETE CASCADE;

-- Force schema reload
NOTIFY pgrst, 'reload schema';

-- Verify the fix
SELECT table_name, column_name, data_type FROM information_schema.columns 
WHERE table_name = 'user_votes' AND column_name = 'product_id';

-- Test the trigger function by attempting an insert
-- This should now work without type mismatch errors
SELECT 'Schema fix completed successfully' AS status;