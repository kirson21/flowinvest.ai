-- =====================================================
-- COMPLETE f01i.ai DATABASE SCHEMA WITH WITHDRAWALS
-- =====================================================
-- Single file with all necessary fixes including:
-- 1. Custom URLs system
-- 2. Public sharing functionality
-- 3. Balance synchronization
-- 4. NowPayments withdrawal system

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
DECLARE
    slug_text TEXT;
    counter INTEGER := 0;
    unique_slug TEXT;
    exists_check INTEGER;
BEGIN
    -- Basic slug generation (lowercase, replace spaces/special chars with hyphens)
    slug_text := lower(trim(input_text));
    slug_text := regexp_replace(slug_text, '[^a-z0-9\s-]', '', 'g');
    slug_text := regexp_replace(slug_text, '\s+', '-', 'g');
    slug_text := regexp_replace(slug_text, '-+', '-', 'g');
    slug_text := trim(slug_text, '-');
    
    -- Ensure minimum length
    IF length(slug_text) < 3 THEN
        slug_text := slug_text || '-' || extract(epoch from now())::text;
    END IF;
    
    -- Check uniqueness across all tables that use slugs
    unique_slug := slug_text;
    LOOP
        -- Check in user_profiles (display_name field)
        SELECT COUNT(*) INTO exists_check FROM public.user_profiles WHERE display_name = unique_slug;
        IF exists_check > 0 THEN
            counter := counter + 1;
            unique_slug := slug_text || '-' || counter::text;
            CONTINUE;
        END IF;
        
        -- Check in user_bots
        SELECT COUNT(*) INTO exists_check FROM public.user_bots WHERE slug = unique_slug;
        IF exists_check > 0 THEN
            counter := counter + 1;
            unique_slug := slug_text || '-' || counter::text;
            CONTINUE;
        END IF;
        
        -- Check in portfolios
        SELECT COUNT(*) INTO exists_check FROM public.portfolios WHERE slug = unique_slug;
        IF exists_check > 0 THEN
            counter := counter + 1;
            unique_slug := slug_text || '-' || counter::text;
            CONTINUE;
        END IF;
        
        -- Check in news_feed
        SELECT COUNT(*) INTO exists_check FROM public.news_feed WHERE slug = unique_slug;
        IF exists_check > 0 THEN
            counter := counter + 1;
            unique_slug := slug_text || '-' || counter::text;
            CONTINUE;
        END IF;
        
        -- Check in reserved words
        SELECT COUNT(*) INTO exists_check FROM public.reserved_words WHERE word = unique_slug;
        IF exists_check > 0 THEN
            counter := counter + 1;
            unique_slug := slug_text || '-' || counter::text;
            CONTINUE;
        END IF;
        
        -- If we get here, the slug is unique
        EXIT;
    END LOOP;
    
    RETURN unique_slug;
END;
$$ LANGUAGE plpgsql;

-- URL validation function
CREATE OR REPLACE FUNCTION validate_url_slug(slug_text TEXT)
RETURNS JSONB AS $$
DECLARE
    reserved_count INTEGER;
    exists_count INTEGER;
BEGIN
    -- Check if reserved
    SELECT COUNT(*) INTO reserved_count FROM public.reserved_words WHERE word = lower(slug_text);
    IF reserved_count > 0 THEN
        RETURN jsonb_build_object('valid', false, 'error', 'reserved_word');
    END IF;
    
    -- Check format (alphanumeric, hyphens, underscores only)
    IF NOT slug_text ~ '^[a-zA-Z0-9_-]+$' THEN
        RETURN jsonb_build_object('valid', false, 'error', 'invalid_format');
    END IF;
    
    -- Check length
    IF length(slug_text) < 3 OR length(slug_text) > 50 THEN
        RETURN jsonb_build_object('valid', false, 'error', 'invalid_length');
    END IF;
    
    -- Check uniqueness across all slug fields
    SELECT COUNT(*) INTO exists_count FROM (
        SELECT display_name FROM public.user_profiles WHERE display_name = slug_text
        UNION ALL
        SELECT slug FROM public.user_bots WHERE slug = slug_text
        UNION ALL  
        SELECT slug FROM public.portfolios WHERE slug = slug_text
        UNION ALL
        SELECT slug FROM public.news_feed WHERE slug = slug_text
    ) combined;
    
    IF exists_count > 0 THEN
        RETURN jsonb_build_object('valid', false, 'error', 'already_exists');
    END IF;
    
    RETURN jsonb_build_object('valid', true);
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- 2. RLS POLICIES FOR PUBLIC SHARING
-- ===========================================

-- Enable RLS on required tables
ALTER TABLE public.user_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.news_feed ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Public access policies for user_bots
CREATE POLICY "Public can view public bots" ON public.user_bots
    FOR SELECT USING (is_public = true);

