#!/usr/bin/env python3
"""
AI Bot Chat System Critical Fixes Testing
Testing the FIXED AI Bot Chat system after resolving critical errors.

CRITICAL FIXES TO TEST:
1. ETH Detection Fix: Verify coin detection properly recognizes "ETH" and creates ETH bots instead of BTC
2. Supabase SQL Error Fix: Test balance deduction works without "invalid input syntax for type numeric" error
3. EmergentIntegrations Error: Verify the module import works without "No module named 'emergentintegrations'" error
4. Bot Creation: Test full conversation flow creates correct ETH futures bot

SPECIFIC TEST SCENARIO:
- Start chat with: "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"
- Provide trading capital when asked: "$10,000"
- Complete conversation flow
- Verify final bot has ETH not BTC
- Verify balance deduction works
- Verify bot creation completes successfully
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://flowinvest-ai.onrender.com/api"
TEST_USER_ID = "621b42ef-1c97-409b-b3d9-18fc83d0e9d8"  # Test user from previous tests

class AIBotChatTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_user_id = TEST_USER_ID
        self.session_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_health_check(self):
        """Test AI Bot Chat health check"""
        try:
            response = requests.get(f"{self.backend_url}/ai-bot-chat/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for emergentintegrations availability
                emergent_configured = data.get('universal_key_configured', False)
                models_available = data.get('ai_models_available', [])
                database_available = data.get('database_available', False)
                
                details = f"Status: {data.get('status')}, Models: {models_available}, DB: {database_available}, Emergent Key: {emergent_configured}"
                
                # This tests CRITICAL FIX 3: EmergentIntegrations Error
                if emergent_configured and len(models_available) >= 3 and database_available:
                    self.log_test("AI Bot Chat Health Check", True, details)
                    return True
                else:
                    self.log_test("AI Bot Chat Health Check", False, details, "Missing required components")
                    return False
            else:
                self.log_test("AI Bot Chat Health Check", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI Bot Chat Health Check", False, error=str(e))
            return False

    def test_user_balance_check(self):
        """Test user balance retrieval - CRITICAL FIX 2: Supabase SQL Error Fix"""
        try:
            response = requests.get(f"{self.backend_url}/ai-bot-chat/balance/{self.test_user_id}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    balance = data.get('balance_usd', 0)
                    has_funds = data.get('has_sufficient_funds', False)
                    cost = data.get('cost_per_message', 0)
                    
                    details = f"Balance: ${balance:.2f}, Sufficient: {has_funds}, Cost per message: ${cost:.2f}"
                    self.log_test("User Balance Check (SQL Fix)", True, details)
                    return True, balance
                else:
                    self.log_test("User Balance Check (SQL Fix)", False, error="API returned success=false")
                    return False, 0
            else:
                self.log_test("User Balance Check (SQL Fix)", False, error=f"HTTP {response.status_code}: {response.text}")
                return False, 0
                
        except Exception as e:
            self.log_test("User Balance Check (SQL Fix)", False, error=str(e))
            return False, 0

    def test_start_chat_session(self, initial_prompt):
        """Test starting chat session with ETH-specific prompt"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "ai_model": "gpt-4o",
                "initial_prompt": initial_prompt
            }
            
            response = requests.post(f"{self.backend_url}/ai-bot-chat/start-session", 
                                   json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    self.session_id = data.get('session_id')
                    ai_response = data.get('message', '')
                    
                    # Check if AI acknowledges ETH in the response
                    eth_mentioned = any(word in ai_response.lower() for word in ['eth', 'ethereum'])
                    futures_mentioned = any(word in ai_response.lower() for word in ['futures', 'leverage', '5x'])
                    
                    details = f"Session ID: {self.session_id}, ETH mentioned: {eth_mentioned}, Futures mentioned: {futures_mentioned}"
                    details += f"\nAI Response length: {len(ai_response)} chars"
                    details += f"\nFirst 200 chars: {ai_response[:200]}..."
                    
                    # This tests CRITICAL FIX 1: ETH Detection Fix
                    if self.session_id and len(ai_response) > 50:
                        self.log_test("Start Chat Session with ETH Prompt", True, details)
                        return True, ai_response
                    else:
                        self.log_test("Start Chat Session with ETH Prompt", False, details, "Missing session ID or short response")
                        return False, ""
                else:
                    error_msg = data.get('message', 'Unknown error')
                    self.log_test("Start Chat Session with ETH Prompt", False, error=error_msg)
                    return False, ""
            else:
                self.log_test("Start Chat Session with ETH Prompt", False, error=f"HTTP {response.status_code}: {response.text}")
                return False, ""
                
        except Exception as e:
            self.log_test("Start Chat Session with ETH Prompt", False, error=str(e))
            return False, ""

    def test_send_message(self, message, expected_keywords=None):
        """Test sending message in chat session"""
        try:
            if not self.session_id:
                self.log_test("Send Message", False, error="No active session")
                return False, "", False, None
                
            payload = {
                "user_id": self.test_user_id,
                "session_id": self.session_id,
                "message_content": message,
                "ai_model": "gpt-4o",
                "bot_creation_stage": "conversation"
            }
            
            response = requests.post(f"{self.backend_url}/ai-bot-chat/send-message", 
                                   json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    ai_response = data.get('message', '')
                    ready_to_create = data.get('ready_to_create', False)
                    bot_config = data.get('bot_config')
                    
                    details = f"Response length: {len(ai_response)} chars, Ready to create: {ready_to_create}"
                    
                    # Check for expected keywords if provided
                    if expected_keywords:
                        keywords_found = [kw for kw in expected_keywords if kw.lower() in ai_response.lower()]
                        details += f", Keywords found: {keywords_found}"
                    
                    if len(ai_response) > 20:
                        self.log_test(f"Send Message: '{message[:30]}...'", True, details)
                        return True, ai_response, ready_to_create, bot_config
                    else:
                        self.log_test(f"Send Message: '{message[:30]}...'", False, details, "Response too short")
                        return False, "", False, None
                else:
                    error_msg = data.get('message', 'Unknown error')
                    self.log_test(f"Send Message: '{message[:30]}...'", False, error=error_msg)
                    return False, "", False, None
            else:
                self.log_test(f"Send Message: '{message[:30]}...'", False, error=f"HTTP {response.status_code}: {response.text}")
                return False, "", False, None
                
        except Exception as e:
            self.log_test(f"Send Message: '{message[:30]}...'", False, error=str(e))
            return False, "", False, None

    def test_create_bot(self, bot_config):
        """Test creating bot from conversation"""
        try:
            if not self.session_id or not bot_config:
                self.log_test("Create AI Bot", False, error="No session or bot config")
                return False, None
                
            payload = {
                "user_id": self.test_user_id,
                "session_id": self.session_id,
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": {},
                "risk_management": {}
            }
            
            response = requests.post(f"{self.backend_url}/ai-bot-chat/create-bot", 
                                   json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    bot_id = data.get('bot_id')
                    message = data.get('message', '')
                    
                    details = f"Bot ID: {bot_id}, Message: {message}"
                    
                    if bot_id:
                        self.log_test("Create AI Bot", True, details)
                        return True, bot_id
                    else:
                        self.log_test("Create AI Bot", False, details, "No bot ID returned")
                        return False, None
                else:
                    error_msg = data.get('message', 'Unknown error')
                    self.log_test("Create AI Bot", False, error=error_msg)
                    return False, None
            else:
                self.log_test("Create AI Bot", False, error=f"HTTP {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_test("Create AI Bot", False, error=str(e))
            return False, None

    def test_verify_bot_details(self, bot_id):
        """Test verifying created bot has correct ETH details"""
        try:
            if not bot_id:
                self.log_test("Verify Bot Details", False, error="No bot ID provided")
                return False
                
            response = requests.get(f"{self.backend_url}/ai-bots/user/{self.test_user_id}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    bots = data.get('bots', [])
                    
                    # Find the created bot
                    created_bot = None
                    for bot in bots:
                        if str(bot.get('id')) == str(bot_id):
                            created_bot = bot
                            break
                    
                    if created_bot:
                        base_coin = created_bot.get('base_coin', '')
                        bot_name = created_bot.get('name', '')
                        description = created_bot.get('description', '')
                        
                        # CRITICAL FIX 1: Verify ETH detection worked correctly
                        is_eth_bot = base_coin.upper() == 'ETH' or 'eth' in bot_name.lower() or 'ethereum' in description.lower()
                        is_not_btc = base_coin.upper() != 'BTC' and 'btc' not in bot_name.lower() and 'bitcoin' not in description.lower()
                        
                        details = f"Base coin: {base_coin}, Name: {bot_name}, ETH bot: {is_eth_bot}, Not BTC: {is_not_btc}"
                        
                        if is_eth_bot and is_not_btc:
                            self.log_test("Verify Bot Details (ETH Detection)", True, details)
                            return True
                        else:
                            self.log_test("Verify Bot Details (ETH Detection)", False, details, "Bot is not ETH-based as expected")
                            return False
                    else:
                        self.log_test("Verify Bot Details (ETH Detection)", False, error=f"Bot with ID {bot_id} not found in user's bots")
                        return False
                else:
                    self.log_test("Verify Bot Details (ETH Detection)", False, error="Failed to get user bots")
                    return False
            else:
                self.log_test("Verify Bot Details (ETH Detection)", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Bot Details (ETH Detection)", False, error=str(e))
            return False

    def test_balance_deduction(self, initial_balance):
        """Test that balance was properly deducted - CRITICAL FIX 2"""
        try:
            success, final_balance = self.test_user_balance_check()
            
            if success:
                expected_deduction = 0.20  # $0.10 per message, 2 messages minimum
                actual_deduction = initial_balance - final_balance
                
                details = f"Initial: ${initial_balance:.2f}, Final: ${final_balance:.2f}, Deducted: ${actual_deduction:.2f}"
                
                # Allow some tolerance for multiple messages
                if actual_deduction >= expected_deduction and actual_deduction <= 1.0:
                    self.log_test("Balance Deduction (SQL Fix)", True, details)
                    return True
                else:
                    self.log_test("Balance Deduction (SQL Fix)", False, details, f"Unexpected deduction amount")
                    return False
            else:
                self.log_test("Balance Deduction (SQL Fix)", False, error="Could not check final balance")
                return False
                
        except Exception as e:
            self.log_test("Balance Deduction (SQL Fix)", False, error=str(e))
            return False

    def run_comprehensive_test(self):
        """Run the complete test scenario from the review request"""
        print("🚀 STARTING AI BOT CHAT CRITICAL FIXES TESTING")
        print("=" * 80)
        print()
        
        # Test 1: Health check (tests EmergentIntegrations fix)
        print("📋 TESTING CRITICAL FIX 3: EmergentIntegrations Error Fix")
        health_ok = self.test_health_check()
        
        # Test 2: Balance check (tests Supabase SQL fix)
        print("📋 TESTING CRITICAL FIX 2: Supabase SQL Error Fix")
        balance_ok, initial_balance = self.test_user_balance_check()
        
        if not balance_ok:
            print("❌ CRITICAL: Balance system not working, aborting test")
            return False
        
        if not health_ok:
            print("⚠️  WARNING: EmergentIntegrations not configured, but continuing with fallback system")
        
        # Test 3: Start chat with ETH-specific prompt (tests ETH detection)
        print("📋 TESTING CRITICAL FIX 1: ETH Detection Fix")
        initial_prompt = "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"
        print(f"Initial prompt: {initial_prompt}")
        
        session_ok, first_response = self.test_start_chat_session(initial_prompt)
        
        if not session_ok:
            print("❌ CRITICAL: Could not start chat session")
            return False
        
        # Test 4: Continue conversation with capital information
        print("📋 TESTING CONVERSATION FLOW")
        capital_message = "$10,000"
        print(f"Providing capital: {capital_message}")
        
        msg_ok, response, ready, bot_config = self.test_send_message(capital_message, ["capital", "10000", "10,000"])
        
        conversation_count = 1
        max_conversations = 5
        
        # Continue conversation until bot is ready or max attempts
        while not ready and conversation_count < max_conversations and msg_ok:
            print(f"📋 CONTINUING CONVERSATION (Attempt {conversation_count + 1})")
            
            # Provide generic positive response to continue
            continue_message = "Yes, that sounds good. Please continue."
            msg_ok, response, ready, bot_config = self.test_send_message(continue_message)
            conversation_count += 1
        
        if not ready or not bot_config:
            print("❌ CRITICAL: Bot configuration not generated after conversation")
            return False
        
        # Test 5: Create the bot
        print("📋 TESTING BOT CREATION")
        bot_created, bot_id = self.test_create_bot(bot_config)
        
        if not bot_created or not bot_id:
            print("❌ CRITICAL: Bot creation failed")
            return False
        
        # Test 6: Verify bot details (ETH detection)
        print("📋 TESTING ETH DETECTION IN CREATED BOT")
        eth_verified = self.test_verify_bot_details(bot_id)
        
        # Test 7: Verify balance deduction
        print("📋 TESTING BALANCE DEDUCTION")
        balance_deducted = self.test_balance_deduction(initial_balance)
        
        # Summary
        print("=" * 80)
        print("🏁 TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Critical fixes verification
        critical_fixes = {
            "ETH Detection Fix": eth_verified,
            "Supabase SQL Error Fix": balance_ok and balance_deducted,
            "EmergentIntegrations Error Fix": health_ok,
            "Bot Creation Flow": bot_created and bot_id is not None
        }
        
        print("CRITICAL FIXES STATUS:")
        for fix_name, status in critical_fixes.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {fix_name}: {'WORKING' if status else 'FAILED'}")
        
        print()
        
        # Detailed results
        print("DETAILED TEST RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"  {status_icon} {result['test']}")
            if result['details']:
                print(f"      {result['details']}")
            if result['error']:
                print(f"      ERROR: {result['error']}")
        
        all_critical_passed = all(critical_fixes.values())
        
        if all_critical_passed:
            print("\n🎉 ALL CRITICAL FIXES ARE WORKING CORRECTLY!")
            print("✅ ETH bots are created instead of BTC")
            print("✅ Balance deduction works without SQL errors")
            print("✅ EmergentIntegrations module imports successfully")
            print("✅ Full conversation flow creates correct ETH futures bot")
        else:
            print("\n⚠️  SOME CRITICAL FIXES ARE STILL BROKEN")
            failed_fixes = [name for name, status in critical_fixes.items() if not status]
            print(f"Failed fixes: {', '.join(failed_fixes)}")
        
        return all_critical_passed

def main():
    """Main test execution"""
    tester = AIBotChatTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🚀 TESTING COMPLETED SUCCESSFULLY - ALL CRITICAL FIXES VERIFIED")
        exit(0)
    else:
        print("\n❌ TESTING FAILED - CRITICAL ISSUES REMAIN")
        exit(1)

if __name__ == "__main__":
    main()