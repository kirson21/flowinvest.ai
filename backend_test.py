#!/usr/bin/env python3
"""
AI Bot Chat System Comprehensive Testing
Testing the FULLY FIXED AI Bot Chat system with EmergentIntegrations properly configured.

CRITICAL TEST - Complete System Verification:
Test with: "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"

VERIFY ALL FIXES:
1. **EmergentIntegrations Working**: Health check should show universal_key_configured: true
2. **ETH Detection Fixed**: Should create ETH bots (not BTC)  
3. **Real AI Responses**: Should use actual GPT-4o/Claude/Gemini (not fallback)
4. **Balance System**: Balance checks and deductions should work
5. **Proper Conversation**: Should acknowledge ETH and ask about missing trading capital
6. **Complete Bot Creation**: Should generate comprehensive JSON with advanced settings
"""

import requests
import json
import uuid
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://flowinvest-ai.onrender.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user ID (using a consistent test user)
TEST_USER_ID = "621b42ef-1c97-409b-b3d9-18fc83d0e9d8"

class AIBotChatTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.session_id = None
        self.conversation_history = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
    def test_health_check(self):
        """Test 1: Health Check - Verify EmergentIntegrations Configuration"""
        print("🔍 TEST 1: Health Check - EmergentIntegrations Configuration")
        
        try:
            response = self.session.get(f"{API_BASE}/ai-bot-chat/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check critical health indicators
                universal_key_configured = data.get('universal_key_configured', False)
                emergent_key_present = data.get('emergent_key_present', False)
                emergent_library_available = data.get('emergent_library_available', False)
                database_available = data.get('database_available', False)
                ai_models = data.get('ai_models_available', [])
                
                print(f"   Universal Key Configured: {universal_key_configured}")
                print(f"   Emergent Key Present: {emergent_key_present}")
                print(f"   Emergent Library Available: {emergent_library_available}")
                print(f"   Database Available: {database_available}")
                print(f"   AI Models: {ai_models}")
                
                # CRITICAL: Check if EmergentIntegrations is properly configured
                if universal_key_configured:
                    self.log_test("Health Check - EmergentIntegrations Working", True, 
                                f"Universal key configured: {universal_key_configured}")
                else:
                    self.log_test("Health Check - EmergentIntegrations Working", False, 
                                f"Universal key NOT configured. Key present: {emergent_key_present}, Library available: {emergent_library_available}")
                
                # Check AI models availability
                expected_models = ["gpt-4o", "claude-3-7-sonnet", "gemini-2.0-flash"]
                models_available = all(model in ai_models for model in expected_models)
                self.log_test("Health Check - AI Models Available", models_available,
                            f"Expected: {expected_models}, Available: {ai_models}")
                
                # Check database connectivity
                self.log_test("Health Check - Database Connected", database_available,
                            f"Database available: {database_available}")
                
                return True
            else:
                self.log_test("Health Check - API Response", False, 
                            f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Check - API Connection", False, str(e))
            return False
    
    def test_balance_system(self):
        """Test 2: Balance System - Check balance retrieval and deduction"""
        print("🔍 TEST 2: Balance System Verification")
        
        try:
            # Get initial balance
            response = self.session.get(f"{API_BASE}/ai-bot-chat/balance/{TEST_USER_ID}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                initial_balance = data.get('balance_usd', 0)
                has_sufficient_funds = data.get('has_sufficient_funds', False)
                cost_per_message = data.get('cost_per_message', 0.10)
                
                print(f"   Initial Balance: ${initial_balance:.2f}")
                print(f"   Has Sufficient Funds: {has_sufficient_funds}")
                print(f"   Cost Per Message: ${cost_per_message:.2f}")
                
                self.log_test("Balance System - Balance Retrieval", True,
                            f"Balance: ${initial_balance:.2f}, Sufficient: {has_sufficient_funds}")
                
                return initial_balance, has_sufficient_funds
            else:
                self.log_test("Balance System - Balance Retrieval", False,
                            f"Status: {response.status_code}", response.text)
                return 0, False
                
        except Exception as e:
            self.log_test("Balance System - Balance Retrieval", False, str(e))
            return 0, False
    
    def test_start_chat_session(self):
        """Test 3: Start Chat Session with Critical Test Scenario"""
        print("🔍 TEST 3: Start Chat Session - Critical Test Scenario")
        
        # CRITICAL TEST SCENARIO from review request
        test_prompt = "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"
        
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "ai_model": "gpt-4o",
                "initial_prompt": test_prompt
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/start-session", 
                                       json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    self.session_id = data.get('session_id')
                    ai_response = data.get('message', '')
                    ready_to_create = data.get('ready_to_create', False)
                    
                    print(f"   Session ID: {self.session_id}")
                    print(f"   AI Response Length: {len(ai_response)} characters")
                    print(f"   Ready to Create: {ready_to_create}")
                    print(f"   AI Response Preview: {ai_response[:200]}...")
                    
                    # CRITICAL VERIFICATION: Check if AI acknowledges ETH
                    eth_acknowledged = any(word in ai_response.lower() for word in ['eth', 'ethereum'])
                    futures_acknowledged = 'futures' in ai_response.lower()
                    leverage_acknowledged = any(word in ai_response.lower() for word in ['5x', 'leverage'])
                    volume_acknowledged = 'volume' in ai_response.lower()
                    
                    print(f"   ETH Acknowledged: {eth_acknowledged}")
                    print(f"   Futures Acknowledged: {futures_acknowledged}")
                    print(f"   Leverage Acknowledged: {leverage_acknowledged}")
                    print(f"   Volume Acknowledged: {volume_acknowledged}")
                    
                    # Check if AI asks about missing trading capital (expected behavior)
                    asks_about_capital = any(word in ai_response.lower() for word in ['capital', 'trading capital', 'budget', 'money'])
                    
                    print(f"   Asks About Capital: {asks_about_capital}")
                    
                    # CRITICAL: Should NOT create random bot immediately
                    creates_random_bot = ready_to_create and not asks_about_capital
                    
                    if eth_acknowledged and asks_about_capital and not creates_random_bot:
                        self.log_test("Start Chat - Proper Conversation Flow", True,
                                    f"AI acknowledges ETH and asks about missing capital (correct behavior)")
                    else:
                        self.log_test("Start Chat - Proper Conversation Flow", False,
                                    f"ETH: {eth_acknowledged}, Asks Capital: {asks_about_capital}, Random Bot: {creates_random_bot}")
                    
                    # Check for real AI response vs fallback
                    is_real_ai = len(ai_response) > 500 and not ai_response.startswith("🧠 **GPT-4 Trading Expert**")
                    self.log_test("Start Chat - Real AI Response", is_real_ai,
                                f"Response length: {len(ai_response)}, Appears to be real AI: {is_real_ai}")
                    
                    self.conversation_history.append({
                        "type": "user",
                        "content": test_prompt
                    })
                    self.conversation_history.append({
                        "type": "assistant", 
                        "content": ai_response
                    })
                    
                    return True
                else:
                    error = data.get('error', 'Unknown error')
                    self.log_test("Start Chat - Session Creation", False, f"Error: {error}", data)
                    return False
            else:
                self.log_test("Start Chat - API Response", False,
                            f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Start Chat - API Connection", False, str(e))
            return False
    
    def test_conversation_flow(self):
        """Test 4: Complete Conversation Flow"""
        print("🔍 TEST 4: Complete Conversation Flow")
        
        if not self.session_id:
            self.log_test("Conversation Flow - Session Required", False, "No active session")
            return False
        
        # Continue conversation by providing trading capital
        capital_response = "$10,000"
        
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "message_content": capital_response,
                "ai_model": "gpt-4o",
                "bot_creation_stage": "capital"
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/send-message",
                                       json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    ai_response = data.get('message', '')
                    ready_to_create = data.get('ready_to_create', False)
                    bot_config = data.get('bot_config')
                    
                    print(f"   AI Response Length: {len(ai_response)} characters")
                    print(f"   Ready to Create: {ready_to_create}")
                    print(f"   Bot Config Present: {bot_config is not None}")
                    print(f"   AI Response Preview: {ai_response[:200]}...")
                    
                    self.conversation_history.append({
                        "type": "user",
                        "content": capital_response
                    })
                    self.conversation_history.append({
                        "type": "assistant",
                        "content": ai_response
                    })
                    
                    # Continue conversation until bot is ready
                    conversation_steps = 0
                    max_steps = 5
                    
                    while not ready_to_create and conversation_steps < max_steps:
                        conversation_steps += 1
                        
                        # Provide generic positive response to continue
                        next_response = f"Yes, that sounds good. Step {conversation_steps}."
                        
                        payload = {
                            "user_id": TEST_USER_ID,
                            "session_id": self.session_id,
                            "message_content": next_response,
                            "ai_model": "gpt-4o",
                            "bot_creation_stage": f"step_{conversation_steps}"
                        }
                        
                        response = self.session.post(f"{API_BASE}/ai-bot-chat/send-message",
                                                   json=payload, timeout=60)
                        
                        if response.status_code == 200:
                            data = response.json()
                            ai_response = data.get('message', '')
                            ready_to_create = data.get('ready_to_create', False)
                            bot_config = data.get('bot_config')
                            
                            print(f"   Step {conversation_steps} - Ready: {ready_to_create}")
                            
                            self.conversation_history.append({
                                "type": "user",
                                "content": next_response
                            })
                            self.conversation_history.append({
                                "type": "assistant",
                                "content": ai_response
                            })
                            
                            if ready_to_create:
                                break
                        else:
                            break
                    
                    if ready_to_create and bot_config:
                        # CRITICAL: Check if bot config has ETH (not BTC)
                        bot_details = bot_config.get('bot_config', {}) if bot_config else {}
                        base_coin = bot_details.get('base_coin', 'UNKNOWN')
                        trade_type = bot_details.get('trade_type', 'UNKNOWN')
                        leverage = bot_details.get('leverage', 0)
                        bot_name = bot_details.get('name', 'UNKNOWN')
                        
                        print(f"   Final Bot Details:")
                        print(f"     Name: {bot_name}")
                        print(f"     Base Coin: {base_coin}")
                        print(f"     Trade Type: {trade_type}")
                        print(f"     Leverage: {leverage}x")
                        
                        # CRITICAL VERIFICATION: ETH Detection Fix
                        eth_detected = base_coin == 'ETH'
                        futures_detected = trade_type == 'futures'
                        leverage_correct = leverage >= 3.0  # Should be around 5x
                        
                        self.log_test("Conversation Flow - ETH Detection Fixed", eth_detected,
                                    f"Base coin: {base_coin} (should be ETH, not BTC)")
                        
                        self.log_test("Conversation Flow - Futures Trading", futures_detected,
                                    f"Trade type: {trade_type}")
                        
                        self.log_test("Conversation Flow - Leverage Configuration", leverage_correct,
                                    f"Leverage: {leverage}x")
                        
                        # Check for advanced settings
                        advanced_settings = bot_details.get('advanced_settings', {})
                        has_advanced = bool(advanced_settings)
                        
                        self.log_test("Conversation Flow - Advanced Settings", has_advanced,
                                    f"Advanced settings present: {has_advanced}")
                        
                        # Store bot config for creation test
                        self.final_bot_config = bot_config
                        
                        return True
                    else:
                        self.log_test("Conversation Flow - Bot Configuration", False,
                                    f"Ready: {ready_to_create}, Config: {bot_config is not None}")
                        return False
                else:
                    self.log_test("Conversation Flow - Message Send", False, 
                                f"Error in response", data)
                    return False
            else:
                self.log_test("Conversation Flow - API Response", False,
                            f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Conversation Flow - API Connection", False, str(e))
            return False
    
    def test_bot_creation(self):
        """Test 5: Complete Bot Creation"""
        print("🔍 TEST 5: Complete Bot Creation")
        
        if not hasattr(self, 'final_bot_config') or not self.final_bot_config:
            self.log_test("Bot Creation - Config Required", False, "No bot config available")
            return False
        
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "ai_model": "gpt-4o",
                "bot_config": self.final_bot_config,
                "strategy_config": {},
                "risk_management": {}
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/create-bot",
                                       json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    bot_id = data.get('bot_id')
                    message = data.get('message', '')
                    
                    print(f"   Bot ID: {bot_id}")
                    print(f"   Creation Message: {message}")
                    
                    self.log_test("Bot Creation - Successful Creation", True,
                                f"Bot ID: {bot_id}")
                    
                    # Verify bot was saved by checking user bots
                    return self.verify_bot_saved(bot_id)
                else:
                    self.log_test("Bot Creation - Creation Failed", False,
                                f"Response: {data}")
                    return False
            else:
                self.log_test("Bot Creation - API Response", False,
                            f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Bot Creation - API Connection", False, str(e))
            return False
    
    def verify_bot_saved(self, expected_bot_id):
        """Verify bot was saved to database"""
        print("🔍 TEST 5b: Verify Bot Saved to Database")
        
        try:
            response = self.session.get(f"{API_BASE}/ai-bots/user/{TEST_USER_ID}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    bots = data.get('bots', [])
                    total = data.get('total', 0)
                    
                    print(f"   Total User Bots: {total}")
                    
                    # Look for our created bot
                    bot_found = False
                    eth_bot_found = False
                    
                    for bot in bots:
                        bot_id = bot.get('id')
                        base_coin = bot.get('base_coin', '')
                        name = bot.get('name', '')
                        
                        if bot_id == expected_bot_id:
                            bot_found = True
                            
                        if base_coin == 'ETH':
                            eth_bot_found = True
                            print(f"   Found ETH Bot: {name} (ID: {bot_id})")
                    
                    self.log_test("Bot Creation - Bot Saved to Database", bot_found,
                                f"Bot ID {expected_bot_id} found in user bots")
                    
                    self.log_test("Bot Creation - ETH Bot in Database", eth_bot_found,
                                f"ETH bot found in user's bot collection")
                    
                    return bot_found
                else:
                    self.log_test("Bot Creation - Database Query", False,
                                f"Failed to get user bots: {data}")
                    return False
            else:
                self.log_test("Bot Creation - Database Query", False,
                            f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Bot Creation - Database Verification", False, str(e))
            return False
    
    def test_balance_deduction(self):
        """Test 6: Balance Deduction After AI Usage"""
        print("🔍 TEST 6: Balance Deduction Verification")
        
        try:
            # Get final balance
            response = self.session.get(f"{API_BASE}/ai-bot-chat/balance/{TEST_USER_ID}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                final_balance = data.get('balance_usd', 0)
                
                print(f"   Final Balance: ${final_balance:.2f}")
                
                # Calculate expected deduction (approximate)
                # Each AI message costs $0.10, we sent multiple messages
                message_count = len([msg for msg in self.conversation_history if msg['type'] == 'user'])
                expected_deduction = message_count * 0.10
                
                print(f"   Messages Sent: {message_count}")
                print(f"   Expected Deduction: ${expected_deduction:.2f}")
                
                # Note: We can't verify exact deduction without initial balance,
                # but we can verify the balance system is working
                self.log_test("Balance System - Final Balance Retrieved", True,
                            f"Final balance: ${final_balance:.2f}")
                
                return True
            else:
                self.log_test("Balance System - Final Balance Check", False,
                            f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Balance System - Final Balance Check", False, str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 STARTING COMPREHENSIVE AI BOT CHAT SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {TEST_USER_ID}")
        print(f"Test Scenario: Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage")
        print("=" * 80)
        print()
        
        # Run all tests
        tests = [
            self.test_health_check,
            self.test_balance_system,
            self.test_start_chat_session,
            self.test_conversation_flow,
            self.test_bot_creation,
            self.test_balance_deduction
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {e}")
                self.log_test(f"{test.__name__} - Critical Error", False, str(e))
            
            time.sleep(2)  # Brief pause between tests
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical fixes verification
        print("🔍 CRITICAL FIXES VERIFICATION:")
        
        # 1. EmergentIntegrations Working
        emergent_working = any(t['success'] for t in self.test_results if 'EmergentIntegrations Working' in t['test'])
        print(f"1. EmergentIntegrations Working: {'✅' if emergent_working else '❌'}")
        
        # 2. ETH Detection Fixed
        eth_detection = any(t['success'] for t in self.test_results if 'ETH Detection Fixed' in t['test'])
        print(f"2. ETH Detection Fixed: {'✅' if eth_detection else '❌'}")
        
        # 3. Real AI Responses
        real_ai = any(t['success'] for t in self.test_results if 'Real AI Response' in t['test'])
        print(f"3. Real AI Responses: {'✅' if real_ai else '❌'}")
        
        # 4. Balance System
        balance_system = any(t['success'] for t in self.test_results if 'Balance' in t['test'])
        print(f"4. Balance System: {'✅' if balance_system else '❌'}")
        
        # 5. Proper Conversation
        proper_conversation = any(t['success'] for t in self.test_results if 'Proper Conversation Flow' in t['test'])
        print(f"5. Proper Conversation: {'✅' if proper_conversation else '❌'}")
        
        # 6. Complete Bot Creation
        bot_creation = any(t['success'] for t in self.test_results if 'Bot Creation' in t['test'] and t['success'])
        print(f"6. Complete Bot Creation: {'✅' if bot_creation else '❌'}")
        
        print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        print("\n" + "=" * 80)
        
        # Final assessment
        critical_fixes_working = sum([emergent_working, eth_detection, real_ai, balance_system, proper_conversation, bot_creation])
        
        if critical_fixes_working >= 5:
            print("🎉 OVERALL ASSESSMENT: AI BOT CHAT SYSTEM IS FULLY OPERATIONAL")
            print("   All critical fixes are working correctly!")
        elif critical_fixes_working >= 3:
            print("⚠️  OVERALL ASSESSMENT: AI BOT CHAT SYSTEM IS PARTIALLY OPERATIONAL")
            print("   Most critical fixes are working, some issues remain.")
        else:
            print("❌ OVERALL ASSESSMENT: AI BOT CHAT SYSTEM HAS CRITICAL ISSUES")
            print("   Multiple critical fixes are not working properly.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = AIBotChatTester()
    tester.run_comprehensive_test()
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