-- =====================================================
-- COMPLETE COMPANY BALANCE SYNC - FULL FIX
-- =====================================================
-- Fix user_funds sync with debugging and manual execution

-- Step 1: Check current data before fixing
DO $$
DECLARE
    current_user_total DECIMAL(12,2);
    current_company_funds DECIMAL(12,2);
BEGIN
    -- Calculate actual user funds total
    SELECT COALESCE(SUM(balance::DECIMAL), 0)
    INTO current_user_total
    FROM public.user_accounts
    WHERE balance IS NOT NULL AND balance != '0' AND balance != '0.00';
    
    -- Get current company balance user_funds
    SELECT COALESCE(user_funds::DECIMAL, 0)
    INTO current_company_funds
    FROM public.company_balance
    ORDER BY updated_at DESC LIMIT 1;
    
    RAISE NOTICE 'BEFORE FIX - Actual user funds: $%, Company balance user_funds: $%', current_user_total, current_company_funds;
END $$;

-- Step 2: Create improved sync function
-- Create function to calculate total user funds from user_accounts
CREATE OR REPLACE FUNCTION calculate_total_user_funds()
RETURNS DECIMAL(12,2) AS $$
DECLARE
    total_funds DECIMAL(12,2) := 0;
    user_record RECORD;
BEGIN
    -- Debug: Log each user balance (balance is NUMERIC type)
    FOR user_record IN 
        SELECT user_id, balance, currency 
        FROM public.user_accounts 
        WHERE balance IS NOT NULL 
        AND balance > 0
    LOOP
        total_funds := total_funds + user_record.balance;
        RAISE NOTICE 'User %: Balance $%', user_record.user_id, user_record.balance;
    END LOOP;
    
    RAISE NOTICE 'Total calculated user funds: $%', total_funds;
    RETURN total_funds;
END;
$$ LANGUAGE plpgsql;

-- Step 3: Create improved sync function
CREATE OR REPLACE FUNCTION sync_company_balance_user_funds()
RETURNS JSON AS $$
DECLARE
    current_user_funds DECIMAL(12,2);
    old_user_funds DECIMAL(12,2);
    update_count INTEGER;
    result JSON;
BEGIN
    -- Calculate total user funds
    current_user_funds := calculate_total_user_funds();
    
    -- Get old value for comparison
    SELECT COALESCE(user_funds::DECIMAL, 0)
    INTO old_user_funds
    FROM public.company_balance
    ORDER BY updated_at DESC LIMIT 1;
    
    RAISE NOTICE 'Syncing: Old user_funds: $%, New user_funds: $%', old_user_funds, current_user_funds;
    
    -- Update company_balance table
    UPDATE public.company_balance
    SET 
        user_funds = current_user_funds::TEXT,
        last_updated = NOW(),
        updated_at = NOW()
    WHERE id = (SELECT id FROM public.company_balance ORDER BY updated_at DESC LIMIT 1);
    
    GET DIAGNOSTICS update_count = ROW_COUNT;
    
    -- If no record was updated, create new one
    IF update_count = 0 THEN
        RAISE NOTICE 'No existing company_balance record found, creating new one';
        INSERT INTO public.company_balance (
            id,
            user_funds, 
            company_funds, 
            total_deposits, 
            total_withdrawals, 
            total_fees_earned, 
            currency, 
            last_updated, 
            updated_at,
            total_subscription_revenue
        )
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            current_user_funds::TEXT, 
            '0.00', 
            '0.00', 
            '0.00', 
            '0.00', 
            'USD', 
            NOW(), 
            NOW(),
            '0.00'
        );
    ELSE
        RAISE NOTICE 'Updated % company_balance record(s)', update_count;
    END IF;
    
    result := json_build_object(
        'success', true,
        'total_user_funds', current_user_funds,
        'old_user_funds', old_user_funds,
        'synced_at', NOW(),
        'records_updated', update_count
    );
    
    RAISE NOTICE 'Sync result: %', result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Step 4: Execute the sync immediately
SELECT sync_company_balance_user_funds() as sync_result;

-- Step 5: Create trigger for automatic future syncing
CREATE OR REPLACE FUNCTION trigger_sync_user_funds()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'User balance trigger fired - syncing company balance';
    PERFORM sync_company_balance_user_funds();
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Remove old trigger and add new one
DROP TRIGGER IF EXISTS sync_user_funds_trigger ON public.user_accounts;
CREATE TRIGGER sync_user_funds_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.user_accounts
    FOR EACH ROW
    EXECUTE FUNCTION trigger_sync_user_funds();

-- Step 6: Verify the fix worked
DO $$
DECLARE
    final_user_total DECIMAL(12,2);
    final_company_funds DECIMAL(12,2);
BEGIN
    -- Calculate actual user funds total
    SELECT COALESCE(SUM(balance::DECIMAL), 0)
    INTO final_user_total
    FROM public.user_accounts
    WHERE balance IS NOT NULL AND balance != '0' AND balance != '0.00';
    
    -- Get updated company balance user_funds
    SELECT COALESCE(user_funds::DECIMAL, 0)
    INTO final_company_funds
    FROM public.company_balance
    ORDER BY updated_at DESC LIMIT 1;
    
    RAISE NOTICE 'AFTER FIX - Actual user funds: $%, Company balance user_funds: $%', final_user_total, final_company_funds;
    
    IF final_user_total = final_company_funds THEN
        RAISE NOTICE '✅ SUCCESS: User funds are now properly synced!';
    ELSE
        RAISE NOTICE '❌ ISSUE: Sync may have failed. Check the sync function.';
    END IF;
END $$;