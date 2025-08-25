-- =====================================================
-- NOWPAYMENTS WITHDRAWALS/PAYOUTS DATABASE SCHEMA
-- =====================================================
-- This schema creates tables for NowPayments withdrawal/payout functionality

-- =====================================================
-- 1. NOWPAYMENTS WITHDRAWALS TABLE
-- =====================================================
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

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_user_id ON public.nowpayments_withdrawals(user_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_withdrawal_id ON public.nowpayments_withdrawals(withdrawal_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_batch_id ON public.nowpayments_withdrawals(batch_withdrawal_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_status ON public.nowpayments_withdrawals(status);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_created_at ON public.nowpayments_withdrawals(created_at);
CREATE INDEX IF NOT EXISTS idx_nowpayments_withdrawals_currency ON public.nowpayments_withdrawals(currency);

-- =====================================================
-- 2. TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- =====================================================

-- Add trigger for updated_at
DROP TRIGGER IF EXISTS update_nowpayments_withdrawals_updated_at ON public.nowpayments_withdrawals;
CREATE TRIGGER update_nowpayments_withdrawals_updated_at
    BEFORE UPDATE ON public.nowpayments_withdrawals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 3. ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on withdrawals table
ALTER TABLE public.nowpayments_withdrawals ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own withdrawals" ON public.nowpayments_withdrawals;
DROP POLICY IF EXISTS "Users can insert their own withdrawals" ON public.nowpayments_withdrawals;
DROP POLICY IF EXISTS "Service role can access all withdrawals" ON public.nowpayments_withdrawals;

-- Withdrawal policies
CREATE POLICY "Users can view their own withdrawals" ON public.nowpayments_withdrawals
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own withdrawals" ON public.nowpayments_withdrawals
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Service role can access all withdrawals (for webhooks and admin operations)
CREATE POLICY "Service role can access all withdrawals" ON public.nowpayments_withdrawals
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 4. HELPER FUNCTIONS
-- =====================================================

-- Function to process withdrawal request
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
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to deduct balance when withdrawal is verified
CREATE OR REPLACE FUNCTION process_verified_withdrawal(
    p_withdrawal_id UUID
)
RETURNS JSONB AS $$
DECLARE
    withdrawal_record RECORD;
    result JSONB;
BEGIN
    -- Get withdrawal details
    SELECT * INTO withdrawal_record
    FROM public.nowpayments_withdrawals
    WHERE id = p_withdrawal_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'withdrawal_not_found',
            'message', 'Withdrawal record not found'
        );
    END IF;
    
    -- Check if withdrawal is verified
    IF withdrawal_record.status != 'verified' THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'withdrawal_not_verified',
            'message', 'Withdrawal must be verified before processing'
        );
    END IF;
    
    -- Create withdrawal transaction
    INSERT INTO public.transactions (
        user_id,
        transaction_type,
        amount,
        platform_fee,
        net_amount,
        status,
        description
    )
    VALUES (
        withdrawal_record.user_id,
        'withdrawal',
        -withdrawal_record.amount,
        0, -- No platform fee on withdrawals
        -withdrawal_record.amount,
        'completed',
        'Crypto withdrawal: ' || withdrawal_record.amount || ' ' || withdrawal_record.currency || ' to ' || withdrawal_record.recipient_address
    );
    
    -- Update user balance (deduct amount)
    UPDATE public.user_accounts
    SET 
        balance = balance - withdrawal_record.amount,
        updated_at = NOW()
    WHERE user_id = withdrawal_record.user_id;
    
    -- Update withdrawal status
    UPDATE public.nowpayments_withdrawals
    SET 
        status = 'processing',
        updated_at = NOW()
    WHERE id = p_withdrawal_id;
    
    -- Create notification
    INSERT INTO public.user_notifications (user_id, title, message, type, is_read)
    VALUES (
        withdrawal_record.user_id,
        'Withdrawal Processing 🔄',
        'Your withdrawal of ' || withdrawal_record.amount || ' ' || withdrawal_record.currency || ' is being processed. You will be notified when the transaction is completed.',
        'info',
        false
    );
    
    RETURN jsonb_build_object(
        'success', true,
        'withdrawal_id', p_withdrawal_id,
        'message', 'Withdrawal processed successfully',
        'amount', withdrawal_record.amount,
        'status', 'processing'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.nowpayments_withdrawals TO authenticated;

COMMENT ON TABLE public.nowpayments_withdrawals IS 'Stores NowPayments withdrawal/payout requests with 2FA verification';