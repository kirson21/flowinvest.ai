-- Create the missing update_user_balance RPC function
CREATE OR REPLACE FUNCTION public.update_user_balance(
    user_uuid UUID,
    amount_change DECIMAL(20, 2)
)
RETURNS JSONB AS $$
DECLARE
    current_balance DECIMAL(20, 2) := 0;
    new_balance DECIMAL(20, 2);
    result JSONB;
BEGIN
    -- Get current balance
    SELECT balance INTO current_balance
    FROM public.user_accounts
    WHERE user_id = user_uuid;
    
    -- If no account exists, create one
    IF NOT FOUND THEN
        INSERT INTO public.user_accounts (user_id, balance, currency)
        VALUES (user_uuid, amount_change, 'USD');
        
        new_balance := amount_change;
    ELSE
        -- Update existing balance
        new_balance := current_balance + amount_change;
        
        UPDATE public.user_accounts
        SET balance = new_balance,
            updated_at = NOW()
        WHERE user_id = user_uuid;
    END IF;
    
    RETURN jsonb_build_object(
        'success', true,
        'user_id', user_uuid,
        'previous_balance', current_balance,
        'amount_change', amount_change,
        'new_balance', new_balance,
        'currency', 'USD'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION public.update_user_balance(UUID, DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_user_balance(UUID, DECIMAL) TO service_role;