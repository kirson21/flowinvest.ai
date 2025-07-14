-- Fix Row Level Security policies for Flow Invest application
-- This script updates the RLS policies to properly handle both user auth and service role access

-- First, update the bots table RLS policies to allow both user access and service role access

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own bots and prebuilt bots" ON public.bots;
DROP POLICY IF EXISTS "Users can manage own bots" ON public.bots;
DROP POLICY IF EXISTS "Users can update own bots" ON public.bots;
DROP POLICY IF EXISTS "Users can delete own bots" ON public.bots;

-- Create new comprehensive policies for bots table

-- Allow SELECT for authenticated users (their own bots + prebuilt bots) and service role
CREATE POLICY "Allow bots select access" ON public.bots
    FOR SELECT USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND (user_id = auth.uid() OR is_prebuilt = true))
    );

-- Allow INSERT for authenticated users and service role
CREATE POLICY "Allow bots insert access" ON public.bots
    FOR INSERT WITH CHECK (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND user_id = auth.uid())
    );

-- Allow UPDATE for authenticated users (own bots) and service role
CREATE POLICY "Allow bots update access" ON public.bots
    FOR UPDATE USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND user_id = auth.uid())
    );

-- Allow DELETE for authenticated users (own bots) and service role
CREATE POLICY "Allow bots delete access" ON public.bots
    FOR DELETE USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND user_id = auth.uid())
    );

-- Update users table policies for service role access
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;

CREATE POLICY "Allow users select access" ON public.users
    FOR SELECT USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND id = auth.uid())
    );

CREATE POLICY "Allow users update access" ON public.users
    FOR UPDATE USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND id = auth.uid())
    );

-- Update user_settings policies
DROP POLICY IF EXISTS "Users can view own settings" ON public.user_settings;

CREATE POLICY "Allow user_settings all access" ON public.user_settings
    FOR ALL USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND user_id = auth.uid())
    );

-- Update api_keys policies
DROP POLICY IF EXISTS "Users can manage own API keys" ON public.api_keys;

CREATE POLICY "Allow api_keys all access" ON public.api_keys
    FOR ALL USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND user_id = auth.uid())
    );

-- Update portfolios policies  
DROP POLICY IF EXISTS "Users can manage own portfolios" ON public.portfolios;

CREATE POLICY "Allow portfolios all access" ON public.portfolios
    FOR ALL USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND user_id = auth.uid())
    );

-- Update portfolio_assets policies
DROP POLICY IF EXISTS "Users can manage portfolio assets" ON public.portfolio_assets;

CREATE POLICY "Allow portfolio_assets all access" ON public.portfolio_assets
    FOR ALL USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND 
         user_id = (SELECT user_id FROM public.portfolios WHERE id = portfolio_id))
    );

-- Update bot_trades policies
DROP POLICY IF EXISTS "Users can view own bot trades" ON public.bot_trades;

CREATE POLICY "Allow bot_trades select access" ON public.bot_trades
    FOR SELECT USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND 
         user_id = (SELECT user_id FROM public.bots WHERE id = bot_id))
    );

-- Update user_sessions policies
DROP POLICY IF EXISTS "Users can view own sessions" ON public.user_sessions;

CREATE POLICY "Allow user_sessions all access" ON public.user_sessions
    FOR ALL USING (
        auth.role() = 'service_role' OR 
        (auth.role() = 'authenticated' AND user_id = auth.uid())
    );

-- Grant necessary permissions to service role
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- Also ensure anon and authenticated roles have proper permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- News feed and translations remain public (no RLS needed)
ALTER TABLE public.news_feed DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.translations DISABLE ROW LEVEL SECURITY;

COMMENT ON POLICY "Allow bots select access" ON public.bots IS 
'Allows service role full access and authenticated users to see their own bots plus prebuilt bots';

COMMENT ON POLICY "Allow bots insert access" ON public.bots IS 
'Allows service role and authenticated users to create bots (must own them)';

COMMENT ON POLICY "Allow bots update access" ON public.bots IS 
'Allows service role and authenticated users to update their own bots';

COMMENT ON POLICY "Allow bots delete access" ON public.bots IS 
'Allows service role and authenticated users to delete their own bots';