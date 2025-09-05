#!/usr/bin/env python3
"""
Final Professional Trading Agent Testing
Tests the critical fixes and identifies the root cause issues
"""

import requests
import json
import uuid
import time

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def run_final_tests():
    """Run final comprehensive tests"""
    base_url = f"{BACKEND_URL}/api"
    session = requests.Session()
    results = []
    
    def log_result(test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
        results.append({"test": test_name, "success": success, "details": details})
        return success
    
    print("🔍 FINAL PROFESSIONAL TRADING AGENT TESTING")
    print("=" * 60)
    
    # Test 1: Health Check
    try:
        response = session.get(f"{base_url}/ai-bot-chat/health")
        if response.status_code == 200:
            data = response.json()
            log_result("AI Bot Chat Health Check", True, 
                      f"Status: {data.get('status')}, Integration: {data.get('integration_status')}")
        else:
            log_result("AI Bot Chat Health Check", False, f"Status: {response.status_code}")
            return results
    except Exception as e:
        log_result("AI Bot Chat Health Check", False, f"Error: {str(e)}")
        return results
    
    # Test 2: User Answer Following Test
    print("\n🎯 CRITICAL TEST: User Answer Following")
    try:
        # Start session with specific user request
        session_data = {
            "user_id": TEST_USER_ID,
            "ai_model": "gpt-4o",
            "initial_prompt": "Futures trading with leverage 3-5x, altcoins"
        }
        
        response = session.post(f"{base_url}/ai-bot-chat/start-session", json=session_data)
        if response.status_code == 200:
            session_result = response.json()
            session_id = session_result.get("session_id")
            log_result("Start Session", True, f"Session: {session_id}")
            
            # Test specific user answers
            test_answers = [
                ("$10,000 capital with 5x leverage", "Should capture 5x leverage"),
                ("Futures trading", "Should capture futures trading"),
                ("2% max per trade, 10% max drawdown, 2 positions", "Should capture risk parameters"),
                ("Momentum strategy for altcoins, 1h timeframe", "Should capture altcoins and momentum"),
                ("Altcoin Futures Pro", "Should capture bot name")
            ]
            
            bot_config = None
            for i, (answer, expectation) in enumerate(test_answers):
                message_data = {
                    "user_id": TEST_USER_ID,
                    "session_id": session_id,
                    "message_content": answer,
                    "ai_model": "gpt-4o",
                    "bot_creation_stage": "clarification"
                }
                
                response = session.post(f"{base_url}/ai-bot-chat/send-message", json=message_data)
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("message", "")
                    
                    # Check if bot config is ready
                    if result.get("ready_to_create") and result.get("bot_config"):
                        bot_config = result.get("bot_config")
                        log_result(f"Bot Config Generated at Step {i+1}", True, "Configuration ready")
                        break
                    
                    # Check if AI is progressing or repeating questions
                    if i == 0:  # After first answer about capital/leverage
                        asks_instruments = any(word in ai_response.lower() for word in ["instrument", "spot", "futures", "margin"])
                        repeats_capital = any(word in ai_response.lower() for word in ["capital", "trading capital"])
                        
                        if asks_instruments and not repeats_capital:
                            log_result("Context Working - Progresses to Q2", True, "AI asks about instruments")
                        elif repeats_capital:
                            log_result("Context Broken - Repeats Q1", False, "AI repeats capital question")
                        else:
                            log_result("Context Unclear", False, "Unclear progression")
                    
                    log_result(f"Answer {i+1} Processed", True, expectation)
                    time.sleep(0.5)
                else:
                    log_result(f"Answer {i+1} Processing", False, f"Status: {response.status_code}")
            
            # Test user specifications if bot config generated
            if bot_config:
                config = bot_config.get("bot_config", {})
                
                # Test 1: Leverage following
                leverage = config.get("leverage_allowed", 1.0)
                leverage_correct = leverage == 5.0
                log_result("User Spec: 5x Leverage Followed", leverage_correct, 
                          f"Expected: 5.0, Got: {leverage}")
                
                # Test 2: Futures trading
                trade_type = config.get("trade_type", "spot")
                futures_correct = trade_type == "futures"
                log_result("User Spec: Futures Trading Followed", futures_correct,
                          f"Trade Type: {trade_type}")
                
                # Test 3: Altcoins (not BTC)
                base_coin = config.get("base_coin", "BTC")
                altcoin_correct = base_coin != "BTC"
                log_result("User Spec: Altcoins Followed", altcoin_correct,
                          f"Base Coin: {base_coin}")
                
                # Test 3: Database Storage Test
                print("\n💾 CRITICAL TEST: Database Storage")
                creation_data = {
                    "user_id": TEST_USER_ID,
                    "session_id": session_id,
                    "ai_model": "gpt-4o",
                    "bot_config": bot_config,
                    "strategy_config": bot_config.get("strategy_config", {}),
                    "risk_management": bot_config.get("risk_management", {})
                }
                
                response = session.post(f"{base_url}/ai-bot-chat/create-bot", json=creation_data)
                if response.status_code == 200:
                    result = response.json()
                    bot_id = result.get("bot_id")
                    if bot_id:
                        log_result("Bot Creation - No VARCHAR Errors", True, f"Bot ID: {bot_id}")
                        
                        # Verify saved to user_ai_bots table
                        bots_response = session.get(f"{base_url}/ai-bots/user/{TEST_USER_ID}")
                        if bots_response.status_code == 200:
                            bots_data = bots_response.json()
                            bots = bots_data.get("bots", [])
                            bot_found = any(bot.get("id") == bot_id for bot in bots)
                            log_result("Bot Saved to user_ai_bots Table", bot_found,
                                      f"Found in user_ai_bots: {bot_found}")
                        else:
                            log_result("Check user_ai_bots Table", False, 
                                      f"Status: {bots_response.status_code}")
                    else:
                        log_result("Bot Creation - No VARCHAR Errors", False, "No bot ID returned")
                else:
                    error_text = response.text
                    varchar_error = "varchar(100)" in error_text.lower() or "value too long" in error_text.lower()
                    if varchar_error:
                        log_result("Bot Creation - No VARCHAR Errors", False, 
                                  f"VARCHAR error: {error_text}")
                    else:
                        log_result("Bot Creation - No VARCHAR Errors", False, 
                                  f"Status: {response.status_code}")
            else:
                log_result("Bot Configuration Generated", False, "No bot config generated after 5 steps")
        else:
            log_result("Start Session", False, f"Status: {response.status_code}")
    
    except Exception as e:
        log_result("User Answer Following Test", False, f"Error: {str(e)}")
    
    # Test 4: Bot Name Integration Test
    print("\n🏷️  CRITICAL TEST: Bot Name Integration (Question 5)")
    try:
        session_data = {
            "user_id": TEST_USER_ID,
            "ai_model": "claude-3-7-sonnet",
            "initial_prompt": "Create a trading bot"
        }
        
        response = session.post(f"{base_url}/ai-bot-chat/start-session", json=session_data)
        if response.status_code == 200:
            session_result = response.json()
            session_id = session_result.get("session_id")
            
            # Go through 4 questions to reach Question 5
            questions = [
                "$5,000 capital with 2x leverage",
                "Spot trading",
                "1% max per trade, 5% max drawdown",
                "Conservative strategy, 4h timeframe"
            ]
            
            bot_name_asked = False
            for i, answer in enumerate(questions):
                message_data = {
                    "user_id": TEST_USER_ID,
                    "session_id": session_id,
                    "message_content": answer,
                    "ai_model": "claude-3-7-sonnet",
                    "bot_creation_stage": "clarification"
                }
                
                response = session.post(f"{base_url}/ai-bot-chat/send-message", json=message_data)
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("message", "")
                    
                    # After 4th answer, should ask for bot name
                    if i == 3:
                        bot_name_asked = any(keyword in ai_response.lower() for keyword in 
                                           ["bot name", "name your", "what would you like to name"])
                        log_result("Question 5: Bot Name Asked", bot_name_asked,
                                  f"Bot name question detected: {bot_name_asked}")
                        break
                    
                    time.sleep(0.5)
                else:
                    log_result(f"Question {i+1} Response", False, f"Status: {response.status_code}")
            
            if not bot_name_asked:
                log_result("Question 5: Bot Name Asked", False, "Bot name question not detected after 4 answers")
        else:
            log_result("Start Bot Name Test Session", False, f"Status: {response.status_code}")
    
    except Exception as e:
        log_result("Bot Name Integration Test", False, f"Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    # Critical issues identified
    print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
    
    context_broken = any(r["test"] == "Context Broken - Repeats Q1" and r["success"] == False for r in results)
    if context_broken:
        print("❌ CONTEXT ISSUE: AI not maintaining conversation context")
        print("   Root Cause: emergentintegrations creates new session each time")
        print("   Impact: User specifications not followed, questions repeated")
    
    no_bot_config = any(r["test"] == "Bot Configuration Generated" and r["success"] == False for r in results)
    if no_bot_config:
        print("❌ BOT CONFIG ISSUE: Bot configuration not generated")
        print("   Root Cause: Conversation doesn't progress through 5 questions")
        print("   Impact: Cannot test database storage or user specifications")
    
    no_bot_name = any(r["test"] == "Question 5: Bot Name Asked" and r["success"] == False for r in results)
    if no_bot_name:
        print("❌ BOT NAME ISSUE: Question 5 (bot name) not asked")
        print("   Root Cause: Context not maintained, conversation resets")
        print("   Impact: Custom bot names not captured")
    
    # Overall assessment
    critical_tests = [
        "User Spec: 5x Leverage Followed",
        "User Spec: Futures Trading Followed", 
        "User Spec: Altcoins Followed",
        "Bot Creation - No VARCHAR Errors",
        "Question 5: Bot Name Asked"
    ]
    
    critical_passed = sum(1 for test_name in critical_tests 
                         for result in results 
                         if result["test"] == test_name and result["success"])
    
    if critical_passed >= len(critical_tests) * 0.8:
        print(f"\n🎉 PROFESSIONAL TRADING AGENT: OPERATIONAL ({critical_passed}/{len(critical_tests)} critical tests passed)")
    else:
        print(f"\n⚠️  PROFESSIONAL TRADING AGENT: NEEDS MAJOR FIXES ({critical_passed}/{len(critical_tests)} critical tests passed)")
        print("\n🔧 REQUIRED FIXES:")
        print("1. Fix conversation context in emergentintegrations integration")
        print("2. Ensure conversation history is passed to AI model")
        print("3. Maintain session continuity for 5-question flow")
        print("4. Test user specification extraction and following")
    
    return results

if __name__ == "__main__":
    run_final_tests()