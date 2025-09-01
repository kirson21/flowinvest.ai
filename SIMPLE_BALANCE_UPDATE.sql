-- =====================================================
-- SIMPLE BALANCE UPDATE FOR WITHDRAWAL
-- =====================================================
-- Just update the user balance without triggering any functions

-- Update the user balance for the successful $20 withdrawal
UPDATE public.user_accounts 
SET balance = CASE 
    WHEN balance >= 20.00 THEN balance - 20.00 
    ELSE 0.00 
END,
updated_at = NOW()
WHERE user_id = '621b42ef-1c97-409b-b3d9-18fc83d0e9d8';

-- Check the updated balance
SELECT 
    user_id, 
    balance, 
    currency,
    updated_at 
FROM public.user_accounts 
WHERE user_id = '621b42ef-1c97-409b-b3d9-18fc83d0e9d8';

-- Show what the balance change was
SELECT 
    '621b42ef-1c97-409b-b3d9-18fc83d0e9d8' as user_id,
    'Balance updated for $20 USDT withdrawal' as action,
    NOW() as timestamp;