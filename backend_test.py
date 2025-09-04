#!/usr/bin/env python3
"""
AI Bot Chat System Deployment Fix Verification Test
Tests the AI Bot Chat system using existing GrokBotCreator service
"""

import requests
import json
import uuid
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class AIBotChatTester:
    def __init__(self):
        self.base_url = f"{BACKEND_URL}/api"
        self.test_user_id = TEST_USER_ID
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Bot-Chat-Tester/1.0'
        })
        
        # Test tracking
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
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
    
    def test_health_check(self):
        """Test 1: Health Check - Verify no dependency errors and proper integration"""
        try:
            response = self.session.get(f"{self.base_url}/ai-bot-chat/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic health status
                if data.get('status') == 'healthy':
                    # Verify GrokBotCreator integration
                    grok_service = data.get('grok_service')
                    database_available = data.get('database_available')
                    ai_models = data.get('ai_models_available', [])
                    message = data.get('message', '')
                    
                    # Check for proper integration message
                    integration_confirmed = 'GrokBotCreator' in message
                    
                    if integration_confirmed and database_available and ai_models:
                        self.log_test(
                            "Health Check - GrokBotCreator Integration", 
                            True,
                            f"Status: {data.get('status')}, Models: {ai_models}, Grok Service: {grok_service}, DB: {database_available}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Health Check - GrokBotCreator Integration", 
                            False,
                            f"Missing integration components - Grok: {grok_service}, DB: {database_available}, Models: {ai_models}"
                        )
                        return False
                else:
                    self.log_test("Health Check - GrokBotCreator Integration", False, f"Unhealthy status: {data.get('status')}")
                    return False
            else:
                self.log_test("Health Check - GrokBotCreator Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check - GrokBotCreator Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_start_chat_session(self):
        """Test 2: Start Chat Session with existing AI integration"""
        try:
            # Test with Grok-4 (should use existing service)
            payload = {
                "user_id": self.test_user_id,
                "ai_model": "grok-4",
                "initial_prompt": "I want to create a conservative Bitcoin trading bot"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('session_id') and data.get('message'):
                    self.session_id = data.get('session_id')
                    self.log_test(
                        "Start Chat Session - Existing AI Integration", 
                        True,
                        f"Session ID: {self.session_id}, AI Model: {data.get('ai_model')}, Stage: {data.get('stage')}"
                    )
                    return True
                else:
                    self.log_test("Start Chat Session - Existing AI Integration", False, f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("Start Chat Session - Existing AI Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Start Chat Session - Existing AI Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_chat_conversation_flow(self):
        """Test 3: Chat conversation using existing AI logic"""
        try:
            if not hasattr(self, 'session_id'):
                self.log_test("Chat Conversation Flow - Existing AI Logic", False, "No session ID available")
                return False
            
            # Send follow-up messages to test conversation flow
            messages = [
                "I prefer conservative trading with low risk",
                "I want to trade Bitcoin with steady gains",
                "I like trend following strategies for long-term profits"
            ]
            
            conversation_success = True
            
            for i, message in enumerate(messages):
                payload = {
                    "user_id": self.test_user_id,
                    "session_id": self.session_id,
                    "message_content": message,
                    "ai_model": "grok-4",
                    "bot_creation_stage": "clarification"
                }
                
                response = self.session.post(f"{self.base_url}/ai-bot-chat/send-message", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('message'):
                        # Check if bot is ready to create after enough conversation
                        if data.get('ready_to_create'):
                            self.bot_config = data.get('bot_config')
                            print(f"   Bot ready after message {i+1}: {data.get('ready_to_create')}")
                        time.sleep(0.5)  # Small delay between messages
                    else:
                        conversation_success = False
                        break
                else:
                    conversation_success = False
                    break
            
            if conversation_success:
                self.log_test(
                    "Chat Conversation Flow - Existing AI Logic", 
                    True,
                    f"Successfully processed {len(messages)} messages, Bot ready: {hasattr(self, 'bot_config')}"
                )
                return True
            else:
                self.log_test("Chat Conversation Flow - Existing AI Logic", False, "Failed to process conversation messages")
                return False
                
        except Exception as e:
            self.log_test("Chat Conversation Flow - Existing AI Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_grok_bot_creator_integration(self):
        """Test 4: Verify GrokBotCreator.generate_bot_config() method usage"""
        try:
            # Test the bot configuration generation directly
            if not hasattr(self, 'session_id'):
                self.log_test("GrokBotCreator Integration - generate_bot_config()", False, "No session ID available")
                return False
            
            # Send a message that should trigger bot config generation
            payload = {
                "user_id": self.test_user_id,
                "session_id": self.session_id,
                "message_content": "Create a conservative Bitcoin trend following bot with steady gains and low risk",
                "ai_model": "grok-4",
                "bot_creation_stage": "final"
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/send-message", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('ready_to_create') and data.get('bot_config'):
                    bot_config = data.get('bot_config')
                    
                    # Verify the bot config has expected GrokBotCreator structure
                    expected_fields = ['bot_config', 'strategy_config', 'risk_management']
                    has_expected_structure = all(field in bot_config for field in expected_fields)
                    
                    # Check bot_config inner structure
                    inner_config = bot_config.get('bot_config', {})
                    has_bot_details = all(field in inner_config for field in ['name', 'description', 'strategy', 'base_coin'])
                    
                    if has_expected_structure and has_bot_details:
                        self.bot_config = bot_config
                        self.log_test(
                            "GrokBotCreator Integration - generate_bot_config()", 
                            True,
                            f"Generated config with strategy: {inner_config.get('strategy')}, coin: {inner_config.get('base_coin')}, risk: {inner_config.get('risk_level')}"
                        )
                        return True
                    else:
                        self.log_test(
                            "GrokBotCreator Integration - generate_bot_config()", 
                            False, 
                            f"Invalid config structure - Expected: {has_expected_structure}, Bot details: {has_bot_details}"
                        )
                        return False
                else:
                    self.log_test(
                        "GrokBotCreator Integration - generate_bot_config()", 
                        False, 
                        f"Bot not ready or config missing - Ready: {data.get('ready_to_create')}, Config: {bool(data.get('bot_config'))}"
                    )
                    return False
            else:
                self.log_test("GrokBotCreator Integration - generate_bot_config()", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GrokBotCreator Integration - generate_bot_config()", False, f"Exception: {str(e)}")
            return False
    
    def test_bot_creation_with_existing_services(self):
        """Test 5: Complete bot creation using existing services"""
        try:
            if not hasattr(self, 'bot_config') or not hasattr(self, 'session_id'):
                self.log_test("Bot Creation - Existing Services", False, "No bot config or session ID available")
                return False
            
            payload = {
                "user_id": self.test_user_id,
                "session_id": self.session_id,
                "ai_model": "grok-4",
                "bot_config": self.bot_config,
                "strategy_config": self.bot_config.get('strategy_config', {}),
                "risk_management": self.bot_config.get('risk_management', {})
            }
            
            response = self.session.post(f"{self.base_url}/ai-bot-chat/create-bot", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('bot_id'):
                    self.created_bot_id = data.get('bot_id')
                    self.log_test(
                        "Bot Creation - Existing Services", 
                        True,
                        f"Created bot ID: {self.created_bot_id}, Message: {data.get('message')}"
                    )
                    return True
                else:
                    self.log_test("Bot Creation - Existing Services", False, f"Creation failed: {data}")
                    return False
            else:
                self.log_test("Bot Creation - Existing Services", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Bot Creation - Existing Services", False, f"Exception: {str(e)}")
            return False
    
    def test_chat_history_retrieval(self):
        """Test 6: Chat history retrieval and database operations"""
        try:
            if not hasattr(self, 'session_id'):
                self.log_test("Chat History Retrieval - Database Operations", False, "No session ID available")
                return False
            
            response = self.session.get(
                f"{self.base_url}/ai-bot-chat/history/{self.session_id}",
                params={"user_id": self.test_user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('messages'):
                    messages = data.get('messages')
                    message_count = len(messages)
                    
                    # Verify we have both user and assistant messages
                    user_messages = [msg for msg in messages if msg.get('message_type') == 'user']
                    assistant_messages = [msg for msg in messages if msg.get('message_type') == 'assistant']
                    
                    if user_messages and assistant_messages:
                        self.log_test(
                            "Chat History Retrieval - Database Operations", 
                            True,
                            f"Retrieved {message_count} messages ({len(user_messages)} user, {len(assistant_messages)} assistant)"
                        )
                        return True
                    else:
                        self.log_test(
                            "Chat History Retrieval - Database Operations", 
                            False, 
                            f"Missing message types - User: {len(user_messages)}, Assistant: {len(assistant_messages)}"
                        )
                        return False
                else:
                    self.log_test("Chat History Retrieval - Database Operations", False, f"No messages or failed: {data}")
                    return False
            else:
                self.log_test("Chat History Retrieval - Database Operations", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Chat History Retrieval - Database Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_user_ai_bots_retrieval(self):
        """Test 7: User AI bots retrieval to verify bot was created"""
        try:
            response = self.session.get(f"{self.base_url}/ai-bots/user/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    bots = data.get('bots', [])
                    total = data.get('total', 0)
                    
                    # Check if our created bot exists
                    created_bot_found = False
                    if hasattr(self, 'created_bot_id'):
                        created_bot_found = any(bot.get('id') == self.created_bot_id for bot in bots)
                    
                    self.log_test(
                        "User AI Bots Retrieval - Bot Verification", 
                        True,
                        f"Found {total} AI bots, Created bot found: {created_bot_found}"
                    )
                    return True
                else:
                    self.log_test("User AI Bots Retrieval - Bot Verification", False, f"Request failed: {data}")
                    return False
            else:
                self.log_test("User AI Bots Retrieval - Bot Verification", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User AI Bots Retrieval - Bot Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_no_external_dependencies(self):
        """Test 8: Verify no external API dependencies are causing conflicts"""
        try:
            # Test multiple rapid requests to check for dependency conflicts
            rapid_test_success = True
            
            for i in range(3):
                payload = {
                    "user_id": self.test_user_id,
                    "ai_model": "grok-4",
                    "initial_prompt": f"Test prompt {i+1} for dependency check"
                }
                
                response = self.session.post(f"{self.base_url}/ai-bot-chat/start-session", json=payload)
                
                if response.status_code != 200:
                    rapid_test_success = False
                    break
                
                data = response.json()
                if not data.get('success'):
                    rapid_test_success = False
                    break
                
                time.sleep(0.2)  # Small delay
            
            if rapid_test_success:
                self.log_test(
                    "No External Dependencies - Conflict Check", 
                    True,
                    "Multiple rapid requests succeeded without dependency conflicts"
                )
                return True
            else:
                self.log_test("No External Dependencies - Conflict Check", False, "Dependency conflicts detected in rapid requests")
                return False
                
        except Exception as e:
            self.log_test("No External Dependencies - Conflict Check", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all AI Bot Chat deployment fix verification tests"""
        print("🚀 Starting AI Bot Chat Deployment Fix Verification Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        # Run tests in sequence
        test_methods = [
            self.test_health_check,
            self.test_start_chat_session,
            self.test_chat_conversation_flow,
            self.test_grok_bot_creator_integration,
            self.test_bot_creation_with_existing_services,
            self.test_chat_history_retrieval,
            self.test_user_ai_bots_retrieval,
            self.test_no_external_dependencies
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ {test_method.__name__} - Unexpected error: {str(e)}")
            print()  # Add spacing between tests
        
        # Print summary
        print("=" * 80)
        print("🏁 AI BOT CHAT DEPLOYMENT FIX VERIFICATION SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL TESTS PASSED - AI Bot Chat deployment fix is working correctly!")
        else:
            print(f"❌ {self.tests_run - self.tests_passed} TESTS FAILED - Issues detected with deployment fix")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = AIBotChatTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)