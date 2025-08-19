-- =====================================================
-- Subscription Restrictions System Database Schema
-- =====================================================

-- Add limits column to existing subscriptions table
ALTER TABLE public.subscriptions 
ADD COLUMN IF NOT EXISTS limits JSONB DEFAULT '{}';

-- Update existing subscriptions to include proper limits
UPDATE public.subscriptions 
SET limits = CASE 
    WHEN plan_type = 'free' THEN '{"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1}'::jsonb
    WHEN plan_type = 'plus' THEN '{"ai_bots": 3, "manual_bots": 5, "marketplace_products": 10}'::jsonb
    WHEN plan_type = 'pro' THEN '{"ai_bots": -1, "manual_bots": -1, "marketplace_products": -1}'::jsonb
    ELSE '{"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1}'::jsonb
END
WHERE limits = '{}' OR limits IS NULL;

-- Create/Update Super Admin subscription
INSERT INTO public.subscriptions (
    user_id, 
    plan_type, 
    status, 
    start_date, 
    end_date, 
    renewal, 
    price_paid,
    limits
) VALUES (
    'cd0e9717-f85d-4726-81e9-f260394ead58',
    'super_admin',
    'active',
    NOW(),
    NULL, -- Never expires
    false,
    0.00,
    NULL -- No limits for super admin
) ON CONFLICT (user_id) 
DO UPDATE SET 
    plan_type = 'super_admin',
    status = 'active',
    limits = NULL,
    updated_at = NOW();

-- Update plan_type check constraint to include super_admin
ALTER TABLE public.subscriptions 
DROP CONSTRAINT IF EXISTS subscriptions_plan_type_check;

ALTER TABLE public.subscriptions 
ADD CONSTRAINT subscriptions_plan_type_check 
CHECK (plan_type IN ('free', 'plus', 'pro', 'super_admin'));

-- Function to check if user has reached subscription limit
CREATE OR REPLACE FUNCTION check_subscription_limit(
    p_user_id UUID,
    p_resource_type VARCHAR(50), -- 'ai_bots', 'manual_bots', 'marketplace_products'
    p_current_count INTEGER DEFAULT 0
)
RETURNS JSON AS $$
DECLARE
    v_subscription RECORD;
    v_limit INTEGER;
    v_result JSON;
BEGIN
    -- Get user's subscription
    SELECT * INTO v_subscription 
    FROM public.subscriptions 
    WHERE user_id = p_user_id;
    
    -- If no subscription found, default to free
    IF v_subscription IS NULL THEN
        INSERT INTO public.subscriptions (user_id, plan_type, limits)
        VALUES (p_user_id, 'free', '{"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1}')
        RETURNING * INTO v_subscription;
    END IF;
    
    -- Super admin has no limits
    IF v_subscription.plan_type = 'super_admin' OR v_subscription.limits IS NULL THEN
        RETURN json_build_object(
            'success', true,
            'can_create', true,
            'limit_reached', false,
            'current_count', p_current_count,
            'limit', -1,
            'plan_type', v_subscription.plan_type,
            'is_super_admin', true
        );
    END IF;
    
    -- Get the limit for the specific resource
    v_limit := COALESCE((v_subscription.limits ->> p_resource_type)::INTEGER, 0);
    
    -- If limit is -1, it means unlimited
    IF v_limit = -1 THEN
        RETURN json_build_object(
            'success', true,
            'can_create', true,
            'limit_reached', false,
            'current_count', p_current_count,
            'limit', -1,
            'plan_type', v_subscription.plan_type,
            'is_super_admin', false
        );
    END IF;
    
    -- Check if limit is reached
    IF p_current_count >= v_limit THEN
        RETURN json_build_object(
            'success', true,
            'can_create', false,
            'limit_reached', true,
            'current_count', p_current_count,
            'limit', v_limit,
            'plan_type', v_subscription.plan_type,
            'is_super_admin', false,
            'message', 'You have reached the limit of your current subscription plan'
        );
    ELSE
        RETURN json_build_object(
            'success', true,
            'can_create', true,
            'limit_reached', false,
            'current_count', p_current_count,
            'limit', v_limit,
            'plan_type', v_subscription.plan_type,
            'is_super_admin', false
        );
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object(
        'success', false,
        'error', 'Failed to check subscription limit: ' || SQLERRM
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's subscription limits overview
CREATE OR REPLACE FUNCTION get_user_limits_overview(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
    v_subscription RECORD;
    v_result JSON;
BEGIN
    -- Get user's subscription
    SELECT * INTO v_subscription 
    FROM public.subscriptions 
    WHERE user_id = p_user_id;
    
    -- If no subscription found, default to free
    IF v_subscription IS NULL THEN
        INSERT INTO public.subscriptions (user_id, plan_type, limits)
        VALUES (p_user_id, 'free', '{"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1}')
        RETURNING * INTO v_subscription;
    END IF;
    
    -- Return subscription info with limits
    RETURN json_build_object(
        'success', true,
        'plan_type', v_subscription.plan_type,
        'limits', v_subscription.limits,
        'is_super_admin', v_subscription.plan_type = 'super_admin',
        'status', v_subscription.status,
        'start_date', v_subscription.start_date,
        'end_date', v_subscription.end_date
    );
    
EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object(
        'success', false,
        'error', 'Failed to get user limits: ' || SQLERRM
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION check_subscription_limit(UUID, VARCHAR, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION check_subscription_limit(UUID, VARCHAR, INTEGER) TO service_role;
GRANT EXECUTE ON FUNCTION get_user_limits_overview(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_limits_overview(UUID) TO service_role;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_type ON public.subscriptions(plan_type);
CREATE INDEX IF NOT EXISTS idx_subscriptions_limits ON public.subscriptions USING GIN(limits);

-- Update subscription plans to include limits in backend response
-- This will be handled in the backend API

SELECT 'Subscription restrictions system schema created successfully' as status;

-- Show current subscription limits
SELECT 
    user_id,
    plan_type,
    limits,
    status,
    CASE 
        WHEN plan_type = 'super_admin' THEN 'Unlimited access to all features'
        WHEN limits IS NULL THEN 'No limits set'
        ELSE 'AI Bots: ' || COALESCE(limits->>'ai_bots', '0') || 
             ', Manual Bots: ' || COALESCE(limits->>'manual_bots', '0') ||
             ', Products: ' || COALESCE(limits->>'marketplace_products', '0')
    END as limits_summary
FROM public.subscriptions 
ORDER BY 
    CASE plan_type 
        WHEN 'super_admin' THEN 1 
        WHEN 'pro' THEN 2 
        WHEN 'plus' THEN 3 
        WHEN 'free' THEN 4 
        ELSE 5 
    END;