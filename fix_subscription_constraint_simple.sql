-- Fix Subscription Plan Type Constraint Error
-- Drop existing constraint
ALTER TABLE public.subscriptions DROP CONSTRAINT IF EXISTS subscriptions_plan_type_check;

-- Add new constraint with super_admin included
ALTER TABLE public.subscriptions ADD CONSTRAINT subscriptions_plan_type_check CHECK (plan_type IN ('free', 'plus', 'pro', 'super_admin'));

-- Verify success
SELECT 'Constraint fixed - super_admin plan type now allowed' as status;