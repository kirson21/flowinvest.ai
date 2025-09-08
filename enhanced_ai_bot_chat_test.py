#!/usr/bin/env python3
"""
Enhanced AI Bot Chat System Testing
Testing enhanced context following and comprehensive bot creation
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"
TEST_USER_ID = "test-user-" + str(uuid.uuid4())[:8]

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

def test_health_check():
    """Test AI Bot Chat health check"""
    print_test_header("AI Bot Chat Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/ai-bot-chat/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"AI Models: {data.get('ai_models_available')}")
            print(f"Database: {data.get('database_available')}")
            print(f"Universal Key: {data.get('universal_key_configured')}")
            
            success = (data.get('status') == 'healthy' and 
                      data.get('database_available') and
                      len(data.get('ai_models_available', [])) >= 3)
            
            print_test_result("Health Check", success, f"Status: {data.get('status')}")
            return success
        else:
            print_test_result("Health Check", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Health Check", False, str(e))
        return False

def test_comprehensive_bot_creation_request():
    """Test comprehensive bot creation request with enhanced context following"""
    print_test_header("Enhanced Context Following - Comprehensive Bot Creation")
    
    # The specific comprehensive request from the review
    comprehensive_request = "Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling"
    
    try:
        # Start chat session with comprehensive request
        session_data = {
            "user_id": TEST_USER_ID,
            "ai_model": "gpt-4o",
            "initial_prompt": comprehensive_request
        }
        
        print(f"📝 Sending comprehensive request: {comprehensive_request}")
        
        response = requests.post(f"{BACKEND_URL}/ai-bot-chat/start-session", 
                               json=session_data, timeout=30)
        
        if response.status_code != 200:
            print_test_result("Comprehensive Request", False, f"HTTP {response.status_code}")
            return False, None
            
        data = response.json()
        session_id = data.get('session_id')
        ai_response = data.get('message', '')
        
        print(f"🤖 AI Response Length: {len(ai_response)} characters")
        print(f"🤖 AI Response Preview: {ai_response[:200]}...")
        
        # Check if AI recognizes this as comprehensive
        has_comprehensive_request = True  # We provided comprehensive info
        
        # Analyze response for context following
        response_lower = ai_response.lower()
        
        # Check if AI asks basic questions it shouldn't need to ask
        asks_basic_questions = any(phrase in response_lower for phrase in [
            "what is your trading capital",
            "what leverage do you want",
            "which instruments",
            "what trading approach"
        ])
        
        # Check if AI recognizes the provided information
        recognizes_eth = "eth" in response_lower or "ethereum" in response_lower
        recognizes_futures = "futures" in response_lower
        recognizes_leverage = "5x" in response_lower or "leverage" in response_lower
        recognizes_volume = "volume" in response_lower
        
        context_following_score = sum([
            recognizes_eth,
            recognizes_futures, 
            recognizes_leverage,
            recognizes_volume,
            not asks_basic_questions
        ])
        
        print(f"📊 Context Following Analysis:")
        print(f"   - Recognizes ETH: {recognizes_eth}")
        print(f"   - Recognizes Futures: {recognizes_futures}")
        print(f"   - Recognizes 5x Leverage: {recognizes_leverage}")
        print(f"   - Recognizes Volume Indicators: {recognizes_volume}")
        print(f"   - Avoids Basic Questions: {not asks_basic_questions}")
        print(f"   - Context Score: {context_following_score}/5")
        
        success = context_following_score >= 3
        print_test_result("Enhanced Context Following", success, 
                         f"Context score: {context_following_score}/5")
        
        return success, session_id
        
    except Exception as e:
        print_test_result("Comprehensive Request", False, str(e))
        return False, None

def test_immediate_bot_creation_flow(session_id):
    """Test that comprehensive requests trigger immediate bot creation without basic questions"""
    print_test_header("Immediate Bot Creation Flow")
    
    if not session_id:
        print_test_result("Immediate Bot Creation", False, "No session ID")
        return False, None
    
    try:
        # Send follow-up message to continue conversation
        follow_up_message = "Yes, create the bot with these specifications"
        
        message_data = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": follow_up_message,
            "ai_model": "gpt-4o",
            "bot_creation_stage": "confirmation"
        }
        
        print(f"📝 Sending follow-up: {follow_up_message}")
        
        response = requests.post(f"{BACKEND_URL}/ai-bot-chat/send-message",
                               json=message_data, timeout=30)
        
        if response.status_code != 200:
            print_test_result("Immediate Bot Creation", False, f"HTTP {response.status_code}")
            return False, None
            
        data = response.json()
        ai_response = data.get('message', '')
        ready_to_create = data.get('ready_to_create', False)
        bot_config = data.get('bot_config')
        
        print(f"🤖 AI Response Length: {len(ai_response)} characters")
        print(f"🚀 Ready to Create: {ready_to_create}")
        print(f"⚙️ Bot Config Present: {bot_config is not None}")
        
        # Check if response contains bot creation elements
        response_lower = ai_response.lower()
        has_bot_creation_elements = any(phrase in response_lower for phrase in [
            "bot created",
            "ready for deployment", 
            "professional trading bot",
            "specifications:",
            "```json"
        ])
        
        # Check for JSON structure in response
        has_json_structure = "```json" in ai_response and "```" in ai_response
        
        print(f"📊 Bot Creation Analysis:")
        print(f"   - Ready to Create Flag: {ready_to_create}")
        print(f"   - Has Bot Creation Elements: {has_bot_creation_elements}")
        print(f"   - Has JSON Structure: {has_json_structure}")
        print(f"   - Bot Config Object: {bot_config is not None}")
        
        success = ready_to_create or has_bot_creation_elements or has_json_structure
        print_test_result("Immediate Bot Creation", success,
                         f"Ready: {ready_to_create}, Elements: {has_bot_creation_elements}")
        
        return success, bot_config
        
    except Exception as e:
        print_test_result("Immediate Bot Creation", False, str(e))
        return False, None

def test_improved_json_structure(bot_config):
    """Test that bot configuration includes all professional parameters"""
    print_test_header("Improved JSON Structure Validation")
    
    if not bot_config:
        print_test_result("JSON Structure", False, "No bot config provided")
        return False
    
    try:
        print(f"📋 Bot Config Keys: {list(bot_config.keys())}")
        
        # Check for main bot_config structure
        main_config = bot_config.get('bot_config', {})
        if not main_config:
            print_test_result("JSON Structure", False, "Missing bot_config section")
            return False
            
        print(f"📋 Main Config Keys: {list(main_config.keys())}")
        
        # Required basic fields
        required_basic = ['name', 'description', 'base_coin', 'trade_type', 'leverage']
        basic_score = sum(1 for field in required_basic if field in main_config)
        
        # Check for advanced_settings
        advanced_settings = main_config.get('advanced_settings', {})
        has_advanced_settings = bool(advanced_settings)
        
        if has_advanced_settings:
            print(f"📋 Advanced Settings Keys: {list(advanced_settings.keys())}")
            
            # Professional parameters in advanced_settings
            professional_params = [
                'entry_conditions',
                'exit_conditions', 
                'technical_indicators',
                'risk_management',
                'order_management'
            ]
            
            advanced_score = sum(1 for param in professional_params 
                                if param in advanced_settings)
            
            # Check specific structures
            has_entry_conditions = bool(advanced_settings.get('entry_conditions'))
            has_exit_conditions = bool(advanced_settings.get('exit_conditions'))
            has_technical_indicators = bool(advanced_settings.get('technical_indicators'))
            has_risk_management = bool(advanced_settings.get('risk_management'))
            has_order_management = bool(advanced_settings.get('order_management'))
            
            print(f"📊 Professional Parameters Analysis:")
            print(f"   - Entry Conditions: {has_entry_conditions}")
            print(f"   - Exit Conditions: {has_exit_conditions}")
            print(f"   - Technical Indicators: {has_technical_indicators}")
            print(f"   - Risk Management: {has_risk_management}")
            print(f"   - Order Management: {has_order_management}")
            print(f"   - Advanced Score: {advanced_score}/5")
            
        else:
            advanced_score = 0
            print("⚠️ No advanced_settings found")
        
        # Overall structure score
        total_score = basic_score + advanced_score
        max_score = len(required_basic) + 5  # 5 + 5 = 10
        
        print(f"📊 JSON Structure Analysis:")
        print(f"   - Basic Fields: {basic_score}/{len(required_basic)}")
        print(f"   - Advanced Settings: {has_advanced_settings}")
        print(f"   - Professional Params: {advanced_score}/5")
        print(f"   - Total Score: {total_score}/{max_score}")
        
        # Success if we have basic fields and some advanced settings
        success = basic_score >= 4 and advanced_score >= 3
        
        print_test_result("Improved JSON Structure", success,
                         f"Score: {total_score}/{max_score}")
        
        return success
        
    except Exception as e:
        print_test_result("JSON Structure", False, str(e))
        return False

def test_ready_to_create_detection():
    """Test ready_to_create flag detection in various scenarios"""
    print_test_header("Ready to Create Detection")
    
    try:
        # Test with a different comprehensive request
        comprehensive_request_2 = "Build me a Bitcoin momentum trading bot for futures with 3x leverage, using RSI and MACD indicators, 2% stop loss, 4% take profit"
        
        session_data = {
            "user_id": TEST_USER_ID + "-2",
            "ai_model": "claude-3-7-sonnet",
            "initial_prompt": comprehensive_request_2
        }
        
        print(f"📝 Testing with: {comprehensive_request_2}")
        
        response = requests.post(f"{BACKEND_URL}/ai-bot-chat/start-session",
                               json=session_data, timeout=30)
        
        if response.status_code != 200:
            print_test_result("Ready to Create Detection", False, f"HTTP {response.status_code}")
            return False
            
        data = response.json()
        session_id = data.get('session_id')
        ai_response = data.get('message', '')
        ready_to_create = data.get('ready_to_create', False)
        
        print(f"🤖 Initial Ready to Create: {ready_to_create}")
        
        # Send confirmation message
        confirm_data = {
            "user_id": TEST_USER_ID + "-2",
            "session_id": session_id,
            "message_content": "Perfect, create this bot now",
            "ai_model": "claude-3-7-sonnet"
        }
        
        response2 = requests.post(f"{BACKEND_URL}/ai-bot-chat/send-message",
                                json=confirm_data, timeout=30)
        
        if response2.status_code == 200:
            data2 = response2.json()
            ready_to_create_2 = data2.get('ready_to_create', False)
            ai_response_2 = data2.get('message', '')
            
            print(f"🤖 Follow-up Ready to Create: {ready_to_create_2}")
            
            # Check for ready_to_create indicators in response text
            response_indicates_ready = any(phrase in ai_response_2.lower() for phrase in [
                "ready_to_create",
                "bot created",
                "ready for deployment",
                "professional trading bot created"
            ])
            
            print(f"📊 Ready to Create Analysis:")
            print(f"   - Initial Flag: {ready_to_create}")
            print(f"   - Follow-up Flag: {ready_to_create_2}")
            print(f"   - Response Indicates Ready: {response_indicates_ready}")
            
            success = ready_to_create_2 or response_indicates_ready
            print_test_result("Ready to Create Detection", success,
                             f"Flags: {ready_to_create}/{ready_to_create_2}")
            
            return success
        else:
            print_test_result("Ready to Create Detection", False, "Follow-up failed")
            return False
            
    except Exception as e:
        print_test_result("Ready to Create Detection", False, str(e))
        return False

def test_bot_config_validation():
    """Test complete bot configuration validation"""
    print_test_header("Bot Configuration Validation")
    
    try:
        # Create a complete bot creation flow
        comprehensive_request = "Create a Solana scalping bot for futures with 2x leverage, using volume and momentum indicators, 1.5% stop loss, 3% take profit, name it 'SOL Scalping Master'"
        
        session_data = {
            "user_id": TEST_USER_ID + "-3",
            "ai_model": "gemini-2.0-flash",
            "initial_prompt": comprehensive_request
        }
        
        print(f"📝 Creating complete bot: {comprehensive_request}")
        
        # Start session
        response = requests.post(f"{BACKEND_URL}/ai-bot-chat/start-session",
                               json=session_data, timeout=30)
        
        if response.status_code != 200:
            print_test_result("Bot Config Validation", False, f"HTTP {response.status_code}")
            return False
            
        data = response.json()
        session_id = data.get('session_id')
        
        # Continue conversation to get bot config
        confirm_data = {
            "user_id": TEST_USER_ID + "-3",
            "session_id": session_id,
            "message_content": "Yes, create this bot with all the specifications I provided",
            "ai_model": "gemini-2.0-flash"
        }
        
        response2 = requests.post(f"{BACKEND_URL}/ai-bot-chat/send-message",
                                json=confirm_data, timeout=30)
        
        if response2.status_code != 200:
            print_test_result("Bot Config Validation", False, "Follow-up failed")
            return False
            
        data2 = response2.json()
        bot_config = data2.get('bot_config')
        ai_response = data2.get('message', '')
        
        # Validate complete configuration
        if not bot_config:
            # Try to extract JSON from response
            if "```json" in ai_response:
                try:
                    json_start = ai_response.find("```json") + 7
                    json_end = ai_response.find("```", json_start)
                    if json_end != -1:
                        json_str = ai_response[json_start:json_end].strip()
                        bot_config = json.loads(json_str)
                        print("✅ Extracted bot config from response")
                except Exception as e:
                    print(f"⚠️ JSON extraction failed: {e}")
        
        if bot_config:
            main_config = bot_config.get('bot_config', {})
            
            # Validate specific requirements from the request
            validations = {
                'has_name': bool(main_config.get('name')),
                'correct_coin': main_config.get('base_coin') == 'SOL',
                'correct_trade_type': main_config.get('trade_type') == 'futures',
                'correct_leverage': main_config.get('leverage') == 2.0,
                'has_advanced_settings': bool(main_config.get('advanced_settings')),
                'has_risk_management': bool(main_config.get('advanced_settings', {}).get('risk_management')),
                'has_technical_indicators': bool(main_config.get('advanced_settings', {}).get('technical_indicators'))
            }
            
            print(f"📊 Bot Configuration Validation:")
            for key, value in validations.items():
                print(f"   - {key.replace('_', ' ').title()}: {value}")
            
            validation_score = sum(validations.values())
            max_validations = len(validations)
            
            success = validation_score >= max_validations - 1  # Allow 1 failure
            print_test_result("Bot Config Validation", success,
                             f"Score: {validation_score}/{max_validations}")
            
            return success
        else:
            print_test_result("Bot Config Validation", False, "No bot config generated")
            return False
            
    except Exception as e:
        print_test_result("Bot Config Validation", False, str(e))
        return False

def run_comprehensive_test_suite():
    """Run the complete enhanced AI bot chat test suite"""
    print(f"\n🚀 ENHANCED AI BOT CHAT SYSTEM TESTING")
    print(f"Testing enhanced context following and comprehensive bot creation")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = []
    
    # Test 1: Health Check
    results.append(test_health_check())
    
    # Test 2: Enhanced Context Following
    context_success, session_id = test_comprehensive_bot_creation_request()
    results.append(context_success)
    
    # Test 3: Immediate Bot Creation
    creation_success, bot_config = test_immediate_bot_creation_flow(session_id)
    results.append(creation_success)
    
    # Test 4: JSON Structure Validation
    results.append(test_improved_json_structure(bot_config))
    
    # Test 5: Ready to Create Detection
    results.append(test_ready_to_create_detection())
    
    # Test 6: Complete Bot Config Validation
    results.append(test_bot_config_validation())
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 ENHANCED AI BOT CHAT TESTING SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    test_names = [
        "Health Check",
        "Enhanced Context Following", 
        "Immediate Bot Creation",
        "Improved JSON Structure",
        "Ready to Create Detection",
        "Bot Config Validation"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 OVERALL RESULTS:")
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"🎉 ENHANCED AI BOT CHAT SYSTEM IS FULLY OPERATIONAL")
    elif success_rate >= 60:
        print(f"⚠️ ENHANCED AI BOT CHAT SYSTEM HAS MINOR ISSUES")
    else:
        print(f"❌ ENHANCED AI BOT CHAT SYSTEM HAS CRITICAL ISSUES")
    
    return success_rate >= 80

if __name__ == "__main__":
    run_comprehensive_test_suite()