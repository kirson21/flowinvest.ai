import os
import json
import httpx
from dotenv import load_dotenv
from typing import Dict, Any
import re

load_dotenv()

class GrokBotCreator:
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        
        # No OpenAI client to avoid Rust dependencies
        # Using httpx directly instead
    
    def validate_prompt(self, prompt: str) -> bool:
        """Validate user prompt for safety and basic requirements"""
        if not prompt or len(prompt.strip()) < 10:
            return False
        
        # Check for malicious content
        forbidden_patterns = ['<script>', 'javascript:', 'eval(', 'exec(', '__import__']
        prompt_lower = prompt.lower()
        
        if any(pattern in prompt_lower for pattern in forbidden_patterns):
            return False
        
        return True
    
    def generate_bot_config(self, user_prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Generate trading bot configuration with fallback (no external AI dependencies)"""
        
        if not self.validate_prompt(user_prompt):
            raise ValueError("Invalid or unsafe prompt provided")
        
        # Skip external AI API calls to avoid deployment issues
        # Use smart fallback configuration instead
        return self._generate_fallback_config(user_prompt, user_id)
    
    def _generate_fallback_config(self, user_prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Generate smart configuration based on prompt analysis"""
        prompt_lower = user_prompt.lower()
        
        # Analyze prompt for key characteristics
        is_conservative = any(word in prompt_lower for word in ['conservative', 'safe', 'low risk', 'stable', 'steady'])
        is_aggressive = any(word in prompt_lower for word in ['aggressive', 'high risk', 'risky', 'fast', 'quick gains'])
        is_scalping = any(word in prompt_lower for word in ['scalp', 'quick', 'frequent', 'short term', 'fast trades'])
        
        # Extract coin mentions
        base_coin = 'BTC'  # Default
        if any(coin in prompt_lower for coin in ['eth', 'ethereum']):
            base_coin = 'ETH'
        elif any(coin in prompt_lower for coin in ['sol', 'solana']):
            base_coin = 'SOL'
        elif any(coin in prompt_lower for coin in ['ada', 'cardano']):
            base_coin = 'ADA'
        elif any(coin in prompt_lower for coin in ['dot', 'polkadot']):
            base_coin = 'DOT'
        elif any(coin in prompt_lower for coin in ['matic', 'polygon']):
            base_coin = 'MATIC'
        
        # Determine strategy and risk level
        if is_scalping:
            strategy = 'scalping'
            risk_level = 'high'
            profit_target = 2.5
            stop_loss = 1.5
            name = f"{base_coin} Lightning Scalper"
            description = f"High-frequency scalping bot for {base_coin} targeting quick 1-3% gains with tight stop losses. Optimized for short-term market movements."
        elif is_conservative:
            strategy = 'trend_following'
            risk_level = 'low' 
            profit_target = 12
            stop_loss = 6
            name = f"{base_coin} Steady Growth Bot"
            description = f"Conservative trend-following strategy for {base_coin} with focus on capital preservation and steady returns over time."
        elif is_aggressive:
            strategy = 'momentum'
            risk_level = 'high'
            profit_target = 30
            stop_loss = 18
            name = f"{base_coin} Momentum Hunter"
            description = f"Aggressive momentum trading bot for {base_coin} targeting high returns by riding strong market trends with calculated risks."
        else:
            # Balanced default
            strategy = 'mean_reversion'
            risk_level = 'medium'
            profit_target = 18
            stop_loss = 10
            name = f"{base_coin} Smart Trader Pro"
            description = f"Balanced mean-reversion strategy for {base_coin} optimized for consistent profits by buying dips and selling peaks."
        
        return {
            "name": name,
            "description": description,
            "strategy": strategy,
            "risk_level": risk_level,
            "trade_type": "spot",
            "base_coin": base_coin,
            "quote_coin": "USDT",
            "exchange": "bybit",  # Focus on Bybit as mentioned
            "deposit_amount": 1000,
            "trading_mode": "advanced",
            "profit_target": profit_target,
            "stop_loss": stop_loss,
            "advanced_settings": {
                "max_positions": 3 if risk_level == 'low' else 5 if risk_level == 'medium' else 7,
                "position_size": 20 if risk_level == 'low' else 30 if risk_level == 'medium' else 40,
                "rebalance_frequency": "daily",
                "technical_indicators": self._get_indicators_for_strategy(strategy)
            },
            # Add metadata for consistency
            "created_by_ai": True,
            "ai_model": "smart_fallback",
            "user_prompt": user_prompt,
            "is_prebuilt": False,
            "status": "inactive",
            "daily_pnl": 0,
            "weekly_pnl": 0,
            "monthly_pnl": 0,
            "win_rate": 0,
            "total_trades": 0,
            "successful_trades": 0
        }
    
    def _get_indicators_for_strategy(self, strategy: str):
        """Return appropriate technical indicators for each strategy"""
        indicators_map = {
            'scalping': ["RSI", "MACD", "Bollinger Bands", "EMA"],
            'trend_following': ["Moving Average", "MACD", "ADX", "Parabolic SAR"],
            'momentum': ["RSI", "Stochastic", "Williams %R", "CCI"],
            'mean_reversion': ["RSI", "Bollinger Bands", "Mean Reversion", "Support/Resistance"]
        }
        return indicators_map.get(strategy, ["RSI", "MACD", "Moving Average"])
    
    def validate_bot_config(self, config: Dict[str, Any]) -> bool:
        """Validate the generated bot configuration"""
        try:
            # Check required fields
            required_fields = ["name", "description", "strategy", "base_coin", "quote_coin", "exchange"]
            if not all(field in config for field in required_fields):
                return False
            
            # Check profit/loss ratios make sense
            profit_target = config.get("profit_target", 0)
            stop_loss = config.get("stop_loss", 0)
            
            if profit_target <= 0 or stop_loss <= 0:
                return False
            
            # Risk management validation
            if profit_target > 50 or stop_loss > 30:  # Unrealistic targets
                return False
            
            # Position size validation
            position_size = config.get("advanced_settings", {}).get("position_size", 0)
            if position_size > 50:  # Too risky
                return False
            
            return True
            
        except Exception:
            return False

# Export the class for use in other modules
__all__ = ['GrokBotCreator']