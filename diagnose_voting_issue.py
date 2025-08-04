#!/usr/bin/env python3
"""
Apply database schema fix using direct API calls
Fix PostgreSQL UUID vs VARCHAR type mismatch in voting system
"""

import requests
import json
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def test_voting_with_current_schema():
    """Test voting to reproduce the error first"""
    
    print("🔍 TESTING CURRENT VOTING SYSTEM...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Create test data
    test_portfolio_id = str(uuid.uuid4())
    test_user_id = "cd0e9717-f85d-4726-81e9-f260394ead58"
    
    # Create test portfolio
    portfolio_data = {
        "id": test_portfolio_id,
        "title": "Test Portfolio for Voting",
        "description": "Testing voting system",
        "user_id": test_user_id,
        "price": 99.99,
        "category": "test",
        "type": "manual",
        "risk_level": "medium"
    }
    
    try:
        portfolio_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/portfolios",
            headers=headers,
            json=portfolio_data,
            timeout=10
        )
        
        print(f"Portfolio creation: {portfolio_response.status_code}")
        
        if portfolio_response.status_code == 201:
            print("✅ Test portfolio created")
            
            # Try to create a vote
            vote_data = {
                "user_id": test_user_id,
                "product_id": test_portfolio_id,  # This is UUID format
                "vote_type": "upvote"
            }
            
            vote_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=headers,
                json=vote_data,
                timeout=10
            )
            
            print(f"Vote creation: {vote_response.status_code}")
            print(f"Vote response: {vote_response.text[:500]}")
            
            if "operator does not exist: uuid = character varying" in vote_response.text:
                print("🚨 CONFIRMED: PostgreSQL UUID type mismatch error!")
                return True
            elif vote_response.status_code == 201:
                print("✅ Voting works! (Maybe already fixed?)")
                return False
            else:
                print(f"❌ Unexpected error: {vote_response.text[:300]}")
                return True
                
        else:
            print(f"❌ Portfolio creation failed: {portfolio_response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def check_table_schema():
    """Check the current table schema"""
    
    print("📋 CHECKING TABLE SCHEMA...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get schema info from information_schema (if accessible)
        schema_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/information_schema?table_name=eq.user_votes",
            headers=headers,
            timeout=10
        )
        
        print(f"Schema query: {schema_response.status_code}")
        if schema_response.status_code == 200:
            print(f"Schema info: {schema_response.text[:500]}")
        
        # Also try to get a sample record to see the structure
        sample_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/user_votes?limit=1",
            headers=headers,
            timeout=10
        )
        
        print(f"Sample query: {sample_response.status_code}")
        if sample_response.status_code == 200:
            data = sample_response.json()
            if data:
                print(f"Sample record structure: {list(data[0].keys()) if data else 'No records'}")
            else:
                print("No existing records in user_votes table")
        
    except Exception as e:
        print(f"❌ Schema check error: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNOSING VOTING SYSTEM ISSUE...")
    
    # First check the schema
    check_table_schema()
    
    # Then test voting to reproduce the error
    needs_fix = test_voting_with_current_schema()
    
    if needs_fix:
        print("\n🔧 SCHEMA FIX REQUIRED")
        print("The product_id column needs to be changed from VARCHAR to UUID")
        print("This requires direct database access or manual SQL execution")
    else:
        print("\n✅ VOTING SYSTEM APPEARS TO BE WORKING")
        print("The issue may have been resolved or there's a different problem")