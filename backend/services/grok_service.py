import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any
import re

load_dotenv()

class GrokBotCreator:
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable is required")
        
        # Initialize xAI client using OpenAI-compatible interface
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
    
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
        """Generate trading bot configuration using Grok 4"""
        
        if not self.validate_prompt(user_prompt):
            raise ValueError("Invalid or unsafe prompt provided")
        
        system_prompt = """
        You are an expert trading bot configuration assistant for Flow Invest. Convert natural language trading instructions into structured JSON configuration.

        IMPORTANT: You must respond with ONLY valid JSON that follows this exact schema:

        {
            "name": "string (creative bot name based on strategy)",
            "description": "string (detailed description of the strategy)",
            "strategy": "string (e.g., 'momentum', 'mean_reversion', 'breakout', 'scalping', 'trend_following')",
            "base_coin": "string (e.g., 'BTC', 'ETH', 'SOL')",
            "quote_coin": "string (e.g., 'USDT', 'USD', 'EUR')",
            "exchange": "string (binance, bybit, or kraken)",
            "risk_level": "string (low, medium, or high)",
            "trade_type": "string (long or short)",
            "deposit_amount": "number (suggested amount in quote currency)",
            "trading_mode": "string (simple, advanced, or signal)",
            "profit_target": "number (percentage, e.g., 5.0 for 5%)",
            "stop_loss": "number (percentage, e.g., 2.0 for 2%)",
            "advanced_settings": {
                "position_size": "number (percentage of deposit, e.g., 10.0 for 10%)",
                "timeframe": "string (1m, 5m, 15m, 1h, 4h, 1d)",
                "max_trades_per_day": "number (1-20)",
                "trailing_stop": "boolean",
                "martingale": "boolean (use cautiously)",
                "entry_conditions": ["array of trading conditions"],
                "exit_conditions": ["array of trading conditions"],
                "indicators": ["array of technical indicators used"]
            },
            "performance_targets": {
                "daily_return": "number (realistic daily return percentage)",
                "win_rate": "number (realistic win rate percentage 50-80)",
                "max_drawdown": "number (maximum acceptable loss percentage)"
            }
        }

        Guidelines:
        - Use realistic and safe trading parameters
        - For beginners, suggest conservative settings (low risk, small position sizes)
        - For experienced traders, allow more aggressive settings if requested
        - Always include proper risk management (stop loss, position sizing)
        - Base coin should be a major cryptocurrency (BTC, ETH, ADA, SOL, etc.)
        - Quote coin should be stable (USDT, USD, EUR, etc.)
        - Timeframes should match strategy (scalping: 1m-5m, swing: 1h-1d)
        - Be creative with bot names that reflect the strategy

        Example valid response:
        {
            "name": "BTC Lightning Scalper",
            "description": "A fast-paced scalping bot designed to capture small price movements in Bitcoin using RSI oversold/overbought signals with tight risk management.",
            "strategy": "scalping",
            "base_coin": "BTC",
            "quote_coin": "USDT",
            "exchange": "binance",
            "risk_level": "medium",
            "trade_type": "long",
            "deposit_amount": 1000,
            "trading_mode": "advanced",
            "profit_target": 1.5,
            "stop_loss": 0.8,
            "advanced_settings": {
                "position_size": 15.0,
                "timeframe": "5m",
                "max_trades_per_day": 10,
                "trailing_stop": true,
                "martingale": false,
                "entry_conditions": ["RSI < 30", "Volume > 20-period average"],
                "exit_conditions": ["RSI > 70", "Profit target reached", "Stop loss hit"],
                "indicators": ["RSI", "Volume", "EMA"]
            },
            "performance_targets": {
                "daily_return": 2.5,
                "win_rate": 65,
                "max_drawdown": 5.0
            }
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model="grok-2-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=30
            )
            
            # Get the response content
            config_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if there's extra text
            json_match = re.search(r'\{.*\}', config_text, re.DOTALL)
            if json_match:
                config_text = json_match.group()
            
            # Parse JSON
            config_json = json.loads(config_text)
            
            # Validate required fields
            required_fields = [
                "name", "description", "strategy", "base_coin", "quote_coin", 
                "exchange", "risk_level", "trade_type", "profit_target", "stop_loss"
            ]
            
            for field in required_fields:
                if field not in config_json:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate risk level
            if config_json.get("risk_level") not in ["low", "medium", "high"]:
                config_json["risk_level"] = "medium"
            
            # Validate exchange
            if config_json.get("exchange") not in ["binance", "bybit", "kraken"]:
                config_json["exchange"] = "binance"
            
            # Validate trade type
            if config_json.get("trade_type") not in ["long", "short"]:
                config_json["trade_type"] = "long"
            
            # Add metadata
            config_json["created_by_ai"] = True
            config_json["ai_model"] = "grok-2-latest"
            config_json["user_prompt"] = user_prompt
            config_json["is_prebuilt"] = False
            config_json["status"] = "inactive"
            
            # Set default performance metrics
            config_json.setdefault("daily_pnl", 0)
            config_json.setdefault("weekly_pnl", 0)
            config_json.setdefault("monthly_pnl", 0)
            config_json.setdefault("win_rate", 0)
            config_json.setdefault("total_trades", 0)
            config_json.setdefault("successful_trades", 0)
            
            return config_json
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Grok returned invalid JSON: {str(e)}")
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise ValueError("Rate limit exceeded. Please try again in a moment.")
            elif "api_key" in str(e).lower():
                raise ValueError("API key error. Please check Grok configuration.")
            else:
                raise ValueError(f"AI service error: {str(e)}")
    
    def validate_bot_config(self, config: Dict[str, Any]) -> bool:
        """Validate the generated bot configuration"""
        try:
            # Check profit/loss ratios make sense
            profit_target = config.get("profit_target", 0)
            stop_loss = config.get("stop_loss", 0)
            
            if profit_target <= 0 or stop_loss <= 0:
                return False
            
            # Risk management validation
            if profit_target > 50 or stop_loss > 25:  # Unrealistic targets
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