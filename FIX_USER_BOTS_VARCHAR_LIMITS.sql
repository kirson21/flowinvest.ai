-- Fix VARCHAR(100) constraints in user_bots table
-- Execute this in your Supabase SQL Editor

-- Increase strategy field length to accommodate longer AI-generated strategy descriptions
ALTER TABLE public.user_bots 
ALTER COLUMN strategy TYPE VARCHAR(500);

-- Increase exchange field length for future flexibility
ALTER TABLE public.user_bots 
ALTER COLUMN exchange TYPE VARCHAR(200);

-- Add comment for documentation
COMMENT ON COLUMN public.user_bots.strategy IS 'Trading strategy description - increased to 500 chars for AI-generated strategies';
COMMENT ON COLUMN public.user_bots.exchange IS 'Exchange name - increased to 200 chars for flexibility';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'User bots table field lengths increased successfully!';
    RAISE NOTICE 'Strategy field: VARCHAR(100) → VARCHAR(500)';  
    RAISE NOTICE 'Exchange field: VARCHAR(100) → VARCHAR(200)';
END $$;