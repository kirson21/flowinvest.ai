-- Create missing tables for voting system
-- Simple table creation without complex policies

-- Create user_votes table
CREATE TABLE user_votes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  product_id UUID NOT NULL,
  vote_type VARCHAR(10) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, product_id)
);

-- Create seller_reviews table  
CREATE TABLE seller_reviews (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  reviewer_id UUID NOT NULL,
  seller_name TEXT NOT NULL,
  seller_id UUID,
  rating INTEGER NOT NULL,
  review_text TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(reviewer_id, seller_name)
);

-- Add vote count columns to portfolios if they don't exist
ALTER TABLE portfolios 
ADD COLUMN IF NOT EXISTS vote_count_upvotes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS vote_count_downvotes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS vote_count_total INTEGER DEFAULT 0;

-- Disable RLS for now (we'll fix this later)
ALTER TABLE user_votes DISABLE ROW LEVEL SECURITY;
ALTER TABLE seller_reviews DISABLE ROW LEVEL SECURITY;

-- Grant all permissions for debugging
GRANT ALL ON user_votes TO anon, authenticated;
GRANT ALL ON seller_reviews TO anon, authenticated;