-- Public access policies for portfolios (marketplace products)
CREATE POLICY "Public can view public portfolios" ON public.portfolios
    FOR SELECT USING (is_public = true);

-- Public access policies for news_feed (feed posts)
CREATE POLICY "Public can view public feed posts" ON public.news_feed
    FOR SELECT USING (true);

-- Public access policies for user_profiles
CREATE POLICY "Public can view user profiles" ON public.user_profiles
    FOR SELECT USING (true);

-- User access policies (for authenticated users to manage their own content)
CREATE POLICY "Users can manage their bots" ON public.user_bots
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can manage their portfolios" ON public.portfolios
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY "Authenticated users can view all bots" ON public.user_bots
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can view all portfolios" ON public.portfolios
    FOR SELECT USING (auth.role() = 'authenticated');

-- Service role access
CREATE POLICY "Service role can access user_bots" ON public.user_bots
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access portfolios" ON public.portfolios
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access news_feed" ON public.news_feed
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access user_profiles" ON public.user_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- ===========================================
-- 3. COMPANY BALANCE SYNC FIX
-- ===========================================

-- Fix the company balance synchronization function
CREATE OR REPLACE FUNCTION sync_company_balance_user_funds()
RETURNS TRIGGER AS $$
BEGIN
    -- Update company_balance.user_funds with the sum of all user balances
    UPDATE public.company_balance 
    SET user_funds = (
        SELECT COALESCE(SUM(balance::NUMERIC), 0)
        FROM public.user_accounts 
        WHERE balance > 0
    ),
    last_updated = NOW()
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to sync company balance when user_accounts changes
DROP TRIGGER IF EXISTS sync_company_balance_trigger ON public.user_accounts;
CREATE TRIGGER sync_company_balance_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.user_accounts
    FOR EACH ROW EXECUTE FUNCTION sync_company_balance_user_funds();

-- ===========================================
-- 4. NOWPAYMENTS WITHDRAWAL SYSTEM
-- ===========================================

