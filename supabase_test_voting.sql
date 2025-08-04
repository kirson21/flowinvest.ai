-- TEST VOTING FUNCTIONALITY
-- This will verify that voting now works properly

-- Test 1: Insert a vote (should work now!)
INSERT INTO user_votes (user_id, product_id, vote_type) 
VALUES ('cd0e9717-f85d-4726-81e9-f260394ead58', 'test-final-vote-123', 'upvote');

-- Test 2: Check if it was inserted
SELECT * FROM user_votes WHERE product_id = 'test-final-vote-123';

-- Test 3: Update the vote
UPDATE user_votes 
SET vote_type = 'downvote' 
WHERE product_id = 'test-final-vote-123' 
AND user_id = 'cd0e9717-f85d-4726-81e9-f260394ead58';

-- Test 4: Verify the update
SELECT * FROM user_votes WHERE product_id = 'test-final-vote-123';

-- Test 5: Clean up test vote
DELETE FROM user_votes WHERE product_id = 'test-final-vote-123';

-- Test 6: Confirm cleanup
SELECT COUNT(*) as remaining_test_votes FROM user_votes WHERE product_id = 'test-final-vote-123';