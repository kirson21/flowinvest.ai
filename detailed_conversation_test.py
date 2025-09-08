#!/usr/bin/env python3
"""
Detailed Professional Trading Agent Conversation Flow Test
"""

import requests
import json
import uuid
import time

# Configuration
BACKEND_URL = "https://ai-flow-invest.preview.emergentagent.com"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def test_conversation_flow():
    """Test the detailed conversation flow"""
    base_url = f"{BACKEND_URL}/api"
    session = requests.Session()
    
    print("🔍 DETAILED CONVERSATION FLOW TEST")
    print("=" * 60)
    
    # Start session
    session_data = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": "I want to create a trading bot for futures trading with leverage 3-5x, altcoins"
    }
    
    response = session.post(f"{base_url}/ai-bot-chat/start-session", json=session_data)
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.status_code}")
        return
    
    session_result = response.json()
    session_id = session_result.get("session_id")
    initial_message = session_result.get("message", "")
    
    print(f"✅ Session started: {session_id}")
    print(f"📝 Initial AI response:\n{initial_message[:500]}...")
    
    # Test conversation with detailed logging
    answers = [
        "$10,000 capital with 5x leverage",
        "Futures trading with margin",
        "2% max per trade, 10% max drawdown, 2 positions maximum",
        "Momentum strategy for altcoins, 1h timeframe",
        "Altcoin Futures Momentum Pro"
    ]
    
    for i, answer in enumerate(answers):
        print(f"\n--- STEP {i+1} ---")
        print(f"👤 User: {answer}")
        
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
            ready_to_create = result.get("ready_to_create", False)
            bot_config = result.get("bot_config")
            
            print(f"🤖 AI response:\n{ai_response[:300]}...")
            print(f"🔧 Ready to create: {ready_to_create}")
            
            if bot_config:
                print(f"⚙️  Bot config generated!")
                config = bot_config.get("bot_config", {})
                print(f"   Name: {config.get('name')}")
                print(f"   Leverage: {config.get('leverage_allowed')}")
                print(f"   Trade Type: {config.get('trade_type')}")
                print(f"   Base Coin: {config.get('base_coin')}")
                print(f"   Strategy: {config.get('strategy_type')}")
                break
            
            # Check for specific question patterns
            if "bot name" in ai_response.lower() or "name your" in ai_response.lower():
                print("🏷️  Bot name question detected!")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
        
        time.sleep(1)
    
    # Get conversation history
    print(f"\n--- CONVERSATION HISTORY ---")
    history_response = session.get(f"{base_url}/ai-bot-chat/history/{session_id}?user_id={TEST_USER_ID}")
    if history_response.status_code == 200:
        history_data = history_response.json()
        messages = history_data.get("messages", [])
        print(f"📚 Total messages: {len(messages)}")
        
        for i, msg in enumerate(messages):
            msg_type = msg.get("message_type", "unknown")
            content = msg.get("message_content", "")[:100]
            print(f"   {i+1}. {msg_type}: {content}...")
    else:
        print(f"❌ Failed to get history: {history_response.status_code}")

if __name__ == "__main__":
    test_conversation_flow()