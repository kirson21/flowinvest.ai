-- =====================================================
-- FIX COMPANY BALANCE SYNC FUNCTION
-- =====================================================
-- Fixes the type casting issue in sync_company_balance_user_funds

-- Fix the company balance synchronization function
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

-- Also create a manual function to sync company balance immediately
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
        'message', 'Company balance synced successfully'
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Test the manual sync function
SELECT manual_sync_company_balance();