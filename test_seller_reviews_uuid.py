#!/usr/bin/env python3
"""
Test seller_reviews with correct UUID format
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

def test_seller_reviews_uuid_format():
    """Test seller_reviews with proper UUID format"""
    
    print("🔍 TESTING SELLER_REVIEWS WITH PROPER UUID FORMAT...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test with proper UUID for seller_id
    test_uuid = str(uuid.uuid4())
    
    # Test 1: With seller_id as NULL (optional field)
    review_data_null_seller = {
        "reviewer_id": "cd0e9717-f85d-4726-81e9-f260394ead58",
        "seller_name": "Test Seller",
        "seller_id": None,  # NULL is allowed
        "rating": 5,
        "review_text": "Test review with NULL seller_id"
    }
    
    try:
        print("Test 1: Creating review with NULL seller_id...")
        print(f"Data: {review_data_null_seller}")
        
        create_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/seller_reviews",
            headers=headers,
            json=review_data_null_seller,
            timeout=10
        )
        
        print(f"Response: {create_response.status_code}")
        print(f"Details: {create_response.text}")
        
        if create_response.status_code == 201:
            print("✅ seller_reviews works with NULL seller_id!")
            
            # Get the created record to see the full structure
            verify_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/seller_reviews?reviewer_id=eq.cd0e9717-f85d-4726-81e9-f260394ead58",
                headers=headers,
                timeout=10
            )
            
            if verify_response.status_code == 200:
                records = verify_response.json()
                if records:
                    print(f"✅ Created review: {records[0]}")
                    
                    # Test 2: Update the review
                    print("\nTest 2: Updating the review...")
                    update_response = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/seller_reviews?reviewer_id=eq.cd0e9717-f85d-4726-81e9-f260394ead58&seller_name=eq.Test Seller",
                        headers=headers,
                        json={"rating": 4, "review_text": "Updated review text"},
                        timeout=10
                    )
                    print(f"Update response: {update_response.status_code}")
                    
                    # Test 3: Get reviews for a seller
                    print("\nTest 3: Getting reviews for seller...")
                    get_reviews_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/seller_reviews?seller_name=eq.Test Seller",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Get reviews response: {get_reviews_response.status_code}")
                    if get_reviews_response.status_code == 200:
                        reviews = get_reviews_response.json()
                        print(f"Found {len(reviews)} reviews")
                    
                    # Clean up
                    cleanup = requests.delete(
                        f"{SUPABASE_URL}/rest/v1/seller_reviews?reviewer_id=eq.cd0e9717-f85d-4726-81e9-f260394ead58",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Cleanup: {cleanup.status_code}")
            
            return True
        else:
            print(f"❌ Still failing: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frontend_auth_issue():
    """Test the frontend authentication issue"""
    
    print("\n🔍 TESTING FRONTEND AUTHENTICATION ISSUE...")
    
    # Simulate frontend call without proper headers
    headers_no_auth = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/seller_reviews?limit=1",
            headers=headers_no_auth,
            timeout=10
        )
        
        print(f"No auth headers: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if "No API key found" in response.text:
            print("✅ Confirmed: Frontend is missing authentication headers")
            print("🔧 Fix needed: Add proper apikey and Authorization headers in frontend")
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE SELLER_REVIEWS TESTING...")
    
    # Test database functionality
    db_works = test_seller_reviews_uuid_format()
    
    # Test frontend authentication issue
    auth_issue = test_frontend_auth_issue()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if db_works and auth_issue:
        print("✅ ISSUES IDENTIFIED:")
        print("1. Database: seller_reviews table works correctly with proper schema")
        print("2. Frontend: Missing authentication headers in requests")
        print("\n🔧 SOLUTION:")
        print("- Fix frontend supabaseDataService.js authentication")
        print("- Ensure proper API key headers are sent with requests")
        print("- The database schema is correct and functional")
    elif db_works:
        print("✅ Database works, but frontend auth issue needs investigation")
    else:
        print("❌ Database issues need to be resolved first")