#!/usr/bin/env python3
"""
Direct EmergentIntegrations Test
Test the EmergentIntegrations library directly to verify it's working
"""

import requests
import json
import uuid

# Configuration
BACKEND_URL = "https://flowinvest-ai.onrender.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_USER_ID = "621b42ef-1c97-409b-b3d9-18fc83d0e9d8"

def test_emergent_integrations():
    """Test EmergentIntegrations by starting a chat session and checking the response quality"""
    
    print("🔍 TESTING EMERGENTINTEGRATIONS DIRECTLY")
    print("=" * 60)
    
    # Test with a simple prompt that should trigger real AI
    test_prompt = "Create a momentum trading bot that follows trends ETH and volume signals, Futures 5x leverage"
    
    payload = {
        "user_id": TEST_USER_ID,
        "ai_model": "gpt-4o",
        "initial_prompt": test_prompt
    }
    
    try:
        print(f"📤 Sending request to: {API_BASE}/ai-bot-chat/start-session")
        print(f"📝 Prompt: {test_prompt}")
        print()
        
        response = requests.post(f"{API_BASE}/ai-bot-chat/start-session", 
                               json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            
            if success:
                ai_response = data.get('message', '')
                session_id = data.get('session_id')
                
                print(f"✅ Session created successfully")
                print(f"📋 Session ID: {session_id}")
                print(f"📏 Response length: {len(ai_response)} characters")
                print()
                print(f"🤖 AI Response:")
                print("-" * 40)
                print(ai_response)
                print("-" * 40)
                print()
                
                # Analyze response quality
                print("🔍 RESPONSE ANALYSIS:")
                
                # Check if it's a fallback response (starts with model prefix)
                is_fallback = ai_response.startswith("🧠 **GPT-4 Trading Expert**")
                print(f"   Is Fallback Response: {is_fallback}")
                
                # Check response length (real AI typically gives longer responses)
                is_substantial = len(ai_response) > 500
                print(f"   Is Substantial (>500 chars): {is_substantial}")
                
                # Check for ETH acknowledgment
                acknowledges_eth = any(word in ai_response.lower() for word in ['eth', 'ethereum'])
                print(f"   Acknowledges ETH: {acknowledges_eth}")
                
                # Check for futures acknowledgment
                acknowledges_futures = 'futures' in ai_response.lower()
                print(f"   Acknowledges Futures: {acknowledges_futures}")
                
                # Check for leverage acknowledgment
                acknowledges_leverage = any(word in ai_response.lower() for word in ['5x', 'leverage'])
                print(f"   Acknowledges Leverage: {acknowledges_leverage}")
                
                # Check for volume acknowledgment
                acknowledges_volume = 'volume' in ai_response.lower()
                print(f"   Acknowledges Volume: {acknowledges_volume}")
                
                print()
                
                # Overall assessment
                if not is_fallback and is_substantial:
                    print("🎉 ASSESSMENT: Real AI integration appears to be working!")
                    print("   Response is substantial and doesn't use fallback format")
                elif is_fallback:
                    print("⚠️  ASSESSMENT: Using fallback logic")
                    print("   Response uses fallback format, EmergentIntegrations may not be active")
                else:
                    print("❓ ASSESSMENT: Unclear - response is short but not fallback format")
                
                return True
            else:
                print(f"❌ Session creation failed: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_emergent_integrations()