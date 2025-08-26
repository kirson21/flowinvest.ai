-- =====================================================
-- USER PROFILES TABLE SCHEMA UPDATE
-- =====================================================
-- Add email column and remove phone column from user_profiles table

-- Step 1: Add email column to user_profiles table
ALTER TABLE public.user_profiles 
ADD COLUMN email TEXT;

-- Step 2: Create index on email column for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);

-- Step 3: Update existing user profiles with emails from auth.users
-- This uses the RPC function we created earlier to get emails from auth.users
UPDATE public.user_profiles 
SET email = auth_users.email
FROM (
    SELECT user_id, email 
    FROM auth.users
) AS auth_users
WHERE user_profiles.user_id = auth_users.user_id;

-- Step 4: Remove phone column from user_profiles table
ALTER TABLE public.user_profiles 
DROP COLUMN IF EXISTS phone;

-- Step 5: Add comment to document the email column
COMMENT ON COLUMN public.user_profiles.email IS 'User email address - synced from auth.users for easier data management and Google Sheets integration';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify the changes worked correctly:

-- Check that email column was added and populated
-- SELECT user_id, display_name, email, created_at 
-- FROM public.user_profiles 
-- ORDER BY created_at DESC 
-- LIMIT 5;

-- Verify phone column was removed (this should show column names without 'phone')
-- SELECT column_name 
-- FROM information_schema.columns 
-- WHERE table_name = 'user_profiles' AND table_schema = 'public'
-- ORDER BY column_name;

-- Check that all existing profiles now have emails
-- SELECT 
--     COUNT(*) as total_profiles,
--     COUNT(email) as profiles_with_email,
--     COUNT(*) - COUNT(email) as profiles_without_email
-- FROM public.user_profiles;