#!/usr/bin/env python3
"""
Test seller_reviews with the correct column names that the frontend expects
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def test_seller_reviews_correct_columns():
    """Test seller_reviews with the columns the frontend expects"""
    
    print("🔍 TESTING SELLER_REVIEWS WITH CORRECT FRONTEND COLUMNS...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Use the exact columns that the frontend code expects
    review_data = {
        "reviewer_id": "cd0e9717-f85d-4726-81e9-f260394ead58",
        "seller_name": "Test Seller",
        "seller_id": "test-seller-123",
        "rating": 5,
        "review_text": "Test review with correct columns"
    }
    
    try:
        print(f"Attempting to create review with data: {review_data}")
        
        create_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/seller_reviews",
            headers=headers,
            json=review_data,
            timeout=10
        )
        
        print(f"Review creation: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        
        if create_response.status_code == 201:
            print("✅ seller_reviews works with correct columns!")
            
            # Get the created record to see the full structure
            verify_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/seller_reviews?reviewer_id=eq.cd0e9717-f85d-4726-81e9-f260394ead58",
                headers=headers,
                timeout=10
            )
            
            if verify_response.status_code == 200:
                records = verify_response.json()
                if records:
                    print(f"✅ Created review columns: {list(records[0].keys())}")
                    
                    # Clean up
                    cleanup = requests.delete(
                        f"{SUPABASE_URL}/rest/v1/seller_reviews?reviewer_id=eq.cd0e9717-f85d-4726-81e9-f260394ead58",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Cleanup: {cleanup.status_code}")
            
            return True
        else:
            print(f"❌ seller_reviews failed with correct columns")
            if "Could not find" in create_response.text:
                missing_column = create_response.text.split("'")[1] if "'" in create_response.text else "unknown"
                print(f"🚨 Missing column: {missing_column}")
                print("📝 Need to check/update database schema")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_seller_reviews_correct_columns()