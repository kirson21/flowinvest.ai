#!/usr/bin/env python3
"""
Complete Conversation Flow Test
Test the complete conversation flow to verify ETH detection and bot creation
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "https://flowinvest-ai.onrender.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_USER_ID = "621b42ef-1c97-409b-b3d9-18fc83d0e9d8"

def test_complete_flow():
    """Test complete conversation flow"""
    
    print("🔍 TESTING COMPLETE CONVERSATION FLOW")
    print("=" * 60)
    
    # Step 1: Start session
    test_prompt = "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"
    
    payload = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": test_prompt
    }
    
    print(f"📝 Step 1: Starting session with prompt")
    print(f"   Prompt: {test_prompt}")
    
    response = requests.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Session creation failed: {data}")
        return False
    
    session_id = data.get('session_id')
    print(f"✅ Session created: {session_id}")
    print()
    
    # Step 2: Provide trading capital
    print(f"📝 Step 2: Providing trading capital")
    
    payload = {
        "user_id": TEST_USER_ID,
        "session_id": session_id,
        "message_content": "$10,000",
        "ai_model": "gpt-4o",
        "bot_creation_stage": "capital"
    }
    
    response = requests.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Message send failed: {data}")
        return False
    
    print(f"✅ Capital provided")
    print()
    
    # Step 3-6: Continue conversation until bot is ready
    conversation_steps = [
        "2% risk per trade, 3% stop loss, 5% take profit",
        "Momentum strategy with volume indicators",
        "5 minute timeframe for scalping",
        "ETH Futures Volume Pro"
    ]
    
    for i, step_message in enumerate(conversation_steps, 3):
        print(f"📝 Step {i}: {step_message}")
        
        payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": step_message,
            "ai_model": "gpt-4o",
            "bot_creation_stage": f"step_{i}"
        }
        
        response = requests.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Failed to send message: {response.status_code}")
            continue
        
        data = response.json()
        if not data.get('success'):
            print(f"❌ Message send failed: {data}")
            continue
        
        ai_response = data.get('message', '')
        ready_to_create = data.get('ready_to_create', False)
        bot_config = data.get('bot_config')
        
        print(f"   Ready to create: {ready_to_create}")
        
        if ready_to_create and bot_config:
            print(f"✅ Bot configuration ready!")
            
            # Analyze bot config
            bot_details = bot_config.get('bot_config', {}) if bot_config else {}
            base_coin = bot_details.get('base_coin', 'UNKNOWN')
            trade_type = bot_details.get('trade_type', 'UNKNOWN')
            leverage = bot_details.get('leverage', 0)
            bot_name = bot_details.get('name', 'UNKNOWN')
            
            print(f"   Bot Details:")
            print(f"     Name: {bot_name}")
            print(f"     Base Coin: {base_coin}")
            print(f"     Trade Type: {trade_type}")
            print(f"     Leverage: {leverage}x")
            
            # CRITICAL TEST: ETH Detection
            if base_coin == 'ETH':
                print(f"✅ ETH DETECTION WORKING: Bot correctly uses ETH")
            else:
                print(f"❌ ETH DETECTION FAILED: Bot uses {base_coin} instead of ETH")
            
            # Test bot creation
            print(f"📝 Step 7: Creating bot")
            
            creation_payload = {
                "user_id": TEST_USER_ID,
                "session_id": session_id,
                "ai_model": "gpt-4o",
                "bot_config": bot_config,
                "strategy_config": {},
                "risk_management": {}
            }
            
            response = requests.post(f"{API_BASE}/ai-bot-chat/create-bot", json=creation_payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bot_id = data.get('bot_id')
                    print(f"✅ Bot created successfully: {bot_id}")
                    
                    # Verify bot in database
                    response = requests.get(f"{API_BASE}/ai-bots/user/{TEST_USER_ID}", timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            bots = data.get('bots', [])
                            eth_bots = [bot for bot in bots if bot.get('base_coin') == 'ETH']
                            print(f"✅ Verification: Found {len(eth_bots)} ETH bots in database")
                            
                            if eth_bots:
                                print(f"🎉 COMPLETE SUCCESS: ETH bot created and saved!")
                                return True
                            else:
                                print(f"⚠️  Bot created but no ETH bots found in database")
                                return False
                        else:
                            print(f"❌ Failed to verify bot in database")
                            return False
                    else:
                        print(f"❌ Failed to query user bots")
                        return False
                else:
                    print(f"❌ Bot creation failed: {data}")
                    return False
            else:
                print(f"❌ Bot creation request failed: {response.status_code}")
                return False
        
        time.sleep(1)  # Brief pause between steps
    
    print(f"❌ Bot was not ready after all conversation steps")
    return False

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n🎉 OVERALL RESULT: COMPLETE FLOW SUCCESSFUL")
    else:
        print("\n❌ OVERALL RESULT: COMPLETE FLOW FAILED")