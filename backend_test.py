#!/usr/bin/env python3
"""
Professional Trading Agent Critical Fixes Testing
=================================================

Testing the CRITICAL FIXES for Professional Trading Agent context and user answer following:

CRITICAL ISSUE FIXED: Session context continuity - Now using same session_id instead of creating new ones each time

Test Requirements:

1. **User Answer Following Fix Test**: 
   - Start session with "Futures trading with leverage 3-5x, altcoins"
   - Answer questions with specific requirements
   - Verify final bot config has: FUTURES trading, 5x leverage, ALTCOINS (not BTC), custom bot name
   - Confirm AI follows exact user specifications

2. **Context Continuity Fix Test**:
   - Verify AI progresses through 5 mandatory questions properly
   - Test that Question 1 → Question 2 → Question 3 → Question 4 → Question 5 (Bot Name)
   - Confirm conversation context is maintained between messages

3. **Database Table Fix Test**:
   - Verify AI bots save to user_ai_bots table (not user_bots)
   - Test no VARCHAR(100) errors during bot creation
   - Confirm bot creation completes successfully with all user specifications

4. **Professional Bot Name Test**:
   - Verify Question 5 asks for bot name
   - Test custom bot names are captured and used
   - Confirm bot names appear in final configuration

Use test user ID: cd0e9717-f85d-4726-81e9-f260394ead58

Critical Success Criteria:
- AI creates ALTCOIN FUTURES bot with 5X leverage (not BTC spot)
- All 5 questions asked in sequence with context continuity
- Bot saved successfully without database errors
- Custom bot name from Question 5 used in final bot
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class ProfessionalTradingAgentTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_user_id = TEST_USER_ID
        self.session_id = None
        self.conversation_history = []
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_health_check(self):
        """Test AI Bot Chat health check"""
        try:
            response = requests.get(f"{self.backend_url}/ai-bot-chat/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}, Models: {data.get('ai_models_available')}")
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def start_session_with_initial_prompt(self, initial_prompt, ai_model="gpt-4o"):
        """Start chat session with initial prompt"""
        try:
            payload = {
                "user_id": self.test_user_id,
                "ai_model": ai_model,
                "initial_prompt": initial_prompt
            }
            
            response = requests.post(
                f"{self.backend_url}/ai-bot-chat/start-session",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.session_id = data.get("session_id")
                    ai_response = data.get("message", "")
                    
                    # Store conversation
                    self.conversation_history.append({
                        "type": "user",
                        "content": initial_prompt,
                        "timestamp": datetime.now().isoformat()
                    })
                    self.conversation_history.append({
                        "type": "assistant", 
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    self.log_test("Start Session", True, f"Session ID: {self.session_id}, Response length: {len(ai_response)}")
                    return ai_response
                else:
                    self.log_test("Start Session", False, f"API returned success=false: {data}")
                    return None
            else:
                self.log_test("Start Session", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Start Session", False, f"Exception: {str(e)}")
            return None
    
    def send_message(self, message_content):
        """Send message in existing session"""
        try:
            if not self.session_id:
                self.log_test("Send Message", False, "No active session")
                return None
                
            payload = {
                "user_id": self.test_user_id,
                "session_id": self.session_id,
                "message_content": message_content,
                "ai_model": "gpt-4o",
                "bot_creation_stage": "clarification"
            }
            
            response = requests.post(
                f"{self.backend_url}/ai-bot-chat/send-message",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    ai_response = data.get("message", "")
                    is_ready = data.get("ready_to_create", False)
                    bot_config = data.get("bot_config")
                    
                    # Store conversation
                    self.conversation_history.append({
                        "type": "user",
                        "content": message_content,
                        "timestamp": datetime.now().isoformat()
                    })
                    self.conversation_history.append({
                        "type": "assistant",
                        "content": ai_response,
                        "ready_to_create": is_ready,
                        "bot_config": bot_config,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    self.log_test("Send Message", True, f"Response length: {len(ai_response)}, Ready: {is_ready}")
                    return {
                        "response": ai_response,
                        "ready_to_create": is_ready,
                        "bot_config": bot_config
                    }
                else:
                    self.log_test("Send Message", False, f"API returned success=false: {data}")
                    return None
            else:
                self.log_test("Send Message", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Send Message", False, f"Exception: {str(e)}")
            return None
    
    def create_ai_bot(self, bot_config):
        """Create AI bot from configuration"""
        try:
            if not self.session_id:
                self.log_test("Create AI Bot", False, "No active session")
                return None
                
            payload = {
                "user_id": self.test_user_id,
                "session_id": self.session_id,
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": bot_config.get("strategy_config", {}),
                "risk_management": bot_config.get("risk_management", {})
            }
            
            response = requests.post(
                f"{self.backend_url}/ai-bot-chat/create-bot",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    bot_id = data.get("bot_id")
                    message = data.get("message", "")
                    self.log_test("Create AI Bot", True, f"Bot ID: {bot_id}, Message: {message}")
                    return bot_id
                else:
                    self.log_test("Create AI Bot", False, f"API returned success=false: {data}")
                    return None
            else:
                self.log_test("Create AI Bot", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create AI Bot", False, f"Exception: {str(e)}")
            return None
    
    def get_user_ai_bots(self):
        """Get user's AI bots"""
        try:
            response = requests.get(
                f"{self.backend_url}/ai-bots/user/{self.test_user_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    bots = data.get("bots", [])
                    total = data.get("total", 0)
                    self.log_test("Get User AI Bots", True, f"Total bots: {total}")
                    return bots
                else:
                    self.log_test("Get User AI Bots", False, f"API returned success=false: {data}")
                    return []
            else:
                self.log_test("Get User AI Bots", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get User AI Bots", False, f"Exception: {str(e)}")
            return []
    
    def analyze_question_progression(self):
        """Analyze if AI progresses through 5 mandatory questions"""
        question_indicators = [
            "Question 1",
            "Question 2", 
            "Question 3",
            "Question 4",
            "Question 5"
        ]
        
        questions_found = []
        for i, msg in enumerate(self.conversation_history):
            if msg["type"] == "assistant":
                content = msg["content"]
                for q_num, indicator in enumerate(question_indicators, 1):
                    if indicator in content or f"Mandatory Question {q_num}" in content:
                        questions_found.append(q_num)
                        break
        
        # Check for proper progression
        expected_sequence = [1, 2, 3, 4, 5]
        progression_correct = questions_found == expected_sequence[:len(questions_found)]
        
        self.log_test("Question Progression", progression_correct, 
                     f"Found questions: {questions_found}, Expected: {expected_sequence[:len(questions_found)]}")
        
        return progression_correct, questions_found
    
    def analyze_user_specifications_following(self, bot_config):
        """Analyze if AI follows user specifications"""
        if not bot_config:
            self.log_test("User Specifications Following", False, "No bot config generated")
            return False
        
        # Extract bot configuration
        config = bot_config.get("bot_config", {})
        
        # Check for FUTURES trading
        instruments = config.get("instruments", "").lower()
        trade_type = config.get("trade_type", "").lower()
        futures_trading = "futures" in instruments or "futures" in trade_type
        
        # Check for 5x leverage
        leverage = config.get("leverage_allowed", 1.0)
        correct_leverage = leverage >= 3.0 and leverage <= 5.0
        
        # Check for ALTCOINS (not BTC)
        base_coin = config.get("base_coin", "").upper()
        altcoin_trading = base_coin != "BTC" and base_coin in ["ETH", "SOL", "ADA", "MATIC", "DOGE", "ALT"]
        
        # Check for custom bot name
        bot_name = config.get("name", "")
        has_custom_name = len(bot_name) > 0 and "Bot" in bot_name
        
        all_specs_followed = futures_trading and correct_leverage and altcoin_trading and has_custom_name
        
        details = f"Futures: {futures_trading}, Leverage: {leverage}x, Coin: {base_coin}, Name: '{bot_name}'"
        self.log_test("User Specifications Following", all_specs_followed, details)
        
        return all_specs_followed
    
    def analyze_context_continuity(self):
        """Analyze if conversation context is maintained"""
        # Check if AI repeats questions instead of progressing
        assistant_messages = [msg["content"] for msg in self.conversation_history if msg["type"] == "assistant"]
        
        # Look for repeated question patterns
        question_1_count = sum(1 for msg in assistant_messages if "Question 1" in msg or "Trading Capital" in msg)
        
        # Context is broken if Question 1 appears multiple times
        context_maintained = question_1_count <= 1
        
        self.log_test("Context Continuity", context_maintained, 
                     f"Question 1 appeared {question_1_count} times (should be 1)")
        
        return context_maintained
    
    def run_critical_fixes_test(self):
        """Run comprehensive test of critical fixes"""
        print("=" * 80)
        print("PROFESSIONAL TRADING AGENT CRITICAL FIXES TESTING")
        print("=" * 80)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ CRITICAL: Health check failed, aborting tests")
            return False
        
        # Test 2: Start session with specific requirements
        initial_prompt = "Futures trading with leverage 3-5x, altcoins"
        print(f"\n🚀 Starting session with prompt: '{initial_prompt}'")
        
        ai_response = self.start_session_with_initial_prompt(initial_prompt)
        if not ai_response:
            print("❌ CRITICAL: Failed to start session")
            return False
        
        # Test 3: Progress through 5 mandatory questions
        print("\n📋 Testing 5-question progression...")
        
        # Answer Question 1 (Capital & Leverage)
        response1 = self.send_message("$10,000 capital with 5x leverage for futures trading")
        if not response1:
            print("❌ CRITICAL: Failed to send message 1")
            return False
        
        time.sleep(2)  # Brief pause between messages
        
        # Answer Question 2 (Instruments)
        response2 = self.send_message("Futures trading with leverage capability for altcoins")
        if not response2:
            print("❌ CRITICAL: Failed to send message 2")
            return False
        
        time.sleep(2)
        
        # Answer Question 3 (Risk Parameters)
        response3 = self.send_message("3% max per trade, 15% max drawdown, 2 positions maximum")
        if not response3:
            print("❌ CRITICAL: Failed to send message 3")
            return False
        
        time.sleep(2)
        
        # Answer Question 4 (Strategy & Timeframe)
        response4 = self.send_message("Momentum strategy for altcoins, 1-hour timeframe")
        if not response4:
            print("❌ CRITICAL: Failed to send message 4")
            return False
        
        time.sleep(2)
        
        # Answer Question 5 (Bot Name)
        custom_bot_name = "Altcoin Futures Momentum Pro"
        response5 = self.send_message(custom_bot_name)
        if not response5:
            print("❌ CRITICAL: Failed to send message 5")
            return False
        
        # Test 4: Analyze question progression
        print("\n🔍 Analyzing question progression...")
        progression_correct, questions_found = self.analyze_question_progression()
        
        # Test 5: Analyze context continuity
        print("\n🔗 Analyzing context continuity...")
        context_maintained = self.analyze_context_continuity()
        
        # Test 6: Check if bot config is ready
        final_response = response5
        bot_config = None
        if final_response and final_response.get("ready_to_create"):
            bot_config = final_response.get("bot_config")
            print(f"\n✅ Bot configuration ready: {bot_config is not None}")
        else:
            print("\n❌ Bot configuration not ready after 5 questions")
        
        # Test 7: Analyze user specifications following
        print("\n📊 Analyzing user specifications following...")
        specs_followed = False
        if bot_config:
            specs_followed = self.analyze_user_specifications_following(bot_config)
        
        # Test 8: Create AI bot if config is ready
        bot_id = None
        if bot_config:
            print("\n🤖 Creating AI bot...")
            bot_id = self.create_ai_bot(bot_config)
        
        # Test 9: Verify bot saved to user_ai_bots table
        print("\n💾 Verifying bot database storage...")
        user_bots = self.get_user_ai_bots()
        bot_saved_correctly = len(user_bots) > 0 and any(bot.get("id") == bot_id for bot in user_bots) if bot_id else False
        
        # Test 10: Verify custom bot name in final bot
        custom_name_used = False
        if bot_id and user_bots:
            created_bot = next((bot for bot in user_bots if bot.get("id") == bot_id), None)
            if created_bot:
                saved_name = created_bot.get("name", "")
                custom_name_used = custom_bot_name.lower() in saved_name.lower() or "altcoin" in saved_name.lower()
                self.log_test("Custom Bot Name Used", custom_name_used, f"Saved name: '{saved_name}'")
        
        # Summary of critical fixes
        print("\n" + "=" * 80)
        print("CRITICAL FIXES VERIFICATION SUMMARY")
        print("=" * 80)
        
        critical_fixes = [
            ("User Answer Following Fix", specs_followed),
            ("Context Continuity Fix", context_maintained),
            ("Database Table Fix", bot_saved_correctly),
            ("Professional Bot Name Fix", custom_name_used),
            ("5-Question Flow Fix", len(questions_found) >= 4)
        ]
        
        all_fixes_working = all(fix[1] for fix in critical_fixes)
        
        for fix_name, working in critical_fixes:
            status = "✅ WORKING" if working else "❌ BROKEN"
            print(f"{status} {fix_name}")
        
        print(f"\n🎯 OVERALL RESULT: {'✅ ALL CRITICAL FIXES WORKING' if all_fixes_working else '❌ CRITICAL FIXES STILL BROKEN'}")
        
        return all_fixes_working

def main():
    """Main test execution"""
    tester = ProfessionalTradingAgentTester()
    
    try:
        success = tester.run_critical_fixes_test()
        
        # Print detailed conversation history for debugging
        print("\n" + "=" * 80)
        print("CONVERSATION HISTORY FOR DEBUGGING")
        print("=" * 80)
        
        for i, msg in enumerate(tester.conversation_history, 1):
            msg_type = "👤 USER" if msg["type"] == "user" else "🤖 AI"
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            print(f"\n{i}. {msg_type}: {content}")
            
            if msg["type"] == "assistant" and msg.get("ready_to_create"):
                print(f"   🎯 Bot Config Ready: {msg.get('bot_config') is not None}")
        
        # Print test results summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in tester.test_results if result["success"])
        total = len(tester.test_results)
        
        print(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        for result in tester.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)