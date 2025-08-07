-- Minimal fix for notification issues
-- Run this in Supabase SQL Editor

-- Alternative approach: Disable the trigger temporarily to see if that fixes mark-as-read
DROP TRIGGER IF EXISTS verification_status_update_trigger ON seller_verification_applications;

-- Create a simpler version that only updates user profiles (no notifications for now)
CREATE OR REPLACE FUNCTION update_user_verification_status_simple()
RETURNS TRIGGER 
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Only update user profile verification status (no notifications to avoid column issues)
    IF NEW.status = 'approved' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'verified'
        WHERE user_id = NEW.user_id;
        
    ELSIF NEW.status = 'rejected' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'rejected'
        WHERE user_id = NEW.user_id;
        
    ELSIF NEW.status = 'pending' AND OLD.status IS NULL THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'pending'
        WHERE user_id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create new trigger with the simple function
CREATE TRIGGER verification_status_update_trigger_simple
    AFTER INSERT OR UPDATE ON seller_verification_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_user_verification_status_simple();

-- This will allow approval to work and enable seller mode
-- Notifications can be handled separately without trigger conflicts