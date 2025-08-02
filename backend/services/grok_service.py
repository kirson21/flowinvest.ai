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
        """Generate trading bot configuration using Grok 4 with fallback"""
        
        if not self.validate_prompt(user_prompt):
            raise ValueError("Invalid or unsafe prompt provided")
        
        # Try to use Grok API first
        try:
            return self._generate_with_grok(user_prompt, user_id)
        except Exception as e:
            print(f"Grok API failed: {e}")
            # Fallback to predefined configuration based on prompt analysis
            return self._generate_fallback_config(user_prompt, user_id)
    
    def _generate_with_grok(self, user_prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Generate using Grok API"""
        system_prompt = """
        You are an expert trading bot configuration assistant for Flow Invest. Convert natural language trading instructions into structured JSON configuration.

        IMPORTANT: You must respond with ONLY valid JSON that follows this exact schema:

        {
            "name": "string (creative bot name based on strategy)",
            "description": "string (detailed description of the strategy)",
            "strategy": "string (e.g., 'momentum', 'mean_reversion', 'breakout', 'scalping', 'trend_following')",
            "risk_level": "string (low, medium, high)",
            "trade_type": "string (spot, futures, options)",
            "base_coin": "string (e.g., BTC, ETH, SOL)",
            "quote_coin": "string (e.g., USDT, USD, BTC)",
            "exchange": "string (e.g., binance, coinbase, kraken)",
            "deposit_amount": "number (initial capital amount)",
            "trading_mode": "string (simple, advanced)",
            "profit_target": "number (percentage for profit taking)",
            "stop_loss": "number (percentage for stop loss)",
            "advanced_settings": {
                "max_positions": "number (1-10)",
                "position_size": "number (percentage of capital per trade)",
                "rebalance_frequency": "string (daily, weekly, monthly)",
                "technical_indicators": ["string array of indicators"]
            }
        }

        Examples:
        - Conservative strategy: low risk, 5-15% profit target, 3-8% stop loss
        - Aggressive strategy: high risk, 20-50% profit target, 10-20% stop loss
        - Scalping: very frequent trades, 1-3% profit target, 1-2% stop loss

        Respond with ONLY the JSON object, no additional text.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a trading bot configuration for: {user_prompt}"}
        ]

        try:
            response = self.client.chat.completions.create(
                model="grok-2-1212",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                config = json.loads(ai_response)
                return config
            except json.JSONDecodeError:
                # Try to extract JSON from response if there's extra text
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    config = json.loads(json_match.group())
                    return config
                else:
                    raise ValueError("Invalid JSON response from AI")

        except Exception as e:
            print(f"Grok API error: {e}")
            raise e
    
    def _generate_fallback_config(self, user_prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Generate fallback configuration when Grok API fails"""
        prompt_lower = user_prompt.lower()
        
        # Analyze prompt for key characteristics
        is_conservative = any(word in prompt_lower for word in ['conservative', 'safe', 'low risk', 'stable'])
        is_aggressive = any(word in prompt_lower for word in ['aggressive', 'high risk', 'risky', 'fast'])
        is_scalping = any(word in prompt_lower for word in ['scalp', 'quick', 'frequent', 'short term'])
        
        # Extract coin mentions
        base_coin = 'BTC'  # Default
        if 'eth' in prompt_lower or 'ethereum' in prompt_lower:
            base_coin = 'ETH'
        elif 'sol' in prompt_lower or 'solana' in prompt_lower:
            base_coin = 'SOL'
        elif 'ada' in prompt_lower or 'cardano' in prompt_lower:
            base_coin = 'ADA'
        
        # Determine strategy and risk level
        if is_scalping:
            strategy = 'scalping'
            risk_level = 'high'
            profit_target = 2
            stop_loss = 1
            name = f"{base_coin} Lightning Scalper"
            description = f"High-frequency scalping bot for {base_coin} targeting quick 1-3% gains with tight stop losses"
        elif is_conservative:
            strategy = 'trend_following'
            risk_level = 'low' 
            profit_target = 10
            stop_loss = 5
            name = f"{base_coin} Steady Growth Bot"
            description = f"Conservative trend-following strategy for {base_coin} with focus on capital preservation"
        elif is_aggressive:
            strategy = 'momentum'
            risk_level = 'high'
            profit_target = 25
            stop_loss = 15
            name = f"{base_coin} Momentum Hunter"
            description = f"Aggressive momentum trading bot for {base_coin} targeting high returns with calculated risks"
        else:
            # Balanced default
            strategy = 'mean_reversion'
            risk_level = 'medium'
            profit_target = 15
            stop_loss = 8
            name = f"{base_coin} Smart Trader Pro"
            description = f"Balanced mean-reversion strategy for {base_coin} optimized for consistent profits"
        
        return {
            "name": name,
            "description": description,
            "strategy": strategy,
            "risk_level": risk_level,
            "trade_type": "spot",
            "base_coin": base_coin,
            "quote_coin": "USDT",
            "exchange": "binance",
            "deposit_amount": 1000,
            "trading_mode": "simple",
            "profit_target": profit_target,
            "stop_loss": stop_loss,
            "advanced_settings": {
                "max_positions": 3,
                "position_size": 33,
                "rebalance_frequency": "daily",
                "technical_indicators": ["RSI", "MACD", "Moving Average"]
            }
        }
    
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