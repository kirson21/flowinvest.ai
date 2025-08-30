-- =====================================================
-- WITHDRAWAL ONLY DATABASE SCHEMA
-- =====================================================
-- Only includes withdrawal-specific tables and functions
-- Safe to run if other parts already exist

-- ===========================================
-- 1. NOWPAYMENTS WITHDRAWAL TABLE
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

-- Create indexes for performance (IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_user_id ON public.nowpayments_withdrawals(user_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_status ON public.nowpayments_withdrawals(status);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_created_at ON public.nowpayments_withdrawals(created_at);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_batch_id ON public.nowpayments_withdrawals(batch_withdrawal_id);

-- ===========================================
-- 2. UPDATED_AT TRIGGER FUNCTION
-- ===========================================

-- Create trigger function if not exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger if it exists, then create new one
DROP TRIGGER IF EXISTS update_nowpayments_withdrawals_updated_at ON public.nowpayments_withdrawals;
CREATE TRIGGER update_nowpayments_withdrawals_updated_at 
    BEFORE UPDATE ON public.nowpayments_withdrawals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===========================================
-- 3. RLS POLICIES FOR WITHDRAWALS
-- ===========================================

-- Enable RLS
ALTER TABLE public.nowpayments_withdrawals ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own withdrawals" ON public.nowpayments_withdrawals;
DROP POLICY IF EXISTS "Users can create own withdrawals" ON public.nowpayments_withdrawals;
DROP POLICY IF EXISTS "Users can update own withdrawals" ON public.nowpayments_withdrawals;
DROP POLICY IF EXISTS "Service role can access all withdrawals" ON public.nowpayments_withdrawals;

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
-- 4. WITHDRAWAL FUNCTIONS
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
-- 5. FUNCTION TO UPDATE WITHDRAWAL STATUS VIA WEBHOOK
-- ===========================================

CREATE OR REPLACE FUNCTION update_withdrawal_status_webhook(
    p_batch_withdrawal_id VARCHAR(255),
    p_status VARCHAR(50),
    p_transaction_hash VARCHAR(255) DEFAULT NULL,
    p_network_fee DECIMAL(20, 8) DEFAULT 0,
    p_actual_amount_sent DECIMAL(20, 8) DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    withdrawal_record RECORD;
    user_balance DECIMAL(20, 2);
BEGIN
    -- Find withdrawal record by batch_withdrawal_id
    SELECT * INTO withdrawal_record
    FROM public.nowpayments_withdrawals
    WHERE batch_withdrawal_id = p_batch_withdrawal_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'withdrawal_not_found',
            'message', 'Withdrawal record not found for batch ID: ' || p_batch_withdrawal_id
        );
    END IF;
    
    -- If this is a completion status and balance hasn't been deducted yet
    IF p_status IN ('FINISHED', 'completed', 'sent') AND withdrawal_record.status NOT IN ('completed', 'sent', 'processing') THEN
        -- Get current user balance
        SELECT balance INTO user_balance
        FROM public.user_accounts
        WHERE user_id = withdrawal_record.user_id;
        
        IF user_balance >= withdrawal_record.amount THEN
            -- Deduct amount from user balance
            UPDATE public.user_accounts
            SET balance = balance - withdrawal_record.amount,
                updated_at = NOW()
            WHERE user_id = withdrawal_record.user_id;
        END IF;
    END IF;
    
    -- Update withdrawal record
    UPDATE public.nowpayments_withdrawals
    SET status = CASE 
                    WHEN p_status = 'FINISHED' THEN 'completed'
                    WHEN p_status = 'SENDING' THEN 'processing' 
                    ELSE LOWER(p_status)
                 END,
        transaction_hash = COALESCE(p_transaction_hash, transaction_hash),
        network_fee = COALESCE(p_network_fee, network_fee),
        actual_amount_sent = COALESCE(p_actual_amount_sent, actual_amount_sent),
        completed_at = CASE WHEN p_status = 'FINISHED' THEN NOW() ELSE completed_at END,
        updated_at = NOW()
    WHERE id = withdrawal_record.id;
    
    RETURN jsonb_build_object(
        'success', true,
        'message', 'Withdrawal status updated successfully',
        'withdrawal_id', withdrawal_record.id,
        'old_status', withdrawal_record.status,
        'new_status', p_status,
        'balance_deducted', CASE WHEN p_status IN ('FINISHED', 'completed', 'sent') THEN withdrawal_record.amount ELSE 0 END
    );
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- WITHDRAWAL SCHEMA COMPLETE
-- ===========================================
-- This schema includes only withdrawal-related components:
-- ✅ nowpayments_withdrawals table
-- ✅ Withdrawal creation function
-- ✅ Withdrawal processing function  
-- ✅ Webhook status update function
-- ✅ RLS policies for security
-- ✅ Proper indexing