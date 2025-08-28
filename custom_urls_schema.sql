-- =====================================================
-- CUSTOM URLS SYSTEM - DATABASE SCHEMA UPDATES
-- =====================================================
-- Add URL routing support for users, bots, marketplace products, and feed posts

-- Step 1: Add uniqueness constraint to display_name in user_profiles
-- This ensures each user has a unique displayName for their profile URL
ALTER TABLE public.user_profiles 
ADD CONSTRAINT unique_display_name UNIQUE (display_name);

-- Step 2: Add slug and is_public columns to user_bots table
ALTER TABLE public.user_bots 
ADD COLUMN IF NOT EXISTS slug VARCHAR(255),
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT false;

-- Create index for slug lookups
CREATE INDEX IF NOT EXISTS idx_user_bots_slug ON public.user_bots(slug);
CREATE INDEX IF NOT EXISTS idx_user_bots_public ON public.user_bots(is_public);

-- Step 3: Add slug and is_public columns to portfolios table (marketplace products)
ALTER TABLE public.portfolios 
ADD COLUMN IF NOT EXISTS slug VARCHAR(255),
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT false;

-- Create index for slug lookups
CREATE INDEX IF NOT EXISTS idx_portfolios_slug ON public.portfolios(slug);
CREATE INDEX IF NOT EXISTS idx_portfolios_public ON public.portfolios(is_public);

-- Step 4: Create feed_posts table for shareable permalinks
-- (AI Feed posts are currently from external API, we need to store them for permalinks)
CREATE TABLE IF NOT EXISTS public.feed_posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    external_id VARCHAR(255), -- Original ID from external API
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    sentiment VARCHAR(50),
    source VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    is_translated BOOLEAN DEFAULT false,
    slug VARCHAR(255) UNIQUE,
    is_public BOOLEAN DEFAULT true, -- Feed posts are public by default
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for feed_posts
CREATE INDEX IF NOT EXISTS idx_feed_posts_slug ON public.feed_posts(slug);
CREATE INDEX IF NOT EXISTS idx_feed_posts_public ON public.feed_posts(is_public);
CREATE INDEX IF NOT EXISTS idx_feed_posts_published_at ON public.feed_posts(published_at);
CREATE INDEX IF NOT EXISTS idx_feed_posts_source ON public.feed_posts(source);

-- Step 5: Create reserved_words table for URL validation
CREATE TABLE IF NOT EXISTS public.reserved_words (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50), -- 'system', 'profanity', 'brand', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert reserved words
INSERT INTO public.reserved_words (word, category) VALUES 
-- System/App reserved words
('admin', 'system'),
('api', 'system'),
('app', 'system'),
('auth', 'system'),
('login', 'system'),
('logout', 'system'),
('signup', 'system'),
('register', 'system'),
('dashboard', 'system'),
('settings', 'system'),
('profile', 'system'),
('user', 'system'),
('users', 'system'),
-- Brand reserved words
('f01i', 'brand'),
('foli', 'brand'),
('f01i.ai', 'brand'),
('f01i.app', 'brand'),
('flowinvest', 'brand'),
('flow-invest', 'brand'),
-- Core app sections
('marketplace', 'system'),
('bots', 'system'),
('feed', 'system'),
('portfolios', 'system'),
('trading', 'system'),
('crypto', 'system'),
('payments', 'system'),
('subscriptions', 'system'),
-- Technical reserved words
('www', 'system'),
('mail', 'system'),
('email', 'system'),
('support', 'system'),
('help', 'system'),
('docs', 'system'),
('blog', 'system'),
('news', 'system'),
('about', 'system'),
('contact', 'system'),
('privacy', 'system'),
('terms', 'system'),
('legal', 'system'),
-- Common profanity (basic list - can be expanded)
('damn', 'profanity'),
('hell', 'profanity'),
('shit', 'profanity'),
('fuck', 'profanity'),
('ass', 'profanity'),
('bitch', 'profanity')
ON CONFLICT (word) DO NOTHING;

-- Step 6: Create slug generation function
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
                    '[^a-zA-Z0-9\s\-_]', '', 'g'  -- Remove special chars except spaces, hyphens, underscores
                ),
                '\s+', '-', 'g'  -- Replace spaces with hyphens
            ),
            '-+', '-', 'g'  -- Replace multiple consecutive hyphens with single hyphen
        )
    );
END;
$$ LANGUAGE plpgsql;

