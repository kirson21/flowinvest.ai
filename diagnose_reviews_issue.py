#!/usr/bin/env python3
"""
Test seller_reviews table directly to diagnose the API key issue
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

def test_seller_reviews_directly():
    """Test seller_reviews table with proper authentication"""
    
    print("🔍 TESTING SELLER_REVIEWS TABLE DIRECTLY...")
    print("=" * 50)
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    test_user_id = "cd0e9717-f85d-4726-81e9-f260394ead58"
    test_seller_id = "test-seller-123"
    
    # Test 1: Check if table exists and is accessible
    print("📋 Checking table accessibility...")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/seller_reviews?limit=1",
            headers=headers,
            timeout=10
        )
        
        print(f"Table access: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Table accessible. Records: {len(data)}")
            if data:
                print(f"Sample columns: {list(data[0].keys())}")
        else:
            print(f"❌ Table access failed: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing table: {e}")
        return False
    
    # Test 2: Try to create a test review
    print("\n⭐ Testing review creation...")
    review_data = {
        "user_id": test_user_id,
        "seller_id": test_seller_id,
        "rating": 5,
        "review_text": "Test review for debugging",
        "product_id": "test-product-123"
    }
    
    try:
        create_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/seller_reviews",
            headers=headers,
            json=review_data,
            timeout=10
        )
        
        print(f"Review creation: {create_response.status_code}")
        print(f"Response: {create_response.text[:300]}")
        
        if create_response.status_code == 201:
            print("✅ Review created successfully with proper API key!")
            
            # Clean up the test review
            cleanup_response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/seller_reviews?user_id=eq.{test_user_id}&seller_id=eq.{test_seller_id}",
                headers=headers,
                timeout=10
            )
            print(f"Cleanup: {cleanup_response.status_code}")
            
            return True
        else:
            print(f"❌ Review creation failed: {create_response.status_code}")
            if "No API key found" in create_response.text:
                print("🚨 API KEY ISSUE: The service key is not being accepted!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating review: {e}")
        return False

def test_without_api_key():
    """Test what happens without API key (simulate frontend issue)"""
    
    print("\n🔍 TESTING WITHOUT API KEY (SIMULATING FRONTEND ISSUE)...")
    print("=" * 50)
    
    # Headers without API key (like frontend might be doing)
    headers = {
        'Content-Type': 'application/json'
        # Missing apikey and Authorization headers
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/seller_reviews?limit=1",
            headers=headers,
            timeout=10
        )
        
        print(f"Without API key: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if "No API key found" in response.text:
            print("✅ Confirmed: This is the exact error the user is seeing!")
            print("🔧 Issue: Frontend is not sending API key in requests")
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNOSING SELLER_REVIEWS API KEY ISSUE...")
    
    # Test with proper API key
    direct_works = test_seller_reviews_directly()
    
    # Test without API key to reproduce the issue
    reproduce_issue = test_without_api_key()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if direct_works and reproduce_issue:
        print("✅ ISSUE IDENTIFIED:")
        print("- seller_reviews table works perfectly with proper API key")
        print("- Frontend is missing API key in requests")
        print("- This is a frontend authentication issue, not database schema")
        print("\n🔧 SOLUTION NEEDED:")
        print("- Check frontend code in supabaseDataService.js")
        print("- Ensure API key is being passed in headers")
        print("- Compare with working voting system authentication")
    else:
        print("❌ Issue is more complex, needs further investigation")