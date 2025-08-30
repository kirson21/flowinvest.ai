-- =====================================================
-- COMPLETE CUSTOM URLS + SHARING + BALANCE SYNC
-- =====================================================
-- Single file with all fixes for f01i.ai Custom URLs system

-- ===========================================
-- 1. CUSTOM URLS DATABASE SCHEMA
-- ===========================================

-- Add uniqueness constraint to display_name
ALTER TABLE public.user_profiles 
ADD CONSTRAINT unique_display_name UNIQUE (display_name);

-- Add slug and is_public columns to user_bots
ALTER TABLE public.user_bots 
ADD COLUMN IF NOT EXISTS slug VARCHAR(255),
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_user_bots_slug ON public.user_bots(slug);

-- Add slug and is_public columns to portfolios  
ALTER TABLE public.portfolios 
ADD COLUMN IF NOT EXISTS slug VARCHAR(255),
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_portfolios_slug ON public.portfolios(slug);

-- Add slug column to existing news_feed table
ALTER TABLE public.news_feed 
ADD COLUMN IF NOT EXISTS slug VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_news_feed_slug ON public.news_feed(slug);

-- Create reserved words table
CREATE TABLE IF NOT EXISTS public.reserved_words (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert reserved words
INSERT INTO public.reserved_words (word, category) VALUES 
('admin', 'system'), ('api', 'system'), ('app', 'system'), ('auth', 'system'), 
('login', 'system'), ('settings', 'system'), ('marketplace', 'system'), 
('bots', 'system'), ('feed', 'system'), ('f01i', 'brand'), ('flowinvest', 'brand')
ON CONFLICT (word) DO NOTHING;

-- Create slug generation function
CREATE OR REPLACE FUNCTION generate_slug(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    IF input_text IS NULL OR LENGTH(TRIM(input_text)) = 0 THEN
        RETURN NULL;
    END IF;
    
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    TRIM(input_text),
                    '[^a-zA-Z0-9\s\-_]', '', 'g'
                ),
                '\s+', '-', 'g'
            ),
            '-+', '-', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql;

-- Generate slugs for existing data
UPDATE public.user_bots 
SET slug = generate_slug(name) || '-' || SUBSTRING(id::TEXT, 1, 8)
WHERE slug IS NULL AND name IS NOT NULL;

UPDATE public.portfolios 
SET slug = generate_slug(title) || '-' || SUBSTRING(id::TEXT, 1, 8)
WHERE slug IS NULL AND title IS NOT NULL;

UPDATE public.news_feed 
SET slug = generate_slug(title) || '-' || SUBSTRING(id::TEXT, 1, 8)
WHERE slug IS NULL AND title IS NOT NULL;

-- ===========================================
-- 2. RLS POLICIES FOR PUBLIC SHARING
-- ===========================================

-- USER_BOTS
ALTER TABLE public.user_bots ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read public prebuilt bots" ON public.user_bots;
DROP POLICY IF EXISTS "Users read own bots" ON public.user_bots;
DROP POLICY IF EXISTS "Service role all access bots" ON public.user_bots;

CREATE POLICY "Public read public prebuilt bots" ON public.user_bots
    FOR SELECT USING (is_public = true AND is_prebuilt = true);
CREATE POLICY "Users read own bots" ON public.user_bots
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);
CREATE POLICY "Service role all access bots" ON public.user_bots
    FOR ALL TO service_role USING (true);

-- PORTFOLIOS
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read public portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Users read own portfolios" ON public.portfolios;
DROP POLICY IF EXISTS "Service role all access portfolios" ON public.portfolios;

CREATE POLICY "Public read public portfolios" ON public.portfolios
    FOR SELECT USING (is_public = true);
CREATE POLICY "Users read own portfolios" ON public.portfolios
    FOR SELECT TO authenticated USING (auth.uid()::text = user_id::text);
CREATE POLICY "Service role all access portfolios" ON public.portfolios
    FOR ALL TO service_role USING (true);

-- NEWS_FEED (your existing table)
ALTER TABLE public.news_feed ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read all news feed" ON public.news_feed;
DROP POLICY IF EXISTS "Service role all access news feed" ON public.news_feed;

CREATE POLICY "Public read all news feed" ON public.news_feed
    FOR SELECT USING (true);
CREATE POLICY "Service role all access news feed" ON public.news_feed
    FOR ALL TO service_role USING (true);

-- ===========================================
-- 3. COMPANY BALANCE SYNC FIX
-- ===========================================

-- Function to calculate total user funds
CREATE OR REPLACE FUNCTION calculate_total_user_funds()
RETURNS DECIMAL(12,2) AS $$
DECLARE
    total_funds DECIMAL(12,2) := 0;
BEGIN
    SELECT COALESCE(SUM(balance), 0)
    INTO total_funds
    FROM public.user_accounts
    WHERE balance > 0;
    
    RETURN total_funds;
END;
$$ LANGUAGE plpgsql;

-- Function to sync company balance
CREATE OR REPLACE FUNCTION sync_company_balance_user_funds()
RETURNS JSON AS $$
DECLARE
    current_user_funds DECIMAL(12,2);
    result JSON;
BEGIN
    current_user_funds := calculate_total_user_funds();
    
    UPDATE public.company_balance
    SET 
        user_funds = current_user_funds::TEXT,
        last_updated = NOW(),
        updated_at = NOW()
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    result := json_build_object(
        'success', true,
        'total_user_funds', current_user_funds,
        'synced_at', NOW()
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-sync
CREATE OR REPLACE FUNCTION trigger_sync_user_funds()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM sync_company_balance_user_funds();
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sync_user_funds_trigger ON public.user_accounts;
CREATE TRIGGER sync_user_funds_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.user_accounts
    FOR EACH ROW
    EXECUTE FUNCTION trigger_sync_user_funds();

-- ===========================================
-- 4. UPDATE DATA FOR SHARING
-- ===========================================

-- Make prebuilt bots public
UPDATE public.user_bots 
SET is_public = true 
WHERE is_prebuilt = true;

-- Make all portfolios public (you can adjust this later)
UPDATE public.portfolios 
SET is_public = true;

-- ===========================================
-- 5. EXECUTE SYNC IMMEDIATELY
-- ===========================================

-- Sync user funds right now
SELECT sync_company_balance_user_funds();

-- ===========================================
-- VERIFICATION (uncomment to test)
-- ===========================================
-- SELECT SUM(balance) as actual_user_funds FROM public.user_accounts WHERE balance > 0;
-- SELECT user_funds as company_balance_user_funds FROM public.company_balance;