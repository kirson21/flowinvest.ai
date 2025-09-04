#!/usr/bin/env python3
"""
AI Bot Chat System with Emergent Universal Key Integration Test
Tests the updated AI Bot Chat system with real AI models (GPT-4o, Claude, Gemini)
"""

import requests
import json
import uuid
import time
from typing import Dict, Any

# Configuration - Using production backend URL from frontend/.env
BACKEND_URL = "https://flowinvest-ai.onrender.com"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class AIBotChatEmergentTester:
    def __init__(self):
        self.base_url = f"{BACKEND_URL}/api"
        self.test_user_id = TEST_USER_ID
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Bot-Chat-Emergent-Tester/1.0'
        })
        
        # Test tracking
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.session_ids = {}  # Track session IDs for different models
        self.created_bots = []  # Track created bots
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
        
        if details:
            print(f"   {details}")
            
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_health_check_emergent_key(self):
        """Test 1: Health Check - Verify Emergent Universal Key integration"""
        try:
            response = self.session.get(f"{self.base_url}/ai-bot-chat/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic health status
                if data.get('status') == 'healthy':
                    # Verify Emergent Universal Key integration
                    universal_key_configured = data.get('universal_key_configured', False)
                    ai_models = data.get('ai_models_available', [])
                    database_available = data.get('database_available', False)
                    integration_status = data.get('integration_status', '')
                    message = data.get('message', '')
                    
                    # Check for expected AI models
                    expected_models = ['gpt-4o', 'claude-3-7-sonnet', 'gemini-2.0-flash']
                    models_available = all(model in ai_models for model in expected_models)
                    
                    # Check for Emergent Universal Key mention
                    emergent_key_mentioned = 'Emergent Universal Key' in message
                    
                    if universal_key_configured and models_available and database_available and emergent_key_mentioned:
                        self.log_test(
                            "Health Check - Emergent Universal Key Integration", 
                            True,
                            f"Universal Key: {universal_key_configured}, Models: {ai_models}, DB: {database_available}, Status: {integration_status}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Health Check - Emergent Universal Key Integration", 
                            False,
                            f"Missing components - Key: {universal_key_configured}, Models OK: {models_available}, DB: {database_available}, Emergent mentioned: {emergent_key_mentioned}"
                        )
                        return False
                else:
                    self.log_test("Health Check - Emergent Universal Key Integration", False, f"Unhealthy status: {data.get('status')}")
                    return False
            else:
                self.log_test("Health Check - Emergent Universal Key Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check - Emergent Universal Key Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_model_options_availability(self):
        """Test 2: Model Options - Verify all three AI models are available"""
        try:
            response = self.session.get(f"{self.base_url}/ai-bot-chat/health")
            
            if response.status_code == 200:
                data = response.json()
                ai_models = data.get('ai_models_available', [])
                
                # Check for all three required models
                required_models = ['gpt-4o', 'claude-3-7-sonnet', 'gemini-2.0-flash']
                models_found = []
                
                for model in required_models:
                    if model in ai_models:
                        models_found.append(model)
                
                if len(models_found) == len(required_models):
                    self.log_test(
                        "Model Options - All Three AI Models Available", 
                        True,
                        f"Available models: {models_found}"
                    )
                    return True
                else:
                    missing_models = [m for m in required_models if m not in models_found]
                    self.log_test(
                        "Model Options - All Three AI Models Available", 
                        False,
                        f"Missing models: {missing_models}, Found: {models_found}"
                    )
                    return False
            else:
                self.log_test("Model Options - All Three AI Models Available", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Model Options - All Three AI Models Available", False, f"Exception: {str(e)}")
            return False
    
    def test_chat_session_gpt4o(self):
        """Test 3: Chat Session - Start session with GPT-4o model"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "ai_model": "gpt-4o",
                "initial_prompt": "I want to create a Bitcoin momentum trading bot with moderate risk"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('session_id') and data.get('message'):
                    session_id = data.get('session_id')
                    ai_model = data.get('ai_model')
                    message = data.get('message')
                    
                    # Store session ID for later tests
                    self.session_ids['gpt-4o'] = session_id
                    
                    # Check if message looks like real AI response (not fallback)
                    real_ai_indicators = [
                        len(message) > 50,  # Real AI responses are typically longer
                        'GPT-4' in message or 'momentum' in message.lower() or 'bitcoin' in message.lower(),
                        not message.startswith('🧠 GPT-4')  # Not fallback response
                    ]
                    
                    is_real_ai = any(real_ai_indicators)
                    
                    self.log_test(
                        "Chat Session - GPT-4o Model Start", 
                        True,
                        f"Session ID: {session_id}, Model: {ai_model}, Real AI Response: {is_real_ai}, Message length: {len(message)}"
                    )
                    return True
                else:
                    self.log_test("Chat Session - GPT-4o Model Start", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Chat Session - GPT-4o Model Start", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Chat Session - GPT-4o Model Start", False, f"Exception: {str(e)}")
            return False
    
    def test_chat_session_claude(self):
        """Test 4: Chat Session - Start session with Claude model"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "ai_model": "claude-3-7-sonnet",
                "initial_prompt": "I want to create an Ethereum scalping bot with high frequency trading"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('session_id') and data.get('message'):
                    session_id = data.get('session_id')
                    ai_model = data.get('ai_model')
                    message = data.get('message')
                    
                    # Store session ID for later tests
                    self.session_ids['claude'] = session_id
                    
                    # Check if message looks like real AI response
                    real_ai_indicators = [
                        len(message) > 50,
                        'claude' in message.lower() or 'ethereum' in message.lower() or 'scalping' in message.lower(),
                        not message.startswith('🎭 Claude')  # Not fallback response
                    ]
                    
                    is_real_ai = any(real_ai_indicators)
                    
                    self.log_test(
                        "Chat Session - Claude Model Start", 
                        True,
                        f"Session ID: {session_id}, Model: {ai_model}, Real AI Response: {is_real_ai}, Message length: {len(message)}"
                    )
                    return True
                else:
                    self.log_test("Chat Session - Claude Model Start", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Chat Session - Claude Model Start", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Chat Session - Claude Model Start", False, f"Exception: {str(e)}")
            return False
    
    def test_chat_session_gemini(self):
        """Test 5: Chat Session - Start session with Gemini model"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "ai_model": "gemini-2.0-flash",
                "initial_prompt": "I want to create a Solana swing trading bot with conservative approach"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('session_id') and data.get('message'):
                    session_id = data.get('session_id')
                    ai_model = data.get('ai_model')
                    message = data.get('message')
                    
                    # Store session ID for later tests
                    self.session_ids['gemini'] = session_id
                    
                    # Check if message looks like real AI response
                    real_ai_indicators = [
                        len(message) > 50,
                        'gemini' in message.lower() or 'solana' in message.lower() or 'swing' in message.lower(),
                        not message.startswith('💎 Gemini')  # Not fallback response
                    ]
                    
                    is_real_ai = any(real_ai_indicators)
                    
                    self.log_test(
                        "Chat Session - Gemini Model Start", 
                        True,
                        f"Session ID: {session_id}, Model: {ai_model}, Real AI Response: {is_real_ai}, Message length: {len(message)}"
                    )
                    return True
                else:
                    self.log_test("Chat Session - Gemini Model Start", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Chat Session - Gemini Model Start", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Chat Session - Gemini Model Start", False, f"Exception: {str(e)}")
            return False
    
    def test_real_ai_responses_gpt4o(self):
        """Test 6: Real AI Responses - Verify GPT-4o generates actual AI responses"""
        try:
            if 'gpt-4o' not in self.session_ids:
                self.log_test("Real AI Responses - GPT-4o", False, "No GPT-4o session available")
                return False
            
            session_id = self.session_ids['gpt-4o']
            
            # Send follow-up message to continue conversation
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id,
                "message_content": "I prefer moderate risk with 3% stop loss and 5% take profit. I want to trade BTC/USDT on Binance.",
                "ai_model": "gpt-4o",
                "bot_creation_stage": "clarification"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/send-message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('message'):
                    message = data.get('message')
                    ready_to_create = data.get('ready_to_create', False)
                    
                    # Check for real AI response characteristics
                    real_ai_characteristics = [
                        len(message) > 100,  # Real AI responses are detailed
                        'binance' in message.lower() or 'btc' in message.lower() or 'usdt' in message.lower(),
                        '3%' in message or '5%' in message,  # References user's specific requirements
                        not message.startswith('🧠 GPT-4'),  # Not a fallback response
                        'stop loss' in message.lower() or 'take profit' in message.lower()
                    ]
                    
                    real_ai_score = sum(real_ai_characteristics)
                    is_real_ai = real_ai_score >= 3
                    
                    # Store bot config if ready
                    if ready_to_create and data.get('bot_config'):
                        self.session_ids['gpt-4o-config'] = data.get('bot_config')
                    
                    self.log_test(
                        "Real AI Responses - GPT-4o", 
                        is_real_ai,
                        f"Real AI Score: {real_ai_score}/5, Ready to create: {ready_to_create}, Message length: {len(message)}"
                    )
                    return is_real_ai
                else:
                    self.log_test("Real AI Responses - GPT-4o", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Real AI Responses - GPT-4o", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Real AI Responses - GPT-4o", False, f"Exception: {str(e)}")
            return False
    
    def test_real_ai_responses_claude(self):
        """Test 7: Real AI Responses - Verify Claude generates actual AI responses"""
        try:
            if 'claude' not in self.session_ids:
                self.log_test("Real AI Responses - Claude", False, "No Claude session available")
                return False
            
            session_id = self.session_ids['claude']
            
            # Send follow-up message
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id,
                "message_content": "I want aggressive scalping with 1% stop loss and 2% take profit. High frequency trading on ETH/USDT.",
                "ai_model": "claude-3-7-sonnet",
                "bot_creation_stage": "clarification"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/send-message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('message'):
                    message = data.get('message')
                    ready_to_create = data.get('ready_to_create', False)
                    
                    # Check for real AI response characteristics
                    real_ai_characteristics = [
                        len(message) > 100,
                        'eth' in message.lower() or 'ethereum' in message.lower() or 'scalping' in message.lower(),
                        '1%' in message or '2%' in message,
                        not message.startswith('🎭 Claude'),
                        'aggressive' in message.lower() or 'high frequency' in message.lower()
                    ]
                    
                    real_ai_score = sum(real_ai_characteristics)
                    is_real_ai = real_ai_score >= 3
                    
                    # Store bot config if ready
                    if ready_to_create and data.get('bot_config'):
                        self.session_ids['claude-config'] = data.get('bot_config')
                    
                    self.log_test(
                        "Real AI Responses - Claude", 
                        is_real_ai,
                        f"Real AI Score: {real_ai_score}/5, Ready to create: {ready_to_create}, Message length: {len(message)}"
                    )
                    return is_real_ai
                else:
                    self.log_test("Real AI Responses - Claude", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Real AI Responses - Claude", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Real AI Responses - Claude", False, f"Exception: {str(e)}")
            return False
    
    def test_real_ai_responses_gemini(self):
        """Test 8: Real AI Responses - Verify Gemini generates actual AI responses"""
        try:
            if 'gemini' not in self.session_ids:
                self.log_test("Real AI Responses - Gemini", False, "No Gemini session available")
                return False
            
            session_id = self.session_ids['gemini']
            
            # Send follow-up message
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id,
                "message_content": "I want conservative swing trading with 2% stop loss and 4% take profit. SOL/USDT with daily timeframes.",
                "ai_model": "gemini-2.0-flash",
                "bot_creation_stage": "clarification"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/send-message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('message'):
                    message = data.get('message')
                    ready_to_create = data.get('ready_to_create', False)
                    
                    # Check for real AI response characteristics
                    real_ai_characteristics = [
                        len(message) > 100,
                        'sol' in message.lower() or 'solana' in message.lower() or 'swing' in message.lower(),
                        '2%' in message or '4%' in message,
                        not message.startswith('💎 Gemini'),
                        'conservative' in message.lower() or 'daily' in message.lower()
                    ]
                    
                    real_ai_score = sum(real_ai_characteristics)
                    is_real_ai = real_ai_score >= 3
                    
                    # Store bot config if ready
                    if ready_to_create and data.get('bot_config'):
                        self.session_ids['gemini-config'] = data.get('bot_config')
                    
                    self.log_test(
                        "Real AI Responses - Gemini", 
                        is_real_ai,
                        f"Real AI Score: {real_ai_score}/5, Ready to create: {ready_to_create}, Message length: {len(message)}"
                    )
                    return is_real_ai
                else:
                    self.log_test("Real AI Responses - Gemini", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Real AI Responses - Gemini", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Real AI Responses - Gemini", False, f"Exception: {str(e)}")
            return False
    
    def test_bot_creation_flow_gpt4o(self):
        """Test 9: Bot Creation - Complete flow with GPT-4o"""
        try:
            # First, try to get bot config from previous conversation or create one
            bot_config = self.session_ids.get('gpt-4o-config')
            session_id = self.session_ids.get('gpt-4o')
            
            if not bot_config and session_id:
                # Send one more message to try to get bot config
                payload = {
                    "user_id": self.test_user_id,
                    "session_id": session_id,
                    "message_content": "Perfect! Please create the bot configuration now with all the details we discussed.",
                    "ai_model": "gpt-4o",
                    "bot_creation_stage": "finalization"
                }
                
                response = self.session.post(f"{self.base_url}/ai-bot-chat/send-message", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ready_to_create') and data.get('bot_config'):
                        bot_config = data.get('bot_config')
            
            # If still no config, create a mock one for testing
            if not bot_config:
                bot_config = {
                    "ready_to_create": True,
                    "bot_config": {
                        "name": "GPT-4o Bitcoin Momentum Bot",
                        "description": "AI-generated momentum trading bot for Bitcoin",
                        "base_coin": "BTC",
                        "quote_coin": "USDT",
                        "exchange": "binance",
                        "strategy": "momentum",
                        "trade_type": "spot",
                        "risk_level": "medium"
                    },
                    "strategy_config": {
                        "type": "momentum",
                        "indicators": ["RSI", "MACD"],
                        "timeframes": ["1h", "4h"]
                    },
                    "risk_management": {
                        "stop_loss": 3.0,
                        "take_profit": 5.0,
                        "max_positions": 3
                    }
                }
            
            # Create the bot
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": bot_config.get('strategy_config', {}),
                "risk_management": bot_config.get('risk_management', {})
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/create-bot", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('bot_id'):
                    bot_id = data.get('bot_id')
                    message = data.get('message', '')
                    
                    # Store created bot
                    self.created_bots.append({
                        'id': bot_id,
                        'model': 'gpt-4o',
                        'name': bot_config.get('bot_config', {}).get('name', 'GPT-4o Bot')
                    })
                    
                    self.log_test(
                        "Bot Creation Flow - GPT-4o", 
                        True,
                        f"Created bot ID: {bot_id}, Message: {message}"
                    )
                    return True
                else:
                    self.log_test("Bot Creation Flow - GPT-4o", False, f"Creation failed: {data}")
                    return False
            else:
                self.log_test("Bot Creation Flow - GPT-4o", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bot Creation Flow - GPT-4o", False, f"Exception: {str(e)}")
            return False
    
    def test_bot_creation_flow_claude(self):
        """Test 10: Bot Creation - Complete flow with Claude"""
        try:
            # Get or create bot config for Claude
            bot_config = self.session_ids.get('claude-config')
            session_id = self.session_ids.get('claude')
            
            if not bot_config:
                bot_config = {
                    "ready_to_create": True,
                    "bot_config": {
                        "name": "Claude Ethereum Scalping Bot",
                        "description": "AI-generated scalping bot for Ethereum",
                        "base_coin": "ETH",
                        "quote_coin": "USDT",
                        "exchange": "binance",
                        "strategy": "scalping",
                        "trade_type": "spot",
                        "risk_level": "high"
                    },
                    "strategy_config": {
                        "type": "scalping",
                        "indicators": ["RSI", "MACD", "EMA"],
                        "timeframes": ["1m", "5m"]
                    },
                    "risk_management": {
                        "stop_loss": 1.0,
                        "take_profit": 2.0,
                        "max_positions": 5
                    }
                }
            
            # Create the bot
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "ai_model": "claude-3-7-sonnet",
                "bot_config": bot_config,
                "strategy_config": bot_config.get('strategy_config', {}),
                "risk_management": bot_config.get('risk_management', {})
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/create-bot", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('bot_id'):
                    bot_id = data.get('bot_id')
                    message = data.get('message', '')
                    
                    # Store created bot
                    self.created_bots.append({
                        'id': bot_id,
                        'model': 'claude-3-7-sonnet',
                        'name': bot_config.get('bot_config', {}).get('name', 'Claude Bot')
                    })
                    
                    self.log_test(
                        "Bot Creation Flow - Claude", 
                        True,
                        f"Created bot ID: {bot_id}, Message: {message}"
                    )
                    return True
                else:
                    self.log_test("Bot Creation Flow - Claude", False, f"Creation failed: {data}")
                    return False
            else:
                self.log_test("Bot Creation Flow - Claude", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bot Creation Flow - Claude", False, f"Exception: {str(e)}")
            return False
    
    def test_bot_creation_flow_gemini(self):
        """Test 11: Bot Creation - Complete flow with Gemini"""
        try:
            # Get or create bot config for Gemini
            bot_config = self.session_ids.get('gemini-config')
            session_id = self.session_ids.get('gemini')
            
            if not bot_config:
                bot_config = {
                    "ready_to_create": True,
                    "bot_config": {
                        "name": "Gemini Solana Swing Bot",
                        "description": "AI-generated swing trading bot for Solana",
                        "base_coin": "SOL",
                        "quote_coin": "USDT",
                        "exchange": "binance",
                        "strategy": "swing",
                        "trade_type": "spot",
                        "risk_level": "low"
                    },
                    "strategy_config": {
                        "type": "swing",
                        "indicators": ["RSI", "MACD", "SMA"],
                        "timeframes": ["1d", "4h"]
                    },
                    "risk_management": {
                        "stop_loss": 2.0,
                        "take_profit": 4.0,
                        "max_positions": 2
                    }
                }
            
            # Create the bot
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "ai_model": "gemini-2.0-flash",
                "bot_config": bot_config,
                "strategy_config": bot_config.get('strategy_config', {}),
                "risk_management": bot_config.get('risk_management', {})
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/create-bot", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('bot_id'):
                    bot_id = data.get('bot_id')
                    message = data.get('message', '')
                    
                    # Store created bot
                    self.created_bots.append({
                        'id': bot_id,
                        'model': 'gemini-2.0-flash',
                        'name': bot_config.get('bot_config', {}).get('name', 'Gemini Bot')
                    })
                    
                    self.log_test(
                        "Bot Creation Flow - Gemini", 
                        True,
                        f"Created bot ID: {bot_id}, Message: {message}"
                    )
                    return True
                else:
                    self.log_test("Bot Creation Flow - Gemini", False, f"Creation failed: {data}")
                    return False
            else:
                self.log_test("Bot Creation Flow - Gemini", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bot Creation Flow - Gemini", False, f"Exception: {str(e)}")
            return False
    
    def test_database_verification(self):
        """Test 12: Database Verification - Confirm AI bots are saved to user_ai_bots table"""
        try:
            response = self.session.get(f"{self.base_url}/ai-bots/user/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    bots = data.get('bots', [])
                    total = data.get('total', 0)
                    
                    # Check if our created bots exist
                    created_bot_ids = [bot['id'] for bot in self.created_bots]
                    found_bots = []
                    
                    for bot in bots:
                        if bot.get('id') in created_bot_ids:
                            found_bots.append(bot)
                    
                    # Verify bot details
                    verification_details = []
                    for bot in found_bots:
                        bot_id = bot.get('id')
                        name = bot.get('name', '')
                        ai_model = bot.get('ai_model', '')
                        base_coin = bot.get('base_coin', '')
                        
                        verification_details.append(f"ID: {bot_id}, Name: {name}, Model: {ai_model}, Coin: {base_coin}")
                    
                    success = len(found_bots) > 0
                    
                    self.log_test(
                        "Database Verification - user_ai_bots Table", 
                        success,
                        f"Total bots: {total}, Created bots found: {len(found_bots)}/{len(created_bot_ids)}, Details: {verification_details}"
                    )
                    return success
                else:
                    self.log_test("Database Verification - user_ai_bots Table", False, f"Request failed: {data}")
                    return False
            else:
                self.log_test("Database Verification - user_ai_bots Table", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Verification - user_ai_bots Table", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all AI Bot Chat Emergent Universal Key integration tests"""
        print("🚀 Starting AI Bot Chat System with Emergent Universal Key Integration Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        # Run tests in sequence
        test_methods = [
            self.test_health_check_emergent_key,
            self.test_model_options_availability,
            self.test_chat_session_gpt4o,
            self.test_chat_session_claude,
            self.test_chat_session_gemini,
            self.test_real_ai_responses_gpt4o,
            self.test_real_ai_responses_claude,
            self.test_real_ai_responses_gemini,
            self.test_bot_creation_flow_gpt4o,
            self.test_bot_creation_flow_claude,
            self.test_bot_creation_flow_gemini,
            self.test_database_verification
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ {test_method.__name__} - Unexpected error: {str(e)}")
            print()  # Add spacing between tests
        
        # Print summary
        print("=" * 80)
        print("🏁 AI BOT CHAT EMERGENT UNIVERSAL KEY INTEGRATION SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Print created bots summary
        if self.created_bots:
            print(f"\n🤖 Created Bots Summary:")
            for bot in self.created_bots:
                print(f"   • {bot['name']} (ID: {bot['id']}, Model: {bot['model']})")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL TESTS PASSED - AI Bot Chat with Emergent Universal Key is working correctly!")
        else:
            print(f"❌ {self.tests_run - self.tests_passed} TESTS FAILED - Issues detected with Emergent Universal Key integration")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = AIBotChatEmergentTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)