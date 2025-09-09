-- Simple Welcome Balance Update
-- Add $3 balance to existing users immediately

-- Update your specific user account
UPDATE user_accounts 
SET balance = 3.00, updated_at = NOW() 
WHERE user_id = 'cd0e9717-f85d-4726-81e9-f260394ead58';

-- Add $3 welcome balance to all existing users who have $0 or NULL balance
UPDATE user_accounts 
SET balance = 3.00, updated_at = NOW()
WHERE balance = 0.00 OR balance IS NULL;

-- For future new users, we'll handle this in the backend registration logic