import openai
import json
import os
from typing import Dict, Any, List
from datetime import datetime

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
    async def generate_trading_strategy(self, description: str, risk_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a trading bot configuration using GPT-5 based on user description"""
        
        # Create comprehensive prompt for strategy generation
        prompt = self._create_strategy_prompt(description, risk_preferences)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Will update to GPT-5 when available
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            bot_config = json.loads(response.choices[0].message.content)
            
            # Validate and enhance the configuration
            validated_config = self._validate_and_enhance_config(bot_config, risk_preferences)
            
            return validated_config
            
        except Exception as e:
            raise Exception(f"Failed to generate trading strategy with OpenAI: {str(e)}")
    
    async def customize_strategy(self, base_config: Dict[str, Any], customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Customize an existing strategy template based on user preferences"""
        
        prompt = f"""
        Customize this trading bot configuration based on user preferences:
        
        Base Configuration:
        {json.dumps(base_config, indent=2)}
        
        User Customizations:
        {json.dumps(customizations, indent=2)}
        
        Apply the customizations while maintaining the core strategy structure and risk management principles.
        Return only the updated JSON configuration.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            customized_config = json.loads(response.choices[0].message.content)
            return customized_config
            
        except Exception as e:
            raise Exception(f"Failed to customize strategy with OpenAI: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for trading bot generation"""
        return """
        You are an expert crypto trading bot configuration generator. Your task is to create safe, profitable, and well-structured trading bot configurations in JSON format.

        CRITICAL REQUIREMENTS:
        
        1. RISK MANAGEMENT (MANDATORY):
           - Always include stop loss (minimum 1%, maximum 10%)
           - Leverage must not exceed 20x (default max 10x unless user specifically requests higher)
           - Maximum 10 concurrent trades
           - Include position sizing rules
           - Avoid liquidation risk at all costs
        
        2. STRATEGY STRUCTURE:
           - Support common strategy types: Trend Following, Breakout, Scalping, Mean Reversion, Grid Trading
           - Include clear entry and exit conditions
           - Specify indicators with proper parameters
           - Define timeframes appropriate for strategy type
        
        3. JSON SCHEMA (MUST FOLLOW EXACTLY):
           {
             "botName": "string",
             "description": "string", 
             "strategy": {
               "type": "string",
               "timeframes": ["string"],
               "entryConditions": {
                 "indicators": [{"name": "string", "parameters": {}, "condition": "string"}],
                 "additionalRules": ["string"]
               },
               "exitConditions": {
                 "takeProfit": {"type": "string", "value": number},
                 "stopLoss": {"type": "string", "value": number}
               }
             },
             "riskManagement": {
               "leverage": number,
               "maxConcurrentTrades": number,
               "stopLossPercent": number,
               "takeProfitPercent": number,
               "positionSizePercent": number,
               "trailingStopPercent": number (optional)
             },
             "executionRules": {
               "orderType": "string",
               "timeInForce": "string",
               "slippage": number
             },
             "filters": {
               "minVolume": number,
               "maxSpread": number,
               "allowedAssets": ["string"] (optional)
             }
           }
        
        4. FINANCIAL BEST PRACTICES:
           - Position size should not exceed 5% of portfolio per trade
           - Risk/Reward ratio should be at least 1:2
           - Include volatility-based position sizing
           - Consider market conditions and correlation
        
        5. TECHNICAL INDICATORS (USE PROPERLY):
           - RSI: overbought (70+), oversold (30-)
           - EMA: Use standard periods (9, 20, 50, 200)
           - MACD: Signal line crossovers
           - Bollinger Bands: Price relative to bands
           - Volume: Confirmation signals
           - Support/Resistance levels
        
        6. EXCHANGE COMPATIBILITY:
           - Design for Bybit API compatibility
           - Use standard order types: Market, Limit, Stop
           - Consider exchange-specific features
        
        RESPONSE FORMAT:
        Return ONLY valid JSON. No explanations, no markdown, no additional text.
        Ensure all numeric values are proper numbers, not strings.
        
        SAFETY CHECKS:
        - Never recommend strategies without stop losses
        - Always validate risk/reward ratios
        - Ensure strategies are suitable for crypto market volatility
        - Include safeguards against black swan events
        """
    
    def _create_strategy_prompt(self, description: str, risk_preferences: Dict[str, Any]) -> str:
        """Create a detailed prompt for strategy generation"""
        
        risk_level = risk_preferences.get('risk_level', 'medium')
        max_leverage = risk_preferences.get('max_leverage', 10)
        portfolio_percent = risk_preferences.get('portfolio_percent_per_trade', 2)
        
        return f"""
        Create a crypto trading bot configuration based on this description:
        
        USER REQUEST: "{description}"
        
        RISK PREFERENCES:
        - Risk Level: {risk_level}
        - Maximum Leverage: {max_leverage}x
        - Portfolio % per trade: {portfolio_percent}%
        - Preferred assets: {risk_preferences.get('preferred_assets', 'Major cryptocurrencies')}
        
        REQUIREMENTS:
        1. Generate a complete trading bot configuration following the JSON schema
        2. Ensure the strategy matches the user's description and risk tolerance
        3. Include appropriate technical indicators for the strategy type
        4. Set realistic profit targets and stop losses
        5. Consider current crypto market conditions (high volatility, 24/7 trading)
        
        RISK LEVEL GUIDELINES:
        - Low Risk: Max 3x leverage, 1-2% stop loss, conservative indicators
        - Medium Risk: Max 5x leverage, 2-3% stop loss, balanced approach  
        - High Risk: Max 10x leverage, 3-5% stop loss, aggressive signals
        
        Return the complete JSON configuration now.
        """
    
    def _validate_and_enhance_config(self, config: Dict[str, Any], risk_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the AI-generated configuration"""
        
        # Ensure required fields exist
        if 'riskManagement' not in config:
            config['riskManagement'] = {}
        
        risk_mgmt = config['riskManagement']
        
        # Apply risk preference constraints
        max_leverage = risk_preferences.get('max_leverage', 10)
        if risk_mgmt.get('leverage', 1) > max_leverage:
            risk_mgmt['leverage'] = max_leverage
        
        # Ensure minimum safety requirements
        if not risk_mgmt.get('stopLossPercent'):
            risk_mgmt['stopLossPercent'] = 2  # Default 2% stop loss
        
        if not risk_mgmt.get('takeProfitPercent'):
            risk_mgmt['takeProfitPercent'] = risk_mgmt['stopLossPercent'] * 2  # 1:2 risk/reward
        
        # Limit concurrent trades based on risk level
        risk_level = risk_preferences.get('risk_level', 'medium')
        max_trades = {'low': 2, 'medium': 4, 'high': 6}.get(risk_level, 4)
        
        if risk_mgmt.get('maxConcurrentTrades', 0) > max_trades:
            risk_mgmt['maxConcurrentTrades'] = max_trades
        
        # Add metadata
        config['generatedAt'] = datetime.utcnow().isoformat()
        config['aiModel'] = 'gpt-4'  # Will be 'gpt-5' when available
        config['riskLevel'] = risk_level
        
        return config
    
    async def analyze_market_conditions(self, symbols: List[str]) -> Dict[str, Any]:
        """Analyze current market conditions for better strategy generation"""
        
        prompt = f"""
        Analyze current crypto market conditions for these symbols: {', '.join(symbols)}
        
        Consider:
        1. Overall market trend (bull/bear/sideways)
        2. Volatility levels
        3. Volume patterns
        4. Key support/resistance levels
        5. Recommended strategy types for current conditions
        
        Return analysis as JSON with actionable insights for trading bot configuration.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a crypto market analyst. Provide objective, data-driven analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            # Return default analysis if AI fails
            return {
                "trend": "neutral",
                "volatility": "medium",
                "recommended_strategies": ["trend_following", "breakout"],
                "risk_assessment": "moderate"
            }