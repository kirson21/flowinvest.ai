#!/usr/bin/env python3
"""
AI Bot Chat System Testing - Focus on Fixed Conversation Flow
Testing the exact failing scenario from review request to verify proper conversation flow.
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://ai-flow-invest.preview.emergentagent.com/api"
TEST_USER_ID = "test-user-" + str(uuid.uuid4())[:8]

class AIBotChatTester:
    def __init__(self):
        self.session_id = None
        self.test_results = []
        self.conversation_history = []
        
    def log_test(self, test_name, success, details="", expected="", actual=""):
        """Log test results with detailed information."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and expected:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
    
    def test_health_check(self):
        """Test AI Bot Chat health endpoint."""
        try:
            response = requests.get(f"{BACKEND_URL}/ai-bot-chat/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check",
                    True,
                    f"Status: {data.get('status')}, Models: {data.get('ai_models_available')}, DB: {data.get('database_available')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_critical_scenario_conversation_flow(self):
        """
        Test the EXACT failing scenario from review request:
        'Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling'
        
        Expected behavior:
        1. AI should acknowledge provided info
        2. AI should ask about MISSING parameters (not create random bot)
        3. Continue conversation flow
        4. Only create bot after collecting all info with ready_to_create: true
        """
        print("\n" + "="*80)
        print("🚨 CRITICAL TEST: Testing Exact Failing Scenario")
        print("="*80)
        
        # The exact failing request from review
        critical_request = "Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling"
        
        # Step 1: Start session with critical request
        try:
            session_data = {
                "user_id": TEST_USER_ID,
                "ai_model": "gpt-4o",
                "initial_prompt": critical_request
            }
            
            response = requests.post(f"{BACKEND_URL}/ai-bot-chat/start-session", 
                                   json=session_data, timeout=15)
            
            if response.status_code != 200:
                self.log_test("Critical Scenario - Session Start", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            self.session_id = data.get('session_id')
            ai_response = data.get('message', '')
            ready_to_create = data.get('ready_to_create', False)
            
            print(f"\n📝 USER REQUEST: {critical_request}")
            print(f"\n🤖 AI RESPONSE: {ai_response[:500]}...")
            print(f"\n🔍 READY TO CREATE: {ready_to_create}")
            
            # CRITICAL CHECK 1: AI should NOT create random bot immediately
            if ready_to_create:
                self.log_test(
                    "Critical Check 1 - No Immediate Bot Creation",
                    False,
                    "AI created bot immediately instead of asking questions",
                    "ready_to_create: false (should ask questions first)",
                    f"ready_to_create: {ready_to_create}"
                )
                return False
            else:
                self.log_test(
                    "Critical Check 1 - No Immediate Bot Creation", 
                    True,
                    "AI correctly did not create bot immediately"
                )
            
            # CRITICAL CHECK 2: AI should acknowledge provided information
            provided_info = ["eth", "futures", "5x leverage", "volume indicators", "long and short"]
            acknowledgment_found = False
            
            for info in provided_info:
                if any(keyword in ai_response.lower() for keyword in info.split()):
                    acknowledgment_found = True
                    break
            
            if acknowledgment_found:
                self.log_test(
                    "Critical Check 2 - Acknowledges Provided Info",
                    True,
                    "AI acknowledged user-provided parameters"
                )
            else:
                self.log_test(
                    "Critical Check 2 - Acknowledges Provided Info",
                    False,
                    "AI did not acknowledge user-provided information",
                    "Should mention ETH, futures, 5x leverage, or volume indicators",
                    f"Response: {ai_response[:200]}..."
                )
            
            # CRITICAL CHECK 3: AI should ask about missing parameters
            missing_params_questions = [
                "capital", "trading capital", "budget", "money", "fund",
                "risk", "stop loss", "take profit", "drawdown",
                "name", "bot name", "call it"
            ]
            
            asks_missing_params = any(param in ai_response.lower() for param in missing_params_questions)
            
            if asks_missing_params:
                self.log_test(
                    "Critical Check 3 - Asks About Missing Parameters",
                    True,
                    "AI correctly asked about missing parameters"
                )
            else:
                self.log_test(
                    "Critical Check 3 - Asks About Missing Parameters",
                    False,
                    "AI did not ask about missing parameters",
                    "Should ask about trading capital, risk management, or bot name",
                    f"Response: {ai_response[:200]}..."
                )
            
            # Continue conversation to test flow
            return self.test_conversation_continuation()
            
        except Exception as e:
            self.log_test("Critical Scenario - Session Start", False, f"Exception: {str(e)}")
            return False
    
    def test_conversation_continuation(self):
        """Test that conversation continues properly without creating random bots."""
        if not self.session_id:
            return False
        
        # Step 2: Provide trading capital (common missing parameter)
        capital_response = "$10,000 trading capital"
        
        try:
            message_data = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "message_content": capital_response,
                "ai_model": "gpt-4o"
            }
            
            response = requests.post(f"{BACKEND_URL}/ai-bot-chat/send-message",
                                   json=message_data, timeout=15)
            
            if response.status_code != 200:
                self.log_test("Conversation Continuation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            ai_response = data.get('message', '')
            ready_to_create = data.get('ready_to_create', False)
            
            print(f"\n📝 USER: {capital_response}")
            print(f"🤖 AI: {ai_response[:300]}...")
            print(f"🔍 READY TO CREATE: {ready_to_create}")
            
            # Check if AI continues conversation appropriately
            continues_conversation = not ready_to_create and len(ai_response) > 50
            
            if continues_conversation:
                self.log_test(
                    "Conversation Continuation",
                    True,
                    "AI continued conversation appropriately"
                )
            else:
                self.log_test(
                    "Conversation Continuation",
                    False,
                    "AI did not continue conversation properly",
                    "Should ask more questions before creating bot",
                    f"ready_to_create: {ready_to_create}, response_length: {len(ai_response)}"
                )
            
            # Step 3: Continue until bot is ready
            return self.test_complete_conversation_flow()
            
        except Exception as e:
            self.log_test("Conversation Continuation", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_conversation_flow(self):
        """Test complete conversation flow until bot creation."""
        if not self.session_id:
            return False
        
        # Provide additional information to complete the bot
        additional_responses = [
            "2% risk per trade, 3% stop loss",
            "Call it ETH Futures Volume Pro"
        ]
        
        for i, response_text in enumerate(additional_responses):
            try:
                message_data = {
                    "user_id": TEST_USER_ID,
                    "session_id": self.session_id,
                    "message_content": response_text,
                    "ai_model": "gpt-4o"
                }
                
                response = requests.post(f"{BACKEND_URL}/ai-bot-chat/send-message",
                                       json=message_data, timeout=15)
                
                if response.status_code != 200:
                    self.log_test(f"Complete Flow Step {i+1}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    continue
                
                data = response.json()
                ai_response = data.get('message', '')
                ready_to_create = data.get('ready_to_create', False)
                bot_config = data.get('bot_config')
                
                print(f"\n📝 USER: {response_text}")
                print(f"🤖 AI: {ai_response[:200]}...")
                print(f"🔍 READY TO CREATE: {ready_to_create}")
                
                if ready_to_create:
                    # CRITICAL CHECK 4: Bot should be created with proper config
                    if bot_config:
                        self.log_test(
                            "Critical Check 4 - Proper Bot Creation",
                            True,
                            f"Bot created with config: {json.dumps(bot_config, indent=2)[:300]}..."
                        )
                        
                        # Test bot creation endpoint
                        return self.test_bot_creation(bot_config)
                    else:
                        self.log_test(
                            "Critical Check 4 - Proper Bot Creation",
                            False,
                            "ready_to_create is true but no bot_config provided"
                        )
                        return False
                
            except Exception as e:
                self.log_test(f"Complete Flow Step {i+1}", False, f"Exception: {str(e)}")
        
        # If we get here, bot wasn't created after full conversation
        self.log_test(
            "Complete Conversation Flow",
            False,
            "Bot was not created after providing all information"
        )
        return False
    
    def test_bot_creation(self, bot_config):
        """Test actual bot creation with the generated config."""
        if not self.session_id or not bot_config:
            return False
        
        try:
            creation_data = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": {},
                "risk_management": {}
            }
            
            response = requests.post(f"{BACKEND_URL}/ai-bot-chat/create-bot",
                                   json=creation_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bot_id = data.get('bot_id')
                    self.log_test(
                        "Bot Creation",
                        True,
                        f"Bot created successfully with ID: {bot_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Bot Creation",
                        False,
                        f"Bot creation failed: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Bot Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Bot Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_user_bots_retrieval(self):
        """Test retrieving user's AI bots."""
        try:
            response = requests.get(f"{BACKEND_URL}/ai-bots/user/{TEST_USER_ID}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                bots = data.get('bots', [])
                total = data.get('total', 0)
                
                self.log_test(
                    "User Bots Retrieval",
                    True,
                    f"Retrieved {total} bots for user"
                )
                return True
            else:
                self.log_test(
                    "User Bots Retrieval",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Bots Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate summary."""
        print("🚀 Starting AI Bot Chat System Testing")
        print("="*60)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_critical_scenario_conversation_flow,
            self.test_user_bots_retrieval
        ]
        
        for test in tests:
            test()
            time.sleep(1)  # Brief pause between tests
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("📊 AI BOT CHAT SYSTEM TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL SCENARIO ANALYSIS:")
        critical_checks = [r for r in self.test_results if 'Critical Check' in r['test']]
        critical_passed = len([r for r in critical_checks if r['success']])
        critical_total = len(critical_checks)
        
        if critical_total > 0:
            print(f"Critical Checks Passed: {critical_passed}/{critical_total}")
            
            if critical_passed == critical_total:
                print("✅ CRITICAL SCENARIO FIXED: All critical checks passed!")
                print("   - No immediate random bot creation")
                print("   - AI acknowledges provided information")
                print("   - AI asks about missing parameters")
                print("   - Proper conversation flow maintained")
            else:
                print("❌ CRITICAL SCENARIO STILL BROKEN:")
                for check in critical_checks:
                    if not check['success']:
                        print(f"   ❌ {check['test']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = AIBotChatTester()
    tester.run_all_tests()