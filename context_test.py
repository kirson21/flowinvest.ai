#!/usr/bin/env python3
"""
Professional Trading Agent Context Test
Tests if the AI is properly using conversation context
"""

import requests
import json
import uuid
import time

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def test_context_and_fallback():
    """Test context handling and fallback system"""
    base_url = f"{BACKEND_URL}/api"
    session = requests.Session()
    
    print("🔍 PROFESSIONAL TRADING AGENT CONTEXT TEST")
    print("=" * 60)
    
    # Test 1: Check if emergentintegrations is working
    print("🧪 Testing AI Integration...")
    
    session_data = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": "Hello, I want to create a trading bot"
    }
    
    response = session.post(f"{base_url}/ai-bot-chat/start-session", json=session_data)
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.status_code}")
        return
    
    session_result = response.json()
    session_id = session_result.get("session_id")
    initial_message = session_result.get("message", "")
    
    print(f"✅ Session started: {session_id}")
    
    # Check if response indicates fallback mode
    if "fallback" in initial_message.lower():
        print("🔄 Using fallback mode")
    elif len(initial_message) > 1000:
        print("🌐 Using real AI integration (long response)")
    else:
        print("❓ Unknown integration mode")
    
    print(f"📝 Initial response length: {len(initial_message)} characters")
    print(f"📝 Contains 'mandatory': {'mandatory' in initial_message.lower()}")
    print(f"📝 Contains 'capital': {'capital' in initial_message.lower()}")
    print(f"📝 Contains 'leverage': {'leverage' in initial_message.lower()}")
    
    # Test 2: Progressive conversation with context check
    print(f"\n🔄 Testing Progressive Conversation...")
    
    # Send a very specific answer to Question 1
    answer1 = "$50,000 capital with 3x leverage for futures"
    message_data = {
        "user_id": TEST_USER_ID,
        "session_id": session_id,
        "message_content": answer1,
        "ai_model": "gpt-4o",
        "bot_creation_stage": "clarification"
    }
    
    response = session.post(f"{base_url}/ai-bot-chat/send-message", json=message_data)
    if response.status_code == 200:
        result = response.json()
        ai_response = result.get("message", "")
        
        print(f"👤 User: {answer1}")
        print(f"🤖 AI response length: {len(ai_response)} characters")
        
        # Check if AI is asking Question 2 (instruments)
        question_2_keywords = ["instrument", "spot", "futures", "margin", "trading type"]
        has_question_2 = any(keyword in ai_response.lower() for keyword in question_2_keywords)
        print(f"📝 Asks about instruments (Q2): {has_question_2}")
        
        # Check if AI repeats Question 1
        question_1_keywords = ["capital", "leverage", "trading capital"]
        repeats_question_1 = any(keyword in ai_response.lower() for keyword in question_1_keywords)
        print(f"📝 Repeats capital question (Q1): {repeats_question_1}")
        
        if has_question_2 and not repeats_question_1:
            print("✅ Context working - progressed to Question 2")
        elif repeats_question_1:
            print("❌ Context broken - repeating Question 1")
        else:
            print("❓ Unclear progression")
        
        print(f"📝 Response preview: {ai_response[:200]}...")
    else:
        print(f"❌ Failed to send message: {response.status_code}")
    
    # Test 3: Check conversation history
    print(f"\n📚 Checking Conversation History...")
    history_response = session.get(f"{base_url}/ai-bot-chat/history/{session_id}?user_id={TEST_USER_ID}")
    if history_response.status_code == 200:
        history_data = history_response.json()
        messages = history_data.get("messages", [])
        print(f"📊 Total messages in history: {len(messages)}")
        
        # Check if history contains our specific answer
        user_messages = [msg for msg in messages if msg.get("message_type") == "user"]
        has_our_answer = any("$50,000" in msg.get("message_content", "") for msg in user_messages)
        print(f"📝 History contains our answer: {has_our_answer}")
        
        if len(messages) >= 4:  # Initial + user + AI + user
            print("✅ History being saved properly")
        else:
            print("❌ History not being saved properly")
    else:
        print(f"❌ Failed to get history: {history_response.status_code}")
    
    # Test 4: Test with different AI model
    print(f"\n🔄 Testing with Claude model...")
    
    session_data_claude = {
        "user_id": TEST_USER_ID,
        "ai_model": "claude-3-7-sonnet",
        "initial_prompt": "Create a professional trading bot"
    }
    
    response = session.post(f"{base_url}/ai-bot-chat/start-session", json=session_data_claude)
    if response.status_code == 200:
        session_result = response.json()
        claude_message = session_result.get("message", "")
        
        print(f"🎭 Claude response length: {len(claude_message)} characters")
        print(f"📝 Contains professional keywords: {'professional' in claude_message.lower()}")
        print(f"📝 Contains mandatory questions: {'mandatory' in claude_message.lower()}")
        print(f"📝 Response preview: {claude_message[:200]}...")
    else:
        print(f"❌ Failed to start Claude session: {response.status_code}")

if __name__ == "__main__":
    test_context_and_fallback()