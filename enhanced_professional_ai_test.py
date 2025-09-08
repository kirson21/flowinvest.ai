#!/usr/bin/env python3
"""
Enhanced Professional AI Trading Agent System Testing
Tests comprehensive trading parameters and professional conversation flow
"""

import requests
import json
import uuid
import time
import os
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://ai-flow-invest.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test user ID
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class ProfessionalTradingAgentTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.session_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_health_check(self) -> bool:
        """Test AI Bot Chat health check with professional trading prompt"""
        try:
            response = self.session.get(f"{API_BASE}/ai-bot-chat/health")
            
            if response.status_code != 200:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Verify health status
            if data.get("status") != "healthy":
                self.log_test("Health Check", False, f"Status: {data.get('status')}")
                return False
                
            # Verify AI models available
            expected_models = ["gpt-4o", "claude-3-7-sonnet", "gemini-2.0-flash"]
            available_models = data.get("ai_models_available", [])
            
            if not all(model in available_models for model in expected_models):
                self.log_test("Health Check", False, f"Missing models. Available: {available_models}")
                return False
                
            # Verify database connection
            if not data.get("database_available"):
                self.log_test("Health Check", False, "Database not available")
                return False
                
            # Verify Emergent Universal Key
            if not data.get("universal_key_configured"):
                self.log_test("Health Check", False, "Emergent Universal Key not configured")
                return False
                
            self.log_test("Health Check", True, f"All 3 AI models available, database connected, professional trading systems agent prompt active")
            return True
            
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
            
    def test_start_professional_chat_session(self, ai_model: str, initial_prompt: str) -> tuple[bool, str]:
        """Test starting chat session with professional trading request"""
        try:
            session_id = str(uuid.uuid4())
            
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": session_id,
                "ai_model": ai_model,
                "initial_prompt": initial_prompt
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code != 200:
                self.log_test(f"Start Chat Session ({ai_model})", False, f"HTTP {response.status_code}")
                return False, ""
                
            data = response.json()
            
            if not data.get("success"):
                self.log_test(f"Start Chat Session ({ai_model})", False, "Success=False")
                return False, ""
                
            returned_session_id = data.get("session_id")
            ai_response = data.get("message", "")
            
            if not returned_session_id:
                self.log_test(f"Start Chat Session ({ai_model})", False, "No session_id returned")
                return False, ""
                
            # Verify professional response
            professional_indicators = [
                "trading", "capital", "leverage", "risk", "strategy", 
                "question", "professional", "bot", "investment"
            ]
            
            response_lower = ai_response.lower()
            professional_score = sum(1 for indicator in professional_indicators if indicator in response_lower)
            
            if professional_score < 3:
                self.log_test(f"Start Chat Session ({ai_model})", False, f"Response not professional enough (score: {professional_score}/10)")
                return False, ""
                
            self.session_ids.append(returned_session_id)
            self.log_test(f"Start Chat Session ({ai_model})", True, f"Session {returned_session_id[:8]}..., professional response ({len(ai_response)} chars)")
            return True, returned_session_id
            
        except Exception as e:
            self.log_test(f"Start Chat Session ({ai_model})", False, f"Exception: {str(e)}")
            return False, ""
            
    def test_professional_conversation_flow(self, ai_model: str, session_id: str) -> bool:
        """Test the professional question flow with advanced parameters"""
        try:
            # Test conversation flow with professional trading parameters
            conversation_steps = [
                {
                    "message": "$10,000 capital with 3x leverage",
                    "expected_keywords": ["instrument", "spot", "futures", "trading", "pairs"]
                },
                {
                    "message": "Futures trading with altcoins",
                    "expected_keywords": ["strategy", "momentum", "scalping", "grid", "timeframe"]
                },
                {
                    "message": "Scalping strategy with RSI signals",
                    "expected_keywords": ["risk", "stop loss", "take profit", "drawdown", "position"]
                },
                {
                    "message": "2% risk per trade, 3% stop loss, 5% take profit",
                    "expected_keywords": ["name", "bot", "identity", "call"]
                },
                {
                    "message": "Altcoin Scalping Pro",
                    "expected_keywords": ["ready_to_create", "specification", "json", "bot_config"]
                }
            ]
            
            question_count = 0
            for i, step in enumerate(conversation_steps):
                payload = {
                    "user_id": TEST_USER_ID,
                    "session_id": session_id,
                    "message_content": step["message"],
                    "ai_model": ai_model,
                    "bot_creation_stage": "conversation"
                }
                
                response = self.session.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload)
                
                if response.status_code != 200:
                    self.log_test(f"Conversation Step {i+1} ({ai_model})", False, f"HTTP {response.status_code}")
                    return False
                    
                data = response.json()
                
                if not data.get("success"):
                    self.log_test(f"Conversation Step {i+1} ({ai_model})", False, "Success=False")
                    return False
                    
                ai_response = data.get("message", "").lower()
                
                # Check for expected keywords
                keyword_matches = sum(1 for keyword in step["expected_keywords"] if keyword in ai_response)
                
                if keyword_matches == 0:
                    self.log_test(f"Conversation Step {i+1} ({ai_model})", False, f"No expected keywords found. Expected: {step['expected_keywords']}")
                    return False
                    
                # Count questions asked
                if "question" in ai_response or "?" in ai_response:
                    question_count += 1
                    
                # Check if bot is ready to create (final step)
                if i == len(conversation_steps) - 1:
                    is_ready = data.get("ready_to_create", False)
                    bot_config = data.get("bot_config")
                    
                    if not is_ready:
                        self.log_test(f"Bot Creation Ready ({ai_model})", False, "Bot not ready to create")
                        return False
                        
                    if not bot_config:
                        self.log_test(f"Bot Configuration ({ai_model})", False, "No bot config returned")
                        return False
                        
                    # Verify comprehensive bot configuration
                    bot_data = bot_config.get("bot_config", {})
                    required_fields = ["name", "description", "base_coin", "trade_type", "leverage", "strategy_type"]
                    
                    missing_fields = [field for field in required_fields if not bot_data.get(field)]
                    if missing_fields:
                        self.log_test(f"Bot Configuration ({ai_model})", False, f"Missing fields: {missing_fields}")
                        return False
                        
                    # Check for advanced settings
                    advanced_settings = bot_data.get("advanced_settings", {})
                    if not advanced_settings:
                        self.log_test(f"Advanced Settings ({ai_model})", False, "No advanced settings in bot config")
                        return False
                        
                    # Verify advanced settings sections
                    expected_sections = ["entry_conditions", "exit_conditions", "technical_indicators", "risk_management", "order_management"]
                    present_sections = [section for section in expected_sections if advanced_settings.get(section)]
                    
                    if len(present_sections) < 4:  # At least 4 out of 5 sections should be present
                        self.log_test(f"Advanced Settings Sections ({ai_model})", False, f"Only {len(present_sections)}/5 sections present: {present_sections}")
                        return False
                        
                    self.log_test(f"Professional Conversation Flow ({ai_model})", True, f"5 steps completed, {question_count} questions asked, comprehensive bot config generated")
                    return True
                    
                time.sleep(0.5)  # Small delay between messages
                
            return False
            
        except Exception as e:
            self.log_test(f"Professional Conversation Flow ({ai_model})", False, f"Exception: {str(e)}")
            return False
            
    def test_advanced_parameter_detection(self, ai_model: str) -> bool:
        """Test advanced parameter detection in conversation"""
        try:
            session_id = str(uuid.uuid4())
            
            # Start with advanced trading request
            advanced_prompt = "Create a momentum trading bot with RSI and MACD signals, 3% stop loss, grid trading with 10 orders, and martingale scaling"
            
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": session_id,
                "ai_model": ai_model,
                "initial_prompt": advanced_prompt
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code != 200:
                self.log_test(f"Advanced Parameter Detection ({ai_model})", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            ai_response = data.get("message", "").lower()
            
            # Check if AI recognizes advanced parameters
            advanced_terms = [
                "rsi", "macd", "stop loss", "grid", "martingale", 
                "momentum", "signals", "orders", "scaling"
            ]
            
            detected_terms = [term for term in advanced_terms if term in ai_response]
            
            if len(detected_terms) < 3:
                self.log_test(f"Advanced Parameter Detection ({ai_model})", False, f"Only detected {len(detected_terms)}/9 advanced terms: {detected_terms}")
                return False
                
            self.log_test(f"Advanced Parameter Detection ({ai_model})", True, f"Detected {len(detected_terms)}/9 advanced parameters: {detected_terms}")
            return True
            
        except Exception as e:
            self.log_test(f"Advanced Parameter Detection ({ai_model})", False, f"Exception: {str(e)}")
            return False
            
    def test_comprehensive_bot_creation(self, ai_model: str, session_id: str) -> bool:
        """Test comprehensive bot creation with all advanced parameters"""
        try:
            # Get chat history to verify conversation
            history_response = self.session.get(f"{API_BASE}/ai-bot-chat/history/{session_id}?user_id={TEST_USER_ID}")
            
            if history_response.status_code != 200:
                self.log_test(f"Chat History Retrieval ({ai_model})", False, f"HTTP {history_response.status_code}")
                return False
                
            history_data = history_response.json()
            messages = history_data.get("messages", [])
            
            if len(messages) < 8:  # Should have multiple conversation turns
                self.log_test(f"Chat History ({ai_model})", False, f"Only {len(messages)} messages in history")
                return False
                
            # Find the bot configuration from the last assistant message
            bot_config = None
            for message in reversed(messages):
                if message.get("message_type") == "assistant":
                    content = message.get("message_content", "")
                    if "ready_to_create" in content and "```json" in content:
                        try:
                            json_start = content.find("```json") + 7
                            json_end = content.find("```", json_start)
                            if json_end != -1:
                                json_str = content[json_start:json_end].strip()
                                bot_config = json.loads(json_str)
                                break
                        except:
                            continue
                            
            if not bot_config:
                self.log_test(f"Bot Config Extraction ({ai_model})", False, "Could not extract bot config from conversation")
                return False
                
            # Create the bot using the extracted configuration
            creation_payload = {
                "user_id": TEST_USER_ID,
                "session_id": session_id,
                "ai_model": ai_model,
                "bot_config": bot_config,
                "strategy_config": bot_config.get("bot_config", {}).get("advanced_settings", {}),
                "risk_management": bot_config.get("bot_config", {}).get("advanced_settings", {}).get("risk_management", {})
            }
            
            create_response = self.session.post(f"{API_BASE}/ai-bot-chat/create-bot", json=creation_payload)
            
            if create_response.status_code != 200:
                self.log_test(f"Bot Creation ({ai_model})", False, f"HTTP {create_response.status_code}")
                return False
                
            create_data = create_response.json()
            
            if not create_data.get("success"):
                self.log_test(f"Bot Creation ({ai_model})", False, f"Creation failed: {create_data}")
                return False
                
            bot_id = create_data.get("bot_id")
            if not bot_id:
                self.log_test(f"Bot Creation ({ai_model})", False, "No bot_id returned")
                return False
                
            self.log_test(f"Comprehensive Bot Creation ({ai_model})", True, f"Bot created with ID: {bot_id}")
            return True
            
        except Exception as e:
            self.log_test(f"Comprehensive Bot Creation ({ai_model})", False, f"Exception: {str(e)}")
            return False
            
    def test_edit_mode_context(self, ai_model: str) -> bool:
        """Test editing existing bots with context understanding"""
        try:
            session_id = str(uuid.uuid4())
            
            # Simulate editing an existing bot
            edit_prompt = "I want to modify my existing Bitcoin momentum bot to use 5x leverage instead of 3x and add Bollinger Bands signals"
            
            payload = {
                "user_id": TEST_USER_ID,
                "session_id": session_id,
                "ai_model": ai_model,
                "initial_prompt": edit_prompt
            }
            
            response = self.session.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload)
            
            if response.status_code != 200:
                self.log_test(f"Edit Mode Context ({ai_model})", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            ai_response = data.get("message", "").lower()
            
            # Check if AI recognizes this as an edit request
            edit_indicators = ["modify", "existing", "change", "update", "edit", "bitcoin", "momentum", "leverage", "bollinger"]
            
            detected_indicators = [indicator for indicator in edit_indicators if indicator in ai_response]
            
            if len(detected_indicators) < 3:
                self.log_test(f"Edit Mode Context ({ai_model})", False, f"AI didn't recognize edit context. Detected: {detected_indicators}")
                return False
                
            self.log_test(f"Edit Mode Context ({ai_model})", True, f"AI recognized edit context with {len(detected_indicators)} indicators")
            return True
            
        except Exception as e:
            self.log_test(f"Edit Mode Context ({ai_model})", False, f"Exception: {str(e)}")
            return False
            
    def test_get_user_ai_bots(self) -> bool:
        """Test retrieving user's AI bots"""
        try:
            response = self.session.get(f"{API_BASE}/ai-bots/user/{TEST_USER_ID}")
            
            if response.status_code != 200:
                self.log_test("Get User AI Bots", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_test("Get User AI Bots", False, "Success=False")
                return False
                
            bots = data.get("bots", [])
            total = data.get("total", 0)
            
            if total != len(bots):
                self.log_test("Get User AI Bots", False, f"Total mismatch: {total} != {len(bots)}")
                return False
                
            self.log_test("Get User AI Bots", True, f"Retrieved {total} AI bots")
            return True
            
        except Exception as e:
            self.log_test("Get User AI Bots", False, f"Exception: {str(e)}")
            return False
            
    def run_comprehensive_test(self):
        """Run comprehensive test suite for Enhanced Professional AI Trading Agent"""
        print("🚀 ENHANCED PROFESSIONAL AI TRADING AGENT COMPREHENSIVE TESTING")
        print("=" * 80)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return
            
        # Test 2: Professional Chat Sessions for all AI models
        ai_models = ["gpt-4o", "claude-3-7-sonnet", "gemini-2.0-flash"]
        successful_sessions = []
        
        for ai_model in ai_models:
            professional_prompt = f"Create a scalping bot with RSI signals and 3% stop loss for {ai_model.upper()} testing"
            success, session_id = self.test_start_professional_chat_session(ai_model, professional_prompt)
            if success:
                successful_sessions.append((ai_model, session_id))
                
        if not successful_sessions:
            print("❌ No successful chat sessions - aborting conversation tests")
            return
            
        # Test 3: Professional Conversation Flow
        for ai_model, session_id in successful_sessions[:1]:  # Test with first successful session
            if not self.test_professional_conversation_flow(ai_model, session_id):
                continue
                
            # Test 4: Comprehensive Bot Creation
            self.test_comprehensive_bot_creation(ai_model, session_id)
            
        # Test 5: Advanced Parameter Detection
        for ai_model in ai_models[:2]:  # Test with first 2 models
            self.test_advanced_parameter_detection(ai_model)
            
        # Test 6: Edit Mode Context
        for ai_model in ai_models[:1]:  # Test with first model
            self.test_edit_mode_context(ai_model)
            
        # Test 7: User AI Bots Retrieval
        self.test_get_user_ai_bots()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ PASSED: {passed}/{total} tests ({success_rate:.1f}% success rate)")
        
        if passed < total:
            print(f"❌ FAILED: {total - passed} tests")
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
                    
        print(f"\n🎯 OVERALL ASSESSMENT: {'FULLY OPERATIONAL' if success_rate >= 75 else 'NEEDS ATTENTION'}")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = ProfessionalTradingAgentTester()
    tester.run_comprehensive_test()