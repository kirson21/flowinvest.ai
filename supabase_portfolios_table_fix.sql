-- Fix portfolios table structure for portfolio creation
-- This addresses HTTP 400 errors when saving portfolios

-- First, let's check and add missing columns to portfolios table
ALTER TABLE portfolios 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS title TEXT NOT NULL DEFAULT 'Unnamed Portfolio',
ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'other',
ADD COLUMN IF NOT EXISTS price DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS risk_level TEXT DEFAULT 'medium',
ADD COLUMN IF NOT EXISTS asset_type TEXT DEFAULT 'stock',
ADD COLUMN IF NOT EXISTS content JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Enable RLS on portfolios table
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to recreate them properly
DROP POLICY IF EXISTS "Users can view portfolios" ON portfolios;
DROP POLICY IF EXISTS "Users can insert own portfolios" ON portfolios;
DROP POLICY IF EXISTS "Users can update own portfolios" ON portfolios;
DROP POLICY IF EXISTS "Users can delete own portfolios" ON portfolios;
DROP POLICY IF EXISTS "Public read access to portfolios" ON portfolios;

-- Create comprehensive RLS policies for portfolios
-- Allow public read access to all portfolios (for marketplace)
CREATE POLICY "Public read access to portfolios" 
ON portfolios FOR SELECT TO public USING (true);

-- Allow authenticated users to insert their own portfolios
CREATE POLICY "Users can insert own portfolios" 
ON portfolios FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own portfolios
CREATE POLICY "Users can update own portfolios" 
ON portfolios FOR UPDATE TO authenticated 
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own portfolios
CREATE POLICY "Users can delete own portfolios" 
ON portfolios FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Grant permissions
GRANT SELECT ON portfolios TO public;
GRANT SELECT, INSERT, UPDATE, DELETE ON portfolios TO authenticated;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_category ON portfolios(category);
CREATE INDEX IF NOT EXISTS idx_portfolios_created_at ON portfolios(created_at);