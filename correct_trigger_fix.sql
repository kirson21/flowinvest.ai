-- Correct fix: Only remove the trigger from user_notifications table
-- Keep the function since other tables need it
DROP TRIGGER IF EXISTS update_user_notifications_updated_at ON user_notifications;