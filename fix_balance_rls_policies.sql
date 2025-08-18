-- =====================================================
-- Fix RLS Policies for Balance System
-- This script fixes the Row Level Security issues preventing balance operations
-- =====================================================

-- First, let's check current RLS status
SELECT schemaname, tablename, rowsecurity, enablerls 
FROM pg_tables 
WHERE tablename = 'user_accounts' AND schemaname = 'public';

-- Disable RLS temporarily to fix the policies
ALTER TABLE public.user_accounts DISABLE ROW LEVEL SECURITY;

-- Drop all existing policies for user_accounts to start fresh
DROP POLICY IF EXISTS "Users can view their own accounts" ON public.user_accounts;
DROP POLICY IF EXISTS "Users can view their own account" ON public.user_accounts;
DROP POLICY IF EXISTS "Users can insert their own account" ON public.user_accounts;
DROP POLICY IF EXISTS "Users can update their own account" ON public.user_accounts;
DROP POLICY IF EXISTS "Users can manage their own account" ON public.user_accounts;
DROP POLICY IF EXISTS "Service role can manage all accounts" ON public.user_accounts;
DROP POLICY IF EXISTS "Allow service role access" ON public.user_accounts;
DROP POLICY IF EXISTS "Enable all operations for service role" ON public.user_accounts;

-- Grant necessary permissions to authenticated users and service role
GRANT ALL ON public.user_accounts TO authenticated;
GRANT ALL ON public.user_accounts TO service_role;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;

-- Re-enable RLS
ALTER TABLE public.user_accounts ENABLE ROW LEVEL SECURITY;

-- Create comprehensive RLS policies that allow service role full access

-- Policy 1: Service role has full access to all accounts
CREATE POLICY "service_role_full_access" ON public.user_accounts
    FOR ALL 
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policy 2: Users can view their own accounts
CREATE POLICY "users_view_own_account" ON public.user_accounts
    FOR SELECT 
    TO authenticated
    USING (auth.uid() = user_id);

-- Policy 3: Users can insert their own accounts
CREATE POLICY "users_insert_own_account" ON public.user_accounts
    FOR INSERT 
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- Policy 4: Users can update their own accounts
CREATE POLICY "users_update_own_account" ON public.user_accounts
    FOR UPDATE 
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy 5: Allow anonymous access for account creation (needed for new user registration)
CREATE POLICY "allow_account_creation" ON public.user_accounts
    FOR INSERT 
    TO anon
    WITH CHECK (true);

-- Test the policies by running some queries
-- (These will only work if you run them in the Supabase SQL editor with proper context)

-- Check if we can see the policies
SELECT schemaname, tablename, policyname, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'user_accounts' 
ORDER BY policyname;

-- Test query to verify service role can access data
-- SELECT * FROM public.user_accounts WHERE user_id = '81fa7673-821a-4e7c-92a2-7007fa5e21ef';

-- Also fix RLS for transactions table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'transactions') THEN
        -- Disable RLS temporarily
        ALTER TABLE public.transactions DISABLE ROW LEVEL SECURITY;
        
        -- Drop existing policies
        DROP POLICY IF EXISTS "Users can view their own transactions" ON public.transactions;
        DROP POLICY IF EXISTS "Users can insert their own transactions" ON public.transactions;
        DROP POLICY IF EXISTS "Users can update their own transactions" ON public.transactions;
        DROP POLICY IF EXISTS "Service role can manage all transactions" ON public.transactions;
        
        -- Grant permissions
        GRANT ALL ON public.transactions TO authenticated;
        GRANT ALL ON public.transactions TO service_role;
        
        -- Re-enable RLS
        ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;
        
        -- Create new policies
        CREATE POLICY "service_role_transactions_access" ON public.transactions
            FOR ALL 
            TO service_role
            USING (true)
            WITH CHECK (true);
            
        CREATE POLICY "users_view_own_transactions" ON public.transactions
            FOR SELECT 
            TO authenticated
            USING (auth.uid() = user_id OR auth.uid() = seller_id);
            
        CREATE POLICY "users_insert_transactions" ON public.transactions
            FOR INSERT 
            TO authenticated
            WITH CHECK (auth.uid() = user_id);
            
        RAISE NOTICE 'Transactions table RLS policies updated';
    ELSE
        RAISE NOTICE 'Transactions table does not exist, skipping';
    END IF;
END $$;

-- Verify the setup
SELECT 'RLS policies for balance system updated successfully' as status;

-- Show current policies
SELECT 
    schemaname,
    tablename,
    policyname,
    roles,
    cmd as operation,
    CASE 
        WHEN qual IS NOT NULL THEN 'USING: ' || qual
        ELSE 'No USING clause'
    END as using_clause,
    CASE 
        WHEN with_check IS NOT NULL THEN 'WITH CHECK: ' || with_check
        ELSE 'No WITH CHECK clause'
    END as with_check_clause
FROM pg_policies 
WHERE tablename IN ('user_accounts', 'transactions')
AND schemaname = 'public'
ORDER BY tablename, policyname;