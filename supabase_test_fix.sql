-- TEST THE FIX
-- Run this after the bulletproof fix to test functionality

-- Insert test vote
INSERT INTO user_votes (user_id, product_id, vote_type) 
VALUES ('cd0e9717-f85d-4726-81e9-f260394ead58', 'test-product-123', 'upvote');

-- Check if it worked
SELECT * FROM user_votes WHERE product_id = 'test-product-123';

-- Clean up test vote
DELETE FROM user_votes WHERE product_id = 'test-product-123';