-- Simple fix: Remove the problematic trigger causing updated_at error
DROP TRIGGER IF EXISTS update_user_notifications_updated_at ON user_notifications;

-- Remove the function causing the issue
DROP FUNCTION IF EXISTS update_updated_at_column();