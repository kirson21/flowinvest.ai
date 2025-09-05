#!/usr/bin/env python3
"""
Critical Professional Trading Agent Fixes Testing
Tests the specific fixes mentioned in the review request
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def test_critical_fixes():
    """Test the critical fixes for Professional Trading Agent"""
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
    
    print("🔍 TESTING CRITICAL PROFESSIONAL TRADING AGENT FIXES")
    print("=" * 60)
    
    # Test 1: Health Check
    try:
        response = session.get(f"{base_url}/ai-bot-chat/health")
        if response.status_code == 200:
            data = response.json()
            log_result("AI Bot Chat Health Check", True, 
                      f"Status: {data.get('status')}, Models: {data.get('ai_models_available')}")
        else:
            log_result("AI Bot Chat Health Check", False, f"Status: {response.status_code}")
            return results
    except Exception as e:
        log_result("AI Bot Chat Health Check", False, f"Error: {str(e)}")
        return results
    
    # Test 2: User Answer Following - Futures with Leverage 3-5x, Altcoins
    print("\n🎯 TEST: User Answer Following (Futures + Altcoins)")
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
            log_result("Start Session for User Answer Test", True, f"Session: {session_id}")
            
            # Provide specific answers to test user specification following
            answers = [
                "$10,000 capital with 5x leverage",  # Should capture 5x leverage
                "Futures trading",                   # Should capture futures
                "2% max per trade, 10% max drawdown, 2 positions",
                "Momentum strategy for altcoins, 1h timeframe",  # Should capture altcoins
                "Altcoin Futures Pro"               # Bot name
            ]
            
            bot_config = None
            for i, answer in enumerate(answers):
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
                    if result.get("ready_to_create") and result.get("bot_config"):
                        bot_config = result.get("bot_config")
                        break
                    time.sleep(0.5)
                else:
                    log_result(f"Answer {i+1} Processing", False, f"Status: {response.status_code}")
            
            # Verify user specifications are followed
            if bot_config:
                config = bot_config.get("bot_config", {})
                
                # Check leverage (should be 5x, not default 1x)
                leverage = config.get("leverage_allowed", 1.0)
                leverage_correct = leverage == 5.0
                log_result("User Spec: 5x Leverage Followed", leverage_correct, 
                          f"Expected: 5.0, Got: {leverage}")
                
                # Check futures (not spot)
                trade_type = config.get("trade_type", "spot")
                futures_correct = trade_type == "futures"
                log_result("User Spec: Futures Trading Followed", futures_correct,
                          f"Trade Type: {trade_type}")
                
                # Check altcoins (not BTC)
                base_coin = config.get("base_coin", "BTC")
                altcoin_correct = base_coin != "BTC"
                log_result("User Spec: Altcoins Followed (not BTC)", altcoin_correct,
                          f"Base Coin: {base_coin}")
                
                # Test 3: Database Storage - No VARCHAR(100) Errors
                print("\n💾 TEST: Database Storage (No VARCHAR Errors)")
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
                                  f"VARCHAR error detected: {error_text}")
                    else:
                        log_result("Bot Creation - No VARCHAR Errors", False, 
                                  f"Status: {response.status_code}")
            else:
                log_result("Bot Configuration Generated", False, "No bot config generated")
        else:
            log_result("Start Session for User Answer Test", False, f"Status: {response.status_code}")
    
    except Exception as e:
        log_result("User Answer Following Test", False, f"Error: {str(e)}")
    
    # Test 4: Bot Name Integration (Question 5)
    print("\n🏷️  TEST: Bot Name Integration (Question 5)")
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
            
            # Go through 4 questions to reach Question 5 (bot name)
            questions = [
                "$5,000 capital with 2x leverage",
                "Spot trading",
                "1% max per trade, 5% max drawdown",
                "Conservative strategy, 4h timeframe"
            ]
            
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
                    
                    # After 4th answer, should ask for bot name (Question 5)
                    if i == 3:
                        bot_name_asked = any(keyword in ai_response.lower() for keyword in 
                                           ["bot name", "name your", "what would you like to name"])
                        log_result("Question 5: Bot Name Asked", bot_name_asked,
                                  f"Bot name question detected: {bot_name_asked}")
                        
                        if bot_name_asked:
                            # Provide custom bot name
                            name_data = {
                                "user_id": TEST_USER_ID,
                                "session_id": session_id,
                                "message_content": "Conservative ETH Accumulator",
                                "ai_model": "claude-3-7-sonnet",
                                "bot_creation_stage": "clarification"
                            }
                            
                            name_response = session.post(f"{base_url}/ai-bot-chat/send-message", 
                                                       json=name_data)
                            if name_response.status_code == 200:
                                name_result = name_response.json()
                                if name_result.get("ready_to_create") and name_result.get("bot_config"):
                                    bot_config = name_result.get("bot_config")
                                    config = bot_config.get("bot_config", {})
                                    bot_name = config.get("name", "")
                                    
                                    name_captured = "Conservative ETH Accumulator" in bot_name
                                    log_result("Custom Bot Name Captured", name_captured,
                                              f"Bot name: {bot_name}")
                        break
                    time.sleep(0.5)
                else:
                    log_result(f"Question {i+1} Response", False, f"Status: {response.status_code}")
        else:
            log_result("Start Bot Name Test Session", False, f"Status: {response.status_code}")
    
    except Exception as e:
        log_result("Bot Name Integration Test", False, f"Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CRITICAL FIXES TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    # Critical test results
    critical_tests = [
        "User Spec: 5x Leverage Followed",
        "User Spec: Futures Trading Followed", 
        "User Spec: Altcoins Followed (not BTC)",
        "Bot Creation - No VARCHAR Errors",
        "Question 5: Bot Name Asked",
        "Custom Bot Name Captured"
    ]
    
    print("\n🎯 CRITICAL FIXES STATUS:")
    critical_passed = 0
    for test_name in critical_tests:
        result = next((r for r in results if r["test"] == test_name), None)
        if result:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {test_name}")
            if result["success"]:
                critical_passed += 1
    
    if critical_passed >= len(critical_tests) * 0.8:
        print(f"\n🎉 CRITICAL FIXES: OPERATIONAL ({critical_passed}/{len(critical_tests)} passed)")
    else:
        print(f"\n⚠️  CRITICAL FIXES: NEED ATTENTION ({critical_passed}/{len(critical_tests)} passed)")
    
    return results

if __name__ == "__main__":
    test_critical_fixes()