#!/usr/bin/env python3
"""
Detailed AI Bot Chat Response Analysis
Analyze the exact AI responses to understand the bot configuration issue
"""

import requests
import json
import uuid
import time
import os

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://ai-flow-invest.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user ID - using existing user from database
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def analyze_ai_responses():
    """Analyze AI responses in detail."""
    session = requests.Session()
    
    print("=" * 80)
    print("DETAILED AI BOT CHAT RESPONSE ANALYSIS")
    print("=" * 80)
    
    # Start session
    comprehensive_request = "Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling"
    
    payload = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": comprehensive_request
    }
    
    response = session.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload)
    data = response.json()
    session_id = data.get('session_id')
    
    print(f"Session ID: {session_id}")
    print()
    
    # Send messages and analyze responses
    messages = [
        "$10,000 trading capital with 5x leverage",
        "2% risk per trade, 3% stop loss, 5% take profit, max 2 positions",
        "ETH Futures Volume Master"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"STEP {i}: Sending message: '{message}'")
        
        payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": message,
            "ai_model": "gpt-4o",
            "bot_creation_stage": f"step_{i}"
        }
        
        response = session.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('message', '')
            ready_to_create = data.get('ready_to_create', False)
            bot_config = data.get('bot_config')
            
            print(f"Ready to Create: {ready_to_create}")
            print(f"Bot Config Available: {bot_config is not None}")
            print(f"Response Length: {len(ai_response)} chars")
            print()
            print("FULL AI RESPONSE:")
            print("-" * 40)
            print(ai_response)
            print("-" * 40)
            print()
            
            # Check for JSON in response
            if '```json' in ai_response:
                print("JSON FOUND IN RESPONSE!")
                json_start = ai_response.find('```json') + 7
                json_end = ai_response.find('```', json_start)
                if json_end != -1:
                    json_str = ai_response[json_start:json_end].strip()
                    print("EXTRACTED JSON:")
                    print(json_str)
                    try:
                        parsed_json = json.loads(json_str)
                        print("JSON PARSING: SUCCESS")
                        print(f"JSON Keys: {list(parsed_json.keys())}")
                        if 'bot_config' in parsed_json:
                            bot_details = parsed_json['bot_config']
                            print(f"Bot Config Keys: {list(bot_details.keys())}")
                            print(f"Base Coin: {bot_details.get('base_coin')}")
                            print(f"Trade Type: {bot_details.get('trade_type')}")
                            print(f"Leverage: {bot_details.get('leverage')}")
                    except Exception as e:
                        print(f"JSON PARSING ERROR: {e}")
                else:
                    print("JSON END MARKER NOT FOUND")
            else:
                print("NO JSON FOUND IN RESPONSE")
            
            print("=" * 80)
            print()
    
    # Final check of chat history
    print("FINAL CHAT HISTORY ANALYSIS:")
    history_response = session.get(f"{API_BASE}/ai-bot-chat/history/{session_id}?user_id={TEST_USER_ID}")
    
    if history_response.status_code == 200:
        history_data = history_response.json()
        messages = history_data.get('messages', [])
        
        print(f"Total Messages: {len(messages)}")
        
        for i, msg in enumerate(messages):
            msg_type = msg.get('message_type')
            content = msg.get('message_content', '')
            print(f"Message {i+1} ({msg_type}): {len(content)} chars")
            
            if msg_type == 'assistant' and ('ready_to_create' in content or '```json' in content):
                print(f"  -> Contains bot config: {'ready_to_create' in content}")
                print(f"  -> Contains JSON: {'```json' in content}")
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    if json_end != -1:
                        json_str = content[json_start:json_end].strip()
                        try:
                            parsed_json = json.loads(json_str)
                            bot_config = parsed_json.get('bot_config', {})
                            print(f"  -> Base Coin: {bot_config.get('base_coin')}")
                            print(f"  -> Trade Type: {bot_config.get('trade_type')}")
                            print(f"  -> Leverage: {bot_config.get('leverage')}")
                        except:
                            print(f"  -> JSON parsing failed")

if __name__ == "__main__":
    analyze_ai_responses()