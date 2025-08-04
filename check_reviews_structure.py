#!/usr/bin/env python3
"""
Check seller_reviews table structure and frontend authentication
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def check_seller_reviews_structure():
    """Check what columns exist in seller_reviews table"""
    
    print("🔍 CHECKING SELLER_REVIEWS TABLE STRUCTURE...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get table structure by trying to insert minimal data
    try:
        # First, let's see if there are any existing records to understand structure
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/seller_reviews",
            headers=headers,
            timeout=10
        )
        
        print(f"Table query: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Existing records: {len(data)}")
            
            # Try to create a minimal review to see what columns are required
            minimal_review = {
                "user_id": "cd0e9717-f85d-4726-81e9-f260394ead58",
                "seller_id": "test-seller-123",
                "rating": 5,
                "review_text": "Test review"
            }
            
            create_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=headers,
                json=minimal_review,
                timeout=10
            )
            
            print(f"Minimal review creation: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            
            if create_response.status_code == 201:
                print("✅ seller_reviews works with minimal data!")
                
                # Get the created record to see the full structure
                verify_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/seller_reviews?user_id=eq.cd0e9717-f85d-4726-81e9-f260394ead58",
                    headers=headers,
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    records = verify_response.json()
                    if records:
                        print(f"Table columns: {list(records[0].keys())}")
                        
                        # Clean up
                        cleanup = requests.delete(
                            f"{SUPABASE_URL}/rest/v1/seller_reviews?user_id=eq.cd0e9717-f85d-4726-81e9-f260394ead58",
                            headers=headers,
                            timeout=10
                        )
                        print(f"Cleanup: {cleanup.status_code}")
                
                return True
            else:
                print(f"❌ Minimal review failed: {create_response.text}")
                return False
        else:
            print(f"❌ Cannot access table: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_seller_reviews_structure()