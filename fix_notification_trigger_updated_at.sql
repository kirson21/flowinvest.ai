-- Fix notification trigger - Remove all updated_at references
-- Run this in Supabase SQL Editor

-- First, let's see what columns actually exist in user_notifications
-- You can run this to check: SELECT column_name FROM information_schema.columns WHERE table_name = 'user_notifications';

-- Drop and recreate the trigger function without any updated_at references
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
        
        -- Create success notification (only use columns that exist)
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
        
        -- Create rejection notification (only use columns that exist)
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

-- Also check and fix any RLS policies that might reference updated_at
-- Drop and recreate RLS policies without updated_at references
DROP POLICY IF EXISTS "Users can update own notifications" ON user_notifications;

-- Recreate the policy without updated_at column reference
CREATE POLICY "Users can update own notifications" ON user_notifications
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);