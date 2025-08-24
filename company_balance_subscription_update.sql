-- Function to update company balance with subscription revenue
-- This function will be called when subscription payments are processed

CREATE OR REPLACE FUNCTION update_company_balance_subscription(subscription_revenue DECIMAL)
RETURNS JSON AS $$
DECLARE
    current_balance RECORD;
    result JSON;
BEGIN
    -- Get current company balance
    SELECT company_funds, total_deposits, total_fees_earned 
    INTO current_balance 
    FROM company_balance 
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    -- Update company balance with subscription revenue
    UPDATE company_balance 
    SET 
        company_funds = company_funds + subscription_revenue,
        total_deposits = total_deposits + subscription_revenue,
        total_fees_earned = total_fees_earned + subscription_revenue,
        last_updated = NOW()
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    -- Return success result
    result := json_build_object(
        'success', true,
        'subscription_revenue_added', subscription_revenue,
        'previous_company_funds', current_balance.company_funds,
        'new_company_funds', current_balance.company_funds + subscription_revenue
    );
    
    RETURN result;
    
EXCEPTION WHEN OTHERS THEN
    -- Return error result
    result := json_build_object(
        'success', false,
        'error', SQLERRM
    );
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to service role
GRANT EXECUTE ON FUNCTION update_company_balance_subscription(DECIMAL) TO service_role;