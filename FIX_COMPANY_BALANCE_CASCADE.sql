-- =====================================================
-- FIX COMPANY BALANCE WITH CASCADE DROP
-- =====================================================
-- Drops all dependent triggers and functions, then recreates them properly

-- First, drop all triggers that might depend on the functions
DROP TRIGGER IF EXISTS sync_company_balance_trigger ON public.user_accounts CASCADE;
DROP TRIGGER IF EXISTS sync_user_funds_trigger ON public.user_accounts CASCADE;

-- Now drop the functions (use CASCADE to handle any remaining dependencies)
DROP FUNCTION IF EXISTS sync_company_balance_user_funds() CASCADE;
DROP FUNCTION IF EXISTS trigger_sync_user_funds() CASCADE;

-- Recreate the fixed company balance sync function
CREATE OR REPLACE FUNCTION sync_company_balance_user_funds()
RETURNS TRIGGER AS $$
BEGIN
    -- Update company_balance.user_funds with the sum of all user balances
    UPDATE public.company_balance 
    SET user_funds = (
        SELECT COALESCE(SUM(balance), 0)::NUMERIC
        FROM public.user_accounts 
        WHERE balance > 0
    ),
    last_updated = NOW(),
    updated_at = NOW()
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Recreate the trigger
CREATE TRIGGER sync_company_balance_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.user_accounts
    FOR EACH ROW EXECUTE FUNCTION sync_company_balance_user_funds();

-- Create a manual sync function for immediate testing
CREATE OR REPLACE FUNCTION manual_sync_company_balance()
RETURNS JSONB AS $$
DECLARE
    total_user_funds NUMERIC;
    result JSONB;
BEGIN
    -- Calculate total user funds
    SELECT COALESCE(SUM(balance), 0)::NUMERIC INTO total_user_funds
    FROM public.user_accounts 
    WHERE balance > 0;
    
    -- Update company balance
    UPDATE public.company_balance 
    SET user_funds = total_user_funds,
        last_updated = NOW(),
        updated_at = NOW()
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    -- Return result
    result := jsonb_build_object(
        'success', true,
        'total_user_funds', total_user_funds,
        'message', 'Company balance synced successfully',
        'timestamp', NOW()
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Now update the user balance for the $20 withdrawal
UPDATE public.user_accounts 
SET balance = GREATEST(balance - 20.00, 0.00),
    updated_at = NOW()
WHERE user_id = '621b42ef-1c97-409b-b3d9-18fc83d0e9d8';

-- Verify the balance was updated
SELECT 
    user_id, 
    balance, 
    currency,
    updated_at,
    'Balance updated after $20 withdrawal' as note
FROM public.user_accounts 
WHERE user_id = '621b42ef-1c97-409b-b3d9-18fc83d0e9d8';

-- Test the manual sync function
SELECT manual_sync_company_balance();

-- Show company balance after sync
SELECT 
    id,
    company_funds,
    user_funds,
    last_updated
FROM public.company_balance 
WHERE id = '00000000-0000-0000-0000-000000000001';