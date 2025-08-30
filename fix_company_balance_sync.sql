-- =====================================================
-- FIX COMPANY BALANCE - USER FUNDS SYNCHRONIZATION
-- =====================================================
-- Sync user_funds in company_balance with actual user balances

-- Create function to calculate total user funds from user_accounts
CREATE OR REPLACE FUNCTION calculate_total_user_funds()
RETURNS DECIMAL(12,2) AS $$
DECLARE
    total_funds DECIMAL(12,2);
BEGIN
    SELECT COALESCE(SUM(balance), 0)
    INTO total_funds
    FROM public.user_accounts
    WHERE balance > 0;
    
    RETURN total_funds;
END;
$$ LANGUAGE plpgsql;

-- Create function to sync user_funds in company_balance
CREATE OR REPLACE FUNCTION sync_company_balance_user_funds()
RETURNS JSON AS $$
DECLARE
    current_user_funds DECIMAL(12,2);
    result JSON;
BEGIN
    -- Calculate total user funds
    current_user_funds := calculate_total_user_funds();
    
    -- Update company_balance table
    UPDATE public.company_balance
    SET 
        user_funds = current_user_funds,
        updated_at = NOW()
    WHERE id = (SELECT id FROM public.company_balance ORDER BY created_at DESC LIMIT 1);
    
    -- If no company_balance record exists, create one
    IF NOT FOUND THEN
        INSERT INTO public.company_balance (user_funds, marketplace_fees, subscription_revenue, created_at, updated_at)
        VALUES (current_user_funds, 0, 0, NOW(), NOW());
    END IF;
    
    result := json_build_object(
        'success', true,
        'total_user_funds', current_user_funds,
        'synced_at', NOW()
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically sync user_funds when user_accounts changes
CREATE OR REPLACE FUNCTION trigger_sync_user_funds()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM sync_company_balance_user_funds();
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Add trigger to user_accounts table
DROP TRIGGER IF EXISTS sync_user_funds_trigger ON public.user_accounts;
CREATE TRIGGER sync_user_funds_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.user_accounts
    FOR EACH ROW
    EXECUTE FUNCTION trigger_sync_user_funds();

-- Immediately sync current user funds
SELECT sync_company_balance_user_funds();

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Check current sync status:
-- SELECT 
--     (SELECT SUM(balance) FROM public.user_accounts WHERE balance > 0) as actual_user_funds,
--     (SELECT user_funds FROM public.company_balance ORDER BY created_at DESC LIMIT 1) as company_balance_user_funds;

-- Test the sync function:
-- SELECT sync_company_balance_user_funds();