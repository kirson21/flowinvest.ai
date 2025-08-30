-- =====================================================
-- COMPLETE PUBLIC SHARING RLS POLICIES
-- =====================================================
-- Enable public access for Custom URLs sharing system

-- ===========================================
-- USER_BOTS TABLE
-- ===========================================
ALTER TABLE public.user_bots ENABLE ROW LEVEL SECURITY;

-- Clean slate - drop all existing policies
DROP POLICY IF EXISTS "Public can read public bots" ON public.user_bots;
DROP POLICY IF EXISTS "Authenticated users can read public bots" ON public.user_bots;
DROP POLICY IF EXISTS "Users can read own bots" ON public.user_bots;
DROP POLICY IF EXISTS "Service role full access bots" ON public.user_bots;

-- Create new policies
CREATE POLICY "Public read public prebuilt bots" ON public.user_bots
    FOR SELECT USING (is_public = true AND is_prebuilt = true);

CREATE POLICY "Users read own bots" ON public.user_bots
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

CREATE POLICY "Service role all access bots" ON public.user_bots
    FOR ALL TO service_role USING (true);

-- ===========================================
-- PORTFOLIOS TABLE  
-- ===========================================
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;

-- Clean slate - drop all existing policies
DROP POLICY IF EXISTS "Public can read public portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Authenticated users can read public portfolios" ON public.portfolios; 
DROP POLICY IF EXISTS "Users can read own portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Service role full access portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "portfolios_all" ON public.portfolios;
DROP POLICY IF EXISTS "Users can view portfolios" ON public.portfolios;

-- Create new policies
CREATE POLICY "Public read public portfolios" ON public.portfolios
    FOR SELECT USING (is_public = true);

CREATE POLICY "Users read own portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

CREATE POLICY "Service role all access portfolios" ON public.portfolios
    FOR ALL TO service_role USING (true);

-- ===========================================
-- FEED_POSTS TABLE
-- ===========================================
ALTER TABLE public.feed_posts ENABLE ROW LEVEL SECURITY;

-- Clean slate - drop all existing policies
DROP POLICY IF EXISTS "Public can read public feed posts" ON public.feed_posts;
DROP POLICY IF EXISTS "Authenticated users can read public feed posts" ON public.feed_posts;
DROP POLICY IF EXISTS "Service role full access" ON public.feed_posts;

-- Create new policies
CREATE POLICY "Public read public feed posts" ON public.feed_posts
    FOR SELECT USING (is_public = true);

CREATE POLICY "Service role all access feed posts" ON public.feed_posts
    FOR ALL TO service_role USING (true);

-- ===========================================
-- UPDATE DATA FOR SHARING
-- ===========================================

-- Make all prebuilt bots public and shareable
UPDATE public.user_bots 
SET is_public = true 
WHERE is_prebuilt = true;

-- Make all portfolios public for now (you can manually set specific ones later)
UPDATE public.portfolios 
SET is_public = true;

-- ===========================================
-- TEST QUERIES (uncomment to verify)
-- ===========================================

-- SELECT name, slug, is_public, is_prebuilt FROM public.user_bots WHERE is_public = true;
-- SELECT title, slug, is_public FROM public.portfolios WHERE is_public = true;
-- SELECT title, slug, is_public FROM public.feed_posts WHERE is_public = true;