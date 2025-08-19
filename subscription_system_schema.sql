-- =====================================================
-- Subscription Management System Database Schema
-- =====================================================

-- Create subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_type VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (plan_type IN ('free', 'plus', 'pro')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled', 'pending')),
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    renewal BOOLEAN DEFAULT false,
    price_paid DECIMAL(10,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique constraint to ensure one subscription per user
CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_user_unique ON public.subscriptions(user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_type ON public.subscriptions(plan_type);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON public.subscriptions(end_date);

-- Enable Row Level Security
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for subscriptions table
-- Service role has full access
DROP POLICY IF EXISTS "service_role_subscriptions_access" ON public.subscriptions;
CREATE POLICY "service_role_subscriptions_access" ON public.subscriptions
    FOR ALL 
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Users can view their own subscription
DROP POLICY IF EXISTS "users_view_own_subscription" ON public.subscriptions;
CREATE POLICY "users_view_own_subscription" ON public.subscriptions
    FOR SELECT 
    TO authenticated
    USING (auth.uid() = user_id);

-- Users can insert their own subscription
DROP POLICY IF EXISTS "users_insert_own_subscription" ON public.subscriptions;
CREATE POLICY "users_insert_own_subscription" ON public.subscriptions
    FOR INSERT 
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own subscription
DROP POLICY IF EXISTS "users_update_own_subscription" ON public.subscriptions;
CREATE POLICY "users_update_own_subscription" ON public.subscriptions
    FOR UPDATE 
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Grant necessary permissions
GRANT ALL ON public.subscriptions TO authenticated;
GRANT ALL ON public.subscriptions TO service_role;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_subscriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updating updated_at
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_subscriptions_updated_at();

-- Function to initialize free subscription for new users
CREATE OR REPLACE FUNCTION initialize_user_subscription()
RETURNS TRIGGER AS $$
BEGIN
    -- Create free subscription for new user
    INSERT INTO public.subscriptions (
        user_id,
        plan_type,
        status,
        start_date,
        end_date,
        renewal,
        price_paid
    ) VALUES (
        NEW.id,
        'free',
        'active',
        NOW(),
        NULL, -- Free plan never expires
        false,
        0.00
    ) ON CONFLICT (user_id) DO NOTHING;
    
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- Create trigger to initialize subscription for new users
DROP TRIGGER IF EXISTS initialize_subscription_trigger ON auth.users;
CREATE TRIGGER initialize_subscription_trigger
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION initialize_user_subscription();

-- Function to upgrade subscription with balance deduction
CREATE OR REPLACE FUNCTION upgrade_subscription(
    p_user_id UUID,
    p_plan_type VARCHAR(20),
    p_price DECIMAL(10,2)
)
RETURNS JSON AS $$
DECLARE
    v_current_balance DECIMAL(10,2);
    v_subscription_record RECORD;
    v_result JSON;
BEGIN
    -- Check user's current balance
    SELECT COALESCE(balance, 0) INTO v_current_balance
    FROM public.user_accounts 
    WHERE user_id = p_user_id;
    
    -- Check if user has sufficient funds
    IF v_current_balance < p_price THEN
        RETURN json_build_object(
            'success', false,
            'error', 'insufficient_funds',
            'message', 'Insufficient balance to upgrade subscription',
            'current_balance', v_current_balance,
            'required_amount', p_price
        );
    END IF;
    
    -- Start transaction
    BEGIN
        -- 1. Deduct amount from user's balance
        UPDATE public.user_accounts 
        SET balance = balance - p_price,
            updated_at = NOW()
        WHERE user_id = p_user_id;
        
        -- 2. Update or create subscription
        INSERT INTO public.subscriptions (
            user_id, plan_type, status, start_date, end_date, 
            renewal, price_paid, currency
        ) VALUES (
            p_user_id, p_plan_type, 'active', NOW(), 
            NOW() + INTERVAL '30 days', -- 30 days subscription
            false, p_price, 'USD'
        ) ON CONFLICT (user_id) 
        DO UPDATE SET 
            plan_type = p_plan_type,
            status = 'active',
            start_date = NOW(),
            end_date = NOW() + INTERVAL '30 days',
            price_paid = p_price,
            updated_at = NOW();
        
        -- 3. Create transaction record for subscription payment
        INSERT INTO public.transactions (
            user_id, transaction_type, amount, platform_fee, 
            net_amount, status, description
        ) VALUES (
            p_user_id, 'subscription', p_price, 0.0, 
            p_price, 'completed', 
            'Subscription upgrade to ' || p_plan_type || ' plan'
        );
        
        -- Get updated subscription info
        SELECT * INTO v_subscription_record 
        FROM public.subscriptions 
        WHERE user_id = p_user_id;
        
        -- Return success result
        v_result := json_build_object(
            'success', true,
            'subscription', row_to_json(v_subscription_record),
            'amount_charged', p_price,
            'new_balance', v_current_balance - p_price
        );
        
        RETURN v_result;
        
    EXCEPTION WHEN OTHERS THEN
        -- Return error if transaction fails
        RETURN json_build_object(
            'success', false,
            'error', 'transaction_failed',
            'message', 'Failed to upgrade subscription: ' || SQLERRM
        );
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION upgrade_subscription(UUID, VARCHAR, DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION upgrade_subscription(UUID, VARCHAR, DECIMAL) TO service_role;

-- Insert default free subscriptions for existing users
INSERT INTO public.subscriptions (user_id, plan_type, status, start_date, renewal, price_paid)
SELECT 
    id as user_id,
    'free' as plan_type,
    'active' as status,
    NOW() as start_date,
    false as renewal,
    0.00 as price_paid
FROM auth.users
WHERE id NOT IN (SELECT user_id FROM public.subscriptions)
ON CONFLICT (user_id) DO NOTHING;

-- Verify the setup
SELECT 'Subscription system schema created successfully' as status;

-- Show subscription plans configuration
SELECT 'Subscription Plans:' as info
UNION ALL
SELECT '- Free Plan: $0/month - 1 AI bot, 2 manual bots, 1 product slot'
UNION ALL  
SELECT '- Plus Plan: $10/month - 3 AI bots, 5 manual bots, 10 product slots'
UNION ALL
SELECT '- Pro Plan: Coming Soon';