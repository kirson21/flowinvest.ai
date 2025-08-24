-- Enhanced Data Structure for Company Balance and Commissions
-- Phase 1: Database Schema Enhancements

-- 1. Enhanced Company Balance with Monthly Reports
ALTER TABLE company_balance 
ADD COLUMN IF NOT EXISTS total_subscription_revenue DECIMAL(15,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create monthly balance reports table
CREATE TABLE IF NOT EXISTS company_balance_monthly (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    report_month DATE NOT NULL, -- First day of the month (e.g., 2025-08-01)
    total_revenue DECIMAL(15,2) DEFAULT 0.00,
    subscription_revenue DECIMAL(15,2) DEFAULT 0.00,
    deposit_revenue DECIMAL(15,2) DEFAULT 0.00,
    commission_revenue DECIMAL(15,2) DEFAULT 0.00,
    total_users INTEGER DEFAULT 0,
    active_subscribers INTEGER DEFAULT 0,
    new_signups INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add unique constraint for monthly reports
ALTER TABLE company_balance_monthly
ADD CONSTRAINT unique_monthly_report UNIQUE (report_month);

-- 2. Create Commissions Table
CREATE TABLE IF NOT EXISTS commissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    commission_type VARCHAR(50) NOT NULL, -- 'referral', 'marketplace_sale', 'subscription_share', etc.
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    source_transaction_id UUID, -- Reference to original transaction
    commission_rate DECIMAL(5,4), -- e.g., 0.1500 for 15%
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'paid', 'cancelled'
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE NULL
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_commissions_user_id ON commissions(user_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON commissions(status);
CREATE INDEX IF NOT EXISTS idx_commissions_type ON commissions(commission_type);
CREATE INDEX IF NOT EXISTS idx_commissions_created_at ON commissions(created_at);
CREATE INDEX IF NOT EXISTS idx_company_balance_monthly_month ON company_balance_monthly(report_month);

-- Enable RLS
ALTER TABLE commissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_balance_monthly ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Commissions
CREATE POLICY "Users can view their own commissions" ON commissions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all commissions" ON commissions
    FOR ALL USING (
        current_setting('role') = 'service_role' OR 
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
    );

-- RLS Policies for Monthly Reports (admin only)
CREATE POLICY "Service role can manage monthly reports" ON company_balance_monthly
    FOR ALL USING (
        current_setting('role') = 'service_role' OR 
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
    );

-- Functions for automated monthly reporting
CREATE OR REPLACE FUNCTION generate_monthly_report(report_month DATE)
RETURNS JSON AS $$
DECLARE
    month_start DATE := date_trunc('month', report_month);
    month_end DATE := month_start + interval '1 month' - interval '1 day';
    total_revenue DECIMAL(15,2) := 0;
    subscription_revenue DECIMAL(15,2) := 0;
    commission_revenue DECIMAL(15,2) := 0;
    total_users INTEGER := 0;
    active_subscribers INTEGER := 0;
    new_signups INTEGER := 0;
    result JSON;
BEGIN
    -- Calculate subscription revenue for the month
    SELECT COALESCE(SUM(price_paid::DECIMAL), 0) INTO subscription_revenue
    FROM subscriptions 
    WHERE created_at >= month_start AND created_at <= month_end + interval '1 day'
    AND status = 'active';
    
    -- Calculate commission revenue for the month
    SELECT COALESCE(SUM(amount), 0) INTO commission_revenue
    FROM commissions 
    WHERE created_at >= month_start AND created_at <= month_end + interval '1 day'
    AND status = 'paid';
    
    -- Total revenue is subscription + commissions for now
    total_revenue := subscription_revenue + commission_revenue;
    
    -- Count total users (registered by end of month)
    SELECT COUNT(*) INTO total_users
    FROM auth.users 
    WHERE created_at <= month_end + interval '1 day';
    
    -- Count active subscribers (active at end of month)
    SELECT COUNT(*) INTO active_subscribers
    FROM subscriptions s
    WHERE s.status = 'active' 
    AND s.end_date > month_end;
    
    -- Count new signups in the month
    SELECT COUNT(*) INTO new_signups
    FROM auth.users 
    WHERE created_at >= month_start AND created_at <= month_end + interval '1 day';
    
    -- Insert or update monthly report
    INSERT INTO company_balance_monthly (
        report_month, total_revenue, subscription_revenue, 
        commission_revenue, total_users, active_subscribers, new_signups
    ) VALUES (
        month_start, total_revenue, subscription_revenue,
        commission_revenue, total_users, active_subscribers, new_signups
    ) ON CONFLICT (report_month) 
    DO UPDATE SET
        total_revenue = EXCLUDED.total_revenue,
        subscription_revenue = EXCLUDED.subscription_revenue,
        commission_revenue = EXCLUDED.commission_revenue,
        total_users = EXCLUDED.total_users,
        active_subscribers = EXCLUDED.active_subscribers,
        new_signups = EXCLUDED.new_signups,
        updated_at = NOW();
    
    -- Return summary
    result := json_build_object(
        'success', true,
        'report_month', month_start,
        'total_revenue', total_revenue,
        'subscription_revenue', subscription_revenue,
        'commission_revenue', commission_revenue,
        'total_users', total_users,
        'active_subscribers', active_subscribers,
        'new_signups', new_signups
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update commissions table when users earn commissions
CREATE OR REPLACE FUNCTION add_user_commission(
    p_user_id UUID,
    p_commission_type VARCHAR(50),
    p_amount DECIMAL(15,2),
    p_description TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'
)
RETURNS JSON AS $$
DECLARE
    commission_id UUID;
    result JSON;
BEGIN
    INSERT INTO commissions (
        user_id, commission_type, amount, description, metadata, status
    ) VALUES (
        p_user_id, p_commission_type, p_amount, p_description, p_metadata, 'approved'
    ) RETURNING id INTO commission_id;
    
    result := json_build_object(
        'success', true,
        'commission_id', commission_id,
        'user_id', p_user_id,
        'amount', p_amount,
        'type', p_commission_type
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create triggers to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_commissions_updated_at
    BEFORE UPDATE ON commissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_balance_monthly_updated_at
    BEFORE UPDATE ON company_balance_monthly
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON commissions TO postgres, service_role;
GRANT ALL ON company_balance_monthly TO postgres, service_role;
GRANT EXECUTE ON FUNCTION generate_monthly_report(DATE) TO service_role;
GRANT EXECUTE ON FUNCTION add_user_commission(UUID, VARCHAR, DECIMAL, TEXT, JSONB) TO service_role;