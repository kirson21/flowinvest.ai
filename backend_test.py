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
                if data.get("status") == "healthy":
                    self.log_test(
                        "AI Bot Chat Health Check",
                        True,
                        f"Status: {data.get('status')}, Models: {data.get('ai_models_available')}, DB: {data.get('database_available')}"
                    )
                    return True
                else:
                    self.log_test(
                        "AI Bot Chat Health Check",
                        False,
                        f"Unhealthy status: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "AI Bot Chat Health Check",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("AI Bot Chat Health Check", False, error=str(e))
            return False
    
    def test_start_session(self, ai_model="gpt-5", initial_prompt=None):
        """Test starting a new chat session"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "ai_model": ai_model,
                "initial_prompt": initial_prompt
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai-bot-chat/start-session",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("session_id"):
                    session_id = data["session_id"]
                    self.session_ids[ai_model] = session_id
                    
                    self.log_test(
                        f"Start Chat Session ({ai_model})",
                        True,
                        f"Session ID: {session_id}, Stage: {data.get('stage')}, Message length: {len(data.get('message', ''))}"
                    )
                    return session_id
                else:
                    self.log_test(
                        f"Start Chat Session ({ai_model})",
                        False,
                        f"Invalid response: {data}"
                    )
                    return None
            else:
                self.log_test(
                    f"Start Chat Session ({ai_model})",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(f"Start Chat Session ({ai_model})", False, error=str(e))
            return None
    
    def test_send_message(self, session_id, ai_model, message_content, stage="clarification"):
        """Test sending a message in chat session"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id,
                "message_content": message_content,
                "ai_model": ai_model,
                "bot_creation_stage": stage
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai-bot-chat/send-message",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        f"Send Message ({ai_model})",
                        True,
                        f"Response length: {len(data.get('message', ''))}, Ready to create: {data.get('ready_to_create', False)}"
                    )
                    return data
                else:
                    self.log_test(
                        f"Send Message ({ai_model})",
                        False,
                        f"Invalid response: {data}"
                    )
                    return None
            else:
                self.log_test(
                    f"Send Message ({ai_model})",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(f"Send Message ({ai_model})", False, error=str(e))
            return None
    
    def test_chat_history(self, session_id, ai_model):
        """Test retrieving chat history"""
        try:
            response = requests.get(
                f"{self.base_url}/api/ai-bot-chat/history/{session_id}",
                params={"user_id": self.test_user_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    messages = data.get("messages", [])
                    self.log_test(
                        f"Get Chat History ({ai_model})",
                        True,
                        f"Retrieved {len(messages)} messages for session {session_id}"
                    )
                    return messages
                else:
                    self.log_test(
                        f"Get Chat History ({ai_model})",
                        False,
                        f"Invalid response: {data}"
                    )
                    return None
            else:
                self.log_test(
                    f"Get Chat History ({ai_model})",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(f"Get Chat History ({ai_model})", False, error=str(e))
            return None
    
    def test_create_bot(self, session_id, ai_model, bot_config):
        """Test creating AI bot from chat configuration"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "session_id": session_id,
                "ai_model": ai_model,
                "bot_config": bot_config
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai-bot-chat/create-bot",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("bot_id"):
                    self.log_test(
                        f"Create AI Bot ({ai_model})",
                        True,
                        f"Bot ID: {data['bot_id']}, Message: {data.get('message', '')}"
                    )
                    return data["bot_id"]
                else:
                    self.log_test(
                        f"Create AI Bot ({ai_model})",
                        False,
                        f"Invalid response: {data}"
                    )
                    return None
            else:
                self.log_test(
                    f"Create AI Bot ({ai_model})",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(f"Create AI Bot ({ai_model})", False, error=str(e))
            return None
    
    def test_get_user_bots(self):
        """Test retrieving user's AI bots"""
        try:
            response = requests.get(
                f"{self.base_url}/api/ai-bots/user/{self.test_user_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    bots = data.get("bots", [])
                    total = data.get("total", 0)
                    self.log_test(
                        "Get User AI Bots",
                        True,
                        f"Retrieved {total} AI bots for user {self.test_user_id}"
                    )
                    return bots
                else:
                    self.log_test(
                        "Get User AI Bots",
                        False,
                        f"Invalid response: {data}"
                    )
                    return None
            else:
                self.log_test(
                    "Get User AI Bots",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Get User AI Bots", False, error=str(e))
            return None
    
    def run_conversation_flow(self, ai_model):
        """Run complete conversation flow from initial prompt to bot creation"""
        print(f"\n🤖 Testing complete conversation flow with {ai_model.upper()}")
        print("=" * 60)
        
        # Step 1: Start session with initial prompt
        initial_prompt = "I want to create a momentum trading bot for Bitcoin that uses RSI and MACD indicators"
        session_id = self.test_start_session(ai_model, initial_prompt)
        
        if not session_id:
            print(f"❌ Failed to start session for {ai_model}")
            return False
        
        # Step 2: Continue conversation with more details
        messages = [
            "I prefer medium risk trading with 2% stop loss",
            "I want to trade on Binance exchange with BTC/USDT pair",
            "Position size should be 0.1 BTC and maximum 2 positions",
            "Take profit at 4% and use 1h and 4h timeframes"
        ]
        
        bot_config = None
        for i, message in enumerate(messages):
            print(f"Sending message {i+1}: {message[:50]}...")
            response = self.test_send_message(session_id, ai_model, message)
            
            if response and response.get("ready_to_create"):
                bot_config = response.get("bot_config")
                print(f"✅ Bot configuration ready after {i+1} messages")
                break
            
            time.sleep(1)  # Small delay between messages
        
        # Step 3: Get chat history
        history = self.test_chat_history(session_id, ai_model)
        
        # Step 4: Create bot if configuration is ready
        if bot_config:
            bot_id = self.test_create_bot(session_id, ai_model, bot_config)
            if bot_id:
                print(f"✅ Successfully created bot with ID: {bot_id}")
                return True
        else:
            # Try to create bot with manual configuration
            manual_config = {
                "ready_to_create": True,
                "bot_config": {
                    "name": f"Test {ai_model.upper()} Momentum Bot",
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
                    "timeframes": ["1h", "4h"],
                    "entry_conditions": ["RSI < 30", "MACD bullish crossover"],
                    "exit_conditions": ["RSI > 70", "Take profit reached"]
                },
                "risk_management": {
                    "stop_loss": 2.0,
                    "take_profit": 4.0,
                    "max_positions": 2,
                    "position_size": 0.1
                }
            }
            
            bot_id = self.test_create_bot(session_id, ai_model, manual_config)
            if bot_id:
                print(f"✅ Successfully created bot with manual config: {bot_id}")
                return True
        
        print(f"❌ Failed to complete conversation flow for {ai_model}")
        return False
    
    def run_all_tests(self):
        """Run all AI Bot Chat tests"""
        print("🚀 Starting AI Bot Chat System Testing")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"AI Models: {AI_MODELS}")
        print()
        
        # Test 1: Health Check
        health_ok = self.test_health_check()
        
        if not health_ok:
            print("❌ Health check failed - stopping tests")
            return self.generate_summary()
        
        # Test 2: Get existing user bots (baseline)
        initial_bots = self.test_get_user_bots()
        initial_count = len(initial_bots) if initial_bots else 0
        print(f"📊 Initial bot count: {initial_count}")
        
        # Test 3: Run conversation flows for both AI models
        successful_flows = 0
        for ai_model in AI_MODELS:
            if self.run_conversation_flow(ai_model):
                successful_flows += 1
        
        # Test 4: Verify bot creation by checking final count
        final_bots = self.test_get_user_bots()
        final_count = len(final_bots) if final_bots else 0
        
        if final_count > initial_count:
            self.log_test(
                "Bot Creation Verification",
                True,
                f"Bot count increased from {initial_count} to {final_count}"
            )
        else:
            self.log_test(
                "Bot Creation Verification",
                False,
                f"Bot count did not increase (was {initial_count}, now {final_count})"
            )
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 AI BOT CHAT SYSTEM TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error'] or result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}")
        
        print("\n" + "=" * 60)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = AIBotChatTester()
    summary = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/ai_bot_chat_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: /app/ai_bot_chat_test_results.json")
    
    return summary["success_rate"] > 70  # Consider 70%+ success rate as passing

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)