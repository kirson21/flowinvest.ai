-- Update user_bots table schema to include missing columns for bot creation API

-- Add missing columns to user_bots table
ALTER TABLE user_bots 
ADD COLUMN IF NOT EXISTS base_coin VARCHAR(20),
ADD COLUMN IF NOT EXISTS quote_coin VARCHAR(20),
ADD COLUMN IF NOT EXISTS trade_type VARCHAR(20) DEFAULT 'spot',
ADD COLUMN IF NOT EXISTS deposit_amount DECIMAL(12,2) DEFAULT 1000,
ADD COLUMN IF NOT EXISTS trading_mode VARCHAR(20) DEFAULT 'simple',
ADD COLUMN IF NOT EXISTS profit_target DECIMAL(5,2) DEFAULT 10,
ADD COLUMN IF NOT EXISTS stop_loss DECIMAL(5,2) DEFAULT 5,
ADD COLUMN IF NOT EXISTS total_trades INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS successful_trades INTEGER DEFAULT 0;

-- Update existing records to have default values for new columns
UPDATE user_bots 
SET 
    base_coin = COALESCE(base_coin, 'BTC'),
    quote_coin = COALESCE(quote_coin, 'USDT'),
    trade_type = COALESCE(trade_type, 'spot'),
    deposit_amount = COALESCE(deposit_amount, 1000),
    trading_mode = COALESCE(trading_mode, 'simple'),
    profit_target = COALESCE(profit_target, 10),
    stop_loss = COALESCE(stop_loss, 5),
    total_trades = COALESCE(total_trades, 0),
    successful_trades = COALESCE(successful_trades, 0)
WHERE base_coin IS NULL OR quote_coin IS NULL OR trade_type IS NULL;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_user_bots_user_id ON user_bots(user_id);
CREATE INDEX IF NOT EXISTS idx_user_bots_strategy ON user_bots(strategy);
CREATE INDEX IF NOT EXISTS idx_user_bots_base_coin ON user_bots(base_coin);