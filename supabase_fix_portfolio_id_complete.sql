-- Complete fix for portfolio ID type issue
-- This addresses the RLS policy conflict and changes the column type properly

-- Step 1: Drop all RLS policies that depend on the id column
DROP POLICY IF EXISTS "portfolio_assets_all_policy" ON portfolio_assets;
DROP POLICY IF EXISTS "Users can view portfolios" ON portfolios;
DROP POLICY IF EXISTS "Users can insert own portfolios" ON portfolios;
DROP POLICY IF EXISTS "Users can update own portfolios" ON portfolios;
DROP POLICY IF EXISTS "Users can delete own portfolios" ON portfolios;
DROP POLICY IF EXISTS "Public read access to portfolios" ON portfolios;

-- Step 2: Now we can safely change the column type
ALTER TABLE portfolios ALTER COLUMN id TYPE TEXT;

-- Step 3: Recreate the RLS policies with TEXT id column
-- Allow public read access to all portfolios (for marketplace)
CREATE POLICY "Public read access to portfolios" 
ON portfolios FOR SELECT TO public USING (true);

-- Allow authenticated users to insert their own portfolios
CREATE POLICY "Users can insert own portfolios" 
ON portfolios FOR INSERT TO authenticated WITH CHECK (auth.uid()::text = user_id);

-- Allow users to update their own portfolios
CREATE POLICY "Users can update own portfolios" 
ON portfolios FOR UPDATE TO authenticated 
USING (auth.uid()::text = user_id) WITH CHECK (auth.uid()::text = user_id);

-- Allow users to delete their own portfolios
CREATE POLICY "Users can delete own portfolios" 
ON portfolios FOR DELETE TO authenticated USING (auth.uid()::text = user_id);

-- Step 4: Make sure the table has proper permissions
GRANT SELECT ON portfolios TO public;
GRANT SELECT, INSERT, UPDATE, DELETE ON portfolios TO authenticated;