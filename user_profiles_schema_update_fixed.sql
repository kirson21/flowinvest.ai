-- =====================================================
-- USER PROFILES TABLE SCHEMA UPDATE (CORRECTED VERSION)
-- =====================================================
-- Add email column and remove phone column from user_profiles table

-- Step 1: Add email column to user_profiles table
ALTER TABLE public.user_profiles 
ADD COLUMN email TEXT;

-- Step 2: Create index on email column for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);

-- Step 3: Remove phone column from user_profiles table
ALTER TABLE public.user_profiles 
DROP COLUMN IF EXISTS phone;

-- Step 4: Create a function to populate emails from auth.users using our working RPC
CREATE OR REPLACE FUNCTION populate_user_profiles_emails()
RETURNS INTEGER AS $$
DECLARE
    user_record RECORD;
    update_count INTEGER := 0;
BEGIN
    -- Use our working RPC function to get emails from auth.users
    FOR user_record IN 
        SELECT user_id, email 
        FROM get_users_emails_simple()
    LOOP
        -- Update the corresponding user_profile with the email
        UPDATE public.user_profiles 
        SET email = user_record.email,
            updated_at = NOW()
        WHERE user_id = user_record.user_id;
        
        IF FOUND THEN
            update_count := update_count + 1;
        END IF;
    END LOOP;
    
    RETURN update_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 5: Execute the population function
SELECT populate_user_profiles_emails() as updated_profiles_count;

-- Step 6: Add comment to document the email column
COMMENT ON COLUMN public.user_profiles.email IS 'User email address - synced from auth.users for easier data management and Google Sheets integration';

-- Step 7: Grant permissions
GRANT EXECUTE ON FUNCTION populate_user_profiles_emails() TO service_role;

-- =====================================================
-- VERIFICATION QUERIES (run after the above)
-- =====================================================
-- Check that email column was added and populated
SELECT user_id, display_name, email, created_at 
FROM public.user_profiles 
WHERE email IS NOT NULL
ORDER BY created_at DESC 
LIMIT 5;

-- Verify phone column was removed
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'user_profiles' AND table_schema = 'public'
ORDER BY column_name;

-- Check email population statistics
SELECT 
    COUNT(*) as total_profiles,
    COUNT(email) as profiles_with_email,
    COUNT(*) - COUNT(email) as profiles_without_email
FROM public.user_profiles;