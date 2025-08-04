#!/usr/bin/env python3
"""
Supabase Voting and Reviews Testing Suite
Focus: Test POST operations to user_votes and seller_reviews tables
Priority: Identify 404/400 errors, RLS policies, authentication issues
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
SUPABASE_URL = os.getenv('REACT_APP_SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('REACT_APP_SUPABASE_ANON_KEY')

class SupabaseVotingTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = str(uuid.uuid4())
        self.test_email = f"voting_test_{uuid.uuid4().hex[:8]}@flowinvest.ai"
        self.auth_token = None
        self.supabase_headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results with enhanced formatting"""
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

    def test_supabase_connection(self):
        """Test basic Supabase connection"""
        print("🔍 TESTING SUPABASE CONNECTION...")
        
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=self.supabase_headers, timeout=10)
            if response.status_code == 200:
                self.log_test("Supabase Connection", True, f"Status: {response.status_code}")
            else:
                self.log_test("Supabase Connection", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Supabase Connection", False, "Connection failed", str(e))

    def test_user_authentication(self):
        """Test user authentication for voting operations"""
        print("🔍 TESTING USER AUTHENTICATION...")
        
        # Test signup to get a valid user
        try:
            signup_data = {
                "email": self.test_email,
                "password": "TestPassword123!"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/auth/v1/signup",
                headers={
                    'apikey': SUPABASE_ANON_KEY,
                    'Content-Type': 'application/json'
                },
                json=signup_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('user') and data.get('session'):
                    self.test_user_id = data['user']['id']
                    self.auth_token = data['session']['access_token']
                    # Update headers with auth token
                    self.supabase_headers['Authorization'] = f'Bearer {self.auth_token}'
                    self.log_test("User Signup", True, f"User created: {self.test_user_id[:8]}..., Token: {'Present' if self.auth_token else 'Missing'}")
                else:
                    self.log_test("User Signup", False, "Missing user or session data", str(data))
            else:
                self.log_test("User Signup", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("User Signup", False, "Connection failed", str(e))

    def test_table_access_get(self):
        """Test GET access to user_votes and seller_reviews tables"""
        print("🔍 TESTING TABLE ACCESS (GET OPERATIONS)...")
        
        # Test user_votes table GET
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/user_votes?select=*&limit=1",
                headers=self.supabase_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Votes Table GET", True, f"Status: {response.status_code}, Records: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                self.log_test("User Votes Table GET", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("User Votes Table GET", False, "Connection failed", str(e))
        
        # Test seller_reviews table GET
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/seller_reviews?select=*&limit=1",
                headers=self.supabase_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Seller Reviews Table GET", True, f"Status: {response.status_code}, Records: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                self.log_test("Seller Reviews Table GET", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Seller Reviews Table GET", False, "Connection failed", str(e))

    def test_user_votes_post(self):
        """Test POST operations to user_votes table - This is where 404 errors occur"""
        print("🔍 TESTING USER VOTES POST OPERATIONS...")
        
        if not self.auth_token:
            self.log_test("User Votes POST", False, "No auth token available", "Authentication required")
            return
        
        # Test 1: Basic vote insertion
        try:
            vote_data = {
                "user_id": self.test_user_id,
                "product_id": f"test-product-{int(time.time())}",
                "vote_type": "upvote"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=self.supabase_headers,
                json=vote_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("User Votes POST - Basic Insert", True, f"Status: {response.status_code}, Vote created")
                
                # Clean up - delete the test vote
                if isinstance(data, list) and len(data) > 0:
                    vote_id = data[0].get('id')
                    if vote_id:
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/user_votes?id=eq.{vote_id}",
                            headers=self.supabase_headers
                        )
            else:
                self.log_test("User Votes POST - Basic Insert", False, f"Status: {response.status_code}", response.text[:300])
                
                # Additional debugging for 404/400 errors
                if response.status_code == 404:
                    self.log_test("User Votes POST - 404 Analysis", False, "Table not found or RLS blocking access", "Check if user_votes table exists and RLS policies allow INSERT")
                elif response.status_code == 400:
                    self.log_test("User Votes POST - 400 Analysis", False, "Bad request - data format or validation issue", f"Request data: {json.dumps(vote_data)}")
                elif response.status_code == 401:
                    self.log_test("User Votes POST - 401 Analysis", False, "Unauthorized - authentication issue", "Check if auth token is valid and RLS policies allow user access")
                elif response.status_code == 403:
                    self.log_test("User Votes POST - 403 Analysis", False, "Forbidden - RLS policy blocking", "Check RLS policies on user_votes table")
                    
        except Exception as e:
            self.log_test("User Votes POST - Basic Insert", False, "Connection failed", str(e))
        
        # Test 2: Vote with missing fields
        try:
            incomplete_vote_data = {
                "user_id": self.test_user_id,
                "product_id": f"test-product-{int(time.time())}"
                # Missing vote_type
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=self.supabase_headers,
                json=incomplete_vote_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("User Votes POST - Missing Fields", True, "Correctly rejected incomplete data")
            else:
                self.log_test("User Votes POST - Missing Fields", False, f"Expected 400, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("User Votes POST - Missing Fields", False, "Connection failed", str(e))

    def test_seller_reviews_post(self):
        """Test POST operations to seller_reviews table - This is where 400 errors occur"""
        print("🔍 TESTING SELLER REVIEWS POST OPERATIONS...")
        
        if not self.auth_token:
            self.log_test("Seller Reviews POST", False, "No auth token available", "Authentication required")
            return
        
        # Test 1: Basic review insertion
        try:
            review_data = {
                "reviewer_id": self.test_user_id,
                "seller_name": "Test Seller",
                "seller_id": None,
                "rating": 5,
                "review_text": "Great seller, highly recommended!"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=self.supabase_headers,
                json=review_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Seller Reviews POST - Basic Insert", True, f"Status: {response.status_code}, Review created")
                
                # Clean up - delete the test review
                if isinstance(data, list) and len(data) > 0:
                    review_id = data[0].get('id')
                    if review_id:
                        requests.delete(
                            f"{SUPABASE_URL}/rest/v1/seller_reviews?id=eq.{review_id}",
                            headers=self.supabase_headers
                        )
            else:
                self.log_test("Seller Reviews POST - Basic Insert", False, f"Status: {response.status_code}", response.text[:300])
                
                # Additional debugging for 400 errors
                if response.status_code == 400:
                    self.log_test("Seller Reviews POST - 400 Analysis", False, "Bad request - data format or validation issue", f"Request data: {json.dumps(review_data)}")
                elif response.status_code == 404:
                    self.log_test("Seller Reviews POST - 404 Analysis", False, "Table not found or RLS blocking access", "Check if seller_reviews table exists and RLS policies allow INSERT")
                elif response.status_code == 401:
                    self.log_test("Seller Reviews POST - 401 Analysis", False, "Unauthorized - authentication issue", "Check if auth token is valid")
                elif response.status_code == 403:
                    self.log_test("Seller Reviews POST - 403 Analysis", False, "Forbidden - RLS policy blocking", "Check RLS policies on seller_reviews table")
                    
        except Exception as e:
            self.log_test("Seller Reviews POST - Basic Insert", False, "Connection failed", str(e))
        
        # Test 2: Review with invalid rating
        try:
            invalid_review_data = {
                "reviewer_id": self.test_user_id,
                "seller_name": "Test Seller",
                "rating": 10,  # Invalid rating (should be 1-5)
                "review_text": "Test review"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=self.supabase_headers,
                json=invalid_review_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Seller Reviews POST - Invalid Rating", True, "Correctly rejected invalid rating")
            else:
                self.log_test("Seller Reviews POST - Invalid Rating", False, f"Expected 400, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("Seller Reviews POST - Invalid Rating", False, "Connection failed", str(e))

    def test_rls_policies(self):
        """Test RLS policies by attempting operations without proper authentication"""
        print("🔍 TESTING RLS POLICIES...")
        
        # Test with anonymous access (no auth token)
        anonymous_headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Test anonymous vote insertion (should fail)
        try:
            vote_data = {
                "user_id": str(uuid.uuid4()),
                "product_id": "test-product-anonymous",
                "vote_type": "upvote"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=anonymous_headers,
                json=vote_data,
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                self.log_test("RLS Policy - Anonymous Vote", True, f"Correctly blocked anonymous vote (Status: {response.status_code})")
            else:
                self.log_test("RLS Policy - Anonymous Vote", False, f"Should block anonymous votes, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("RLS Policy - Anonymous Vote", False, "Connection failed", str(e))
        
        # Test anonymous review insertion (should fail)
        try:
            review_data = {
                "reviewer_id": str(uuid.uuid4()),
                "seller_name": "Test Seller",
                "rating": 5,
                "review_text": "Anonymous review"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=anonymous_headers,
                json=review_data,
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                self.log_test("RLS Policy - Anonymous Review", True, f"Correctly blocked anonymous review (Status: {response.status_code})")
            else:
                self.log_test("RLS Policy - Anonymous Review", False, f"Should block anonymous reviews, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("RLS Policy - Anonymous Review", False, "Connection failed", str(e))

    def test_data_format_validation(self):
        """Test various data format scenarios"""
        print("🔍 TESTING DATA FORMAT VALIDATION...")
        
        if not self.auth_token:
            self.log_test("Data Format Validation", False, "No auth token available", "Authentication required")
            return
        
        # Test vote with wrong data types
        try:
            invalid_vote_data = {
                "user_id": 12345,  # Should be string UUID
                "product_id": None,  # Should be string
                "vote_type": "invalid_vote"  # Should be 'upvote' or 'downvote'
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=self.supabase_headers,
                json=invalid_vote_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Data Format - Invalid Vote Types", True, "Correctly rejected invalid data types")
            else:
                self.log_test("Data Format - Invalid Vote Types", False, f"Expected 400, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("Data Format - Invalid Vote Types", False, "Connection failed", str(e))
        
        # Test review with wrong data types
        try:
            invalid_review_data = {
                "reviewer_id": "not-a-uuid",
                "seller_name": 12345,  # Should be string
                "rating": "five",  # Should be integer
                "review_text": None
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=self.supabase_headers,
                json=invalid_review_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Data Format - Invalid Review Types", True, "Correctly rejected invalid data types")
            else:
                self.log_test("Data Format - Invalid Review Types", False, f"Expected 400, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("Data Format - Invalid Review Types", False, "Connection failed", str(e))

    def test_postgrest_schema_cache(self):
        """Test if PostgREST schema cache is causing issues"""
        print("🔍 TESTING POSTGREST SCHEMA CACHE...")
        
        # Test schema introspection
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/",
                headers=self.supabase_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                schema_info = response.json()
                self.log_test("PostgREST Schema Cache", True, f"Schema accessible, definitions: {len(schema_info.get('definitions', {}))}")
            else:
                self.log_test("PostgREST Schema Cache", False, f"Status: {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("PostgREST Schema Cache", False, "Connection failed", str(e))
        
        # Test specific table schema
        try:
            response = requests.options(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=self.supabase_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("User Votes Table Schema", True, f"Table schema accessible")
            else:
                self.log_test("User Votes Table Schema", False, f"Status: {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("User Votes Table Schema", False, "Connection failed", str(e))

    def run_all_tests(self):
        """Run all Supabase voting and reviews tests"""
        print("🚀 SUPABASE VOTING AND REVIEWS TESTING")
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"Test User: {self.test_email}")
        print("=" * 80)
        
        # Run test suites in order
        self.test_supabase_connection()
        self.test_user_authentication()
        self.test_table_access_get()
        self.test_user_votes_post()
        self.test_seller_reviews_post()
        self.test_rls_policies()
        self.test_data_format_validation()
        self.test_postgrest_schema_cache()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("🏁 SUPABASE VOTING AND REVIEWS TESTING SUMMARY")
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
        
        # Analyze specific issues
        print("CRITICAL ISSUES FOUND:")
        critical_issues = []
        
        for result in self.test_results:
            if not result['success']:
                test_name = result['test']
                if 'POST' in test_name and ('404' in result['details'] or '400' in result['details']):
                    critical_issues.append(f"❌ {test_name}: {result['details']}")
                elif 'RLS' in test_name:
                    critical_issues.append(f"⚠️ {test_name}: {result['details']}")
        
        if critical_issues:
            for issue in critical_issues:
                print(issue)
        else:
            print("🎉 No critical issues found!")
        
        print()
        print("DETAILED ANALYSIS:")
        
        # Check for specific error patterns
        has_404_errors = any('404' in r['details'] for r in self.test_results if not r['success'])
        has_400_errors = any('400' in r['details'] for r in self.test_results if not r['success'])
        has_auth_issues = any('401' in r['details'] or '403' in r['details'] for r in self.test_results if not r['success'])
        
        if has_404_errors:
            print("🚨 404 ERRORS DETECTED: Tables may not exist or RLS policies are blocking access")
        if has_400_errors:
            print("🚨 400 ERRORS DETECTED: Data format issues or validation problems")
        if has_auth_issues:
            print("🚨 AUTHENTICATION ISSUES: RLS policies or token problems")
        
        # Recommendations
        print()
        print("RECOMMENDATIONS:")
        if has_404_errors:
            print("1. Verify user_votes and seller_reviews tables exist in Supabase")
            print("2. Check RLS policies allow INSERT operations for authenticated users")
        if has_400_errors:
            print("3. Verify table schema matches expected data format")
            print("4. Check for required fields and data type constraints")
        if has_auth_issues:
            print("5. Review RLS policies for proper user authentication checks")
            print("6. Ensure auth tokens are properly formatted and valid")
        
        print()
        print("NEXT STEPS:")
        print("1. Check Supabase dashboard for table structure and RLS policies")
        print("2. Test with Supabase client directly to isolate issues")
        print("3. Review PostgREST logs for detailed error information")
        print("4. Verify authentication flow in frontend application")

if __name__ == "__main__":
    tester = SupabaseVotingTester()
    tester.run_all_tests()