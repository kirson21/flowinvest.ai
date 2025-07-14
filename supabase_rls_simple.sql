-- SIMPLIFIED Row Level Security Fix for Flow Invest
-- This script only modifies public schema and avoids auth schema

-- Drop existing policies safely
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT policyname, tablename 
        FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename IN ('bots', 'users', 'user_settings', 'api_keys', 'portfolios', 'portfolio_assets', 'bot_trades', 'user_sessions')
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', r.policyname, r.tablename);
    END LOOP;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Continuing after policy cleanup...';
END $$;

-- BOTS table - simplified policies
CREATE POLICY "bots_select" ON public.bots FOR SELECT USING (
    is_prebuilt = true OR user_id = auth.uid()
);

CREATE POLICY "bots_insert" ON public.bots FOR INSERT WITH CHECK (
    user_id = auth.uid()
);

CREATE POLICY "bots_update" ON public.bots FOR UPDATE USING (
    user_id = auth.uid()
);

CREATE POLICY "bots_delete" ON public.bots FOR DELETE USING (
    user_id = auth.uid() AND is_prebuilt = false
);

-- USERS table
CREATE POLICY "users_select" ON public.users FOR SELECT USING (
    id = auth.uid()
);

CREATE POLICY "users_update" ON public.users FOR UPDATE USING (
    id = auth.uid()
);

-- USER_SETTINGS table
CREATE POLICY "user_settings_all" ON public.user_settings FOR ALL USING (
    user_id = auth.uid()
);

-- Only create policies for tables that exist
DO $$ 
BEGIN
    -- API_KEYS
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'api_keys') THEN
        CREATE POLICY "api_keys_all" ON public.api_keys FOR ALL USING (user_id = auth.uid());
    END IF;
    
    -- PORTFOLIOS
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'portfolios') THEN
        CREATE POLICY "portfolios_all" ON public.portfolios FOR ALL USING (user_id = auth.uid());
    END IF;
    
    -- PORTFOLIO_ASSETS
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'portfolio_assets') THEN
        CREATE POLICY "portfolio_assets_all" ON public.portfolio_assets FOR ALL USING (
            EXISTS (SELECT 1 FROM public.portfolios WHERE id = portfolio_id AND user_id = auth.uid())
        );
    END IF;
    
    -- BOT_TRADES
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'bot_trades') THEN
        CREATE POLICY "bot_trades_select" ON public.bot_trades FOR SELECT USING (
            EXISTS (SELECT 1 FROM public.bots WHERE id = bot_id AND user_id = auth.uid())
        );
    END IF;
    
    -- USER_SESSIONS
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_sessions') THEN
        CREATE POLICY "user_sessions_all" ON public.user_sessions FOR ALL USING (user_id = auth.uid());
    END IF;
END $$;

-- Disable RLS for public tables
ALTER TABLE public.news_feed DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.translations DISABLE ROW LEVEL SECURITY;

-- Grant basic permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT SELECT ON public.news_feed TO anon;
GRANT SELECT ON public.translations TO anon;
GRANT SELECT ON public.bots TO anon; -- Filtered by RLS to show only prebuilt

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ Simplified RLS policies applied successfully!';
    RAISE NOTICE '✅ Users can manage their own data';
    RAISE NOTICE '✅ Public content remains accessible';
    RAISE NOTICE '✅ Bot operations should now work';
    RAISE NOTICE '';
END $$;