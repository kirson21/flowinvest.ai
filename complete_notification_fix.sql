-- Complete fix for user_notifications based on actual schema
-- Run this in Supabase SQL Editor

-- Fix the trigger function to use correct column names
CREATE OR REPLACE FUNCTION update_user_verification_status()
RETURNS TRIGGER 
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update user profile verification status when application status changes
    IF NEW.status = 'approved' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'verified'
        WHERE user_id = NEW.user_id;
        
        -- Create success notification using correct column names
        INSERT INTO user_notifications (user_id, title, message, type, is_read, created_at)
        VALUES (
            NEW.user_id,
            'Seller Verification Approved!',
            'Congratulations! Your seller verification has been approved. You now have access to all seller features including product creation and seller mode.',
            'success',
            false,
            NOW()
        );
        
    ELSIF NEW.status = 'rejected' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'rejected'
        WHERE user_id = NEW.user_id;
        
        -- Create rejection notification using correct column names
        INSERT INTO user_notifications (user_id, title, message, type, is_read, created_at)
        VALUES (
            NEW.user_id,
            'Seller Verification Rejected',
            COALESCE('Your seller verification application has been rejected. Reason: ' || NEW.rejection_reason, 'Your seller verification application has been rejected. Please contact support for more information.'),
            'error',
            false,
            NOW()
        );
        
    ELSIF NEW.status = 'pending' AND OLD.status IS NULL THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'pending'
        WHERE user_id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Ensure the trigger exists
DROP TRIGGER IF EXISTS verification_status_update_trigger ON seller_verification_applications;
CREATE TRIGGER verification_status_update_trigger
    AFTER INSERT OR UPDATE ON seller_verification_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_user_verification_status();

-- Fix RLS policies for user_notifications to match actual schema
DROP POLICY IF EXISTS "Users can update own notifications" ON user_notifications;
CREATE POLICY "Users can update own notifications" ON user_notifications
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);