-- Comprehensive schema update for localStorage to Supabase migration - FIXED VERSION
-- This script adds all missing tables and columns needed for complete migration

-- 1. USER VOTES TABLE - Store individual user votes on products
CREATE TABLE IF NOT EXISTS user_votes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  product_id UUID NOT NULL, -- References portfolios.id
  vote_type VARCHAR(10) NOT NULL CHECK (vote_type IN ('upvote', 'downvote')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, product_id) -- One vote per user per product
);

-- Enable RLS for user_votes
ALTER TABLE user_votes ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist to avoid conflicts
DROP POLICY IF EXISTS "Users can view own votes" ON user_votes;
DROP POLICY IF EXISTS "Users can insert own votes" ON user_votes;
DROP POLICY IF EXISTS "Users can update own votes" ON user_votes;
DROP POLICY IF EXISTS "Users can delete own votes" ON user_votes;

-- RLS policies for user_votes
CREATE POLICY "Users can view own votes" 
ON user_votes FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own votes" 
ON user_votes FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own votes" 
ON user_votes FOR UPDATE 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own votes" 
ON user_votes FOR DELETE USING (auth.uid() = user_id);

-- 2. SELLER REVIEWS TABLE - Store reviews for sellers
CREATE TABLE IF NOT EXISTS seller_reviews (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  reviewer_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  seller_name TEXT NOT NULL,
  seller_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(reviewer_id, seller_name) -- One review per reviewer per seller
);

-- Enable RLS for seller_reviews
ALTER TABLE seller_reviews ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist to avoid conflicts
DROP POLICY IF EXISTS "Anyone can view reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Users can insert own reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Users can update own reviews" ON seller_reviews;
DROP POLICY IF EXISTS "Users can delete own reviews" ON seller_reviews;

-- RLS policies for seller_reviews (reviews are public to read, users can manage their own)
CREATE POLICY "Anyone can view reviews" 
ON seller_reviews FOR SELECT TO authenticated, anon USING (true);

CREATE POLICY "Users can insert own reviews" 
ON seller_reviews FOR INSERT WITH CHECK (auth.uid() = reviewer_id);

CREATE POLICY "Users can update own reviews" 
ON seller_reviews FOR UPDATE 
USING (auth.uid() = reviewer_id) WITH CHECK (auth.uid() = reviewer_id);

CREATE POLICY "Users can delete own reviews" 
ON seller_reviews FOR DELETE USING (auth.uid() = reviewer_id);

-- 3. Update user_profiles table with additional columns for social links and seller data
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS seller_data JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS seller_mode BOOLEAN DEFAULT false;

-- 4. Create user_notifications table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  type VARCHAR(50) DEFAULT 'info', -- info, success, warning, error
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for user_notifications if not already enabled
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist to avoid conflicts
DROP POLICY IF EXISTS "Users can view own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can insert own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON user_notifications;
DROP POLICY IF EXISTS "Users can delete own notifications" ON user_notifications;

-- RLS policies for user_notifications
CREATE POLICY "Users can view own notifications" 
ON user_notifications FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own notifications" 
ON user_notifications FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" 
ON user_notifications FOR UPDATE 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own notifications" 
ON user_notifications FOR DELETE USING (auth.uid() = user_id);

-- 5. Create user_accounts table for account balance if it doesn't exist
CREATE TABLE IF NOT EXISTS user_accounts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  balance DECIMAL(20, 8) DEFAULT 0.00,
  currency VARCHAR(10) DEFAULT 'USD',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Enable RLS for user_accounts
ALTER TABLE user_accounts ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist to avoid conflicts
DROP POLICY IF EXISTS "Users can view own account" ON user_accounts;
DROP POLICY IF EXISTS "Users can insert own account" ON user_accounts;
DROP POLICY IF EXISTS "Users can update own account" ON user_accounts;

-- RLS policies for user_accounts
CREATE POLICY "Users can view own account" 
ON user_accounts FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own account" 
ON user_accounts FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own account" 
ON user_accounts FOR UPDATE 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- 6. Update portfolios table to ensure vote tracking
ALTER TABLE portfolios 
ADD COLUMN IF NOT EXISTS vote_count_upvotes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS vote_count_downvotes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS vote_count_total INTEGER DEFAULT 0;

