-- =====================================================
-- PUBLIC SHARING RLS POLICIES - SINGLE CLEAN FILE
-- =====================================================
-- Enable public access to shared bots and portfolios for Custom URLs system

-- Enable RLS for tables (if not already enabled)
ALTER TABLE public.user_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;

-- ===========================================
-- USER_BOTS TABLE POLICIES
-- ===========================================

-- Drop existing policies to start clean
DROP POLICY IF EXISTS "Public can read public bots" ON public.user_bots;
DROP POLICY IF EXISTS "Authenticated users can read public bots" ON public.user_bots;
DROP POLICY IF EXISTS "Users can read own bots" ON public.user_bots;
DROP POLICY IF EXISTS "Service role full access bots" ON public.user_bots;

-- Allow public (unauthenticated) users to read public prebuilt bots
CREATE POLICY "Public can read public bots" ON public.user_bots
    FOR SELECT USING (is_public = true AND is_prebuilt = true);

-- Allow authenticated users to read public bots
CREATE POLICY "Authenticated users can read public bots" ON public.user_bots
    FOR SELECT TO authenticated USING (is_public = true AND is_prebuilt = true);

-- Allow users to read their own bots
CREATE POLICY "Users can read own bots" ON public.user_bots
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

-- Allow service role full access (admin)
CREATE POLICY "Service role full access bots" ON public.user_bots
    FOR ALL TO service_role USING (true);

-- ===========================================
-- PORTFOLIOS TABLE POLICIES
-- ===========================================

-- Drop existing policies to start clean
DROP POLICY IF EXISTS "Public can read public portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Authenticated users can read public portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Users can read own portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Service role full access portfolios" ON public.portfolios;

-- Allow public (unauthenticated) users to read public portfolios
CREATE POLICY "Public can read public portfolios" ON public.portfolios
    FOR SELECT USING (is_public = true);

-- Allow authenticated users to read public portfolios
CREATE POLICY "Authenticated users can read public portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (is_public = true);

-- Allow users to read their own portfolios
CREATE POLICY "Users can read own portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

-- Allow service role full access (admin)
CREATE POLICY "Service role full access portfolios" ON public.portfolios
    FOR ALL TO service_role USING (true);

-- ===========================================
-- UPDATE EXISTING DATA FOR SHARING
-- ===========================================

-- Make all prebuilt bots public (so they can be shared)
UPDATE public.user_bots 
SET is_public = true 
WHERE is_prebuilt = true;

-- Optional: Make some sample portfolios public for testing
-- Uncomment the line below to make your existing products shareable:
-- UPDATE public.portfolios SET is_public = true WHERE title IN ('SHMYAAAU', 'CHILL BOT', 'ULTRA TEST TOOLS', 'JSON FILE FOR BOT');

-- ===========================================
-- VERIFICATION QUERIES (uncomment to test)
-- ===========================================

-- Test if public bots are accessible:
-- SELECT name, slug, is_public, is_prebuilt FROM public.user_bots WHERE is_public = true;

-- Test if public portfolios are accessible:
-- SELECT title, slug, is_public FROM public.portfolios WHERE is_public = true;