-- Create nowpayments_withdrawals table
CREATE TABLE IF NOT EXISTS public.nowpayments_withdrawals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Withdrawal request details
    withdrawal_id VARCHAR(255), -- NowPayments batch withdrawal ID
    recipient_address VARCHAR(255) NOT NULL,
    currency VARCHAR(50) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL CHECK (amount > 0),
    description TEXT,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'created', 'verifying', 'verified', 
        'processing', 'sent', 'completed', 'failed', 'cancelled'
    )),
    
    -- NowPayments specific fields
    batch_withdrawal_id VARCHAR(255), -- For 2FA verification
    transaction_hash VARCHAR(255), -- Blockchain transaction hash when sent
    network_fee DECIMAL(20, 8) DEFAULT 0,
    actual_amount_sent DECIMAL(20, 8), -- Amount actually sent (after fees)
    
    -- 2FA verification
    verification_required BOOLEAN DEFAULT true,
    verification_code VARCHAR(10), -- 2FA code
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Response data from NowPayments API
    api_response JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_user_id ON public.nowpayments_withdrawals(user_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_status ON public.nowpayments_withdrawals(status);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_created_at ON public.nowpayments_withdrawals(created_at);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_nowpayments_withdrawals_updated_at BEFORE UPDATE ON public.nowpayments_withdrawals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS policies for withdrawals
ALTER TABLE public.nowpayments_withdrawals ENABLE ROW LEVEL SECURITY;

-- Users can only see their own withdrawals
CREATE POLICY "Users can view own withdrawals" ON public.nowpayments_withdrawals
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Users can only create withdrawals for themselves
CREATE POLICY "Users can create own withdrawals" ON public.nowpayments_withdrawals
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- Users can update their own withdrawals
CREATE POLICY "Users can update own withdrawals" ON public.nowpayments_withdrawals
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Service role can access all withdrawals
CREATE POLICY "Service role can access all withdrawals" ON public.nowpayments_withdrawals
    FOR ALL USING (auth.role() = 'service_role');

-- ===========================================
-- 5. WITHDRAWAL FUNCTIONS
-- ===========================================

-- Function to create withdrawal request
CREATE OR REPLACE FUNCTION create_withdrawal_request(
    p_user_id UUID,
    p_recipient_address VARCHAR(255),
    p_currency VARCHAR(50),
    p_amount DECIMAL(20, 8),
    p_description TEXT DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    user_balance DECIMAL(20, 2);
    withdrawal_record RECORD;
    result JSONB;
BEGIN
    -- Check user balance
    SELECT balance INTO user_balance
    FROM public.user_accounts
    WHERE user_id = p_user_id;
    
    IF NOT FOUND OR user_balance IS NULL THEN
        user_balance := 0;
    END IF;
    
    -- Check if user has sufficient balance
    IF user_balance < p_amount THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'insufficient_balance',
            'message', 'Insufficient balance for withdrawal',
            'current_balance', user_balance,
            'requested_amount', p_amount
        );
    END IF;
    
    -- Create withdrawal record
    INSERT INTO public.nowpayments_withdrawals (
        user_id,
        recipient_address,
        currency,
        amount,
        description,
        status,
        verification_expires_at
    )
    VALUES (
        p_user_id,
        p_recipient_address,
        p_currency,
        p_amount,
        p_description,
        'pending',
        NOW() + INTERVAL '1 hour'
    )
    RETURNING * INTO withdrawal_record;
    
    RETURN jsonb_build_object(
        'success', true,
        'withdrawal_id', withdrawal_record.id,
        'message', 'Withdrawal request created successfully',
        'amount', p_amount,
        'currency', p_currency,
        'recipient_address', p_recipient_address
    );
END;
$$ LANGUAGE plpgsql;

-- Function to process verified withdrawal
CREATE OR REPLACE FUNCTION process_verified_withdrawal(
    p_withdrawal_id UUID,
    p_batch_withdrawal_id VARCHAR(255) DEFAULT NULL,
    p_transaction_hash VARCHAR(255) DEFAULT NULL,
    p_network_fee DECIMAL(20, 8) DEFAULT 0,
    p_actual_amount_sent DECIMAL(20, 8) DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    withdrawal_record RECORD;
    user_balance DECIMAL(20, 2);
BEGIN
    -- Get withdrawal record
    SELECT * INTO withdrawal_record
    FROM public.nowpayments_withdrawals
    WHERE id = p_withdrawal_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'withdrawal_not_found',
            'message', 'Withdrawal request not found'
        );
    END IF;
    
    -- Check if already processed
    IF withdrawal_record.status IN ('completed', 'sent', 'cancelled', 'failed') THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'already_processed',
            'message', 'Withdrawal has already been processed'
        );
    END IF;
    
    -- Get current user balance
    SELECT balance INTO user_balance
    FROM public.user_accounts
    WHERE user_id = withdrawal_record.user_id;
    
    IF NOT FOUND OR user_balance IS NULL THEN
        user_balance := 0;
    END IF;
    
    -- Check if user still has sufficient balance
    IF user_balance < withdrawal_record.amount THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'insufficient_balance',
            'message', 'Insufficient balance for withdrawal',
            'current_balance', user_balance,
            'requested_amount', withdrawal_record.amount
        );
    END IF;
    
    -- Deduct amount from user balance
    UPDATE public.user_accounts
    SET balance = balance - withdrawal_record.amount,
        updated_at = NOW()
    WHERE user_id = withdrawal_record.user_id;
    
    -- Update withdrawal record
    UPDATE public.nowpayments_withdrawals
    SET status = 'processing',
        batch_withdrawal_id = p_batch_withdrawal_id,
        transaction_hash = p_transaction_hash,
        network_fee = p_network_fee,
        actual_amount_sent = COALESCE(p_actual_amount_sent, amount - p_network_fee),
        verified_at = NOW(),
        updated_at = NOW()
    WHERE id = p_withdrawal_id;
    
    RETURN jsonb_build_object(
        'success', true,
        'message', 'Withdrawal processed successfully',
        'withdrawal_id', p_withdrawal_id,
        'amount_deducted', withdrawal_record.amount,
        'new_balance', user_balance - withdrawal_record.amount
    );
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- 6. FINAL DATA UPDATES
-- ===========================================

-- Generate slugs for existing user_bots
UPDATE public.user_bots 
SET slug = generate_slug(COALESCE(name, 'bot-' || id::text))
WHERE slug IS NULL AND name IS NOT NULL;

-- Generate slugs for existing portfolios
UPDATE public.portfolios 
SET slug = generate_slug(COALESCE(name, 'product-' || id::text))
WHERE slug IS NULL AND name IS NOT NULL;

-- Generate slugs for existing news_feed posts
UPDATE public.news_feed 
SET slug = generate_slug(COALESCE(content, 'post-' || id::text))
WHERE slug IS NULL;

-- Trigger initial company balance sync
SELECT sync_company_balance_user_funds();

-- ===========================================
-- SCHEMA COMPLETE
-- ===========================================
-- This schema includes:
-- ✅ Custom URLs system with slug generation
-- ✅ Public sharing with RLS policies
-- ✅ Company balance synchronization fix
-- ✅ Complete NowPayments withdrawal system
-- ✅ Database functions and triggers
-- ✅ Proper indexing and constraints
-- ✅ Data migration for existing records