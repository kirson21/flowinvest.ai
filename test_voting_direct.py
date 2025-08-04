#!/usr/bin/env python3
"""
Test voting system with existing portfolio
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def test_voting_system():
    """Test voting with existing portfolio"""
    
    print("🔍 TESTING VOTING SYSTEM...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # First, get an existing portfolio
    try:
        portfolio_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/portfolios?limit=1",
            headers=headers,
            timeout=10
        )
        
        print(f"Portfolio query: {portfolio_response.status_code}")
        
        if portfolio_response.status_code == 200:
            portfolios = portfolio_response.json()
            if portfolios:
                portfolio = portfolios[0]
                portfolio_id = portfolio['id']
                print(f"Found portfolio: {portfolio_id}")
                print(f"Portfolio ID type appears to be: {type(portfolio_id)}")
                
                # Try to create a vote
                test_user_id = "cd0e9717-f85d-4726-81e9-f260394ead58"
                
                vote_data = {
                    "user_id": test_user_id,
                    "product_id": portfolio_id,  # Use existing portfolio ID
                    "vote_type": "upvote"
                }
                
                print(f"Attempting to create vote with data: {vote_data}")
                
                vote_response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/user_votes",
                    headers=headers,
                    json=vote_data,
                    timeout=10
                )
                
                print(f"Vote creation: {vote_response.status_code}")
                print(f"Vote response: {vote_response.text}")
                
                if "operator does not exist: uuid = character varying" in vote_response.text:
                    print("🚨 CONFIRMED: PostgreSQL UUID type mismatch error!")
                    print("The user_votes.product_id column is VARCHAR but portfolios.id is UUID")
                elif vote_response.status_code == 201:
                    print("✅ Vote created successfully!")
                else:
                    print(f"❌ Vote creation failed with: {vote_response.status_code}")
                    
            else:
                print("No portfolios found")
        else:
            print(f"Error getting portfolios: {portfolio_response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_voting_system()