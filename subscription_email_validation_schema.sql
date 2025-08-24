-- Email Validation Table for NowPayments Subscriptions
-- This table will store email-to-user mappings for subscription validation

-- Create the subscription_email_validation table
CREATE TABLE IF NOT EXISTS subscription_email_validation (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) NOT NULL DEFAULT 'plus',
    amount DECIMAL(10,2) NOT NULL DEFAULT 10.00,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    nowpayments_subscription_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour')
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscription_email_validation_user_id ON subscription_email_validation(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_email_validation_email ON subscription_email_validation(email);
CREATE INDEX IF NOT EXISTS idx_subscription_email_validation_status ON subscription_email_validation(status);
CREATE INDEX IF NOT EXISTS idx_subscription_email_validation_nowpayments_id ON subscription_email_validation(nowpayments_subscription_id);

-- Enable RLS
ALTER TABLE subscription_email_validation ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own subscription email validations" ON subscription_email_validation
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own subscription email validations" ON subscription_email_validation
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own subscription email validations" ON subscription_email_validation
    FOR UPDATE USING (auth.uid() = user_id);

-- Service role can do anything (for webhook processing)
CREATE POLICY "Service role can manage all subscription email validations" ON subscription_email_validation
    FOR ALL USING (
        current_setting('role') = 'service_role' OR 
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
    );

-- Function to clean expired validation records
CREATE OR REPLACE FUNCTION cleanup_expired_subscription_validations()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    DELETE FROM subscription_email_validation
    WHERE status = 'pending' AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_subscription_email_validation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_subscription_email_validation_updated_at
    BEFORE UPDATE ON subscription_email_validation
    FOR EACH ROW
    EXECUTE FUNCTION update_subscription_email_validation_updated_at();

-- Grant permissions
GRANT ALL ON subscription_email_validation TO postgres, service_role;
GRANT USAGE ON SEQUENCE subscription_email_validation_id_seq TO postgres, service_role;