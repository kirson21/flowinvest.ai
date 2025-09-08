#!/usr/bin/env python3
"""
Debug AI Bot Chat Conversation Flow
Simple test to debug the conversation step by step
"""

import requests
import json
import uuid
import time
import os

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://ai-flow-invest.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user ID - using proper UUID format
# Test user ID - using existing user from database
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def test_conversation_flow():
    """Test the complete conversation flow step by step."""
    session = requests.Session()
    
    print("=" * 60)
    print("DEBUG: AI BOT CHAT CONVERSATION FLOW")
    print("=" * 60)
    print(f"Test User ID: {TEST_USER_ID}")
    print()
    
    # Step 1: Start session with comprehensive request
    print("STEP 1: Starting chat session with comprehensive request...")
    comprehensive_request = "Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling"
    
    payload = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": comprehensive_request
    }
    
    response = session.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        ai_response = data.get('message', '')
        ready_to_create = data.get('ready_to_create', False)
        
        print(f"Session ID: {session_id}")
        print(f"Ready to Create: {ready_to_create}")
        print(f"AI Response Length: {len(ai_response)} chars")
        print(f"AI Response Preview: {ai_response[:200]}...")
        print()
        
        # Check what the AI acknowledged
        acknowledges_eth = 'eth' in ai_response.lower() or 'ethereum' in ai_response.lower()
        acknowledges_futures = 'futures' in ai_response.lower()
        acknowledges_5x = '5x' in ai_response.lower()
        acknowledges_volume = 'volume' in ai_response.lower()
        
        print(f"Acknowledges ETH: {acknowledges_eth}")
        print(f"Acknowledges Futures: {acknowledges_futures}")
        print(f"Acknowledges 5x Leverage: {acknowledges_5x}")
        print(f"Acknowledges Volume Indicators: {acknowledges_volume}")
        print()
        
        if not session_id:
            print("❌ Failed to get session ID")
            return
            
        # Step 2: Check chat history
        print("STEP 2: Checking chat history...")
        history_response = session.get(f"{API_BASE}/ai-bot-chat/history/{session_id}?user_id={TEST_USER_ID}")
        print(f"History Status Code: {history_response.status_code}")
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            messages = history_data.get('messages', [])
            print(f"Messages in History: {len(messages)}")
            
            for i, msg in enumerate(messages):
                print(f"  Message {i+1}: {msg.get('message_type')} - {len(msg.get('message_content', ''))} chars")
        else:
            print(f"❌ Failed to get chat history: {history_response.text}")
        print()
        
        # Step 3: Send trading capital
        print("STEP 3: Providing trading capital...")
        capital_payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": "$10,000 trading capital with 5x leverage",
            "ai_model": "gpt-4o",
            "bot_creation_stage": "capital_provided"
        }
        
        capital_response = session.post(f"{API_BASE}/ai-bot-chat/send-message", json=capital_payload)
        print(f"Capital Response Status: {capital_response.status_code}")
        
        if capital_response.status_code == 200:
            capital_data = capital_response.json()
            capital_ai_response = capital_data.get('message', '')
            capital_ready = capital_data.get('ready_to_create', False)
            
            print(f"Capital AI Response Length: {len(capital_ai_response)} chars")
            print(f"Capital Ready to Create: {capital_ready}")
            print(f"Capital AI Response Preview: {capital_ai_response[:200]}...")
        else:
            print(f"❌ Failed to send capital: {capital_response.text}")
        print()
        
        # Step 4: Check updated chat history
        print("STEP 4: Checking updated chat history...")
        history_response2 = session.get(f"{API_BASE}/ai-bot-chat/history/{session_id}?user_id={TEST_USER_ID}")
        
        if history_response2.status_code == 200:
            history_data2 = history_response2.json()
            messages2 = history_data2.get('messages', [])
            print(f"Updated Messages in History: {len(messages2)}")
            
            for i, msg in enumerate(messages2):
                print(f"  Message {i+1}: {msg.get('message_type')} - {len(msg.get('message_content', ''))} chars")
        else:
            print(f"❌ Failed to get updated chat history: {history_response2.text}")
        print()
        
        # Step 5: Continue with risk management
        print("STEP 5: Providing risk management...")
        risk_payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": "2% risk per trade, 3% stop loss, 5% take profit, max 2 positions",
            "ai_model": "gpt-4o",
            "bot_creation_stage": "risk_provided"
        }
        
        risk_response = session.post(f"{API_BASE}/ai-bot-chat/send-message", json=risk_payload)
        print(f"Risk Response Status: {risk_response.status_code}")
        
        if risk_response.status_code == 200:
            risk_data = risk_response.json()
            risk_ai_response = risk_data.get('message', '')
            risk_ready = risk_data.get('ready_to_create', False)
            
            print(f"Risk AI Response Length: {len(risk_ai_response)} chars")
            print(f"Risk Ready to Create: {risk_ready}")
            print(f"Risk AI Response Preview: {risk_ai_response[:200]}...")
        else:
            print(f"❌ Failed to send risk: {risk_response.text}")
        print()
        
        # Step 6: Provide bot name
        print("STEP 6: Providing bot name...")
        name_payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": "ETH Futures Volume Master",
            "ai_model": "gpt-4o",
            "bot_creation_stage": "name_provided"
        }
        
        name_response = session.post(f"{API_BASE}/ai-bot-chat/send-message", json=name_payload)
        print(f"Name Response Status: {name_response.status_code}")
        
        if name_response.status_code == 200:
            name_data = name_response.json()
            name_ai_response = name_data.get('message', '')
            name_ready = name_data.get('ready_to_create', False)
            name_bot_config = name_data.get('bot_config')
            
            print(f"Name AI Response Length: {len(name_ai_response)} chars")
            print(f"Name Ready to Create: {name_ready}")
            print(f"Name Bot Config Available: {name_bot_config is not None}")
            print(f"Name AI Response Preview: {name_ai_response[:200]}...")
            
            if name_bot_config:
                print(f"Bot Config Keys: {list(name_bot_config.keys())}")
                bot_details = name_bot_config.get('bot_config', {})
                print(f"Bot Details Keys: {list(bot_details.keys())}")
                print(f"Base Coin: {bot_details.get('base_coin')}")
                print(f"Trade Type: {bot_details.get('trade_type')}")
                print(f"Leverage: {bot_details.get('leverage')}")
        else:
            print(f"❌ Failed to send name: {name_response.text}")
        print()
        
        # Step 7: Final chat history check
        print("STEP 7: Final chat history check...")
        history_response3 = session.get(f"{API_BASE}/ai-bot-chat/history/{session_id}?user_id={TEST_USER_ID}")
        
        if history_response3.status_code == 200:
            history_data3 = history_response3.json()
            messages3 = history_data3.get('messages', [])
            print(f"Final Messages in History: {len(messages3)}")
            
            user_messages = [msg for msg in messages3 if msg.get('message_type') == 'user']
            assistant_messages = [msg for msg in messages3 if msg.get('message_type') == 'assistant']
            
            print(f"User Messages: {len(user_messages)}")
            print(f"Assistant Messages: {len(assistant_messages)}")
            
            # Check for bot configuration in final messages
            bot_config_found = False
            for msg in reversed(messages3):
                if msg.get('message_type') == 'assistant':
                    content = msg.get('message_content', '')
                    if 'ready_to_create' in content and '```json' in content:
                        bot_config_found = True
                        print("✅ Bot configuration found in chat history!")
                        break
            
            if not bot_config_found:
                print("❌ No bot configuration found in chat history")
        else:
            print(f"❌ Failed to get final chat history: {history_response3.text}")
        
    else:
        print(f"❌ Failed to start session: {response.text}")
    
    print("=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_conversation_flow()