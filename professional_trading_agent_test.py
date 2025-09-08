#!/usr/bin/env python3
"""
Professional Trading Agent System Backend Testing
Tests the new expert prompt and Emergent Universal Key integration
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://ai-flow-invest.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class ProfessionalTradingAgentTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.user_id = TEST_USER_ID
        self.test_results = []
        self.session_ids = {}
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        if data and isinstance(data, dict) and len(str(data)) < 500:
            print(f"   Data: {data}")
        return success

    def test_health_check(self) -> bool:
        """Test 1: Professional Health Check - Verify new trading systems agent prompt is active"""
        try:
            response = requests.get(f"{self.backend_url}/ai-bot-chat/health", timeout=10)
            
            if response.status_code != 200:
                return self.log_test("Professional Health Check", False, f"Health endpoint returned {response.status_code}")
            
            data = response.json()
            
            # Check for professional trading system indicators
            required_models = ["gpt-4o", "claude-3-7-sonnet", "gemini-2.0-flash"]
            available_models = data.get("ai_models_available", [])
            
            models_available = all(model in available_models for model in required_models)
            universal_key_configured = data.get("universal_key_configured", False)
            database_available = data.get("database_available", False)
            
            if not models_available:
                return self.log_test("Professional Health Check", False, f"Missing AI models. Available: {available_models}")
            
            if not universal_key_configured:
                return self.log_test("Professional Health Check", False, "Emergent Universal Key not configured")
            
            if not database_available:
                return self.log_test("Professional Health Check", False, "Database not available")
            
            return self.log_test("Professional Health Check", True, 
                               f"All systems operational: {len(available_models)} AI models, Universal Key configured, Database connected", 
                               data)
            
        except Exception as e:
            return self.log_test("Professional Health Check", False, f"Health check failed: {str(e)}")

    def test_professional_conversation_flow(self, ai_model: str, trading_scenario: str) -> Dict[str, Any]:
        """Test expert conversation flow with mandatory questions structure"""
        try:
            session_id = str(uuid.uuid4())
            self.session_ids[ai_model] = session_id
            
            # Start professional trading conversation
            start_payload = {
                "user_id": self.user_id,
                "session_id": session_id,
                "ai_model": ai_model,
                "initial_prompt": trading_scenario
            }
            
            response = requests.post(f"{self.backend_url}/ai-bot-chat/start-session", 
                                   json=start_payload, timeout=15)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Session start failed: {response.status_code}"}
            
            data = response.json()
            initial_message = data.get("message", "")
            
            # Check for professional trading expertise indicators
            professional_indicators = [
                "trading capital", "leverage", "risk", "capital preservation",
                "mandatory question", "professional", "institutional", "expert"
            ]
            
            has_professional_content = any(indicator.lower() in initial_message.lower() 
                                         for indicator in professional_indicators)
            
            if not has_professional_content:
                return {"success": False, "error": "Initial response lacks professional trading expertise"}
            
            # Simulate conversation flow with mandatory questions
            conversation_steps = [
                "$10,000 capital with 2x leverage",  # Capital question
                "Futures trading with short capability",  # Instruments question  
                "2% max per trade, 10% max drawdown, 2 positions maximum",  # Risk parameters
                f"Momentum strategy with 1h timeframe for {trading_scenario.split()[0]}"  # Strategy/timeframe
            ]
            
            responses = [initial_message]
            mandatory_questions_asked = 0
            
            for step, user_input in enumerate(conversation_steps):
                message_payload = {
                    "user_id": self.user_id,
                    "session_id": session_id,
                    "message_content": user_input,
                    "ai_model": ai_model,
                    "bot_creation_stage": "clarification"
                }
                
                response = requests.post(f"{self.backend_url}/ai-bot-chat/send-message", 
                                       json=message_payload, timeout=15)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Message {step+1} failed: {response.status_code}"}
                
                data = response.json()
                ai_response = data.get("message", "")
                responses.append(ai_response)
                
                # Check for mandatory question patterns
                mandatory_patterns = [
                    "mandatory question", "essential", "required", "must specify",
                    "capital", "leverage", "risk", "timeframe", "strategy"
                ]
                
                if any(pattern.lower() in ai_response.lower() for pattern in mandatory_patterns):
                    mandatory_questions_asked += 1
                
                # Check if bot configuration is ready
                if data.get("ready_to_create", False):
                    bot_config = data.get("bot_config")
                    if bot_config:
                        return {
                            "success": True,
                            "session_id": session_id,
                            "responses": responses,
                            "mandatory_questions_asked": mandatory_questions_asked,
                            "bot_config": bot_config,
                            "conversation_complete": True
                        }
                
                time.sleep(1)  # Rate limiting
            
            return {
                "success": True,
                "session_id": session_id,
                "responses": responses,
                "mandatory_questions_asked": mandatory_questions_asked,
                "conversation_complete": False
            }
            
        except Exception as e:
            return {"success": False, "error": f"Conversation flow failed: {str(e)}"}

    def test_gpt4o_bitcoin_momentum(self) -> bool:
        """Test 2: GPT-4o with Bitcoin momentum trading scenario"""
        scenario = "Bitcoin momentum trading with institutional risk management"
        result = self.test_professional_conversation_flow("gpt-4o", scenario)
        
        if not result["success"]:
            return self.log_test("GPT-4o Bitcoin Momentum", False, result["error"])
        
        # Verify professional conversation structure
        mandatory_questions = result.get("mandatory_questions_asked", 0)
        responses = result.get("responses", [])
        
        if mandatory_questions < 3:
            return self.log_test("GPT-4o Bitcoin Momentum", False, 
                               f"Insufficient mandatory questions asked: {mandatory_questions}/4")
        
        # Check for Bitcoin-specific content
        bitcoin_content = any("bitcoin" in response.lower() or "btc" in response.lower() 
                            for response in responses)
        
        if not bitcoin_content:
            return self.log_test("GPT-4o Bitcoin Momentum", False, "Missing Bitcoin-specific content")
        
        # Check for momentum strategy content
        momentum_content = any("momentum" in response.lower() for response in responses)
        
        if not momentum_content:
            return self.log_test("GPT-4o Bitcoin Momentum", False, "Missing momentum strategy content")
        
        return self.log_test("GPT-4o Bitcoin Momentum", True, 
                           f"Professional conversation completed: {mandatory_questions} mandatory questions, Bitcoin/momentum content verified",
                           {"session_id": result["session_id"], "questions_asked": mandatory_questions})

    def test_claude_ethereum_scalping(self) -> bool:
        """Test 3: Claude with Ethereum scalping strategy"""
        scenario = "Ethereum scalping strategy with high-frequency execution"
        result = self.test_professional_conversation_flow("claude-3-7-sonnet", scenario)
        
        if not result["success"]:
            return self.log_test("Claude Ethereum Scalping", False, result["error"])
        
        mandatory_questions = result.get("mandatory_questions_asked", 0)
        responses = result.get("responses", [])
        
        if mandatory_questions < 3:
            return self.log_test("Claude Ethereum Scalping", False, 
                               f"Insufficient mandatory questions asked: {mandatory_questions}/4")
        
        # Check for Ethereum-specific content
        ethereum_content = any("ethereum" in response.lower() or "eth" in response.lower() 
                             for response in responses)
        
        if not ethereum_content:
            return self.log_test("Claude Ethereum Scalping", False, "Missing Ethereum-specific content")
        
        # Check for scalping strategy content
        scalping_content = any("scalping" in response.lower() or "high-frequency" in response.lower() 
                             for response in responses)
        
        if not scalping_content:
            return self.log_test("Claude Ethereum Scalping", False, "Missing scalping strategy content")
        
        return self.log_test("Claude Ethereum Scalping", True, 
                           f"Professional conversation completed: {mandatory_questions} mandatory questions, Ethereum/scalping content verified",
                           {"session_id": result["session_id"], "questions_asked": mandatory_questions})

    def test_gemini_conservative_trading(self) -> bool:
        """Test 4: Gemini with conservative trading approach"""
        scenario = "Conservative trading approach with capital preservation focus"
        result = self.test_professional_conversation_flow("gemini-2.0-flash", scenario)
        
        if not result["success"]:
            return self.log_test("Gemini Conservative Trading", False, result["error"])
        
        mandatory_questions = result.get("mandatory_questions_asked", 0)
        responses = result.get("responses", [])
        
        if mandatory_questions < 3:
            return self.log_test("Gemini Conservative Trading", False, 
                               f"Insufficient mandatory questions asked: {mandatory_questions}/4")
        
        # Check for conservative trading content
        conservative_content = any(term in response.lower() for response in responses 
                                 for term in ["conservative", "capital preservation", "low risk", "risk management"])
        
        if not conservative_content:
            return self.log_test("Gemini Conservative Trading", False, "Missing conservative trading content")
        
        return self.log_test("Gemini Conservative Trading", True, 
                           f"Professional conversation completed: {mandatory_questions} mandatory questions, conservative approach verified",
                           {"session_id": result["session_id"], "questions_asked": mandatory_questions})

    def test_institutional_bot_creation(self) -> bool:
        """Test 5: Professional Bot Creation - Test institutional-grade bot specifications"""
        try:
            # Use GPT-4o session for bot creation test
            session_id = self.session_ids.get("gpt-4o")
            if not session_id:
                return self.log_test("Institutional Bot Creation", False, "No GPT-4o session available")
            
            # Get chat history to check for bot configuration
            response = requests.get(f"{self.backend_url}/ai-bot-chat/history/{session_id}?user_id={self.user_id}", 
                                  timeout=10)
            
            if response.status_code != 200:
                return self.log_test("Institutional Bot Creation", False, f"History retrieval failed: {response.status_code}")
            
            data = response.json()
            messages = data.get("messages", [])
            
            # Look for bot configuration in messages
            bot_config = None
            for message in messages:
                content = message.get("message_content", "")
                if "```json" in content and "ready_to_create" in content:
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
                # Try to trigger bot creation with final message
                final_message = {
                    "user_id": self.user_id,
                    "session_id": session_id,
                    "message_content": "Please create the bot configuration now with all the information we discussed",
                    "ai_model": "gpt-4o",
                    "bot_creation_stage": "finalization"
                }
                
                response = requests.post(f"{self.backend_url}/ai-bot-chat/send-message", 
                                       json=final_message, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    bot_config = data.get("bot_config")
            
            if not bot_config:
                return self.log_test("Institutional Bot Creation", False, "No bot configuration generated")
            
            # Verify institutional-grade specifications
            required_sections = ["bot_config", "strategy_config", "risk_management", "execution_config"]
            missing_sections = [section for section in required_sections if section not in bot_config]
            
            if missing_sections:
                return self.log_test("Institutional Bot Creation", False, 
                                   f"Missing required sections: {missing_sections}")
            
            # Check bot_config section
            bot_section = bot_config.get("bot_config", {})
            required_bot_fields = ["name", "description", "trading_capital_usd", "leverage_allowed", 
                                 "instruments", "base_coin", "quote_coin", "exchange", "strategy_type", 
                                 "risk_level", "timeframe"]
            
            missing_bot_fields = [field for field in required_bot_fields if field not in bot_section]
            if missing_bot_fields:
                return self.log_test("Institutional Bot Creation", False, 
                                   f"Missing bot config fields: {missing_bot_fields}")
            
            # Check risk_management section
            risk_section = bot_config.get("risk_management", {})
            required_risk_fields = ["max_risk_per_trade_percent", "max_portfolio_drawdown_percent", 
                                  "max_concurrent_positions", "stop_loss_percent", "take_profit_percent",
                                  "kill_switch_conditions"]
            
            missing_risk_fields = [field for field in required_risk_fields if field not in risk_section]
            if missing_risk_fields:
                return self.log_test("Institutional Bot Creation", False, 
                                   f"Missing risk management fields: {missing_risk_fields}")
            
            # Check execution_config section
            execution_section = bot_config.get("execution_config", {})
            required_execution_fields = ["slippage_assumption_bps", "trading_fees_bps", 
                                       "execution_latency_tolerance_ms", "rate_limit_handling", 
                                       "secrets_handling", "idempotency"]
            
            missing_execution_fields = [field for field in required_execution_fields if field not in execution_section]
            if missing_execution_fields:
                return self.log_test("Institutional Bot Creation", False, 
                                   f"Missing execution config fields: {missing_execution_fields}")
            
            # Verify kill switch conditions exist
            kill_switches = risk_section.get("kill_switch_conditions", [])
            if not kill_switches or len(kill_switches) < 2:
                return self.log_test("Institutional Bot Creation", False, 
                                   f"Insufficient kill switch conditions: {len(kill_switches)}")
            
            # Create the bot
            creation_payload = {
                "user_id": self.user_id,
                "session_id": session_id,
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": bot_config.get("strategy_config", {}),
                "risk_management": bot_config.get("risk_management", {})
            }
            
            response = requests.post(f"{self.backend_url}/ai-bot-chat/create-bot", 
                                   json=creation_payload, timeout=15)
            
            if response.status_code != 200:
                return self.log_test("Institutional Bot Creation", False, 
                                   f"Bot creation failed: {response.status_code}")
            
            creation_data = response.json()
            bot_id = creation_data.get("bot_id")
            
            if not bot_id:
                return self.log_test("Institutional Bot Creation", False, "No bot ID returned")
            
            return self.log_test("Institutional Bot Creation", True, 
                               f"Institutional-grade bot created successfully: {bot_id}",
                               {"bot_id": bot_id, "config_sections": len(required_sections), 
                                "kill_switches": len(kill_switches)})
            
        except Exception as e:
            return self.log_test("Institutional Bot Creation", False, f"Bot creation test failed: {str(e)}")

    def test_mandatory_information_gathering(self) -> bool:
        """Test 6: Verify mandatory information gathering across all models"""
        try:
            mandatory_info_coverage = {}
            
            for model in ["gpt-4o", "claude-3-7-sonnet", "gemini-2.0-flash"]:
                session_id = self.session_ids.get(model)
                if not session_id:
                    continue
                
                # Get conversation history
                response = requests.get(f"{self.backend_url}/ai-bot-chat/history/{session_id}?user_id={self.user_id}", 
                                      timeout=10)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                messages = data.get("messages", [])
                
                # Analyze conversation for mandatory information coverage
                conversation_text = " ".join([msg.get("message_content", "") for msg in messages])
                conversation_lower = conversation_text.lower()
                
                mandatory_topics = {
                    "trading_capital": any(term in conversation_lower for term in 
                                         ["trading capital", "capital", "budget", "usd", "dollar"]),
                    "leverage": any(term in conversation_lower for term in 
                                  ["leverage", "margin", "futures", "spot"]),
                    "risk_limits": any(term in conversation_lower for term in 
                                     ["risk", "drawdown", "stop loss", "risk per trade"]),
                    "timeframe": any(term in conversation_lower for term in 
                                   ["timeframe", "minute", "hour", "day", "scalping", "swing"]),
                    "strategy_intent": any(term in conversation_lower for term in 
                                         ["strategy", "momentum", "scalping", "conservative", "mean reversion"])
                }
                
                coverage_score = sum(mandatory_topics.values()) / len(mandatory_topics)
                mandatory_info_coverage[model] = {
                    "coverage_score": coverage_score,
                    "topics_covered": mandatory_topics,
                    "total_messages": len(messages)
                }
            
            if not mandatory_info_coverage:
                return self.log_test("Mandatory Information Gathering", False, "No conversation data available")
            
            # Calculate overall coverage
            avg_coverage = sum(data["coverage_score"] for data in mandatory_info_coverage.values()) / len(mandatory_info_coverage)
            
            if avg_coverage < 0.8:  # 80% coverage threshold
                return self.log_test("Mandatory Information Gathering", False, 
                                   f"Insufficient mandatory information coverage: {avg_coverage:.1%}")
            
            return self.log_test("Mandatory Information Gathering", True, 
                               f"Excellent mandatory information gathering: {avg_coverage:.1%} average coverage across {len(mandatory_info_coverage)} models",
                               mandatory_info_coverage)
            
        except Exception as e:
            return self.log_test("Mandatory Information Gathering", False, f"Information gathering test failed: {str(e)}")

    def test_production_ready_output(self) -> bool:
        """Test 7: Verify production-ready bot configurations"""
        try:
            # Get user's AI bots to verify production readiness
            response = requests.get(f"{self.backend_url}/ai-bots/user/{self.user_id}", timeout=10)
            
            if response.status_code != 200:
                return self.log_test("Production-Ready Output", False, f"Failed to get user bots: {response.status_code}")
            
            data = response.json()
            bots = data.get("bots", [])
            
            if not bots:
                return self.log_test("Production-Ready Output", False, "No bots found for production readiness test")
            
            # Analyze most recent bot for production readiness
            latest_bot = max(bots, key=lambda x: x.get("created_at", ""))
            bot_config_str = latest_bot.get("bot_config", "{}")
            
            try:
                bot_config = json.loads(bot_config_str)
            except:
                return self.log_test("Production-Ready Output", False, "Invalid bot configuration JSON")
            
            # Check production readiness criteria
            production_criteria = {
                "execution_config_present": "execution_config" in bot_config,
                "kill_switch_conditions": bool(bot_config.get("risk_management", {}).get("kill_switch_conditions")),
                "rate_limit_handling": bot_config.get("execution_config", {}).get("rate_limit_handling", False),
                "secrets_handling": bool(bot_config.get("execution_config", {}).get("secrets_handling")),
                "idempotency": bot_config.get("execution_config", {}).get("idempotency", False),
                "risk_management_complete": len(bot_config.get("risk_management", {})) >= 6,
                "strategy_config_detailed": len(bot_config.get("strategy_config", {})) >= 5
            }
            
            production_score = sum(production_criteria.values()) / len(production_criteria)
            
            if production_score < 0.85:  # 85% production readiness threshold
                return self.log_test("Production-Ready Output", False, 
                                   f"Insufficient production readiness: {production_score:.1%}",
                                   production_criteria)
            
            return self.log_test("Production-Ready Output", True, 
                               f"Excellent production readiness: {production_score:.1%} compliance",
                               {"bot_id": latest_bot.get("id"), "criteria": production_criteria})
            
        except Exception as e:
            return self.log_test("Production-Ready Output", False, f"Production readiness test failed: {str(e)}")

    def test_emergent_universal_key_integration(self) -> bool:
        """Test 8: Verify real AI integration using Emergent Universal Key"""
        try:
            # Test direct AI response generation
            test_prompt = "Generate a professional trading system specification for Bitcoin momentum trading"
            
            # Start a test session to verify real AI integration
            session_id = str(uuid.uuid4())
            start_payload = {
                "user_id": self.user_id,
                "session_id": session_id,
                "ai_model": "gpt-4o",
                "initial_prompt": test_prompt
            }
            
            response = requests.post(f"{self.backend_url}/ai-bot-chat/start-session", 
                                   json=start_payload, timeout=20)
            
            if response.status_code != 200:
                return self.log_test("Emergent Universal Key Integration", False, 
                                   f"AI integration test failed: {response.status_code}")
            
            data = response.json()
            ai_response = data.get("message", "")
            
            # Check for real AI response characteristics
            real_ai_indicators = [
                len(ai_response) > 500,  # Substantial response length
                "trading" in ai_response.lower(),
                "bitcoin" in ai_response.lower() or "btc" in ai_response.lower(),
                any(term in ai_response.lower() for term in ["professional", "institutional", "risk management"]),
                "mandatory" in ai_response.lower() or "question" in ai_response.lower()
            ]
            
            ai_quality_score = sum(real_ai_indicators) / len(real_ai_indicators)
            
            if ai_quality_score < 0.8:
                return self.log_test("Emergent Universal Key Integration", False, 
                                   f"AI response quality insufficient: {ai_quality_score:.1%}")
            
            # Test all three models for integration
            models_tested = []
            for model in ["claude-3-7-sonnet", "gemini-2.0-flash"]:
                test_session = str(uuid.uuid4())
                test_payload = {
                    "user_id": self.user_id,
                    "session_id": test_session,
                    "ai_model": model,
                    "initial_prompt": "Professional trading system design consultation"
                }
                
                model_response = requests.post(f"{self.backend_url}/ai-bot-chat/start-session", 
                                             json=test_payload, timeout=15)
                
                if model_response.status_code == 200:
                    model_data = model_response.json()
                    model_message = model_data.get("message", "")
                    if len(model_message) > 200:
                        models_tested.append(model)
            
            total_models_working = len(models_tested) + 1  # +1 for GPT-4o
            
            return self.log_test("Emergent Universal Key Integration", True, 
                               f"Real AI integration verified: {total_models_working}/3 models working, response quality {ai_quality_score:.1%}",
                               {"models_working": models_tested + ["gpt-4o"], "response_length": len(ai_response)})
            
        except Exception as e:
            return self.log_test("Emergent Universal Key Integration", False, f"AI integration test failed: {str(e)}")

    def run_all_tests(self):
        """Run all professional trading agent tests"""
        print("🚀 PROFESSIONAL TRADING AGENT SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test User ID: {self.user_id}")
        print("=" * 60)
        
        # Run tests in sequence
        tests = [
            self.test_health_check,
            self.test_gpt4o_bitcoin_momentum,
            self.test_claude_ethereum_scalping,
            self.test_gemini_conservative_trading,
            self.test_institutional_bot_creation,
            self.test_mandatory_information_gathering,
            self.test_production_ready_output,
            self.test_emergent_universal_key_integration
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(2)  # Rate limiting between tests
            except Exception as e:
                print(f"❌ {test.__name__} failed with exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 PROFESSIONAL TRADING AGENT TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Professional Trading Agent System is FULLY OPERATIONAL!")
        elif passed >= total * 0.75:
            print("✅ MOSTLY OPERATIONAL - Minor issues detected")
        else:
            print("⚠️  SIGNIFICANT ISSUES - Professional Trading Agent needs attention")
        
        # Detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return passed, total

if __name__ == "__main__":
    tester = ProfessionalTradingAgentTester()
    passed, total = tester.run_all_tests()
    
    if passed < total:
        exit(1)  # Exit with error code if not all tests passed