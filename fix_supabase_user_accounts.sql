-- Fix for Supabase "user_accounts does not exist" error
-- Run this in Supabase Dashboard → SQL Editor

-- Option 1: Create the missing user_accounts table (if it's expected to exist)
CREATE TABLE IF NOT EXISTS public.user_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable RLS on the new table
ALTER TABLE public.user_accounts ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for user_accounts
CREATE POLICY "Users can view own account" ON public.user_accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own account" ON public.user_accounts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own account" ON public.user_accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Option 2: Alternative - Check what's referencing user_accounts
-- Run this to find any triggers/functions that reference the missing table:
-- SELECT * FROM information_schema.routines 
-- WHERE routine_definition ILIKE '%user_accounts%';

-- Option 3: If user_accounts shouldn't exist, we need to find and fix the reference
-- Check for database triggers that might be causing this:
SELECT 
    trigger_name,
    event_object_table,
    trigger_schema,
    action_statement
FROM information_schema.triggers 
WHERE action_statement ILIKE '%user_accounts%';

-- Check for functions that reference user_accounts:
SELECT 
    routine_name,
    routine_schema,
    routine_definition
FROM information_schema.routines 
WHERE routine_definition ILIKE '%user_accounts%' 
  AND routine_type = 'FUNCTION';