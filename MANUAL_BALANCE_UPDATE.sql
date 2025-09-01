-- =====================================================
-- MANUAL BALANCE UPDATE (BYPASS TRIGGER)
-- =====================================================
-- Update user balance manually without triggering the problematic sync function

-- Temporarily disable the trigger
ALTER TABLE public.user_accounts DISABLE TRIGGER sync_company_balance_trigger;

-- Update the user balance for the successful $20 withdrawal
UPDATE public.user_accounts 
SET balance = balance - 20.00,
    updated_at = NOW()
WHERE user_id = '621b42ef-1c97-409b-b3d9-18fc83d0e9d8';

-- Check the updated balance
SELECT user_id, balance, updated_at, currency
FROM public.user_accounts 
WHERE user_id = '621b42ef-1c97-409b-b3d9-18fc83d0e9d8';

-- Re-enable the trigger after fixing it
ALTER TABLE public.user_accounts ENABLE TRIGGER sync_company_balance_trigger;