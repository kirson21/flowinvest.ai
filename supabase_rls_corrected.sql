-- Corrected Row Level Security policies for Flow Invest application
-- This script carefully updates RLS policies with proper column references

-- First, let's check and drop existing policies more carefully
DO $$ 
BEGIN
    -- Drop existing bots policies if they exist
    DROP POLICY IF EXISTS "Users can view own bots and prebuilt bots" ON public.bots;
    DROP POLICY IF EXISTS "Users can manage own bots" ON public.bots;
    DROP POLICY IF EXISTS "Users can update own bots" ON public.bots;
    DROP POLICY IF EXISTS "Users can delete own bots" ON public.bots;
    DROP POLICY IF EXISTS "Allow bots select access" ON public.bots;
    DROP POLICY IF EXISTS "Allow bots insert access" ON public.bots;
    DROP POLICY IF EXISTS "Allow bots update access" ON public.bots;
    DROP POLICY IF EXISTS "Allow bots delete access" ON public.bots;
    
    -- Drop existing users policies if they exist
    DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
    DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
    DROP POLICY IF EXISTS "Allow users select access" ON public.users;
    DROP POLICY IF EXISTS "Allow users update access" ON public.users;
    
    -- Drop user_settings policies if they exist
    DROP POLICY IF EXISTS "Users can view own settings" ON public.user_settings;
    DROP POLICY IF EXISTS "Allow user_settings all access" ON public.user_settings;
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Some policies may not exist yet, continuing...';
END $$;

-- Now create the corrected policies for BOTS table
-- The bots table has: user_id, is_prebuilt columns confirmed

CREATE POLICY "Enable select for users and service" ON public.bots
    FOR SELECT USING (
        -- Service role can see everything
        auth.jwt() ->> 'role' = 'service_role' OR
        -- Authenticated users can see their own bots OR prebuilt bots
        (auth.role() = 'authenticated' AND (
            user_id = auth.uid()::text OR 
            is_prebuilt = true
        ))
    );

CREATE POLICY "Enable insert for users and service" ON public.bots
    FOR INSERT WITH CHECK (
        -- Service role can insert anything
        auth.jwt() ->> 'role' = 'service_role' OR
        -- Authenticated users can only insert bots for themselves
        (auth.role() = 'authenticated' AND user_id = auth.uid()::text)
    );

CREATE POLICY "Enable update for users and service" ON public.bots
    FOR UPDATE USING (
        -- Service role can update everything
        auth.jwt() ->> 'role' = 'service_role' OR
        -- Authenticated users can only update their own bots
        (auth.role() = 'authenticated' AND user_id = auth.uid()::text)
    );

CREATE POLICY "Enable delete for users and service" ON public.bots
    FOR DELETE USING (
        -- Service role can delete everything
        auth.jwt() ->> 'role' = 'service_role' OR
        -- Authenticated users can only delete their own bots (not prebuilt)
        (auth.role() = 'authenticated' AND user_id = auth.uid()::text AND is_prebuilt = false)
    );

-- USERS table policies
-- The users table has: id column confirmed (no user_id, the id IS the user_id)

CREATE POLICY "Enable select for users and service" ON public.users
    FOR SELECT USING (
        -- Service role can see everything
        auth.jwt() ->> 'role' = 'service_role' OR
        -- Authenticated users can see their own profile
        (auth.role() = 'authenticated' AND id = auth.uid()::text)
    );

CREATE POLICY "Enable update for users and service" ON public.users
    FOR UPDATE USING (
        -- Service role can update everything
        auth.jwt() ->> 'role' = 'service_role' OR
        -- Authenticated users can update their own profile
        (auth.role() = 'authenticated' AND id = auth.uid()::text)
    );

-- USER_SETTINGS table policies
-- This table should have user_id referencing users.id

CREATE POLICY "Enable all for user_settings" ON public.user_settings
    FOR ALL USING (
        -- Service role can do everything
        auth.jwt() ->> 'role' = 'service_role' OR
        -- Authenticated users can manage their own settings
        (auth.role() = 'authenticated' AND user_id = auth.uid()::text)
    );

-- API_KEYS table policies (if exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'api_keys') THEN
        CREATE POLICY "Enable all for api_keys" ON public.api_keys
            FOR ALL USING (
                auth.jwt() ->> 'role' = 'service_role' OR
                (auth.role() = 'authenticated' AND user_id = auth.uid()::text)
            );
    END IF;
END $$;

-- PORTFOLIOS table policies (if exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'portfolios') THEN
        CREATE POLICY "Enable all for portfolios" ON public.portfolios
            FOR ALL USING (
                auth.jwt() ->> 'role' = 'service_role' OR
                (auth.role() = 'authenticated' AND user_id = auth.uid()::text)
            );
    END IF;
END $$;

-- PORTFOLIO_ASSETS table policies (if exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'portfolio_assets') THEN
        CREATE POLICY "Enable all for portfolio_assets" ON public.portfolio_assets
            FOR ALL USING (
                auth.jwt() ->> 'role' = 'service_role' OR
                (auth.role() = 'authenticated' AND EXISTS (
                    SELECT 1 FROM public.portfolios 
                    WHERE id = portfolio_id AND user_id = auth.uid()::text
                ))
            );
    END IF;
END $$;

-- BOT_TRADES table policies (if exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'bot_trades') THEN
        CREATE POLICY "Enable select for bot_trades" ON public.bot_trades
            FOR SELECT USING (
                auth.jwt() ->> 'role' = 'service_role' OR
                (auth.role() = 'authenticated' AND EXISTS (
                    SELECT 1 FROM public.bots 
                    WHERE id = bot_id AND user_id = auth.uid()::text
                ))
            );
    END IF;
END $$;

-- USER_SESSIONS table policies (if exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_sessions') THEN
        CREATE POLICY "Enable all for user_sessions" ON public.user_sessions
            FOR ALL USING (
                auth.jwt() ->> 'role' = 'service_role' OR
                (auth.role() = 'authenticated' AND user_id = auth.uid()::text)
            );
    END IF;
END $$;

-- Ensure service role has all necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- Ensure authenticated role has necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Ensure anon role has read access to public data
GRANT SELECT ON public.news_feed TO anon;
GRANT SELECT ON public.translations TO anon;
GRANT SELECT ON public.bots TO anon; -- For viewing prebuilt bots

-- Make sure news_feed and translations tables don't have RLS enabled for public access
ALTER TABLE public.news_feed DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.translations DISABLE ROW LEVEL SECURITY;

-- Add helpful comments
COMMENT ON POLICY "Enable select for users and service" ON public.bots IS 
'Service role: full access. Users: own bots + prebuilt bots only';

COMMENT ON POLICY "Enable insert for users and service" ON public.bots IS 
'Service role: can insert anything. Users: can create bots for themselves only';

COMMENT ON POLICY "Enable update for users and service" ON public.bots IS 
'Service role: can update anything. Users: can update own bots only';

COMMENT ON POLICY "Enable delete for users and service" ON public.bots IS 
'Service role: can delete anything. Users: can delete own non-prebuilt bots only';

-- Print success message
DO $$ 
BEGIN
    RAISE NOTICE 'Row Level Security policies updated successfully!';
    RAISE NOTICE 'Service role has full access to all tables';
    RAISE NOTICE 'Authenticated users have appropriate access to their own data';
    RAISE NOTICE 'Public tables (news_feed, translations) remain publicly accessible';
END $$;