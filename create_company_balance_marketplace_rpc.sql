-- Create function to update company balance with marketplace fees and user funds tracking
CREATE OR REPLACE FUNCTION public.update_company_balance_marketplace(
    platform_fee_amount DECIMAL(20, 2)
)
RETURNS JSONB AS $$
DECLARE
    current_record RECORD;
    total_user_balances DECIMAL(20, 2) := 0;
    result JSONB;
BEGIN
    -- Calculate total user funds from all user accounts
    SELECT COALESCE(SUM(balance), 0) INTO total_user_balances
    FROM public.user_accounts
    WHERE balance > 0;
    
    -- Get current company balance record
    SELECT * INTO current_record
    FROM public.company_balance
    WHERE id = '00000000-0000-0000-0000-000000000001';
    
    IF NOT FOUND THEN
        -- Create initial record if it doesn't exist
        INSERT INTO public.company_balance (
            id,
            company_funds,
            user_funds,
            total_deposits,
            total_withdrawals,
            total_fees_earned,
            total_subscription_revenue,
            currency,
            last_updated
        ) VALUES (
            '00000000-0000-0000-0000-000000000001',
            platform_fee_amount,
            total_user_balances,
            0,
            0,
            platform_fee_amount,
            0,
            'USD',
            NOW()
        );
        
        RETURN jsonb_build_object(
            'success', true,
            'platform_fee_added', platform_fee_amount,
            'previous_fees_earned', 0,
            'new_fees_earned', platform_fee_amount,
            'previous_company_funds', 0,
            'new_company_funds', platform_fee_amount,
            'current_user_funds', total_user_balances
        );
    ELSE
        -- Update existing record
        UPDATE public.company_balance
        SET 
            company_funds = company_funds + platform_fee_amount,
            user_funds = total_user_balances,
            total_fees_earned = total_fees_earned + platform_fee_amount,
            last_updated = NOW()
        WHERE id = '00000000-0000-0000-0000-000000000001';
        
        RETURN jsonb_build_object(
            'success', true,
            'platform_fee_added', platform_fee_amount,
            'previous_fees_earned', current_record.total_fees_earned,
            'new_fees_earned', current_record.total_fees_earned + platform_fee_amount,
            'previous_company_funds', current_record.company_funds,
            'new_company_funds', current_record.company_funds + platform_fee_amount,
            'current_user_funds', total_user_balances
        );
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION public.update_company_balance_marketplace(DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_company_balance_marketplace(DECIMAL) TO service_role;