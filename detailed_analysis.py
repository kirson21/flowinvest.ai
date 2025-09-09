#!/usr/bin/env python3
"""
Detailed Conversation Analysis
Analyze each step of the conversation to understand why bot creation isn't completing
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "https://flowinvest-ai.onrender.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_USER_ID = "621b42ef-1c97-409b-b3d9-18fc83d0e9d8"

def analyze_conversation():
    """Analyze conversation step by step"""
    
    print("🔍 DETAILED CONVERSATION ANALYSIS")
    print("=" * 80)
    
    # Step 1: Start session
    test_prompt = "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"
    
    payload = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": test_prompt
    }
    
    print(f"📝 STEP 1: Initial Request")
    print(f"User: {test_prompt}")
    print()
    
    response = requests.post(f"{API_BASE}/ai-bot-chat/start-session", json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        return
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Failed: {data}")
        return
    
    session_id = data.get('session_id')
    ai_response = data.get('message', '')
    
    print(f"AI Response:")
    print(f"{ai_response}")
    print()
    print("-" * 80)
    print()
    
    # Continue conversation with detailed responses
    conversation_steps = [
        "$10,000 trading capital",
        "2% risk per trade, 3% stop loss, 5% take profit", 
        "Momentum strategy with volume indicators",
        "5 minute timeframe",
        "Call it ETH Futures Volume Pro"
    ]
    
    for i, step_message in enumerate(conversation_steps, 2):
        print(f"📝 STEP {i}: User Response")
        print(f"User: {step_message}")
        print()
        
        payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "message_content": step_message,
            "ai_model": "gpt-4o",
            "bot_creation_stage": f"step_{i}"
        }
        
        response = requests.post(f"{API_BASE}/ai-bot-chat/send-message", json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            break
        
        data = response.json()
        if not data.get('success'):
            print(f"❌ API Error: {data}")
            break
        
        ai_response = data.get('message', '')
        ready_to_create = data.get('ready_to_create', False)
        bot_config = data.get('bot_config')
        
        print(f"AI Response (Ready: {ready_to_create}):")
        print(f"{ai_response}")
        
        if ready_to_create and bot_config:
            print()
            print("🎉 BOT CONFIGURATION READY!")
            print("Bot Config:")
            print(json.dumps(bot_config, indent=2))
            
            # Test ETH detection
            bot_details = bot_config.get('bot_config', {}) if bot_config else {}
            base_coin = bot_details.get('base_coin', 'UNKNOWN')
            
            if base_coin == 'ETH':
                print(f"✅ ETH DETECTION SUCCESS: {base_coin}")
            else:
                print(f"❌ ETH DETECTION FAILED: {base_coin}")
            
            break
        
        print()
        print("-" * 80)
        print()
        
        time.sleep(1)
    
    print("\n🔍 ANALYSIS COMPLETE")

if __name__ == "__main__":
    analyze_conversation()