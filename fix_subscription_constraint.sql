-- =====================================================
-- Fix Subscription Plan Type Constraint Error
-- =====================================================

-- Drop the existing constraint that doesn't include 'super_admin'
ALTER TABLE public.subscriptions 
DROP CONSTRAINT IF EXISTS subscriptions_plan_type_check;

-- Add the updated constraint that includes 'super_admin'
ALTER TABLE public.subscriptions 
ADD CONSTRAINT subscriptions_plan_type_check 
CHECK (plan_type IN ('free', 'plus', 'pro', 'super_admin'));

-- Verify the fix
SELECT 'Constraint updated successfully - super_admin plan type now allowed' as status;

-- Show current constraint definition
SELECT 
    conname as constraint_name,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conname = 'subscriptions_plan_type_check';