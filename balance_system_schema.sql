-- =====================================================
-- User Balance System Database Schema
-- =====================================================

-- Create transactions table for marketplace purchases and balance operations
CREATE TABLE IF NOT EXISTS public.transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    seller_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    product_id UUID REFERENCES public.portfolios(id) ON DELETE SET NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('purchase', 'topup', 'withdrawal', 'platform_fee')),
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    platform_fee DECIMAL(10,2) DEFAULT 0 CHECK (platform_fee >= 0),
    net_amount DECIMAL(10,2) NOT NULL CHECK (net_amount >= 0),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON public.transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_seller_id ON public.transactions(seller_id);
CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON public.transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON public.transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON public.transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON public.transactions(created_at);

-- Enable Row Level Security
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for transactions table
-- Users can view their own transactions (as buyer or seller)
DROP POLICY IF EXISTS "Users can view their own transactions" ON public.transactions;
CREATE POLICY "Users can view their own transactions" ON public.transactions
    FOR SELECT USING (
        auth.uid() = user_id OR 
        auth.uid() = seller_id OR
        -- Super admin can view all transactions
        auth.uid() = 'cd0e9717-f85d-4726-81e9-f260394ead58'::uuid
    );

-- Users can insert their own transactions
DROP POLICY IF EXISTS "Users can insert their own transactions" ON public.transactions;
CREATE POLICY "Users can insert their own transactions" ON public.transactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own transactions (status changes only for certain fields)
DROP POLICY IF EXISTS "Users can update their own transactions" ON public.transactions;
CREATE POLICY "Users can update their own transactions" ON public.transactions
    FOR UPDATE USING (
        auth.uid() = user_id OR 
        auth.uid() = seller_id OR
        auth.uid() = 'cd0e9717-f85d-4726-81e9-f260394ead58'::uuid
    );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updating updated_at
DROP TRIGGER IF EXISTS update_transactions_updated_at ON public.transactions;
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON public.transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to process marketplace purchase with balance checking
CREATE OR REPLACE FUNCTION process_marketplace_purchase(
    p_buyer_id UUID,
    p_seller_id UUID,
    p_product_id UUID,
    p_amount DECIMAL(10,2),
    p_description TEXT DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_buyer_balance DECIMAL(10,2);
    v_platform_fee DECIMAL(10,2);
    v_seller_amount DECIMAL(10,2);
    v_transaction_id UUID;
    v_result JSON;
BEGIN
    -- Check buyer's current balance
    SELECT COALESCE(balance, 0) INTO v_buyer_balance
    FROM public.user_accounts 
    WHERE user_id = p_buyer_id;
    
    -- Check if buyer has sufficient funds
    IF v_buyer_balance < p_amount THEN
        RETURN json_build_object(
            'success', false,
            'error', 'insufficient_funds',
            'message', 'Insufficient balance to complete purchase',
            'current_balance', v_buyer_balance,
            'required_amount', p_amount
        );
    END IF;
    
    -- Calculate fees (10% platform fee)
    v_platform_fee := p_amount * 0.10;
    v_seller_amount := p_amount * 0.90;
    
    -- Start transaction
    BEGIN
        -- 1. Deduct amount from buyer's balance
        UPDATE public.user_accounts 
        SET balance = balance - p_amount,
            updated_at = NOW()
        WHERE user_id = p_buyer_id;
        
        -- 2. Add seller amount to seller's balance (create account if doesn't exist)
        INSERT INTO public.user_accounts (user_id, balance, currency, created_at, updated_at)
        VALUES (p_seller_id, v_seller_amount, 'USD', NOW(), NOW())
        ON CONFLICT (user_id) 
        DO UPDATE SET 
            balance = user_accounts.balance + v_seller_amount,
            updated_at = NOW();
        
        -- 3. Create transaction record for the purchase
        INSERT INTO public.transactions (
            user_id, seller_id, product_id, transaction_type, 
            amount, platform_fee, net_amount, status, description
        ) VALUES (
            p_buyer_id, p_seller_id, p_product_id, 'purchase',
            p_amount, v_platform_fee, v_seller_amount, 'completed', p_description
        ) RETURNING id INTO v_transaction_id;
        
        -- Return success result
        v_result := json_build_object(
            'success', true,
            'transaction_id', v_transaction_id,
            'amount_charged', p_amount,
            'platform_fee', v_platform_fee,
            'seller_received', v_seller_amount,
            'buyer_new_balance', v_buyer_balance - p_amount
        );
        
        RETURN v_result;
        
    EXCEPTION WHEN OTHERS THEN
        -- Return error if transaction fails
        RETURN json_build_object(
            'success', false,
            'error', 'transaction_failed',
            'message', 'Failed to process purchase: ' || SQLERRM
        );
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE ON public.transactions TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT EXECUTE ON FUNCTION process_marketplace_purchase(UUID, UUID, UUID, DECIMAL, TEXT) TO authenticated;

-- Create sample data for testing (optional - can be removed in production)
-- This creates a test transaction to verify the table structure
INSERT INTO public.transactions (
    user_id, 
    transaction_type, 
    amount, 
    platform_fee, 
    net_amount, 
    status, 
    description
) VALUES (
    'cd0e9717-f85d-4726-81e9-f260394ead58'::uuid,
    'topup',
    100.00,
    0.00,
    100.00,
    'completed',
    'Initial test transaction for balance system'
) ON CONFLICT DO NOTHING;

-- Verify the setup
SELECT 'Balance system schema created successfully' as status;