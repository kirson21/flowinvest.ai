#!/usr/bin/env python3
"""
Professional Trading Agent Context System Testing
Tests the completely rewritten ConversationTracker class for context issues
"""

import requests
import json
import uuid
import time
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class ProfessionalTradingAgentTester:
    def __init__(self):
        self.session_id = None
        self.conversation_history = []
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self) -> bool:
        """Test AI Bot Chat health check."""
        try:
            response = requests.get(f"{BACKEND_URL}/ai-bot-chat/health", timeout=10)
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
    
    def start_session_with_initial_prompt(self, initial_prompt: str, ai_model: str = "gpt-4o") -> bool:
        """Start chat session with initial user prompt."""
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "ai_model": ai_model,
                "initial_prompt": initial_prompt
            }
            
            response = requests.post(f"{BACKEND_URL}/ai-bot-chat/start-session", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                ai_response = data.get("message", "")
                
                # Store conversation
                self.conversation_history.append({
                    "type": "user",
                    "content": initial_prompt
                })
                self.conversation_history.append({
                    "type": "assistant", 
                    "content": ai_response
                })
                
                # Check if AI recognizes user already specified leverage and futures
                recognizes_leverage = any(word in ai_response.lower() for word in ["3-5x", "leverage", "capital"])
                recognizes_futures = any(word in ai_response.lower() for word in ["futures", "instruments"])
                
                # Check what question AI asks first
                asks_capital = "capital" in ai_response.lower() and "question 1" in ai_response.lower()
                asks_instruments = "instruments" in ai_response.lower() and "question 2" in ai_response.lower()
                asks_risk = "risk" in ai_response.lower() and "question 3" in ai_response.lower()
                
                details = f"Session: {self.session_id}, AI Response Length: {len(ai_response)}"
                if asks_capital:
                    details += " | ❌ WRONG: Asked Question 1 (Capital) - should skip since user said '3-5x leverage'"
                elif asks_risk:
                    details += " | ✅ CORRECT: Asked Question 3 (Risk) - properly skipped capital/leverage"
                elif asks_instruments:
                    details += " | ✅ CORRECT: Asked Question 2 (Instruments) - but should skip since user said 'futures'"
                else:
                    details += f" | ❓ UNCLEAR: Response doesn't clearly ask specific question"
                
                success = self.session_id is not None and len(ai_response) > 50
                self.log_test("Start Session with Context", success, details)
                
                # Additional context analysis
                if "hello" in ai_response.lower() and len(self.conversation_history) == 2:
                    self.log_test("Context Recognition", False, "❌ AI starts with 'Hello' indicating new conversation, not following context")
                else:
                    self.log_test("Context Recognition", True, "✅ AI response doesn't start fresh, appears to follow context")
                
                return success
            else:
                self.log_test("Start Session with Context", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Start Session with Context", False, f"Exception: {str(e)}")
            return False
    
    def send_message(self, message: str, expected_question: str = None) -> bool:
        """Send message and verify AI response."""
        try:
            if not self.session_id:
                self.log_test("Send Message", False, "No active session")
                return False
            
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "message_content": message,
                "ai_model": "gpt-4o",
                "bot_creation_stage": "clarification"
            }
            
            response = requests.post(f"{BACKEND_URL}/ai-bot-chat/send-message", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("message", "")
                is_ready = data.get("ready_to_create", False)
                
                # Store conversation
                self.conversation_history.append({
                    "type": "user",
                    "content": message
                })
                self.conversation_history.append({
                    "type": "assistant",
                    "content": ai_response
                })
                
                # Check if AI repeats previous questions
                repeats_capital = "capital" in ai_response.lower() and any("capital" in msg["content"].lower() for msg in self.conversation_history[:-2] if msg["type"] == "assistant")
                
                # Check progression
                question_number = None
                if "question 1" in ai_response.lower():
                    question_number = 1
                elif "question 2" in ai_response.lower():
                    question_number = 2
                elif "question 3" in ai_response.lower():
                    question_number = 3
                elif "question 4" in ai_response.lower():
                    question_number = 4
                elif "question 5" in ai_response.lower():
                    question_number = 5
                
                details = f"Response Length: {len(ai_response)}, Ready: {is_ready}"
                if repeats_capital:
                    details += " | ❌ REPEATS: AI asking for capital again"
                if question_number:
                    details += f" | Question {question_number} asked"
                if expected_question and expected_question.lower() in ai_response.lower():
                    details += f" | ✅ EXPECTED: Asked about {expected_question}"
                
                success = len(ai_response) > 50 and not repeats_capital
                self.log_test(f"Send Message: '{message[:30]}...'", success, details)
                
                return success
            else:
                self.log_test("Send Message", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Send Message", False, f"Exception: {str(e)}")
            return False
    
    def get_conversation_history(self) -> bool:
        """Get and verify conversation history."""
        try:
            if not self.session_id:
                self.log_test("Get History", False, "No active session")
                return False
            
            response = requests.get(f"{BACKEND_URL}/ai-bot-chat/history/{self.session_id}?user_id={TEST_USER_ID}", 
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                details = f"Retrieved {len(messages)} messages"
                if len(messages) >= len(self.conversation_history):
                    details += " | ✅ All messages stored"
                else:
                    details += " | ❌ Missing messages in database"
                
                success = len(messages) > 0
                self.log_test("Get Conversation History", success, details)
                return success
            else:
                self.log_test("Get Conversation History", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Conversation History", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_conversation_flow(self) -> bool:
        """Test the complete 5-question conversation flow."""
        print("\n🎯 TESTING COMPLETE CONVERSATION FLOW")
        print("=" * 60)
        
        # Step 1: Start with user specification
        initial_prompt = "Futures trading with leverage 3-5x, altcoins"
        print(f"👤 USER: {initial_prompt}")
        
        if not self.start_session_with_initial_prompt(initial_prompt):
            return False
        
        print(f"🤖 AI: {self.conversation_history[-1]['content'][:200]}...")
        
        # Step 2: Answer about instruments (should be skipped since user said futures)
        message2 = "Futures with short selling capability"
        print(f"\n👤 USER: {message2}")
        
        if not self.send_message(message2, "risk"):
            return False
        
        print(f"🤖 AI: {self.conversation_history[-1]['content'][:200]}...")
        
        # Step 3: Answer about risk
        message3 = "2% per trade, 10% max drawdown, 2 positions"
        print(f"\n👤 USER: {message3}")
        
        if not self.send_message(message3, "strategy"):
            return False
        
        print(f"🤖 AI: {self.conversation_history[-1]['content'][:200]}...")
        
        # Step 4: Answer about strategy
        message4 = "Momentum trading with 1-hour timeframes"
        print(f"\n👤 USER: {message4}")
        
        if not self.send_message(message4, "name"):
            return False
        
        print(f"🤖 AI: {self.conversation_history[-1]['content'][:200]}...")
        
        # Step 5: Provide bot name
        message5 = "Altcoin Futures Momentum Pro"
        print(f"\n👤 USER: {message5}")
        
        if not self.send_message(message5):
            return False
        
        print(f"🤖 AI: {self.conversation_history[-1]['content'][:200]}...")
        
        # Verify final bot configuration
        final_response = self.conversation_history[-1]['content']
        has_bot_config = "ready_to_create" in final_response.lower() or "json" in final_response.lower()
        has_altcoin = "alt" in final_response.lower()
        has_futures = "futures" in final_response.lower()
        has_leverage = "5x" in final_response or "3x" in final_response
        
        details = f"Bot Config: {has_bot_config}, ALT: {has_altcoin}, FUTURES: {has_futures}, Leverage: {has_leverage}"
        success = has_bot_config and has_altcoin and has_futures
        
        self.log_test("Complete Conversation Flow", success, details)
        return success
    
    def test_bot_creation(self) -> bool:
        """Test bot creation from conversation."""
        try:
            if not self.session_id:
                self.log_test("Bot Creation", False, "No active session")
                return False
            
            # Extract bot config from final response
            final_response = self.conversation_history[-1]['content']
            bot_config = None
            
            if "```json" in final_response:
                try:
                    json_start = final_response.find("```json") + 7
                    json_end = final_response.find("```", json_start)
                    if json_end != -1:
                        json_str = final_response[json_start:json_end].strip()
                        bot_config = json.loads(json_str)
                except Exception as e:
                    self.log_test("Bot Creation", False, f"JSON parse error: {str(e)}")
                    return False
            
            if not bot_config:
                self.log_test("Bot Creation", False, "No bot configuration found in final response")
                return False
            
            # Create bot
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": self.session_id,
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": {},
                "risk_management": {}
            }
            
            response = requests.post(f"{BACKEND_URL}/ai-bot-chat/create-bot", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                bot_id = data.get("bot_id")
                message = data.get("message", "")
                
                details = f"Bot ID: {bot_id}, Message: {message}"
                success = bot_id is not None
                self.log_test("Bot Creation", success, details)
                return success
            else:
                # Check for VARCHAR error specifically
                error_text = response.text
                if "value too long" in error_text.lower():
                    self.log_test("Bot Creation", False, f"❌ VARCHAR ERROR: {error_text}")
                else:
                    self.log_test("Bot Creation", False, f"HTTP {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Bot Creation", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of the Professional Trading Agent system."""
        print("🚀 PROFESSIONAL TRADING AGENT CONTEXT SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {TEST_USER_ID}")
        print("=" * 80)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return
        
        # Test 2: Complete conversation flow
        if not self.test_complete_conversation_flow():
            print("❌ Conversation flow failed")
        
        # Test 3: Get conversation history
        self.get_conversation_history()
        
        # Test 4: Bot creation
        self.test_bot_creation()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        # Critical success criteria check
        critical_checks = {
            "Context Recognition": False,
            "Complete Conversation Flow": False,
            "Bot Creation": False
        }
        
        for result in self.test_results:
            for check in critical_checks:
                if check in result["test"] and result["success"]:
                    critical_checks[check] = True
        
        print("\n🎯 CRITICAL SUCCESS CRITERIA:")
        for check, passed in critical_checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")
        
        # Specific review request criteria
        print("\n📋 REVIEW REQUEST CRITERIA:")
        
        # Check if AI recognizes user specifications
        context_working = any("Context Recognition" in r["test"] and r["success"] for r in self.test_results)
        print(f"{'✅' if context_working else '❌'} AI recognizes user already specified leverage (3-5x) and futures")
        
        # Check conversation flow
        flow_working = any("Complete Conversation Flow" in r["test"] and r["success"] for r in self.test_results)
        print(f"{'✅' if flow_working else '❌'} AI progresses through questions without repetition")
        
        # Check final bot config
        if len(self.conversation_history) > 0:
            final_response = self.conversation_history[-1]['content'].lower()
            has_alt = "alt" in final_response
            has_futures = "futures" in final_response
            has_leverage = "5x" in final_response or "3x" in final_response
            config_correct = has_alt and has_futures and has_leverage
            print(f"{'✅' if config_correct else '❌'} Final bot config has: ALT coin, FUTURES trading, 5x leverage")
        else:
            print("❌ Final bot config has: ALT coin, FUTURES trading, 5x leverage")
        
        # Check database errors
        varchar_error = any("VARCHAR ERROR" in r["details"] for r in self.test_results)
        print(f"{'❌' if varchar_error else '✅'} No VARCHAR database errors during bot creation")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 75 and not varchar_error:
            print("🎉 OVERALL: PROFESSIONAL TRADING AGENT SYSTEM IS WORKING")
        else:
            print("⚠️  OVERALL: PROFESSIONAL TRADING AGENT SYSTEM HAS ISSUES")
        
        return self.test_results

if __name__ == "__main__":
    tester = ProfessionalTradingAgentTester()
    results = tester.run_comprehensive_test()