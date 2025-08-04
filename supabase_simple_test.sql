INSERT INTO user_votes (user_id, product_id, vote_type) VALUES ('cd0e9717-f85d-4726-81e9-f260394ead58', 'test123', 'upvote');
SELECT * FROM user_votes WHERE product_id = 'test123';
DELETE FROM user_votes WHERE product_id = 'test123';