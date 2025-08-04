-- Minimal RLS disable for debugging voting issues

ALTER TABLE user_votes DISABLE ROW LEVEL SECURITY;

GRANT ALL ON user_votes TO anon;

ALTER TABLE seller_reviews DISABLE ROW LEVEL SECURITY;

GRANT ALL ON seller_reviews TO anon;

GRANT SELECT ON portfolios TO anon;

GRANT ALL ON user_votes TO authenticated;

GRANT ALL ON seller_reviews TO authenticated;