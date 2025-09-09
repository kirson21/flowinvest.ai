-- Welcome Balance and AI Billing System Schema
-- This script adds $3 welcome balance for new users and AI token billing functionality

-- 1. Add welcome balance to existing users who have $0 balance
UPDATE user_accounts 
SET balance_usd = 3.00 
WHERE balance_usd = 0.00 OR balance_usd IS NULL;

-- 2. Create trigger function to give $3 welcome balance to new users
CREATE OR REPLACE FUNCTION give_welcome_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Give $3 welcome balance to new users
    INSERT INTO user_accounts (user_id, balance_usd, created_at, updated_at)
    VALUES (NEW.id, 3.00, NOW(), NOW())
    ON CONFLICT (user_id) 
    DO UPDATE SET 
        balance_usd = CASE 
            WHEN user_accounts.balance_usd = 0 THEN 3.00 
            ELSE user_accounts.balance_usd 
        END,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Create trigger on user registration (assuming auth.users table or similar)
-- Note: This might need adjustment based on your auth system
DROP TRIGGER IF EXISTS welcome_balance_trigger ON auth.users;
CREATE TRIGGER welcome_balance_trigger
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION give_welcome_balance();

-- 4. Create AI billing transactions table
CREATE TABLE IF NOT EXISTS ai_billing_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL,
    ai_model TEXT NOT NULL,
    message_content TEXT,
    tokens_used INTEGER DEFAULT 1,
    cost_usd DECIMAL(10, 4) NOT NULL DEFAULT 0.10,
    transaction_type TEXT DEFAULT 'ai_chat_message',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_ai_billing_user_id ON ai_billing_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_billing_session ON ai_billing_transactions(session_id);

-- 5. Row Level Security for ai_billing_transactions
ALTER TABLE ai_billing_transactions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own billing transactions
DROP POLICY IF EXISTS "Users can view own billing transactions" ON ai_billing_transactions;
CREATE POLICY "Users can view own billing transactions"
    ON ai_billing_transactions FOR ALL
    USING (auth.uid() = user_id);

-- 6. Function to deduct AI usage cost from user balance
CREATE OR REPLACE FUNCTION deduct_ai_usage_cost(
    p_user_id UUID,
    p_session_id TEXT,
    p_ai_model TEXT,
    p_message_content TEXT DEFAULT '',
    p_cost_usd DECIMAL DEFAULT 0.10
)
RETURNS TABLE (
    success BOOLEAN,
    new_balance DECIMAL,
    transaction_id UUID,
    error_message TEXT
) AS $$
DECLARE
    v_current_balance DECIMAL;
    v_new_transaction_id UUID;
    v_new_balance DECIMAL;
BEGIN
    -- Get current user balance
    SELECT balance_usd INTO v_current_balance
    FROM user_accounts
    WHERE user_id = p_user_id;
    
    -- Check if user has sufficient balance
    IF v_current_balance IS NULL THEN
        RETURN QUERY SELECT FALSE, 0.00::DECIMAL, NULL::UUID, 'User account not found'::TEXT;
        RETURN;
    END IF;
    
    IF v_current_balance < p_cost_usd THEN
        RETURN QUERY SELECT FALSE, v_current_balance, NULL::UUID, 'Insufficient balance for AI usage'::TEXT;
        RETURN;
    END IF;
    
    -- Deduct cost from user balance
    UPDATE user_accounts 
    SET balance_usd = balance_usd - p_cost_usd,
        updated_at = NOW()
    WHERE user_id = p_user_id;
    
    -- Get new balance
    SELECT balance_usd INTO v_new_balance
    FROM user_accounts 
    WHERE user_id = p_user_id;
    
    -- Create billing transaction record
    INSERT INTO ai_billing_transactions (
        user_id, session_id, ai_model, message_content, 
        tokens_used, cost_usd, transaction_type, created_at, updated_at
    ) VALUES (
        p_user_id, p_session_id, p_ai_model, SUBSTRING(p_message_content, 1, 500),
        1, p_cost_usd, 'ai_chat_message', NOW(), NOW()
    )
    RETURNING id INTO v_new_transaction_id;
    
    RETURN QUERY SELECT TRUE, v_new_balance, v_new_transaction_id, NULL::TEXT;
END;
$$ LANGUAGE plpgsql;

-- 7. Function to check user balance for AI usage
CREATE OR REPLACE FUNCTION check_ai_usage_balance(p_user_id UUID, p_required_cost DECIMAL DEFAULT 0.10)
RETURNS TABLE (
    has_sufficient_balance BOOLEAN,
    current_balance DECIMAL,
    required_cost DECIMAL
) AS $$
DECLARE
    v_balance DECIMAL;
BEGIN
    SELECT balance_usd INTO v_balance
    FROM user_accounts
    WHERE user_id = p_user_id;
    
    IF v_balance IS NULL THEN
        v_balance := 0.00;
    END IF;
    
    RETURN QUERY SELECT 
        (v_balance >= p_required_cost), 
        v_balance, 
        p_required_cost;
END;
$$ LANGUAGE plpgsql;

-- 8. Create RPC functions for frontend access
-- Function to get user balance
CREATE OR REPLACE FUNCTION get_user_balance_for_ai()
RETURNS TABLE (
    balance_usd DECIMAL,
    has_sufficient_funds BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ua.balance_usd,
        (ua.balance_usd >= 0.10) as has_sufficient_funds
    FROM user_accounts ua
    WHERE ua.user_id = auth.uid();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant access to authenticated users
GRANT EXECUTE ON FUNCTION get_user_balance_for_ai() TO authenticated;
GRANT EXECUTE ON FUNCTION check_ai_usage_balance(UUID, DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION deduct_ai_usage_cost(UUID, TEXT, TEXT, TEXT, DECIMAL) TO authenticated;