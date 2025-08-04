#!/usr/bin/env python3
"""
Direct Supabase Voting and Reviews Test
Focus: Test the actual voting and reviews functionality using direct API calls
"""

import requests
import json
import uuid
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

SUPABASE_URL = os.getenv('REACT_APP_SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('REACT_APP_SUPABASE_ANON_KEY')

class DirectSupabaseTest:
    def __init__(self):
        self.test_results = []
        self.headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        self.test_user_id = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Use super admin ID
        
    def log_test(self, test_name, success, details="", error=""):
        status = "✅" if success else "❌"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_table_structure(self):
        """Test table structure and constraints"""
        print("🔍 TESTING TABLE STRUCTURE...")
        
        # Test user_votes table structure
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/user_votes?select=*&limit=0",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("User Votes Table Structure", True, "Table accessible")
            else:
                self.log_test("User Votes Table Structure", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("User Votes Table Structure", False, "Connection failed", str(e))
        
        # Test seller_reviews table structure
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/seller_reviews?select=*&limit=0",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Seller Reviews Table Structure", True, "Table accessible")
            else:
                self.log_test("Seller Reviews Table Structure", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Seller Reviews Table Structure", False, "Connection failed", str(e))

    def test_user_votes_insert(self):
        """Test user votes insertion with known user ID"""
        print("🔍 TESTING USER VOTES INSERT...")
        
        # Test with super admin user ID (should exist)
        try:
            vote_data = {
                "user_id": self.test_user_id,
                "product_id": f"test-product-{int(time.time())}",
                "vote_type": "upvote"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=self.headers,
                json=vote_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("User Votes INSERT", True, f"Status: {response.status_code}, Vote created")
                
                # Clean up
                if isinstance(data, list) and len(data) > 0:
                    vote_id = data[0].get('id')
                    if vote_id:
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/user_votes?id=eq.{vote_id}",
                            headers=self.headers
                        )
            else:
                error_text = response.text
                self.log_test("User Votes INSERT", False, f"Status: {response.status_code}", error_text[:300])
                
                # Detailed error analysis
                if response.status_code == 404:
                    self.log_test("404 Error Analysis", False, "Table not found or RLS blocking", "Check table existence and RLS policies")
                elif response.status_code == 400:
                    self.log_test("400 Error Analysis", False, "Bad request", f"Data: {json.dumps(vote_data)}")
                elif response.status_code == 409:
                    if "foreign key" in error_text.lower():
                        self.log_test("Foreign Key Error", False, "User ID not found in users table", f"User ID: {self.test_user_id}")
                    else:
                        self.log_test("Conflict Error", False, "Data conflict", error_text[:200])
                        
        except Exception as e:
            self.log_test("User Votes INSERT", False, "Connection failed", str(e))

    def test_seller_reviews_insert(self):
        """Test seller reviews insertion with known user ID"""
        print("🔍 TESTING SELLER REVIEWS INSERT...")
        
        try:
            review_data = {
                "reviewer_id": self.test_user_id,
                "seller_name": "Test Seller",
                "seller_id": None,
                "rating": 5,
                "review_text": "Test review"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=self.headers,
                json=review_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Seller Reviews INSERT", True, f"Status: {response.status_code}, Review created")
                
                # Clean up
                if isinstance(data, list) and len(data) > 0:
                    review_id = data[0].get('id')
                    if review_id:
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/seller_reviews?id=eq.{review_id}",
                            headers=self.headers
                        )
            else:
                error_text = response.text
                self.log_test("Seller Reviews INSERT", False, f"Status: {response.status_code}", error_text[:300])
                
                # Detailed error analysis
                if response.status_code == 400:
                    self.log_test("400 Error Analysis", False, "Bad request", f"Data: {json.dumps(review_data)}")
                elif response.status_code == 409:
                    if "foreign key" in error_text.lower():
                        self.log_test("Foreign Key Error", False, "Reviewer ID not found in users table", f"Reviewer ID: {self.test_user_id}")
                    else:
                        self.log_test("Conflict Error", False, "Data conflict", error_text[:200])
                        
        except Exception as e:
            self.log_test("Seller Reviews INSERT", False, "Connection failed", str(e))

    def test_users_table(self):
        """Test if users table exists and contains our test user"""
        print("🔍 TESTING USERS TABLE...")
        
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/users?select=id&id=eq.{self.test_user_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Users Table - Test User Exists", True, f"User found: {self.test_user_id[:8]}...")
                else:
                    self.log_test("Users Table - Test User Exists", False, "Test user not found in users table", f"User ID: {self.test_user_id}")
            else:
                self.log_test("Users Table Access", False, f"Status: {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("Users Table Access", False, "Connection failed", str(e))

    def test_auth_users_table(self):
        """Test auth.users table (Supabase auth table)"""
        print("🔍 TESTING AUTH.USERS TABLE...")
        
        try:
            # Try to access auth.users table
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/auth.users?select=id&id=eq.{self.test_user_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Auth Users Table - Test User", True, f"User found in auth.users: {self.test_user_id[:8]}...")
                else:
                    self.log_test("Auth Users Table - Test User", False, "Test user not found in auth.users", f"User ID: {self.test_user_id}")
            else:
                self.log_test("Auth Users Table Access", False, f"Status: {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("Auth Users Table Access", False, "Connection failed", str(e))

    def test_rls_policies(self):
        """Test RLS policies by checking what happens with different scenarios"""
        print("🔍 TESTING RLS POLICIES...")
        
        # Test with anonymous headers (no user context)
        anon_headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        try:
            vote_data = {
                "user_id": self.test_user_id,
                "product_id": "test-rls-product",
                "vote_type": "upvote"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=anon_headers,
                json=vote_data,
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                self.log_test("RLS Policy - Anonymous Access", True, f"Correctly blocked anonymous access (Status: {response.status_code})")
            elif response.status_code == 409:
                self.log_test("RLS Policy - Foreign Key Check", True, "RLS allows access but foreign key constraint blocks invalid user")
            else:
                self.log_test("RLS Policy - Anonymous Access", False, f"Should block anonymous access, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("RLS Policy - Anonymous Access", False, "Connection failed", str(e))

    def run_all_tests(self):
        """Run all direct Supabase tests"""
        print("🚀 DIRECT SUPABASE VOTING AND REVIEWS TESTING")
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        self.test_table_structure()
        self.test_users_table()
        self.test_auth_users_table()
        self.test_user_votes_insert()
        self.test_seller_reviews_insert()
        self.test_rls_policies()
        
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("🏁 DIRECT SUPABASE TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        print("FAILED TESTS:")
        for result in self.test_results:
            if not result['success']:
                print(f"❌ {result['test']}: {result['details']}")
                if result['error']:
                    print(f"   Error: {result['error']}")
        
        print()
        print("ROOT CAUSE ANALYSIS:")
        
        # Check for foreign key issues
        foreign_key_issues = [r for r in self.test_results if not r['success'] and 'foreign key' in r['error'].lower()]
        if foreign_key_issues:
            print("🚨 FOREIGN KEY CONSTRAINT ISSUES:")
            print("   - user_votes and seller_reviews tables have foreign key constraints to 'users' table")
            print("   - The test user ID may not exist in the 'users' table")
            print("   - This is the likely cause of 404/400 errors in POST operations")
        
        # Check for RLS issues
        rls_issues = [r for r in self.test_results if not r['success'] and any(code in r['details'] for code in ['401', '403'])]
        if rls_issues:
            print("🚨 RLS POLICY ISSUES:")
            print("   - RLS policies may be blocking INSERT operations")
            print("   - Check if policies allow authenticated users to insert their own data")
        
        print()
        print("RECOMMENDATIONS:")
        print("1. Check if 'users' table exists and contains the required user records")
        print("2. Verify foreign key constraints between user_votes/seller_reviews and users tables")
        print("3. Review RLS policies to ensure they allow INSERT operations for authenticated users")
        print("4. Consider using Supabase auth.users table instead of custom users table")

if __name__ == "__main__":
    tester = DirectSupabaseTest()
    tester.run_all_tests()