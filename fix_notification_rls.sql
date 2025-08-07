-- Fix RLS policies for user_notifications table
-- Run this in Supabase SQL Editor

-- Drop existing policies that might be blocking the trigger
DROP POLICY IF EXISTS "Users can view own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can create own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Super admin can manage all notifications" ON user_notifications;

-- Create new RLS policies for user_notifications
-- Users can view their own notifications
CREATE POLICY "Users can view own notifications" ON user_notifications
    FOR SELECT USING (auth.uid() = user_id);

-- Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications" ON user_notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- Super admin can view all notifications
CREATE POLICY "Super admin can view all notifications" ON user_notifications
    FOR SELECT USING (
        auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
    );

-- Super admin can create notifications for any user (needed for verification approval)
CREATE POLICY "Super admin can create all notifications" ON user_notifications
    FOR INSERT WITH CHECK (
        auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
    );

-- Allow system triggers to create notifications (this is the key fix)
-- Create a policy that allows notifications to be created by the database trigger
CREATE POLICY "System can create notifications" ON user_notifications
    FOR INSERT WITH CHECK (true);

-- Alternative approach: Make the trigger function run with SECURITY DEFINER
-- This allows the trigger to bypass RLS policies
CREATE OR REPLACE FUNCTION update_user_verification_status()
RETURNS TRIGGER 
SECURITY DEFINER  -- This is the key addition
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update user profile verification status when application status changes
    IF NEW.status = 'approved' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'verified'
        WHERE user_id = NEW.user_id;
        
        -- Create success notification (runs with elevated privileges)
        INSERT INTO user_notifications (user_id, title, message, type)
        VALUES (
            NEW.user_id,
            'Seller Verification Approved!',
            'Congratulations! Your seller verification has been approved. You now have access to all seller features including product creation and seller mode.',
            'success'
        );
        
    ELSIF NEW.status = 'rejected' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'rejected'
        WHERE user_id = NEW.user_id;
        
        -- Create rejection notification (runs with elevated privileges)
        INSERT INTO user_notifications (user_id, title, message, type)
        VALUES (
            NEW.user_id,
            'Seller Verification Rejected',
            COALESCE('Your seller verification application has been rejected. Reason: ' || NEW.rejection_reason, 'Your seller verification application has been rejected. Please contact support for more information.'),
            'error'
        );
        
    ELSIF NEW.status = 'pending' AND OLD.status IS NULL THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'pending'
        WHERE user_id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$;