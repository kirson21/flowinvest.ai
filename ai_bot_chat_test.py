#!/usr/bin/env python3
"""
AI Bot Chat System Comprehensive Testing
Testing the FIXED AI Bot Chat system with proper conversational flow.

CRITICAL TEST: Test the conversation flow with the exact request that failed:
"Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling"

EXPECTED BEHAVIOR:
1. AI should acknowledge what the user provided (ETH, Long/Short, futures, 5x leverage, volume indicators)
2. AI should ask about MISSING parameters like trading capital, risk management, etc.
3. AI should NOT create a random bot immediately
4. After collecting all info, then create the bot with ready_to_create: true
"""

import requests
import json
import uuid
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://ai-flow-invest.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user ID - using proper UUID format
TEST_USER_ID = str(uuid.uuid4())

class AIBotChatTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.session_id = None
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
        
    def test_health_check(self):
        """Test AI Bot Chat health endpoint."""
        try:
            response = self.session.get(f"{API_BASE}/ai-bot-chat/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test(
                        "AI Bot Chat Health Check",
                        True,
                        f"Status: {data.get('status')}, Models: {data.get('ai_models_available')}, DB: {data.get('database_available')}"
                    )
                    return True
                else:
                    self.log_test("AI Bot Chat Health Check", False, f"Unhealthy status: {data}")
                    return False
            else:
                self.log_test("AI Bot Chat Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI Bot Chat Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_start_chat_session_with_comprehensive_request(self):
        """Test starting chat session with the comprehensive request that should trigger intelligent conversation."""
        try:
            # The exact request from the review that should trigger intelligent conversation
            comprehensive_request = "Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling"
            
            payload = {
                "user_id": TEST_USER_ID,
                "ai_model": "gpt-4o",
                "initial_prompt": comprehensive_request
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.session_id = data.get('session_id')
                    ai_response = data.get('message', '')
                    ready_to_create = data.get('ready_to_create', False)
                    
                    # Check if AI acknowledges the provided information
                    acknowledges_eth = any(word in ai_response.lower() for word in ['eth', 'ethereum'])
                    acknowledges_futures = any(word in ai_response.lower() for word in ['futures', 'leverage'])
                    acknowledges_5x = any(word in ai_response.lower() for word in ['5x', 'leverage'])
                    acknowledges_volume = any(word in ai_response.lower() for word in ['volume', 'indicators'])
                    
                    # Check if AI asks about missing parameters instead of creating bot immediately
                    asks_about_capital = any(word in ai_response.lower() for word in ['capital', 'budget', 'money', 'usd', '$'])
                    asks_about_risk = any(word in ai_response.lower() for word in ['risk', 'stop', 'loss', 'profit'])
                    
                    # Should NOT create bot immediately
                    creates_bot_immediately = ready_to_create or 'ready_to_create' in ai_response
                    
                    context_score = sum([acknowledges_eth, acknowledges_futures, acknowledges_5x, acknowledges_volume])
                    
                    success = (
                        context_score >= 2 and  # Acknowledges at least 2 provided parameters
                        (asks_about_capital or asks_about_risk) and  # Asks about missing info
                        not creates_bot_immediately  # Doesn't create bot immediately
                    )
                    
                    details = f"Context Score: {context_score}/4, Asks Missing Info: {asks_about_capital or asks_about_risk}, Creates Immediately: {creates_bot_immediately}"
                    
                    self.log_test(
                        "Start Chat Session with Comprehensive Request",
                        success,
                        details,
                        {"ai_response": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response}
                    )
                    return success
                else:
                    self.log_test("Start Chat Session with Comprehensive Request", False, f"API returned success=False: {data}")
                    return False
            else:
                self.log_test("Start Chat Session with Comprehensive Request", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Start Chat Session with Comprehensive Request", False, f"Exception: {str(e)}")
            return False
    
    def test_provide_trading_capital(self):
        """Test providing trading capital and verify AI asks about next missing parameter."""
        if not self.session_id:
            self.log_test("Provide Trading Capital", False, "No session ID available")
            return False
            
        try:
            capital_response = "$10,000 trading capital with 5x leverage"
            
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "message_content": capital_response,
                "ai_model": "gpt-4o",
                "bot_creation_stage": "capital_provided"
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    ai_response = data.get('message', '')
                    ready_to_create = data.get('ready_to_create', False)
                    
                    # AI should acknowledge capital and ask about next missing parameter
                    acknowledges_capital = any(word in ai_response.lower() for word in ['10000', '10,000', 'capital', 'budget'])
                    asks_next_question = any(word in ai_response.lower() for word in ['risk', 'strategy', 'timeframe', 'question'])
                    still_not_ready = not ready_to_create
                    
                    success = acknowledges_capital and asks_next_question and still_not_ready
                    
                    details = f"Acknowledges Capital: {acknowledges_capital}, Asks Next: {asks_next_question}, Not Ready: {still_not_ready}"
                    
                    self.log_test(
                        "Provide Trading Capital",
                        success,
                        details,
                        {"ai_response": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response}
                    )
                    return success
                else:
                    self.log_test("Provide Trading Capital", False, f"API returned success=False: {data}")
                    return False
            else:
                self.log_test("Provide Trading Capital", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Provide Trading Capital", False, f"Exception: {str(e)}")
            return False
    
    def test_provide_risk_management(self):
        """Test providing risk management and verify AI continues conversation flow."""
        if not self.session_id:
            self.log_test("Provide Risk Management", False, "No session ID available")
            return False
            
        try:
            risk_response = "2% risk per trade, 3% stop loss, 5% take profit, max 2 positions"
            
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "message_content": risk_response,
                "ai_model": "gpt-4o",
                "bot_creation_stage": "risk_provided"
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    ai_response = data.get('message', '')
                    ready_to_create = data.get('ready_to_create', False)
                    
                    # AI should acknowledge risk parameters
                    acknowledges_risk = any(word in ai_response.lower() for word in ['risk', 'stop', 'profit', '2%', '3%', '5%'])
                    continues_flow = any(word in ai_response.lower() for word in ['question', 'next', 'name', 'strategy', 'timeframe'])
                    
                    success = acknowledges_risk and (continues_flow or ready_to_create)
                    
                    details = f"Acknowledges Risk: {acknowledges_risk}, Continues Flow: {continues_flow}, Ready: {ready_to_create}"
                    
                    self.log_test(
                        "Provide Risk Management",
                        success,
                        details,
                        {"ai_response": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response}
                    )
                    return success
                else:
                    self.log_test("Provide Risk Management", False, f"API returned success=False: {data}")
                    return False
            else:
                self.log_test("Provide Risk Management", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Provide Risk Management", False, f"Exception: {str(e)}")
            return False
    
    def test_provide_bot_name_and_complete_flow(self):
        """Test providing bot name and completing the conversation flow."""
        if not self.session_id:
            self.log_test("Provide Bot Name and Complete Flow", False, "No session ID available")
            return False
            
        try:
            bot_name_response = "ETH Futures Volume Master"
            
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "message_content": bot_name_response,
                "ai_model": "gpt-4o",
                "bot_creation_stage": "name_provided"
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    ai_response = data.get('message', '')
                    ready_to_create = data.get('ready_to_create', False)
                    bot_config = data.get('bot_config')
                    
                    # AI should now be ready to create bot with proper configuration
                    has_bot_config = bot_config is not None
                    config_has_eth = False
                    config_has_futures = False
                    config_has_5x_leverage = False
                    config_has_volume_indicators = False
                    
                    if has_bot_config and isinstance(bot_config, dict):
                        bot_details = bot_config.get('bot_config', {})
                        config_has_eth = bot_details.get('base_coin', '').upper() == 'ETH'
                        config_has_futures = bot_details.get('trade_type', '') == 'futures'
                        config_has_5x_leverage = bot_details.get('leverage', 0) == 5.0
                        
                        # Check for volume indicators in advanced settings
                        advanced_settings = bot_details.get('advanced_settings', {})
                        entry_conditions = advanced_settings.get('entry_conditions', [])
                        config_has_volume_indicators = any('volume' in str(condition).lower() for condition in entry_conditions)
                    
                    success = (
                        ready_to_create and
                        has_bot_config and
                        config_has_eth and
                        config_has_futures and
                        config_has_5x_leverage
                    )
                    
                    details = f"Ready: {ready_to_create}, ETH: {config_has_eth}, Futures: {config_has_futures}, 5x: {config_has_5x_leverage}, Volume: {config_has_volume_indicators}"
                    
                    self.log_test(
                        "Provide Bot Name and Complete Flow",
                        success,
                        details,
                        {"ready_to_create": ready_to_create, "bot_config_keys": list(bot_config.keys()) if bot_config else None}
                    )
                    return success
                else:
                    self.log_test("Provide Bot Name and Complete Flow", False, f"API returned success=False: {data}")
                    return False
            else:
                self.log_test("Provide Bot Name and Complete Flow", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Provide Bot Name and Complete Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_create_final_bot(self):
        """Test creating the final bot with the collected configuration."""
        if not self.session_id:
            self.log_test("Create Final Bot", False, "No session ID available")
            return False
            
        try:
            # Get the final bot configuration from the last message
            history_response = self.session.get(f"{API_BASE}/ai-bot-chat/history/{self.session_id}?user_id={TEST_USER_ID}")
            
            if history_response.status_code != 200:
                self.log_test("Create Final Bot", False, f"Failed to get chat history: {history_response.status_code}")
                return False
            
            history_data = history_response.json()
            messages = history_data.get('messages', [])
            
            # Find the last assistant message with bot configuration
            bot_config = None
            for message in reversed(messages):
                if message.get('message_type') == 'assistant':
                    content = message.get('message_content', '')
                    if 'ready_to_create' in content and '```json' in content:
                        try:
                            json_start = content.find('```json') + 7
                            json_end = content.find('```', json_start)
                            if json_end != -1:
                                json_str = content[json_start:json_end].strip()
                                bot_config = json.loads(json_str)
                                break
                        except:
                            continue
            
            if not bot_config:
                self.log_test("Create Final Bot", False, "No bot configuration found in chat history")
                return False
            
            # Create the bot
            create_payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": {},
                "risk_management": {}
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/create-bot", json=create_payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bot_id = data.get('bot_id')
                    message = data.get('message', '')
                    
                    success = bot_id is not None and 'created successfully' in message.lower()
                    
                    self.log_test(
                        "Create Final Bot",
                        success,
                        f"Bot ID: {bot_id}, Message: {message}",
                        {"bot_id": bot_id}
                    )
                    return success
                else:
                    self.log_test("Create Final Bot", False, f"API returned success=False: {data}")
                    return False
            else:
                self.log_test("Create Final Bot", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Final Bot", False, f"Exception: {str(e)}")
            return False
    
    def test_get_user_ai_bots(self):
        """Test retrieving user AI bots to verify bot was created."""
        try:
            response = self.session.get(f"{API_BASE}/ai-bots/user/{TEST_USER_ID}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bots = data.get('bots', [])
                    total = data.get('total', 0)
                    
                    # Check if our bot was created
                    eth_bot_found = False
                    for bot in bots:
                        if 'eth' in bot.get('name', '').lower() or bot.get('base_coin', '').upper() == 'ETH':
                            eth_bot_found = True
                            break
                    
                    success = total > 0 and eth_bot_found
                    
                    self.log_test(
                        "Get User AI Bots",
                        success,
                        f"Total bots: {total}, ETH bot found: {eth_bot_found}",
                        {"total_bots": total, "bot_names": [bot.get('name') for bot in bots]}
                    )
                    return success
                else:
                    self.log_test("Get User AI Bots", False, f"API returned success=False: {data}")
                    return False
            else:
                self.log_test("Get User AI Bots", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get User AI Bots", False, f"Exception: {str(e)}")
            return False
    
    def test_conversation_context_preservation(self):
        """Test that conversation context is preserved throughout the flow."""
        if not self.session_id:
            self.log_test("Conversation Context Preservation", False, "No session ID available")
            return False
            
        try:
            # Get full conversation history
            response = self.session.get(f"{API_BASE}/ai-bot-chat/history/{self.session_id}?user_id={TEST_USER_ID}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    messages = data.get('messages', [])
                    
                    # Check that we have a reasonable conversation flow
                    user_messages = [msg for msg in messages if msg.get('message_type') == 'user']
                    assistant_messages = [msg for msg in messages if msg.get('message_type') == 'assistant']
                    
                    # Should have multiple exchanges
                    has_multiple_exchanges = len(user_messages) >= 3 and len(assistant_messages) >= 3
                    
                    # Check that assistant messages don't repeat the same question
                    assistant_contents = [msg.get('message_content', '') for msg in assistant_messages]
                    no_repeated_questions = len(set(assistant_contents)) == len(assistant_contents)
                    
                    # Check that context is maintained (ETH mentioned consistently)
                    eth_mentioned_consistently = sum(1 for content in assistant_contents if 'eth' in content.lower()) >= 2
                    
                    success = has_multiple_exchanges and no_repeated_questions and eth_mentioned_consistently
                    
                    details = f"Exchanges: {len(user_messages)}/{len(assistant_messages)}, No Repeats: {no_repeated_questions}, ETH Consistent: {eth_mentioned_consistently}"
                    
                    self.log_test(
                        "Conversation Context Preservation",
                        success,
                        details,
                        {"total_messages": len(messages), "user_messages": len(user_messages), "assistant_messages": len(assistant_messages)}
                    )
                    return success
                else:
                    self.log_test("Conversation Context Preservation", False, f"API returned success=False: {data}")
                    return False
            else:
                self.log_test("Conversation Context Preservation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Conversation Context Preservation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all AI Bot Chat tests."""
        print("=" * 80)
        print("AI BOT CHAT SYSTEM COMPREHENSIVE TESTING")
        print("Testing FIXED AI Bot Chat system with proper conversational flow")
        print("=" * 80)
        print()
        
        tests = [
            self.test_health_check,
            self.test_start_chat_session_with_comprehensive_request,
            self.test_provide_trading_capital,
            self.test_provide_risk_management,
            self.test_provide_bot_name_and_complete_flow,
            self.test_create_final_bot,
            self.test_get_user_ai_bots,
            self.test_conversation_context_preservation
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Print detailed results
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("=" * 80)
        
        if success_rate >= 75:
            print("🎉 AI BOT CHAT SYSTEM IS WORKING CORRECTLY!")
            print("✅ Intelligent conversation flow implemented")
            print("✅ Context preservation working")
            print("✅ Proper bot creation with user specifications")
        else:
            print("⚠️  AI BOT CHAT SYSTEM HAS ISSUES")
            print("❌ Some critical functionality is not working")
        
        print("=" * 80)
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = AIBotChatTester()
    tester.run_all_tests()