-- Step 7: Create function to check if word is reserved
CREATE OR REPLACE FUNCTION is_reserved_word(word_to_check TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    IF word_to_check IS NULL THEN
        RETURN false;
    END IF;
    
    RETURN EXISTS (
        SELECT 1 FROM public.reserved_words 
        WHERE LOWER(word) = LOWER(word_to_check)
    );
END;
$$ LANGUAGE plpgsql;

-- Step 8: Create function to validate display_name/slug
CREATE OR REPLACE FUNCTION validate_url_slug(slug_to_check TEXT, exclude_user_id UUID DEFAULT NULL)
RETURNS JSON AS $$
DECLARE
    result JSON;
    is_valid BOOLEAN := true;
    error_message TEXT := '';
BEGIN
    -- Check if slug is null or empty
    IF slug_to_check IS NULL OR LENGTH(TRIM(slug_to_check)) = 0 THEN
        RETURN json_build_object(
            'valid', false,
            'error', 'Slug cannot be empty'
        );
    END IF;
    
    -- Check if it's a reserved word
    IF is_reserved_word(slug_to_check) THEN
        RETURN json_build_object(
            'valid', false,
            'error', 'This name is reserved and cannot be used'
        );
    END IF;
    
    -- Check if display_name is already taken by another user
    IF EXISTS (
        SELECT 1 FROM public.user_profiles 
        WHERE LOWER(display_name) = LOWER(slug_to_check)
        AND (exclude_user_id IS NULL OR user_id != exclude_user_id)
    ) THEN
        RETURN json_build_object(
            'valid', false,
            'error', 'This display name is already taken'
        );
    END IF;
    
    -- Check format (alphanumeric, hyphens, underscores only)
    IF NOT slug_to_check ~ '^[a-zA-Z0-9_-]+$' THEN
        RETURN json_build_object(
            'valid', false,
            'error', 'Only letters, numbers, hyphens, and underscores are allowed'
        );
    END IF;
    
    -- Check length (3-50 characters)
    IF LENGTH(slug_to_check) < 3 OR LENGTH(slug_to_check) > 50 THEN
        RETURN json_build_object(
            'valid', false,
            'error', 'Name must be between 3 and 50 characters'
        );
    END IF;
    
    RETURN json_build_object('valid', true);
END;
$$ LANGUAGE plpgsql;

-- Step 9: Auto-generate slugs for existing user_bots (based on bot name)
UPDATE public.user_bots 
SET slug = generate_slug(name)
WHERE slug IS NULL AND name IS NOT NULL;

-- Handle duplicate slugs for user_bots by appending user_id suffix
UPDATE public.user_bots 
SET slug = generate_slug(name) || '-' || SUBSTRING(user_id::TEXT, 1, 8)
WHERE id IN (
    SELECT id FROM (
        SELECT id, slug, 
        ROW_NUMBER() OVER (PARTITION BY slug ORDER BY created_at) as rn
        FROM public.user_bots 
        WHERE slug IS NOT NULL
    ) t WHERE rn > 1
);

-- Step 10: Auto-generate slugs for existing portfolios (based on title)
UPDATE public.portfolios 
SET slug = generate_slug(title)
WHERE slug IS NULL AND title IS NOT NULL;

-- Handle duplicate slugs for portfolios by appending ID suffix
UPDATE public.portfolios 
SET slug = generate_slug(title) || '-' || SUBSTRING(id::TEXT, 1, 8)
WHERE id IN (
    SELECT id FROM (
        SELECT id, slug, 
        ROW_NUMBER() OVER (PARTITION BY slug ORDER BY created_at) as rn
        FROM public.portfolios 
        WHERE slug IS NOT NULL
    ) t WHERE rn > 1
);

-- Step 11: Add updated_at triggers for new tables
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to feed_posts table
DROP TRIGGER IF EXISTS update_feed_posts_updated_at ON public.feed_posts;
CREATE TRIGGER update_feed_posts_updated_at
    BEFORE UPDATE ON public.feed_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Step 12: Add Row Level Security (RLS) policies for new tables

-- Enable RLS for feed_posts
ALTER TABLE public.feed_posts ENABLE ROW LEVEL SECURITY;

-- Policy: Public can read published public feed posts
CREATE POLICY "Public can read public feed posts" ON public.feed_posts
    FOR SELECT USING (is_public = true);

-- Policy: Authenticated users can read all public feed posts
CREATE POLICY "Authenticated users can read public feed posts" ON public.feed_posts
    FOR SELECT TO authenticated USING (is_public = true);

-- Policy: Service role can do everything (for admin operations)
CREATE POLICY "Service role full access" ON public.feed_posts
    FOR ALL TO service_role USING (true);

-- Enable RLS for reserved_words (read-only for most users)
ALTER TABLE public.reserved_words ENABLE ROW LEVEL SECURITY;

-- Policy: Everyone can read reserved words (needed for validation)
CREATE POLICY "Public can read reserved words" ON public.reserved_words
    FOR SELECT USING (true);

-- Policy: Only service role can modify reserved words
CREATE POLICY "Service role can modify reserved words" ON public.reserved_words
    FOR ALL TO service_role USING (true);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify the schema changes worked:

-- Check user_profiles display_name uniqueness
-- SELECT display_name, COUNT(*) 
-- FROM public.user_profiles 
-- GROUP BY display_name 
-- HAVING COUNT(*) > 1;

-- Check generated slugs for user_bots
-- SELECT name, slug, is_public 
-- FROM public.user_bots 
-- WHERE slug IS NOT NULL 
-- LIMIT 10;

-- Check generated slugs for portfolios
-- SELECT title, slug, is_public 
-- FROM public.portfolios 
-- WHERE slug IS NOT NULL 
-- LIMIT 10;

-- Test reserved word validation
-- SELECT validate_url_slug('admin');
-- SELECT validate_url_slug('valid-username');

-- Test slug generation
-- SELECT generate_slug('My Awesome Bot Name!!!');
-- SELECT generate_slug('Portfolio: High-Yield Strategy (2025)');