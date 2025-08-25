-- Supabase RPC Function to get all users with emails from auth.users table
-- This function allows us to access auth.users data and join it with other tables

CREATE OR REPLACE FUNCTION get_all_users_with_emails()
RETURNS TABLE (
    user_id UUID,
    email TEXT,
    created_at TIMESTAMPTZ,
    name TEXT,
    country TEXT,
    phone TEXT,
    seller_verification_status TEXT,
    plan_type TEXT,
    subscription_status TEXT,
    subscription_end_date DATE,
    total_commission_earned NUMERIC
) 
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        au.id as user_id,
        au.email::TEXT,
        au.created_at,
        COALESCE(up.name, '')::TEXT as name,
        COALESCE(up.country, '')::TEXT as country,
        COALESCE(up.phone, '')::TEXT as phone,
        COALESCE(up.seller_verification_status, 'not_verified')::TEXT as seller_verification_status,
        COALESCE(s.plan_type, 'free')::TEXT as plan_type,
        COALESCE(s.status, 'inactive')::TEXT as subscription_status,
        s.end_date as subscription_end_date,
        COALESCE(comm.total_commissions, 0) as total_commission_earned
    FROM 
        auth.users au
    LEFT JOIN 
        public.user_profiles up ON au.id = up.user_id
    LEFT JOIN 
        public.subscriptions s ON au.id = s.user_id
    LEFT JOIN (
        SELECT 
            user_id, 
            SUM(amount) as total_commissions
        FROM public.commissions 
        WHERE status = 'paid'
        GROUP BY user_id
    ) comm ON au.id = comm.user_id
    ORDER BY au.created_at DESC;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_all_users_with_emails() TO authenticated;
GRANT EXECUTE ON FUNCTION get_all_users_with_emails() TO service_role;

-- Create a simpler version for just getting user emails if the above is too complex
CREATE OR REPLACE FUNCTION get_users_emails_simple()
RETURNS TABLE (
    user_id UUID,
    email TEXT,
    created_at TIMESTAMPTZ
) 
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        au.id as user_id,
        au.email::TEXT,
        au.created_at
    FROM 
        auth.users au
    ORDER BY au.created_at DESC;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_users_emails_simple() TO authenticated;
GRANT EXECUTE ON FUNCTION get_users_emails_simple() TO service_role;

-- Test the functions (uncomment to test)
-- SELECT * FROM get_all_users_with_emails();
-- SELECT * FROM get_users_emails_simple();