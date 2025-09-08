import requests
import json

# Test the specific comprehensive request
comprehensive_request = 'Create a bot that trades Eth, Long and Short, only futures, with 5x leverage. Uses volume indicators to understand when there is active buying or selling'

session_data = {
    'user_id': 'test-debug-user-2',
    'ai_model': 'gpt-4o',
    'initial_prompt': comprehensive_request
}

response = requests.post('https://flowinvest-ai.onrender.com/api/ai-bot-chat/start-session', json=session_data, timeout=30)

if response.status_code == 200:
    data = response.json()
    print('=== FULL AI RESPONSE ===')
    print(data.get('message', ''))
    print('\n=== SESSION DATA ===')
    print(f'Session ID: {data.get("session_id")}')
    print(f'Ready to Create: {data.get("ready_to_create")}')
    print(f'Bot Config: {data.get("bot_config") is not None}')
    
    # Check if response contains bot creation elements
    response_text = data.get('message', '').lower()
    has_json = '```json' in data.get('message', '')
    has_bot_creation = any(phrase in response_text for phrase in ['bot created', 'ready for deployment', 'professional trading bot'])
    
    print(f'Has JSON: {has_json}')
    print(f'Has Bot Creation Elements: {has_bot_creation}')
else:
    print(f'Error: HTTP {response.status_code}')
    print(response.text)