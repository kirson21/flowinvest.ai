#!/usr/bin/env python3
"""
Data Type Fix Test for User Votes
Focus: Test different data type formats for user_votes table
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

SUPABASE_URL = os.getenv('REACT_APP_SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('REACT_APP_SUPABASE_ANON_KEY')

class DataTypeFixTest:
    def __init__(self):
        self.headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        self.test_user_id = "cd0e9717-f85d-4726-81e9-f260394ead58"
        
    def test_user_votes_with_string_cast(self):
        """Test user votes with explicit string casting"""
        print("🔍 TESTING USER VOTES WITH STRING CASTING...")
        
        try:
            # Test with user_id as string (not UUID)
            vote_data = {
                "user_id": str(self.test_user_id),  # Explicit string conversion
                "product_id": f"test-product-{int(time.time())}",
                "vote_type": "upvote"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=self.headers,
                json=vote_data,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print("✅ SUCCESS: User vote created with string casting")
                
                # Clean up
                if isinstance(data, list) and len(data) > 0:
                    vote_id = data[0].get('id')
                    if vote_id:
                        cleanup_response = requests.delete(
                            f"{SUPABASE_URL}/rest/v1/user_votes?id=eq.{vote_id}",
                            headers=self.headers
                        )
                        print(f"Cleanup status: {cleanup_response.status_code}")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    def test_table_schema_info(self):
        """Get table schema information"""
        print("🔍 GETTING TABLE SCHEMA INFO...")
        
        try:
            # Try to get schema info using OPTIONS request
            response = requests.options(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=self.headers,
                timeout=10
            )
            
            print(f"OPTIONS Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            # Try to get a sample record to understand the structure
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/user_votes?select=*&limit=1",
                headers=self.headers,
                timeout=10
            )
            
            print(f"GET Status: {response.status_code}")
            print(f"Sample data: {response.text}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    def test_seller_reviews_comparison(self):
        """Test seller reviews to compare working vs non-working"""
        print("🔍 TESTING SELLER REVIEWS (WORKING COMPARISON)...")
        
        try:
            review_data = {
                "reviewer_id": str(self.test_user_id),  # Same format as user_votes
                "seller_name": "Test Seller",
                "seller_id": None,
                "rating": 5,
                "review_text": "Test review for comparison"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=self.headers,
                json=review_data,
                timeout=10
            )
            
            print(f"Seller Reviews Status: {response.status_code}")
            print(f"Seller Reviews Response: {response.text[:300]}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print("✅ SUCCESS: Seller review created (for comparison)")
                
                # Clean up
                if isinstance(data, list) and len(data) > 0:
                    review_id = data[0].get('id')
                    if review_id:
                        cleanup_response = requests.delete(
                            f"{SUPABASE_URL}/rest/v1/seller_reviews?id=eq.{review_id}",
                            headers=self.headers
                        )
                        print(f"Cleanup status: {cleanup_response.status_code}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    def run_tests(self):
        print("🚀 DATA TYPE FIX TESTING")
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        self.test_table_schema_info()
        print()
        self.test_seller_reviews_comparison()
        print()
        self.test_user_votes_with_string_cast()

if __name__ == "__main__":
    tester = DataTypeFixTest()
    tester.run_tests()