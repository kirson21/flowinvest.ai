import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

from .bybit_service import BybitService
from .encryption_service import EncryptionService

class BotExecutionService:
    def __init__(self):
        self.bybit_service = BybitService()
        self.encryption_service = EncryptionService()
        
        # Active bots tracking
        self.active_bots = {}
        self.bot_tasks = {}
        
        # Market data cache
        self.market_data_cache = {}
        self.cache_update_task = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def start_bot(self, bot_id: str, bot_config: Dict[str, Any], exchange_keys: Dict[str, Any]):
        """Start executing a trading bot"""
        
        try:
            # Decrypt API keys
            decrypted_keys = self.encryption_service.decrypt_api_credentials(
                bot_config["user_id"], 
                exchange_keys
            )
            
            if not decrypted_keys["success"]:
                raise Exception(f"Failed to decrypt API keys: {decrypted_keys['error']}")
            
            # Parse bot configuration
            bot_strategy = json.loads(bot_config["bot_config"]) if isinstance(bot_config["bot_config"], str) else bot_config["bot_config"]
            
            # Create bot execution context
            bot_context = {
                "bot_id": bot_id,
                "user_id": bot_config["user_id"],
                "config": bot_strategy,
                "api_key": decrypted_keys["api_key"],
                "api_secret": decrypted_keys["api_secret"],
                "is_testnet": exchange_keys.get("exchange_account_type", "testnet") == "testnet",
                "trading_mode": bot_config.get("trading_mode", "paper"),
                "status": "active",
                "created_at": datetime.utcnow(),
                "last_signal_at": None,
                "active_positions": {},
                "performance_metrics": {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "total_pnl": 0.0,
                    "max_drawdown": 0.0
                }
            }
            
            # Store active bot
            self.active_bots[bot_id] = bot_context
            
            # Start bot execution task
            task = asyncio.create_task(self._execute_bot_loop(bot_context))
            self.bot_tasks[bot_id] = task
            
            # Start market data updates if not already running
            if not self.cache_update_task:
                self.cache_update_task = asyncio.create_task(self._update_market_data_cache())
            
            await self._log_bot_activity(
                bot_id, 
                bot_config["user_id"], 
                "info", 
                "Bot started successfully",
                {"config": bot_strategy}
            )
            
            self.logger.info(f"Bot {bot_id} started successfully")
            
        except Exception as e:
            await self._log_bot_activity(
                bot_id, 
                bot_config["user_id"], 
                "error", 
                f"Failed to start bot: {str(e)}"
            )
            raise
    
    async def stop_bot(self, bot_id: str):
        """Stop a trading bot"""
        
        try:
            if bot_id in self.bot_tasks:
                # Cancel the bot task
                self.bot_tasks[bot_id].cancel()
                del self.bot_tasks[bot_id]
            
            if bot_id in self.active_bots:
                bot_context = self.active_bots[bot_id]
                
                # Close any open positions (paper trading)
                await self._close_all_positions(bot_context)
                
                # Log stop activity
                await self._log_bot_activity(
                    bot_id,
                    bot_context["user_id"],
                    "info",
                    "Bot stopped successfully"
                )
                
                del self.active_bots[bot_id]
            
            self.logger.info(f"Bot {bot_id} stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to stop bot {bot_id}: {e}")
    
    async def _execute_bot_loop(self, bot_context: Dict[str, Any]):
        """Main execution loop for a trading bot"""
        
        bot_id = bot_context["bot_id"]
        config = bot_context["config"]
        
        try:
            while bot_context["status"] == "active":
                try:
                    # Get trading signals
                    signals = await self._analyze_trading_signals(bot_context)
                    
                    if signals:
                        await self._process_trading_signals(bot_context, signals)
                    
                    # Update performance metrics
                    await self._update_performance_metrics(bot_context)
                    
                    # Check risk management
                    await self._check_risk_management(bot_context)
                    
                    # Wait before next iteration
                    strategy_type = config["strategy"]["type"].lower()
                    sleep_duration = self._get_sleep_duration(strategy_type)
                    await asyncio.sleep(sleep_duration)
                    
                except Exception as e:
                    await self._log_bot_activity(
                        bot_id,
                        bot_context["user_id"],
                        "error",
                        f"Bot execution error: {str(e)}"
                    )
                    
                    # Pause bot on error
                    bot_context["status"] = "error"
                    break
        
        except asyncio.CancelledError:
            self.logger.info(f"Bot {bot_id} execution cancelled")
        except Exception as e:
            self.logger.error(f"Bot {bot_id} execution failed: {e}")
    
    async def _analyze_trading_signals(self, bot_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze market conditions and generate trading signals"""
        
        config = bot_context["config"]
        strategy = config["strategy"]
        
        signals = []
        
        try:
            # Get relevant symbols for analysis
            symbols = self._get_trading_symbols(config)
            
            for symbol in symbols:
                # Get market data
                market_data = await self._get_market_data(symbol, bot_context["is_testnet"])
                
                if not market_data:
                    continue
                
                # Analyze based on strategy type
                if strategy["type"] == "Trend Following":
                    signal = await self._analyze_trend_following(symbol, market_data, strategy)
                elif strategy["type"] == "Breakout":
                    signal = await self._analyze_breakout(symbol, market_data, strategy)
                elif strategy["type"] == "Scalping":
                    signal = await self._analyze_scalping(symbol, market_data, strategy)
                else:
                    signal = await self._analyze_custom_strategy(symbol, market_data, strategy)
                
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Signal analysis failed: {e}")
            return []
    
    async def _analyze_trend_following(self, symbol: str, market_data: Dict[str, Any], strategy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze trend following signals"""
        
        # Simplified trend analysis
        price = market_data["price"]
        volume = market_data["volume"]
        change_24h = market_data["change_24h"]
        
        # Basic trend detection
        if change_24h > 2 and volume > 1000000:  # Strong uptrend
            return {
                "symbol": symbol,
                "action": "long",
                "strength": min(abs(change_24h) / 10, 1.0),
                "price": price,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "Strong uptrend detected"
            }
        elif change_24h < -2 and volume > 1000000:  # Strong downtrend
            return {
                "symbol": symbol,
                "action": "short",
                "strength": min(abs(change_24h) / 10, 1.0),
                "price": price,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "Strong downtrend detected"
            }
        
        return None
    
    async def _analyze_breakout(self, symbol: str, market_data: Dict[str, Any], strategy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze breakout signals"""
        
        price = market_data["price"]
        high_24h = market_data["high_24h"]
        low_24h = market_data["low_24h"]
        volume = market_data["volume"]
        
        # Simple breakout detection
        price_range = high_24h - low_24h
        upper_breakout = high_24h - (price_range * 0.05)
        lower_breakout = low_24h + (price_range * 0.05)
        
        if price >= upper_breakout and volume > 1500000:
            return {
                "symbol": symbol,
                "action": "long",
                "strength": 0.8,
                "price": price,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "Upper resistance breakout"
            }
        elif price <= lower_breakout and volume > 1500000:
            return {
                "symbol": symbol,
                "action": "short",
                "strength": 0.8,
                "price": price,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "Lower support breakdown"
            }
        
        return None
    
    async def _analyze_scalping(self, symbol: str, market_data: Dict[str, Any], strategy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze scalping signals"""
        
        # Scalping requires more frequent, smaller moves
        change_24h = market_data["change_24h"]
        volume = market_data["volume"]
        price = market_data["price"]
        
        # Look for small, quick opportunities
        if 0.5 <= abs(change_24h) <= 2 and volume > 500000:
            action = "long" if change_24h > 0 else "short"
            return {
                "symbol": symbol,
                "action": action,
                "strength": 0.6,
                "price": price,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "Scalping opportunity detected"
            }
        
        return None
    
    async def _analyze_custom_strategy(self, symbol: str, market_data: Dict[str, Any], strategy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze custom strategy signals"""
        
        # Implement custom logic based on strategy configuration
        # This is a placeholder for more sophisticated custom analysis
        return None
    
    async def _process_trading_signals(self, bot_context: Dict[str, Any], signals: List[Dict[str, Any]]):
        """Process trading signals and execute trades"""
        
        config = bot_context["config"]
        risk_mgmt = config["riskManagement"]
        
        # Check concurrent trade limits
        max_trades = risk_mgmt.get("maxConcurrentTrades", 5)
        current_positions = len(bot_context["active_positions"])
        
        if current_positions >= max_trades:
            return
        
        for signal in signals:
            if current_positions >= max_trades:
                break
            
            # Calculate position size
            position_size = self._calculate_position_size(bot_context, signal)
            
            if position_size > 0:
                # Execute trade
                trade_result = await self._execute_trade(bot_context, signal, position_size)
                
                if trade_result["success"]:
                    current_positions += 1
                    
                    # Store active position
                    position_id = trade_result["order_id"]
                    bot_context["active_positions"][position_id] = {
                        "signal": signal,
                        "position_size": position_size,
                        "entry_price": signal["price"],
                        "timestamp": datetime.utcnow(),
                        "trade_result": trade_result
                    }
    
    async def _execute_trade(self, bot_context: Dict[str, Any], signal: Dict[str, Any], position_size: float) -> Dict[str, Any]:
        """Execute a trade based on signal"""
        
        try:
            symbol = signal["symbol"]
            side = "Buy" if signal["action"] == "long" else "Sell"
            
            # Execute trade (paper trade for now)
            trade_result = await self.bybit_service.place_order(
                api_key=bot_context["api_key"],
                api_secret=bot_context["api_secret"],
                symbol=symbol,
                side=side,
                order_type="Market",
                qty=str(position_size),
                is_testnet=bot_context["is_testnet"],
                is_paper_trade=bot_context["trading_mode"] == "paper"
            )
            
            if trade_result["success"]:
                # Log trade to database
                await self._log_trade_to_database(bot_context, trade_result, signal)
                
                await self._log_bot_activity(
                    bot_context["bot_id"],
                    bot_context["user_id"],
                    "trade",
                    f"Trade executed: {side} {position_size} {symbol}",
                    {"signal": signal, "trade_result": trade_result}
                )
            
            return trade_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Trade execution failed: {str(e)}"
            }
    
    def _calculate_position_size(self, bot_context: Dict[str, Any], signal: Dict[str, Any]) -> float:
        """Calculate appropriate position size based on risk management"""
        
        config = bot_context["config"]
        risk_mgmt = config["riskManagement"]
        
        # Simple position sizing (can be enhanced)
        base_position_size = 0.1  # Base position in the quote currency
        leverage = risk_mgmt.get("leverage", 1)
        
        # Adjust based on signal strength
        strength_multiplier = signal.get("strength", 0.5)
        
        position_size = base_position_size * leverage * strength_multiplier
        
        # Apply maximum position size limits
        max_position = 1.0  # Maximum position size
        return min(position_size, max_position)
    
    async def _get_market_data(self, symbol: str, is_testnet: bool) -> Optional[Dict[str, Any]]:
        """Get market data with caching"""
        
        cache_key = f"{symbol}_{is_testnet}"
        
        # Check cache first
        if cache_key in self.market_data_cache:
            data = self.market_data_cache[cache_key]
            # Check if data is fresh (less than 30 seconds old)
            if datetime.utcnow() - data["cached_at"] < timedelta(seconds=30):
                return data["data"]
        
        # Fetch fresh data
        market_data = await self.bybit_service.get_market_data(symbol, is_testnet)
        
        if market_data["success"]:
            # Cache the data
            self.market_data_cache[cache_key] = {
                "data": market_data,
                "cached_at": datetime.utcnow()
            }
            return market_data
        
        return None
    
    def _get_trading_symbols(self, config: Dict[str, Any]) -> List[str]:
        """Get list of symbols to trade based on configuration"""
        
        # Default major pairs
        default_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]
        
        # Check if specific symbols are configured
        filters = config.get("filters", {})
        allowed_assets = filters.get("allowedAssets")
        
        if allowed_assets:
            return allowed_assets[:10]  # Limit to 10 symbols max
        
        return default_symbols
    
    def _get_sleep_duration(self, strategy_type: str) -> int:
        """Get sleep duration between analysis cycles based on strategy"""
        
        durations = {
            "scalping": 30,      # 30 seconds
            "breakout": 60,      # 1 minute
            "trend following": 300, # 5 minutes
            "default": 180       # 3 minutes
        }
        
        return durations.get(strategy_type.lower(), durations["default"])
    
    async def _update_market_data_cache(self):
        """Periodically update market data cache"""
        
        try:
            while True:
                # Update cache for all tracked symbols
                symbols_to_update = set()
                
                for bot_context in self.active_bots.values():
                    symbols = self._get_trading_symbols(bot_context["config"])
                    symbols_to_update.update(symbols)
                
                # Update each symbol
                for symbol in symbols_to_update:
                    for is_testnet in [True, False]:
                        try:
                            await self._get_market_data(symbol, is_testnet)
                        except Exception as e:
                            self.logger.warning(f"Failed to update {symbol} data: {e}")
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            self.logger.info("Market data cache update task cancelled")
        except Exception as e:
            self.logger.error(f"Market data cache update failed: {e}")
    
    async def _log_trade_to_database(self, bot_context: Dict[str, Any], trade_result: Dict[str, Any], signal: Dict[str, Any]):
        """Log trade execution to database"""
        
        try:
            from database import supabase
            
            trade_record = {
                "bot_id": bot_context["bot_id"],
                "user_id": bot_context["user_id"],
                "exchange_order_id": trade_result.get("order_id"),
                "symbol": signal["symbol"],
                "side": signal["action"],
                "order_type": "market",
                "quantity": float(trade_result.get("quantity", 0)),
                "price": float(trade_result.get("price", 0)),
                "filled_quantity": float(trade_result.get("quantity", 0)),
                "average_fill_price": float(trade_result.get("price", 0)),
                "status": "filled",
                "is_paper_trade": trade_result.get("is_paper_trade", True),
                "executed_at": datetime.utcnow().isoformat()
            }
            
            supabase.table('bot_trades').insert(trade_record).execute()
            
        except Exception as e:
            self.logger.error(f"Failed to log trade to database: {e}")
    
    async def _log_bot_activity(self, bot_id: str, user_id: str, log_level: str, message: str, details: Dict[str, Any] = None):
        """Log bot activity to database"""
        
        try:
            from ..database import supabase
            
            log_record = {
                "bot_id": bot_id,
                "user_id": user_id,
                "log_type": "trade" if "executed" in message.lower() else "signal",
                "log_level": log_level,
                "message": message,
                "details": json.dumps(details) if details else None
            }
            
            supabase.table('bot_logs').insert(log_record).execute()
            
        except Exception as e:
            self.logger.error(f"Failed to log bot activity: {e}")
    
    async def _close_all_positions(self, bot_context: Dict[str, Any]):
        """Close all active positions for a bot"""
        
        # For paper trading, just clear the positions
        if bot_context["trading_mode"] == "paper":
            bot_context["active_positions"].clear()
            return
        
        # For live trading, would need to place closing orders
        # Implementation depends on specific exchange requirements
    
    async def _update_performance_metrics(self, bot_context: Dict[str, Any]):
        """Update bot performance metrics"""
        
        # This would calculate and update performance metrics
        # Implementation depends on specific requirements
        pass
    
    async def _check_risk_management(self, bot_context: Dict[str, Any]):
        """Check and enforce risk management rules"""
        
        config = bot_context["config"]
        risk_mgmt = config["riskManagement"]
        
        # Check maximum drawdown
        # Check position limits
        # Check leverage limits
        # Implementation depends on specific risk rules
        pass