#!/usr/bin/env python3
"""
Manual Bot Creation Test
Extract the JSON manually and test bot creation
"""

import requests
import json
import re

# Configuration
BACKEND_URL = "https://flowinvest-ai.onrender.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_USER_ID = "621b42ef-1c97-409b-b3d9-18fc83d0e9d8"

def test_manual_bot_creation():
    """Test manual bot creation with extracted JSON"""
    
    print("🔍 MANUAL BOT CREATION TEST")
    print("=" * 60)
    
    # Start a conversation to get bot config
    test_prompt = "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"
    
    payload = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": test_prompt
    }
    
    response = requests.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.status_code}")
        return
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Session creation failed: {data}")
        return
    
    session_id = data.get('session_id')
    print(f"✅ Session created: {session_id}")
    
    # Continue conversation to get bot config
    conversation_steps = [
        "$10,000 trading capital",
        "2% risk per trade, 3% stop loss, 5% take profit",
        "5 minute timeframe"
    ]
    
    for step_message in conversation_steps:
        payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": step_message,
            "ai_model": "gpt-4o",
            "bot_creation_stage": "step"
        }
        
        response = requests.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Failed to send message: {response.status_code}")
            return
        
        data = response.json()
        if not data.get('success'):
            print(f"❌ Message send failed: {data}")
            return
        
        ai_response = data.get('message', '')
        
        # Check if response contains JSON
        if "```json" in ai_response:
            print(f"✅ Found JSON in response")
            
            # Extract JSON manually
            json_start = ai_response.find("```json") + 7
            json_end = ai_response.find("```", json_start)
            
            if json_end != -1:
                json_str = ai_response[json_start:json_end].strip()
                
                try:
                    bot_config = json.loads(json_str)
                    print(f"✅ JSON parsed successfully")
                    
                    # Check if it has ready_to_create flag
                    if "ready_to_create" in bot_config:
                        print(f"✅ ready_to_create flag found: {bot_config['ready_to_create']}")
                    else:
                        print(f"⚠️  ready_to_create flag not found, adding it")
                        # Wrap the config properly
                        if "base_coin" in bot_config:  # This is just the bot_config part
                            bot_config = {
                                "ready_to_create": True,
                                "bot_config": bot_config
                            }
                        else:
                            bot_config["ready_to_create"] = True
                    
                    # Check ETH detection
                    bot_details = bot_config.get('bot_config', bot_config)
                    base_coin = bot_details.get('base_coin', 'UNKNOWN')
                    trade_type = bot_details.get('trade_type', 'UNKNOWN')
                    leverage = bot_details.get('leverage', 0)
                    
                    print(f"📋 Bot Configuration:")
                    print(f"   Base Coin: {base_coin}")
                    print(f"   Trade Type: {trade_type}")
                    print(f"   Leverage: {leverage}x")
                    
                    if base_coin == 'ETH':
                        print(f"✅ ETH DETECTION SUCCESS")
                    else:
                        print(f"❌ ETH DETECTION FAILED")
                    
                    # Test bot creation
                    print(f"📝 Testing bot creation...")
                    
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
                            
                            # Verify in database
                            response = requests.get(f"{API_BASE}/ai-bots/user/{TEST_USER_ID}", timeout=30)
                            if response.status_code == 200:
                                data = response.json()
                                if data.get('success'):
                                    bots = data.get('bots', [])
                                    eth_bots = [bot for bot in bots if bot.get('base_coin') == 'ETH']
                                    print(f"✅ Database verification: {len(eth_bots)} ETH bots found")
                                    
                                    if eth_bots:
                                        print(f"🎉 COMPLETE SUCCESS: ETH bot created and verified!")
                                        return True
                                    else:
                                        print(f"⚠️  Bot created but no ETH bots in database")
                                else:
                                    print(f"❌ Database query failed: {data}")
                            else:
                                print(f"❌ Database query error: {response.status_code}")
                        else:
                            print(f"❌ Bot creation failed: {data}")
                    else:
                        print(f"❌ Bot creation request failed: {response.status_code}")
                        print(f"Response: {response.text}")
                    
                    return False
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
                    print(f"JSON string: {json_str[:200]}...")
            else:
                print(f"❌ Could not find end of JSON block")
        
    print(f"❌ No JSON found in any response")
    return False

if __name__ == "__main__":
    success = test_manual_bot_creation()
    if success:
        print("\n🎉 MANUAL TEST SUCCESS")
    else:
        print("\n❌ MANUAL TEST FAILED")