-- 7. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_votes_user_id ON user_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_votes_product_id ON user_votes(product_id);
CREATE INDEX IF NOT EXISTS idx_user_votes_vote_type ON user_votes(vote_type);

CREATE INDEX IF NOT EXISTS idx_seller_reviews_reviewer_id ON seller_reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_seller_reviews_seller_name ON seller_reviews(seller_name);
CREATE INDEX IF NOT EXISTS idx_seller_reviews_seller_id ON seller_reviews(seller_id);
CREATE INDEX IF NOT EXISTS idx_seller_reviews_rating ON seller_reviews(rating);

CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id_read ON user_notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_user_notifications_created_at ON user_notifications(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_accounts_user_id ON user_accounts(user_id);

CREATE INDEX IF NOT EXISTS idx_portfolios_votes ON portfolios(vote_count_total DESC);

-- 8. Create or replace triggers for updated_at columns (WITHOUT IF NOT EXISTS)
-- Drop existing triggers to avoid conflicts
DROP TRIGGER IF EXISTS update_user_votes_updated_at ON user_votes;
DROP TRIGGER IF EXISTS update_seller_reviews_updated_at ON seller_reviews;
DROP TRIGGER IF EXISTS update_user_accounts_updated_at ON user_accounts;

-- Create triggers (PostgreSQL doesn't support IF NOT EXISTS for triggers)
CREATE TRIGGER update_user_votes_updated_at
  BEFORE UPDATE ON user_votes
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_seller_reviews_updated_at
  BEFORE UPDATE ON seller_reviews
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_accounts_updated_at
  BEFORE UPDATE ON user_accounts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 9. Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_votes TO authenticated;
GRANT SELECT ON user_votes TO anon; -- For viewing vote counts

GRANT SELECT, INSERT, UPDATE, DELETE ON seller_reviews TO authenticated;
GRANT SELECT ON seller_reviews TO anon; -- For viewing reviews

GRANT SELECT, INSERT, UPDATE, DELETE ON user_accounts TO authenticated;

-- 10. Create or replace functions for vote aggregation
CREATE OR REPLACE FUNCTION update_portfolio_vote_counts()
RETURNS TRIGGER AS $$
BEGIN
  -- Update vote counts for the affected portfolio
  UPDATE portfolios 
  SET 
    vote_count_upvotes = (
      SELECT COUNT(*) FROM user_votes 
      WHERE product_id = COALESCE(NEW.product_id, OLD.product_id) 
      AND vote_type = 'upvote'
    ),
    vote_count_downvotes = (
      SELECT COUNT(*) FROM user_votes 
      WHERE product_id = COALESCE(NEW.product_id, OLD.product_id) 
      AND vote_type = 'downvote'
    ),
    vote_count_total = (
      SELECT COUNT(*) FROM user_votes 
      WHERE product_id = COALESCE(NEW.product_id, OLD.product_id)
    )
  WHERE id = COALESCE(NEW.product_id, OLD.product_id);
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Drop existing vote count triggers to avoid conflicts
DROP TRIGGER IF EXISTS update_portfolio_votes_on_insert ON user_votes;
DROP TRIGGER IF EXISTS update_portfolio_votes_on_update ON user_votes;
DROP TRIGGER IF EXISTS update_portfolio_votes_on_delete ON user_votes;

-- Create triggers to automatically update vote counts
CREATE TRIGGER update_portfolio_votes_on_insert
  AFTER INSERT ON user_votes
  FOR EACH ROW
  EXECUTE FUNCTION update_portfolio_vote_counts();

CREATE TRIGGER update_portfolio_votes_on_update
  AFTER UPDATE ON user_votes
  FOR EACH ROW
  EXECUTE FUNCTION update_portfolio_vote_counts();

CREATE TRIGGER update_portfolio_votes_on_delete
  AFTER DELETE ON user_votes
  FOR EACH ROW
  EXECUTE FUNCTION update_portfolio_vote_counts();