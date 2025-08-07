-- Check the actual schema of user_notifications table
-- Run this in Supabase SQL Editor to see what columns exist

SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'user_notifications'
ORDER BY ordinal_position;

-- This will show you exactly what columns exist in the table
-- Common columns might be: id, user_id, title, message, type, is_read, created_at
-- But updated_at might not exist, which is causing the error