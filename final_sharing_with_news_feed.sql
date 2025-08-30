-- =====================================================
-- FINAL SHARING RLS - USING EXISTING TABLES
-- =====================================================
-- Fix RLS for sharing using existing news_feed table

-- ===========================================
-- NEWS_FEED TABLE (YOUR EXISTING TABLE)
-- ===========================================
ALTER TABLE public.news_feed ENABLE ROW LEVEL SECURITY;

-- Clean all existing policies
DROP POLICY IF EXISTS "Enable read access for all users" ON public.news_feed;
DROP POLICY IF EXISTS "Public read all news feed" ON public.news_feed;
DROP POLICY IF EXISTS "Everyone can read news feed" ON public.news_feed;

-- Allow everyone to read news feed (public content)
CREATE POLICY "Public read all news feed" ON public.news_feed
    FOR SELECT USING (true);

CREATE POLICY "Service role all access news feed" ON public.news_feed
    FOR ALL TO service_role USING (true);

-- Add slug column to existing news_feed table
ALTER TABLE public.news_feed 
ADD COLUMN IF NOT EXISTS slug VARCHAR(255);

-- Create index for slug lookups
CREATE INDEX IF NOT EXISTS idx_news_feed_slug ON public.news_feed(slug);

-- Generate slugs for existing news_feed posts using title and id
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
-- USER_BOTS TABLE
-- ===========================================
ALTER TABLE public.user_bots ENABLE ROW LEVEL SECURITY;

-- Clean policies
DROP POLICY IF EXISTS "Public read public prebuilt bots" ON public.user_bots;
DROP POLICY IF EXISTS "Users read own bots" ON public.user_bots;
DROP POLICY IF EXISTS "Service role all access bots" ON public.user_bots;

-- Create policies
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

-- Clean policies
DROP POLICY IF EXISTS "Public read public portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Users read own portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Service role all access portfolios" ON public.portfolios;

-- Create policies
CREATE POLICY "Public read public portfolios" ON public.portfolios
    FOR SELECT USING (is_public = true);

CREATE POLICY "Users read own portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);

CREATE POLICY "Service role all access portfolios" ON public.portfolios
    FOR ALL TO service_role USING (true);

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