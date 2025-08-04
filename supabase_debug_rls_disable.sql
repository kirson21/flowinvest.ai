-- Temporary fix: Disable RLS on user_votes table to debug API key errors
-- This is for debugging purposes only

-- Check if user_votes table exists
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_votes') THEN
        -- Temporarily disable RLS on user_votes table
        ALTER TABLE user_votes DISABLE ROW LEVEL SECURITY;
        
        -- Make the table accessible to anon users temporarily
        GRANT SELECT, INSERT, UPDATE, DELETE ON user_votes TO anon;
        
        RAISE NOTICE 'RLS disabled on user_votes table for debugging';
    ELSE
        RAISE NOTICE 'user_votes table does not exist';
    END IF;
END $$;

-- Check if seller_reviews table exists
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'seller_reviews') THEN
        -- Temporarily disable RLS on seller_reviews table
        ALTER TABLE seller_reviews DISABLE ROW LEVEL SECURITY;
        
        -- Make the table accessible to anon users temporarily
        GRANT SELECT, INSERT, UPDATE, DELETE ON seller_reviews TO anon;
        
        RAISE NOTICE 'RLS disabled on seller_reviews table for debugging';
    ELSE
        RAISE NOTICE 'seller_reviews table does not exist';
    END IF;
END $$;

-- Check if portfolios table vote columns exist
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'portfolios' AND column_name = 'vote_count_upvotes') THEN
        RAISE NOTICE 'Portfolios table has vote count columns';
    ELSE
        RAISE NOTICE 'Portfolios table missing vote count columns';
    END IF;
END $$;