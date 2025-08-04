-- Simple test to check user_votes table schema
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'user_votes' 
ORDER BY column_name;