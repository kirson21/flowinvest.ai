-- FINAL FIX: Remove the problematic trigger that's causing updated_at error
-- Run this in Supabase SQL Editor

-- Drop the trigger that's trying to update the non-existent updated_at column
DROP TRIGGER IF EXISTS update_user_notifications_updated_at ON user_notifications;

-- Also drop the trigger function if it's not used elsewhere
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Verify no more triggers exist on user_notifications table
-- (You can run this to check): SELECT trigger_name FROM information_schema.triggers WHERE event_object_table = 'user_notifications';

-- Optional: Recreate our verification trigger to make sure it's working
DROP TRIGGER IF EXISTS verification_status_update_trigger ON seller_verification_applications;

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
        
        -- Create success notification using only existing columns
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
        
        -- Create rejection notification using only existing columns
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

CREATE TRIGGER verification_status_update_trigger
    AFTER INSERT OR UPDATE ON seller_verification_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_user_verification_status();