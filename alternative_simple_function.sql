CREATE OR REPLACE FUNCTION get_users_emails_simple()
RETURNS TABLE (
    user_id UUID,
    email TEXT,
    created_at TIMESTAMPTZ
) 
SECURITY DEFINER
LANGUAGE plpgsql
AS '
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
';