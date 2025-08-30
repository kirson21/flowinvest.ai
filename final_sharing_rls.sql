-- =====================================================
-- FINAL RLS POLICIES FOR PUBLIC SHARING
-- =====================================================
-- Using existing tables: user_bots, portfolios, news_feed

-- ===========================================
-- USER_BOTS TABLE
-- ===========================================
ALTER TABLE public.user_bots ENABLE ROW LEVEL SECURITY;

-- Clean existing policies
DROP POLICY IF EXISTS "Public read public prebuilt bots" ON public.user_bots;
DROP POLICY IF EXISTS "Users read own bots" ON public.user_bots;
DROP POLICY IF EXISTS "Service role all access bots" ON public.user_bots;

-- Create clean policies
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

-- Clean existing policies
DROP POLICY IF EXISTS "Public read public portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Users read own portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Service role all access portfolios" ON public.portfolios;

-- Create clean policies
CREATE POLICY "Public read public portfolios" ON public.portfolios
    FOR SELECT USING (is_public = true);

CREATE POLICY "Users read own portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

CREATE POLICY "Service role all access portfolios" ON public.portfolios
    FOR ALL TO service_role USING (true);

-- ===========================================
-- NEWS_FEED TABLE (EXISTING TABLE)
-- ===========================================
ALTER TABLE public.news_feed ENABLE ROW LEVEL SECURITY;

-- Clean existing policies
DROP POLICY IF EXISTS "Public read all news feed" ON public.news_feed;
DROP POLICY IF EXISTS "Everyone can read news feed" ON public.news_feed;

-- Allow everyone to read news feed (it's public content)
CREATE POLICY "Public read all news feed" ON public.news_feed
    FOR SELECT USING (true);

CREATE POLICY "Service role all access news feed" ON public.news_feed
    FOR ALL TO service_role USING (true);

-- ===========================================
-- ADD SLUG COLUMN TO NEWS_FEED
-- ===========================================

-- Add slug column to news_feed table if it doesn't exist
ALTER TABLE public.news_feed 
ADD COLUMN IF NOT EXISTS slug VARCHAR(255);

-- Create index for slug lookups
CREATE INDEX IF NOT EXISTS idx_news_feed_slug ON public.news_feed(slug);

-- Generate slugs for existing news_feed posts
UPDATE public.news_feed 
SET slug = LOWER(
    REGEXP_REPLACE(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                TRIM(title),
                '[^a-zA-Z0-9\s\-_]', '', 'g'
            ),
            '\s+', '-', 'g'
        ),
        '-+', '-', 'g'
    )
) || '-' || SUBSTRING(id::TEXT, 1, 8)
WHERE slug IS NULL AND title IS NOT NULL;

-- ===========================================
-- UPDATE DATA FOR SHARING
-- ===========================================

-- Make all prebuilt bots public
UPDATE public.user_bots 
SET is_public = true 
WHERE is_prebuilt = true;

-- Make all portfolios public for testing
UPDATE public.portfolios 
SET is_public = true;

-- ===========================================
-- VERIFICATION QUERIES
-- ===========================================
-- SELECT name, slug, is_public, is_prebuilt FROM public.user_bots WHERE is_public = true LIMIT 5;
-- SELECT title, slug, is_public FROM public.portfolios WHERE is_public = true LIMIT 5;
-- SELECT title, slug FROM public.news_feed WHERE slug IS NOT NULL LIMIT 5;