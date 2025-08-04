#!/usr/bin/env python3
"""
Simulate frontend authentication issue with seller reviews
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

SUPABASE_URL = os.getenv('REACT_APP_SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('REACT_APP_SUPABASE_ANON_KEY')

def test_frontend_authentication():
    """Test how frontend should authenticate with Supabase"""
    
    print("🔍 TESTING FRONTEND AUTHENTICATION WITH SELLER_REVIEWS...")
    print("=" * 60)
    
    # Test 1: Using anon key (like frontend should do)
    print("Test 1: Using ANON key (frontend approach)...")
    headers_anon = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Just try to read reviews (should work with anon key)
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/seller_reviews?limit=1",
            headers=headers_anon,
            timeout=10
        )
        
        print(f"Anon read access: {response.status_code}")
        if response.status_code == 200:
            print("✅ Anon key works for reading reviews")
        else:
            print(f"❌ Anon key failed: {response.text[:200]}")
        
        # Try to insert (should fail without proper user auth)
        review_data = {
            "reviewer_id": "cd0e9717-f85d-4726-81e9-f260394ead58",
            "seller_name": "Test Seller",
            "seller_id": None,
            "rating": 5,
            "review_text": "Test review with anon key"
        }
        
        insert_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/seller_reviews",
            headers=headers_anon,
            json=review_data,
            timeout=10
        )
        
        print(f"Anon insert attempt: {insert_response.status_code}")
        print(f"Response: {insert_response.text[:300]}")
        
        if insert_response.status_code == 401:
            print("✅ Correctly rejected - anon key cannot insert without user auth")
        elif insert_response.status_code == 201:
            print("⚠️ Unexpected: anon key allowed insert (RLS might be disabled)")
        else:
            print(f"❌ Unexpected error: {insert_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error with anon key: {e}")
    
    # Test 2: Missing authentication entirely (user's error)
    print("\nTest 2: No authentication headers...")
    headers_none = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/seller_reviews?limit=1",
            headers=headers_none,
            timeout=10
        )
        
        print(f"No auth headers: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if "No API key found" in response.text:
            print("✅ This matches the user's error exactly!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_rls_policies():
    """Check if RLS policies are properly configured"""
    
    print("\n🔍 CHECKING RLS POLICIES...")
    print("=" * 40)
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Check if we can read reviews (should be allowed for anon)
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/seller_reviews",
            headers=headers,
            timeout=10
        )
        
        print(f"RLS read test: {response.status_code}")
        if response.status_code == 200:
            print("✅ RLS allows anonymous reading")
        else:
            print(f"❌ RLS blocks anonymous reading: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error checking RLS: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNOSING FRONTEND AUTHENTICATION ISSUE...")
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Anon Key: {SUPABASE_ANON_KEY[:20]}..." if SUPABASE_ANON_KEY else "MISSING")
    
    test_frontend_authentication()
    check_rls_policies()
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS")
    print("=" * 60)
    print("The user's error 'No API key found in request' means:")
    print("1. The frontend is making requests without ANY authentication headers")
    print("2. Not even the anon key is being sent")
    print("3. This suggests a problem with the Supabase client configuration")
    print("4. Or the authentication context is not properly initialized")
    print()
    print("🔧 SOLUTION STEPS:")
    print("1. Check if user is logged in before making review requests")
    print("2. Ensure Supabase client is properly initialized")
    print("3. Debug the actual network requests in browser dev tools")
    print("4. Check if authentication context is working")