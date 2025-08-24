-- Add subscription revenue column to company_balance table
ALTER TABLE company_balance 
ADD COLUMN IF NOT EXISTS total_subscription_revenue DECIMAL(15,2) DEFAULT 0.00;

-- Update the existing record to initialize the column
UPDATE company_balance 
SET total_subscription_revenue = 0.00 
WHERE id = '00000000-0000-0000-0000-000000000001';

-- Update the function to include subscription revenue tracking
CREATE OR REPLACE FUNCTION update_company_balance_subscription(subscription_revenue DECIMAL)
RETURNS JSON AS $$
DECLARE
    current_balance RECORD;
    result JSON;
BEGIN
    -- Get current company balance
    SELECT company_funds, total_deposits, total_fees_earned, total_subscription_revenue
    INTO current_balance 
    FROM company_balance 
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    -- Update company balance with subscription revenue
    UPDATE company_balance 
    SET 
        company_funds = company_funds + subscription_revenue,
        total_subscription_revenue = total_subscription_revenue + subscription_revenue,
        total_fees_earned = total_fees_earned + subscription_revenue,
        last_updated = NOW()
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    -- Return success result
    result := json_build_object(
        'success', true,
        'subscription_revenue_added', subscription_revenue,
        'previous_company_funds', current_balance.company_funds,
        'new_company_funds', current_balance.company_funds + subscription_revenue,
        'previous_subscription_revenue', current_balance.total_subscription_revenue,
        'new_subscription_revenue', current_balance.total_subscription_revenue + subscription_revenue
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