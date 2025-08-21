-- =====================================================
-- CAPITALIST API CRYPTO PAYMENT SYSTEM DATABASE SCHEMA (FIXED)
-- =====================================================
-- This schema extends the existing balance system with crypto payment functionality
-- Supporting USDT (ERC20/TRC20) and USDC (ERC20) via Capitalist API

-- =====================================================
-- 1. DEPOSIT ADDRESSES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.deposit_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    currency VARCHAR(10) NOT NULL CHECK (currency IN ('USDT', 'USDC')),
    network VARCHAR(10) NOT NULL CHECK (network IN ('ERC20', 'TRC20')),
    memo TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one active address per user per currency/network combination
    UNIQUE(user_id, currency, network, is_active) DEFERRABLE INITIALLY DEFERRED
);

-- Index for efficient queries
CREATE INDEX IF NOT EXISTS idx_deposit_addresses_user_currency ON public.deposit_addresses(user_id, currency, network);
CREATE INDEX IF NOT EXISTS idx_deposit_addresses_address ON public.deposit_addresses(address);

-- =====================================================
-- 2. CRYPTO TRANSACTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.crypto_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('deposit', 'withdrawal')),
    currency VARCHAR(10) NOT NULL CHECK (currency IN ('USDT', 'USDC')),
    network VARCHAR(10) NOT NULL CHECK (network IN ('ERC20', 'TRC20')),
    amount DECIMAL(20, 8) NOT NULL CHECK (amount > 0),
    
    -- Deposit specific fields
    deposit_address TEXT,
    
    -- Withdrawal specific fields
    recipient_address TEXT,
    memo TEXT,
    
    -- Transaction tracking
    transaction_hash TEXT,
    capitalist_batch_id TEXT,
    confirmations INTEGER DEFAULT 0,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'confirmed', 'failed', 'cancelled')),
    
    -- Fee information
    network_fee DECIMAL(20, 8) DEFAULT 0,
    platform_fee DECIMAL(20, 8) DEFAULT 0,
    total_fee DECIMAL(20, 8) DEFAULT 0,
    
    -- References
    balance_transaction_id UUID REFERENCES public.transactions(id) ON DELETE SET NULL,
    
    -- Metadata
    reference TEXT,
    error_message TEXT,
    external_data JSONB, -- Store additional data from Capitalist API
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_user_id ON public.crypto_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_status ON public.crypto_transactions(status);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_type ON public.crypto_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_hash ON public.crypto_transactions(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_batch_id ON public.crypto_transactions(capitalist_batch_id);
CREATE INDEX IF NOT EXISTS idx_crypto_transactions_created_at ON public.crypto_transactions(created_at);

-- =====================================================
-- 3. COMPANY BALANCE TRACKING TABLE (FIXED)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.company_balance (
    id UUID PRIMARY KEY DEFAULT '00000000-0000-0000-0000-000000000001'::UUID,
    user_funds DECIMAL(20, 2) DEFAULT 0 NOT NULL CHECK (user_funds >= 0),
    company_funds DECIMAL(20, 2) DEFAULT 0 NOT NULL CHECK (company_funds >= 0),
    total_deposits DECIMAL(20, 2) DEFAULT 0 NOT NULL CHECK (total_deposits >= 0),
    total_withdrawals DECIMAL(20, 2) DEFAULT 0 NOT NULL CHECK (total_withdrawals >= 0),
    total_fees_earned DECIMAL(20, 2) DEFAULT 0 NOT NULL CHECK (total_fees_earned >= 0),
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Initialize company balance record with fixed UUID
INSERT INTO public.company_balance (id, user_funds, company_funds, total_deposits, total_withdrawals, total_fees_earned)
VALUES ('00000000-0000-0000-0000-000000000001'::UUID, 0, 0, 0, 0, 0)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 4. TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- =====================================================

-- Create updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
DROP TRIGGER IF EXISTS update_deposit_addresses_updated_at ON public.deposit_addresses;
CREATE TRIGGER update_deposit_addresses_updated_at
    BEFORE UPDATE ON public.deposit_addresses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_crypto_transactions_updated_at ON public.crypto_transactions;
CREATE TRIGGER update_crypto_transactions_updated_at
    BEFORE UPDATE ON public.crypto_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_company_balance_updated_at ON public.company_balance;
CREATE TRIGGER update_company_balance_updated_at
    BEFORE UPDATE ON public.company_balance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.deposit_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crypto_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.company_balance ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist to avoid conflicts
DROP POLICY IF EXISTS "Users can view their own deposit addresses" ON public.deposit_addresses;
DROP POLICY IF EXISTS "Users can insert their own deposit addresses" ON public.deposit_addresses;
DROP POLICY IF EXISTS "Users can update their own deposit addresses" ON public.deposit_addresses;
DROP POLICY IF EXISTS "Service role can access all deposit addresses" ON public.deposit_addresses;

-- Deposit addresses policies
CREATE POLICY "Users can view their own deposit addresses" ON public.deposit_addresses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own deposit addresses" ON public.deposit_addresses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own deposit addresses" ON public.deposit_addresses
    FOR UPDATE USING (auth.uid() = user_id);

-- Service role can access all deposit addresses
CREATE POLICY "Service role can access all deposit addresses" ON public.deposit_addresses
    FOR ALL USING (auth.role() = 'service_role');

-- Drop existing crypto transaction policies
DROP POLICY IF EXISTS "Users can view their own crypto transactions" ON public.crypto_transactions;
DROP POLICY IF EXISTS "Users can insert their own crypto transactions" ON public.crypto_transactions;
DROP POLICY IF EXISTS "Service role can access all crypto transactions" ON public.crypto_transactions;

-- Crypto transactions policies
CREATE POLICY "Users can view their own crypto transactions" ON public.crypto_transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own crypto transactions" ON public.crypto_transactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Service role can access all crypto transactions
CREATE POLICY "Service role can access all crypto transactions" ON public.crypto_transactions
    FOR ALL USING (auth.role() = 'service_role');

-- Drop existing company balance policy
DROP POLICY IF EXISTS "Service role can access company balance" ON public.company_balance;

-- Company balance policies (admin only)
CREATE POLICY "Service role can access company balance" ON public.company_balance
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 6. USEFUL FUNCTIONS FOR CRYPTO PAYMENTS
-- =====================================================

-- Function to get or create deposit address for user
CREATE OR REPLACE FUNCTION get_or_create_deposit_address(
    p_user_id UUID,
    p_currency VARCHAR(10),
    p_network VARCHAR(10),
    p_address TEXT DEFAULT NULL
)
RETURNS TABLE (
    address TEXT,
    is_new BOOLEAN
) AS $$
DECLARE
    existing_address TEXT;
    new_address TEXT;
BEGIN
    -- Check if user already has an active address for this currency/network
    SELECT da.address INTO existing_address
    FROM public.deposit_addresses da
    WHERE da.user_id = p_user_id 
      AND da.currency = p_currency 
      AND da.network = p_network 
      AND da.is_active = true
    LIMIT 1;
    
    IF existing_address IS NOT NULL THEN
        -- Return existing address
        RETURN QUERY SELECT existing_address, false;
    ELSE
        -- Create new address (if provided)
        IF p_address IS NOT NULL THEN
            INSERT INTO public.deposit_addresses (user_id, address, currency, network, is_active)
            VALUES (p_user_id, p_address, p_currency, p_network, true)
            RETURNING deposit_addresses.address INTO new_address;
            
            RETURN QUERY SELECT new_address, true;
        ELSE
            -- Return null if no address provided and none exists
            RETURN QUERY SELECT NULL::TEXT, false;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update company balance after crypto transaction
CREATE OR REPLACE FUNCTION update_company_balance_crypto(
    p_transaction_type VARCHAR(20),
    p_amount DECIMAL(20, 2),
    p_fee DECIMAL(20, 2) DEFAULT 0
)
RETURNS BOOLEAN AS $$
BEGIN
    IF p_transaction_type = 'deposit' THEN
        UPDATE public.company_balance
        SET 
            user_funds = user_funds + p_amount,
            total_deposits = total_deposits + p_amount,
            last_updated = NOW()
        WHERE id = '00000000-0000-0000-0000-000000000001'::UUID;
    ELSIF p_transaction_type = 'withdrawal' THEN
        UPDATE public.company_balance
        SET 
            user_funds = user_funds - p_amount,
            total_withdrawals = total_withdrawals + p_amount,
            company_funds = company_funds + p_fee,
            total_fees_earned = total_fees_earned + p_fee,
            last_updated = NOW()
        WHERE id = '00000000-0000-0000-0000-000000000001'::UUID;
    END IF;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to process crypto deposit confirmation
CREATE OR REPLACE FUNCTION process_crypto_deposit(
    p_crypto_transaction_id UUID,
    p_transaction_hash TEXT,
    p_confirmations INTEGER DEFAULT 1
)
RETURNS JSONB AS $$
DECLARE
    crypto_tx RECORD;
    balance_tx_id UUID;
    result JSONB;
BEGIN
    -- Get crypto transaction details
    SELECT * INTO crypto_tx
    FROM public.crypto_transactions
    WHERE id = p_crypto_transaction_id
      AND transaction_type = 'deposit'
      AND status IN ('pending', 'processing');
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'crypto_transaction_not_found',
            'message', 'Crypto transaction not found or already processed'
        );
    END IF;
    
    -- Update crypto transaction
    UPDATE public.crypto_transactions
    SET 
        status = 'confirmed',
        transaction_hash = p_transaction_hash,
        confirmations = p_confirmations,
        updated_at = NOW()
    WHERE id = p_crypto_transaction_id;
    
    -- Create balance transaction (credit user account)
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
        crypto_tx.user_id,
        'topup',
        crypto_tx.amount,
        0, -- No platform fee on deposits
        crypto_tx.amount,
        'completed',
        'Crypto deposit: ' || crypto_tx.amount || ' USD from ' || crypto_tx.currency || ' (' || crypto_tx.network || ')'
    )
    RETURNING id INTO balance_tx_id;
    
    -- Link crypto transaction to balance transaction
    UPDATE public.crypto_transactions
    SET balance_transaction_id = balance_tx_id
    WHERE id = p_crypto_transaction_id;
    
    -- Update user balance
    INSERT INTO public.user_accounts (user_id, balance, currency)
    VALUES (crypto_tx.user_id, crypto_tx.amount, 'USD')
    ON CONFLICT (user_id)
    DO UPDATE SET 
        balance = user_accounts.balance + crypto_tx.amount,
        updated_at = NOW();
    
    -- Update company balance tracking
    PERFORM update_company_balance_crypto('deposit', crypto_tx.amount);
    
    -- Create notification
    INSERT INTO public.user_notifications (user_id, title, message, type, is_read)
    VALUES (
        crypto_tx.user_id,
        'Crypto Deposit Confirmed',
        'Your ' || crypto_tx.currency || ' deposit of $' || crypto_tx.amount || ' has been confirmed and added to your balance.',
        'success',
        false
    );
    
    RETURN jsonb_build_object(
        'success', true,
        'crypto_transaction_id', p_crypto_transaction_id,
        'balance_transaction_id', balance_tx_id,
        'amount', crypto_tx.amount,
        'new_balance', (SELECT balance FROM public.user_accounts WHERE user_id = crypto_tx.user_id)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 7. EXAMPLE QUERIES AND USAGE
-- =====================================================

-- Example: Get user's crypto transaction history
-- SELECT * FROM public.crypto_transactions WHERE user_id = 'user-uuid' ORDER BY created_at DESC;

-- Example: Get company balance overview
-- SELECT * FROM public.company_balance;

-- Example: Get all active deposit addresses for a user
-- SELECT * FROM public.deposit_addresses WHERE user_id = 'user-uuid' AND is_active = true;

-- Example: Process a deposit confirmation
-- SELECT process_crypto_deposit('crypto-tx-uuid', '0xabc123...', 6);

COMMENT ON TABLE public.deposit_addresses IS 'Stores crypto deposit addresses generated for users via Capitalist API';
COMMENT ON TABLE public.crypto_transactions IS 'Tracks all crypto deposits and withdrawals with Capitalist API integration';
COMMENT ON TABLE public.company_balance IS 'Tracks total user funds vs company funds for accounting purposes';