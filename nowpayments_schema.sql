-- =====================================================
-- NOWPAYMENTS INTEGRATION DATABASE SCHEMA
-- =====================================================
-- This schema creates tables for NowPayments invoice-based payments and subscriptions
-- Replaces the previous Capitalist API integration

-- =====================================================
-- 1. NOWPAYMENTS INVOICES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.nowpayments_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    order_id VARCHAR(255) NOT NULL UNIQUE,
    invoice_id VARCHAR(255) NOT NULL UNIQUE,
    
    -- Payment details
    payment_status VARCHAR(50) DEFAULT 'waiting' CHECK (payment_status IN (
        'waiting', 'confirming', 'confirmed', 'sending', 
        'partially_paid', 'finished', 'failed', 'expired'
    )),
    amount DECIMAL(20, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(10) NOT NULL DEFAULT 'usd',
    pay_currency VARCHAR(50), -- Crypto currency used for payment
    actually_paid DECIMAL(20, 8) DEFAULT 0,
    
    -- NowPayments specific fields
    invoice_url TEXT NOT NULL,
    user_email VARCHAR(255),
    description TEXT,
    
    -- Webhook and callback data
    webhook_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_nowpayments_invoices_user_id ON public.nowpayments_invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_invoices_order_id ON public.nowpayments_invoices(order_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_invoices_invoice_id ON public.nowpayments_invoices(invoice_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_invoices_status ON public.nowpayments_invoices(payment_status);
CREATE INDEX IF NOT EXISTS idx_nowpayments_invoices_created_at ON public.nowpayments_invoices(created_at);

-- =====================================================
-- 2. NOWPAYMENTS SUBSCRIPTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.nowpayments_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id VARCHAR(255) NOT NULL UNIQUE,
    plan_id VARCHAR(255) NOT NULL,
    
    -- Subscription details
    user_email VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'WAITING_PAY' CHECK (status IN (
        'WAITING_PAY', 'PAID', 'PARTIALLY_PAID', 'EXPIRED'
    )),
    is_active BOOLEAN DEFAULT false,
    
    -- Dates
    expire_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for subscriptions
CREATE INDEX IF NOT EXISTS idx_nowpayments_subscriptions_user_id ON public.nowpayments_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_subscriptions_subscription_id ON public.nowpayments_subscriptions(subscription_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_subscriptions_plan_id ON public.nowpayments_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_nowpayments_subscriptions_status ON public.nowpayments_subscriptions(status);

-- =====================================================
-- 3. SUBSCRIPTION PLANS TABLE (Local cache)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.nowpayments_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    interval_days INTEGER NOT NULL CHECK (interval_days > 0),
    amount DECIMAL(20, 2) NOT NULL CHECK (amount >= 0), -- Allow 0 for free plans
    currency VARCHAR(10) DEFAULT 'usd',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 4. TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- =====================================================

-- Create or update the trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
DROP TRIGGER IF EXISTS update_nowpayments_invoices_updated_at ON public.nowpayments_invoices;
CREATE TRIGGER update_nowpayments_invoices_updated_at
    BEFORE UPDATE ON public.nowpayments_invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_nowpayments_subscriptions_updated_at ON public.nowpayments_subscriptions;
CREATE TRIGGER update_nowpayments_subscriptions_updated_at
    BEFORE UPDATE ON public.nowpayments_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_nowpayments_plans_updated_at ON public.nowpayments_plans;
CREATE TRIGGER update_nowpayments_plans_updated_at
    BEFORE UPDATE ON public.nowpayments_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.nowpayments_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nowpayments_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nowpayments_plans ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own invoices" ON public.nowpayments_invoices;
DROP POLICY IF EXISTS "Users can insert their own invoices" ON public.nowpayments_invoices;
DROP POLICY IF EXISTS "Service role can access all invoices" ON public.nowpayments_invoices;

-- Invoice policies
CREATE POLICY "Users can view their own invoices" ON public.nowpayments_invoices
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own invoices" ON public.nowpayments_invoices
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Service role can access all invoices (for webhooks and admin operations)
CREATE POLICY "Service role can access all invoices" ON public.nowpayments_invoices
    FOR ALL USING (auth.role() = 'service_role');

-- Drop existing subscription policies
DROP POLICY IF EXISTS "Users can view their own subscriptions" ON public.nowpayments_subscriptions;
DROP POLICY IF EXISTS "Users can insert their own subscriptions" ON public.nowpayments_subscriptions;
DROP POLICY IF EXISTS "Service role can access all subscriptions" ON public.nowpayments_subscriptions;

-- Subscription policies
CREATE POLICY "Users can view their own subscriptions" ON public.nowpayments_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own subscriptions" ON public.nowpayments_subscriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Service role can access all subscriptions
CREATE POLICY "Service role can access all subscriptions" ON public.nowpayments_subscriptions
    FOR ALL USING (auth.role() = 'service_role');

-- Drop existing plan policies
DROP POLICY IF EXISTS "Anyone can view active plans" ON public.nowpayments_plans;
DROP POLICY IF EXISTS "Service role can manage plans" ON public.nowpayments_plans;

-- Plan policies (plans are public for viewing)
CREATE POLICY "Anyone can view active plans" ON public.nowpayments_plans
    FOR SELECT USING (is_active = true);

-- Service role can manage all plans
CREATE POLICY "Service role can manage plans" ON public.nowpayments_plans
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 6. HELPER FUNCTIONS
-- =====================================================

-- Function to process successful NowPayments webhook
CREATE OR REPLACE FUNCTION process_nowpayments_webhook(
    p_invoice_id VARCHAR(255),
    p_payment_status VARCHAR(50),
    p_actually_paid DECIMAL(20, 8),
    p_webhook_data JSONB
)
RETURNS JSONB AS $$
DECLARE
    invoice_record RECORD;
    balance_tx_id UUID;
    result JSONB;
BEGIN
    -- Get invoice details
    SELECT * INTO invoice_record
    FROM public.nowpayments_invoices
    WHERE invoice_id = p_invoice_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'invoice_not_found',
            'message', 'Invoice not found'
        );
    END IF;
    
    -- Update invoice record
    UPDATE public.nowpayments_invoices
    SET 
        payment_status = p_payment_status,
        actually_paid = p_actually_paid,
        webhook_data = p_webhook_data,
        completed_at = CASE WHEN p_payment_status = 'finished' THEN NOW() ELSE completed_at END,
        updated_at = NOW()
    WHERE invoice_id = p_invoice_id;
    
    -- If payment is completed, credit user account
    IF p_payment_status = 'finished' AND p_actually_paid > 0 THEN
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
            invoice_record.user_id,
            'topup',
            p_actually_paid,
            0, -- No platform fee on deposits
            p_actually_paid,
            'completed',
            'Crypto payment via NowPayments: $' || p_actually_paid || ' (Order: ' || invoice_record.order_id || ')'
        )
        RETURNING id INTO balance_tx_id;
        
        -- Update user balance
        INSERT INTO public.user_accounts (user_id, balance, currency)
        VALUES (invoice_record.user_id, p_actually_paid, 'USD')
        ON CONFLICT (user_id)
        DO UPDATE SET 
            balance = user_accounts.balance + p_actually_paid,
            updated_at = NOW();
        
        -- Create success notification
        INSERT INTO public.user_notifications (user_id, title, message, type, is_read)
        VALUES (
            invoice_record.user_id,
            'Payment Successful! 🎉',
            'Your payment of $' || p_actually_paid || ' has been confirmed and added to your balance.',
            'success',
            false
        );
    END IF;
    
    RETURN jsonb_build_object(
        'success', true,
        'invoice_id', p_invoice_id,
        'balance_transaction_id', balance_tx_id,
        'amount', p_actually_paid,
        'status', p_payment_status
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 7. EXAMPLE QUERIES AND USAGE
-- =====================================================

-- Example: Get user's invoice history
-- SELECT * FROM public.nowpayments_invoices WHERE user_id = 'user-uuid' ORDER BY created_at DESC;

-- Example: Get active subscriptions for a user
-- SELECT * FROM public.nowpayments_subscriptions WHERE user_id = 'user-uuid' AND is_active = true;

-- Example: Process a successful payment webhook
-- SELECT process_nowpayments_webhook('invoice-id', 'finished', 100.0, '{"payment_id": "12345"}');

COMMENT ON TABLE public.nowpayments_invoices IS 'Stores NowPayments invoice-based payment records';
COMMENT ON TABLE public.nowpayments_subscriptions IS 'Tracks user subscriptions created via NowPayments email system';
COMMENT ON TABLE public.nowpayments_plans IS 'Local cache of NowPayments subscription plans';

-- Insert some default subscription plans
INSERT INTO public.nowpayments_plans (plan_id, title, interval_days, amount, currency)
VALUES 
    ('plan_free', 'Free Plan', 30, 0.00, 'usd'),
    ('plan_plus', 'Plus Plan', 30, 9.99, 'usd'),
    ('plan_pro', 'Pro Plan', 30, 29.99, 'usd')
ON CONFLICT (plan_id) DO NOTHING;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.nowpayments_invoices TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.nowpayments_subscriptions TO authenticated;
GRANT SELECT ON public.nowpayments_plans TO anon, authenticated;