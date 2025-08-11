import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any
import re

load_dotenv()

class OpenAIBotCreator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
    
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
        """Generate trading bot configuration using GPT-5 with fallback"""
        
        if not self.validate_prompt(user_prompt):
            raise ValueError("Invalid or unsafe prompt provided")
        
        # Try to use OpenAI API first
        try:
            return self._generate_with_openai(user_prompt, user_id)
        except Exception as e:
            print(f"OpenAI API failed: {e}")
            # Fallback to predefined configuration based on prompt analysis
            return self._generate_fallback_config(user_prompt, user_id)
    
    def _generate_with_openai(self, user_prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Generate using OpenAI GPT-5 API"""
        system_prompt = """
        You are an expert trading bot configuration assistant for Flow Invest. Convert natural language trading instructions into structured JSON configuration.

        IMPORTANT: You must respond with ONLY valid JSON that follows this exact schema:

        {
            "botName": "string (creative bot name based on strategy)",
            "description": "string (detailed description of the strategy)",
            "strategy": {
                "type": "string (e.g., 'Trend Following', 'Mean Reversion', 'Breakout', 'Scalping', 'Momentum')",
                "trendTypes": ["array of trend types like 'Bullish', 'Bearish']",
                "entryConditions": {
                    "indicators": [
                        {"name": "RSI", "overbought": 70, "oversold": 30},
                        {"name": "EMA", "periods": [20, 50], "condition": "description"}
                    ],
                    "gridOrders": {
                        "levels": 5,
                        "spacingPercent": 0.5
                    }
                }
            },
            "riskManagement": {
                "leverage": "number (1-20, conservative to aggressive)",
                "maxConcurrentTrades": "number (1-5)",
                "stopLossPercent": "number (1-15%)",
                "takeProfitPercent": "number (3-25%)",
                "avoidLiquidation": true
            },
            "executionRules": {
                "orderType": "string ('Limit' or 'Market')",
                "timeInForce": "string ('GTC', 'IOC', 'FOK')"
            }
        }

        Examples based on risk level:
        - Conservative (Low Risk): leverage 2-3x, stop loss 2-3%, take profit 5-8%, max 2 trades
        - Moderate (Medium Risk): leverage 5-10x, stop loss 5-8%, take profit 10-15%, max 3 trades  
        - Aggressive (High Risk): leverage 15-20x, stop loss 10-15%, take profit 20-25%, max 5 trades

        Respond with ONLY the JSON object, no additional text or explanation.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a trading bot configuration for: {user_prompt}"}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o as GPT-5 might not be available yet
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                config = json.loads(ai_response)
                
                # Validate required fields
                required_fields = [
                    "botName", "description", "strategy", "riskManagement", "executionRules"
                ]
                
                for field in required_fields:
                    if field not in config:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate nested required fields
                if "type" not in config.get("strategy", {}):
                    raise ValueError("Missing strategy type")
                if "leverage" not in config.get("riskManagement", {}):
                    raise ValueError("Missing risk management leverage")
                
                # Add metadata
                config["created_by_ai"] = True
                config["ai_model"] = "gpt-4o"
                config["user_prompt"] = user_prompt
                config["is_predefined_strategy"] = False
                config["trading_mode"] = "paper"
                
                return config
                
            except json.JSONDecodeError:
                # Try to extract JSON from response if there's extra text
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    config = json.loads(json_match.group())
                    
                    # Apply same validation as above
                    required_fields = [
                        "botName", "description", "strategy", "riskManagement", "executionRules"
                    ]
                    
                    for field in required_fields:
                        if field not in config:
                            raise ValueError(f"Missing required field: {field}")
                    
                    # Add metadata
                    config["created_by_ai"] = True
                    config["ai_model"] = "gpt-4o"
                    config["user_prompt"] = user_prompt
                    config["is_predefined_strategy"] = False
                    config["trading_mode"] = "paper"
                    
                    return config
                else:
                    raise ValueError("Invalid JSON response from AI")

        except json.JSONDecodeError as e:
            raise ValueError(f"OpenAI returned invalid JSON: {str(e)}")
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise ValueError("Rate limit exceeded. Please try again in a moment.")
            elif "api_key" in str(e).lower():
                raise ValueError("API key error. Please check OpenAI configuration.")
            else:
                print(f"OpenAI API error: {e}")
                raise e
    
    def _generate_fallback_config(self, user_prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Generate fallback configuration when OpenAI API fails"""
        prompt_lower = user_prompt.lower()
        
        # Analyze prompt for key characteristics
        is_conservative = any(word in prompt_lower for word in ['conservative', 'safe', 'low risk', 'stable'])
        is_aggressive = any(word in prompt_lower for word in ['aggressive', 'high risk', 'risky', 'fast'])
        is_scalping = any(word in prompt_lower for word in ['scalp', 'quick', 'frequent', 'short term'])
        
        # Determine strategy and risk level
        if is_scalping:
            strategy_type = 'Scalping'
            leverage = 10
            stop_loss = 2
            take_profit = 3
            max_trades = 5
            bot_name = "Lightning Scalper Pro"
            description = "High-frequency scalping bot targeting quick 2-3% gains with tight risk management"
        elif is_conservative:
            strategy_type = 'Trend Following'
            leverage = 3
            stop_loss = 3
            take_profit = 8
            max_trades = 2
            bot_name = "Steady Growth Follower"
            description = "Conservative trend-following strategy focusing on capital preservation and steady growth"
        elif is_aggressive:
            strategy_type = 'Momentum'
            leverage = 15
            stop_loss = 12
            take_profit = 20
            max_trades = 4
            bot_name = "Momentum Beast"
            description = "Aggressive momentum trading bot targeting high returns with calculated risk exposure"
        else:
            # Balanced default
            strategy_type = 'Breakout'
            leverage = 5
            stop_loss = 5
            take_profit = 12
            max_trades = 3
            bot_name = "Smart Breakout Trader"
            description = "Balanced breakout strategy optimized for consistent profits with moderate risk"
        
        return {
            "botName": bot_name,
            "description": description,
            "strategy": {
                "type": strategy_type,
                "trendTypes": ["Bullish", "Bearish"],
                "entryConditions": {
                    "indicators": [
                        {"name": "RSI", "overbought": 70, "oversold": 30},
                        {"name": "EMA", "periods": [20, 50], "condition": "EMA20 > EMA50 for long, EMA20 < EMA50 for short"}
                    ],
                    "gridOrders": {
                        "levels": 5,
                        "spacingPercent": 0.5
                    }
                }
            },
            "riskManagement": {
                "leverage": leverage,
                "maxConcurrentTrades": max_trades,
                "stopLossPercent": stop_loss,
                "takeProfitPercent": take_profit,
                "avoidLiquidation": True
            },
            "executionRules": {
                "orderType": "Limit",
                "timeInForce": "GTC"
            },
            # Add metadata for consistency
            "created_by_ai": True,
            "ai_model": "fallback",
            "user_prompt": user_prompt,
            "is_predefined_strategy": False,
            "trading_mode": "paper"
        }
    
    def validate_bot_config(self, config: Dict[str, Any]) -> bool:
        """Validate the generated bot configuration"""
        try:
            # Check basic structure
            if not all(key in config for key in ["botName", "description", "strategy", "riskManagement"]):
                return False
            
            # Check risk management values
            risk_mgmt = config.get("riskManagement", {})
            leverage = risk_mgmt.get("leverage", 0)
            stop_loss = risk_mgmt.get("stopLossPercent", 0)
            take_profit = risk_mgmt.get("takeProfitPercent", 0)
            
            if leverage < 1 or leverage > 20:
                return False
            if stop_loss <= 0 or stop_loss > 25:
                return False
            if take_profit <= 0 or take_profit > 50:
                return False
            
            # Ensure take profit is greater than stop loss
            if take_profit <= stop_loss:
                return False
            
            return True
            
        except Exception:
            return False

# Export the class for use in other modules
__all__ = ['OpenAIBotCreator']