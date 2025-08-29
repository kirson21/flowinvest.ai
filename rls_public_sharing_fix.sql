-- =====================================================
-- FIX RLS POLICIES FOR PUBLIC SHARING
-- =====================================================
-- Allow unauthenticated users to view public bots and portfolios

-- Enable RLS for user_bots table if not already enabled
ALTER TABLE public.user_bots ENABLE ROW LEVEL SECURITY;

-- Enable RLS for portfolios table if not already enabled  
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;

-- Add policy for public read access to public bots
DROP POLICY IF EXISTS "Public can read public bots" ON public.user_bots;
CREATE POLICY "Public can read public bots" ON public.user_bots
    FOR SELECT USING (is_public = true AND is_prebuilt = true);

-- Add policy for authenticated users to read public bots
DROP POLICY IF EXISTS "Authenticated users can read public bots" ON public.user_bots;
CREATE POLICY "Authenticated users can read public bots" ON public.user_bots
    FOR SELECT TO authenticated USING (is_public = true AND is_prebuilt = true);

-- Add policy for users to read their own bots
-- Note: Using string comparison to handle potential type mismatches
DROP POLICY IF EXISTS "Users can read own bots" ON public.user_bots;
CREATE POLICY "Users can read own bots" ON public.user_bots
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

-- Add policy for service role (admin access)
DROP POLICY IF EXISTS "Service role full access bots" ON public.user_bots;
CREATE POLICY "Service role full access bots" ON public.user_bots
    FOR ALL TO service_role USING (true);

-- Add policy for public read access to public portfolios/products
DROP POLICY IF EXISTS "Public can read public portfolios" ON public.portfolios;
CREATE POLICY "Public can read public portfolios" ON public.portfolios
    FOR SELECT USING (is_public = true);

-- Add policy for authenticated users to read public portfolios
DROP POLICY IF EXISTS "Authenticated users can read public portfolios" ON public.portfolios;
CREATE POLICY "Authenticated users can read public portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (is_public = true);

-- Add policy for users to read their own portfolios
-- Note: Using string comparison to handle potential type mismatches
DROP POLICY IF EXISTS "Users can read own portfolios" ON public.portfolios;
CREATE POLICY "Users can read own portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

-- Add policy for service role (admin access)
DROP POLICY IF EXISTS "Service role full access portfolios" ON public.portfolios;
CREATE POLICY "Service role full access portfolios" ON public.portfolios
    FOR ALL TO service_role USING (true);

-- Update existing bots to be public if they're prebuilt (so they can be shared)
UPDATE public.user_bots 
SET is_public = true 
WHERE is_prebuilt = true AND (is_public IS NULL OR is_public = false);

-- Update some sample portfolios to be public (for testing sharing)
-- You can manually set specific products to be public in your Supabase dashboard
-- UPDATE public.portfolios 
-- SET is_public = true 
-- WHERE title IN ('SHMYAAAU', 'CHILL BOT', 'ULTRA TEST TOOLS', 'JSON FILE FOR BOT');

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Test public access (these should return data without authentication):

-- Test public bots access
-- SELECT name, description, strategy, slug, is_public, is_prebuilt 
-- FROM public.user_bots 
-- WHERE is_public = true AND is_prebuilt = true;

-- Test public portfolios access  
-- SELECT title, description, price, slug, is_public
-- FROM public.portfolios
-- WHERE is_public = true;