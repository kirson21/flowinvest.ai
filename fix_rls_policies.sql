-- Fix RLS policies for user_accounts table
-- This script fixes the Row Level Security issues preventing balance operations

-- Enable RLS on user_accounts if not already enabled
ALTER TABLE public.user_accounts ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to start fresh
DROP POLICY IF EXISTS "Users can view their own account" ON public.user_accounts;
DROP POLICY IF EXISTS "Users can insert their own account" ON public.user_accounts;
DROP POLICY IF EXISTS "Users can update their own account" ON public.user_accounts;
DROP POLICY IF EXISTS "Service role can manage all accounts" ON public.user_accounts;

-- Create comprehensive RLS policies for user_accounts
-- Policy 1: Users can view their own account
CREATE POLICY "Users can view their own account" ON public.user_accounts
    FOR SELECT USING (auth.uid() = user_id);

-- Policy 2: Users can insert their own account
CREATE POLICY "Users can insert their own account" ON public.user_accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy 3: Users can update their own account
CREATE POLICY "Users can update their own account" ON public.user_accounts
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy 4: Service role can manage all accounts (for backend operations)
CREATE POLICY "Service role can manage all accounts" ON public.user_accounts
    FOR ALL USING (
        -- Allow service role key to bypass RLS
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
        OR
        -- Allow super admin to manage all accounts  
        auth.uid() = 'cd0e9717-f85d-4726-81e9-f260394ead58'::uuid
    );

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON public.user_accounts TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Also fix user_notifications table RLS if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_notifications') THEN
        -- Enable RLS
        ALTER TABLE public.user_notifications ENABLE ROW LEVEL SECURITY;
        
        -- Drop existing policies
        DROP POLICY IF EXISTS "Users can view their own notifications" ON public.user_notifications;
        DROP POLICY IF EXISTS "Users can manage their own notifications" ON public.user_notifications;
        DROP POLICY IF EXISTS "Service role can create notifications" ON public.user_notifications;
        
        -- Create new policies
        CREATE POLICY "Users can view their own notifications" ON public.user_notifications
            FOR SELECT USING (auth.uid() = user_id);
            
        CREATE POLICY "Users can manage their own notifications" ON public.user_notifications
            FOR ALL USING (auth.uid() = user_id);
            
        CREATE POLICY "Service role can create notifications" ON public.user_notifications
            FOR INSERT WITH CHECK (
                current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
                OR auth.uid() = 'cd0e9717-f85d-4726-81e9-f260394ead58'::uuid
            );
        
        -- Grant permissions
        GRANT SELECT, INSERT, UPDATE ON public.user_notifications TO authenticated;
    END IF;
END $$;

SELECT 'RLS policies updated successfully' as status;