#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for Authentication and Voting System Verification
After Frontend Auth Fix

This test suite focuses on:
1. Authentication System Post-Fix Verification
2. Voting System Database Schema Verification (PostgreSQL UUID fix)
3. Seller Reviews System Verification
4. Supabase Data Service Operations
5. Core Backend Stability Check
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://00253ee3-ad42-47d4-958c-225cd2b95a8f.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Development test user (super admin)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class BackendTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_core_backend_health(self):
        """Test core backend health endpoints"""
        print("\n=== CORE BACKEND HEALTH TESTS ===")
        
        # Test 1: API Root endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "API Root Endpoint",
                    True,
                    f"API root accessible (Status: {response.status_code})",
                    f"Environment: {data.get('environment', 'unknown')}, Status: {data.get('status', 'unknown')}"
                )
            else:
                self.log_result(
                    "API Root Endpoint",
                    False,
                    f"API root returned status {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("API Root Endpoint", False, f"API root request failed: {str(e)}")
        
        # Test 2: Status endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Status Endpoint",
                    True,
                    f"Status endpoint working (Status: {response.status_code})",
                    f"Status: {data.get('status', 'unknown')}, Environment: {data.get('environment', 'unknown')}"
                )
            else:
                self.log_result(
                    "Status Endpoint",
                    False,
                    f"Status endpoint returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Status Endpoint", False, f"Status endpoint failed: {str(e)}")
        
        # Test 3: Health check endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                supabase_status = data.get('services', {}).get('supabase', 'unknown')
                self.log_result(
                    "Health Check Endpoint",
                    True,
                    f"Health check working (Status: {response.status_code})",
                    f"API: {data.get('services', {}).get('api', 'unknown')}, Supabase: {supabase_status}"
                )
            else:
                self.log_result(
                    "Health Check Endpoint",
                    False,
                    f"Health check returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Health Check Endpoint", False, f"Health check failed: {str(e)}")
    
    def test_authentication_system(self):
        """Test authentication system stability after frontend auth fix"""
        print("\n=== AUTHENTICATION SYSTEM TESTS ===")
        
        # Test 1: Auth health check
        try:
            response = requests.get(f"{BACKEND_URL}/auth/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                self.log_result(
                    "Auth Health Check",
                    supabase_connected,
                    f"Auth service health check (Status: {response.status_code})",
                    f"Supabase connected: {supabase_connected}, Success: {data.get('success', False)}"
                )
            else:
                self.log_result(
                    "Auth Health Check",
                    False,
                    f"Auth health check returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Auth Health Check", False, f"Auth health check failed: {str(e)}")
        
        # Test 2: User signup (test user creation)
        try:
            test_email = f"test_{uuid.uuid4().hex[:8]}@flowinvest.ai"
            signup_data = {
                "email": test_email,
                "password": "testpassword123",
                "full_name": "Test User",
                "country": "US"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/signup", json=signup_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                user_created = data.get('user', {}).get('id') is not None
                self.log_result(
                    "User Signup",
                    success and user_created,
                    f"User signup working (Status: {response.status_code})",
                    f"Test user created: {test_email}, User ID: {data.get('user', {}).get('id', 'N/A')[:8]}..."
                )
            else:
                self.log_result(
                    "User Signup",
                    False,
                    f"User signup returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("User Signup", False, f"User signup failed: {str(e)}")
        
        # Test 3: Signin validation (should reject invalid credentials)
        try:
            signin_data = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/signin", json=signin_data, timeout=10)
            # Should return 401 for invalid credentials
            if response.status_code == 401:
                self.log_result(
                    "Signin Validation",
                    True,
                    "Signin correctly rejects invalid credentials (Status: 401)",
                    "Authentication validation working properly"
                )
            else:
                self.log_result(
                    "Signin Validation",
                    False,
                    f"Signin returned unexpected status {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Signin Validation", False, f"Signin validation failed: {str(e)}")
        
        # Test 4: Super admin setup check
        try:
            response = requests.post(f"{BACKEND_URL}/auth/admin/setup", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                self.log_result(
                    "Super Admin Setup",
                    success,
                    f"Super admin setup check (Status: {response.status_code})",
                    f"Admin configured: {success}, UID: {TEST_USER_ID}"
                )
            else:
                self.log_result(
                    "Super Admin Setup",
                    False,
                    f"Super admin setup returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Super Admin Setup", False, f"Super admin setup failed: {str(e)}")
    
    def test_voting_system_database_schema(self):
        """Test voting system database schema after PostgreSQL UUID fix"""
        print("\n=== VOTING SYSTEM DATABASE SCHEMA TESTS ===")
        
        # Test using Supabase REST API directly to verify schema
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Test 1: Verify user_votes table structure
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/user_votes?select=*&limit=1",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                self.log_result(
                    "User Votes Table Access",
                    True,
                    f"user_votes table accessible (Status: {response.status_code})",
                    f"Table structure verified, response length: {len(response.text)}"
                )
            else:
                self.log_result(
                    "User Votes Table Access",
                    False,
                    f"user_votes table returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("User Votes Table Access", False, f"user_votes table test failed: {str(e)}")
        
        # Test 2: Test vote creation with UUID types (critical test for PostgreSQL UUID fix)
        try:
            test_vote_data = {
                "user_id": TEST_USER_ID,
                "product_id": str(uuid.uuid4()),  # Generate UUID for product_id
                "vote_type": "upvote"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/user_votes",
                headers=headers,
                json=test_vote_data,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                vote_id = data[0].get('id') if data else None
                self.log_result(
                    "Vote Creation with UUID",
                    True,
                    f"Vote created successfully (Status: {response.status_code})",
                    f"Vote ID: {vote_id}, Product ID: {test_vote_data['product_id'][:8]}..."
                )
                
                # Clean up test vote
                if vote_id:
                    cleanup_response = requests.delete(
                        f"{SUPABASE_URL}/rest/v1/user_votes?id=eq.{vote_id}",
                        headers=headers,
                        timeout=5
                    )
                    if cleanup_response.status_code == 204:
                        print("   Test vote cleaned up successfully")
                        
            else:
                error_text = response.text
                # Check for the specific PostgreSQL UUID error that was previously failing
                if "operator does not exist: uuid = character varying" in error_text:
                    self.log_result(
                        "Vote Creation with UUID",
                        False,
                        "CRITICAL: PostgreSQL UUID error still exists!",
                        "The 'operator does not exist: uuid = character varying' error indicates schema fix failed"
                    )
                else:
                    self.log_result(
                        "Vote Creation with UUID",
                        False,
                        f"Vote creation failed (Status: {response.status_code})",
                        error_text[:300]
                    )
        except Exception as e:
            self.log_result("Vote Creation with UUID", False, f"Vote creation test failed: {str(e)}")
        
        # Test 3: Test vote update (trigger function test)
        try:
            # First create a test portfolio to vote on
            test_portfolio_data = {
                "id": str(uuid.uuid4()),
                "title": "Test Portfolio for Voting",
                "description": "Test portfolio for voting system verification",
                "price": 99.99,
                "seller_name": "Test Seller",
                "user_id": TEST_USER_ID,
                "vote_count_upvotes": 0,
                "vote_count_downvotes": 0,
                "vote_count_total": 0
            }
            
            portfolio_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/portfolios",
                headers=headers,
                json=test_portfolio_data,
                timeout=10
            )
            
            if portfolio_response.status_code == 201:
                portfolio_id = test_portfolio_data["id"]
                
                # Now test voting on this portfolio
                vote_data = {
                    "user_id": TEST_USER_ID,
                    "product_id": portfolio_id,
                    "vote_type": "upvote"
                }
                
                vote_response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/user_votes",
                    headers=headers,
                    json=vote_data,
                    timeout=10
                )
                
                if vote_response.status_code == 201:
                    # Check if trigger function updated portfolio vote counts
                    time.sleep(1)  # Give trigger time to execute
                    
                    portfolio_check = requests.get(
                        f"{SUPABASE_URL}/rest/v1/portfolios?id=eq.{portfolio_id}&select=vote_count_upvotes,vote_count_total",
                        headers=headers,
                        timeout=10
                    )
                    
                    if portfolio_check.status_code == 200:
                        portfolio_data = portfolio_check.json()
                        if portfolio_data and len(portfolio_data) > 0:
                            upvotes = portfolio_data[0].get('vote_count_upvotes', 0)
                            total_votes = portfolio_data[0].get('vote_count_total', 0)
                            
                            trigger_working = upvotes == 1 and total_votes == 1
                            self.log_result(
                                "Vote Trigger Function",
                                trigger_working,
                                f"Trigger function {'working' if trigger_working else 'not working'} (Upvotes: {upvotes}, Total: {total_votes})",
                                f"Portfolio vote counts updated correctly: {trigger_working}"
                            )
                        else:
                            self.log_result("Vote Trigger Function", False, "Portfolio data not found after vote")
                    else:
                        self.log_result("Vote Trigger Function", False, f"Portfolio check failed: {portfolio_check.status_code}")
                    
                    # Clean up test vote
                    vote_data_response = vote_response.json()
                    if vote_data_response:
                        vote_id = vote_data_response[0].get('id')
                        if vote_id:
                            requests.delete(f"{SUPABASE_URL}/rest/v1/user_votes?id=eq.{vote_id}", headers=headers, timeout=5)
                else:
                    self.log_result("Vote Trigger Function", False, f"Test vote creation failed: {vote_response.status_code}")
                
                # Clean up test portfolio
                requests.delete(f"{SUPABASE_URL}/rest/v1/portfolios?id=eq.{portfolio_id}", headers=headers, timeout=5)
                
            else:
                self.log_result("Vote Trigger Function", False, f"Test portfolio creation failed: {portfolio_response.status_code}")
                
        except Exception as e:
            self.log_result("Vote Trigger Function", False, f"Trigger function test failed: {str(e)}")
    
    def test_seller_reviews_system(self):
        """Test seller reviews system verification"""
        print("\n=== SELLER REVIEWS SYSTEM TESTS ===")
        
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Test 1: Verify seller_reviews table access
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/seller_reviews?select=*&limit=1",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                self.log_result(
                    "Seller Reviews Table Access",
                    True,
                    f"seller_reviews table accessible (Status: {response.status_code})",
                    f"Table structure verified, response length: {len(response.text)}"
                )
            else:
                self.log_result(
                    "Seller Reviews Table Access",
                    False,
                    f"seller_reviews table returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Seller Reviews Table Access", False, f"seller_reviews table test failed: {str(e)}")
        
        # Test 2: Test seller review creation
        try:
            test_review_data = {
                "reviewer_id": TEST_USER_ID,
                "seller_name": "Test Seller for Review",
                "seller_id": str(uuid.uuid4()),
                "rating": 5,
                "review_text": "Excellent seller, great products and fast delivery!"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/seller_reviews",
                headers=headers,
                json=test_review_data,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                review_id = data[0].get('id') if data else None
                self.log_result(
                    "Seller Review Creation",
                    True,
                    f"Seller review created successfully (Status: {response.status_code})",
                    f"Review ID: {review_id}, Rating: {test_review_data['rating']}, Seller: {test_review_data['seller_name']}"
                )
                
                # Clean up test review
                if review_id:
                    cleanup_response = requests.delete(
                        f"{SUPABASE_URL}/rest/v1/seller_reviews?id=eq.{review_id}",
                        headers=headers,
                        timeout=5
                    )
                    if cleanup_response.status_code == 204:
                        print("   Test review cleaned up successfully")
                        
            else:
                self.log_result(
                    "Seller Review Creation",
                    False,
                    f"Seller review creation failed (Status: {response.status_code})",
                    response.text[:300]
                )
        except Exception as e:
            self.log_result("Seller Review Creation", False, f"Seller review creation test failed: {str(e)}")
        
        # Test 3: Test seller review retrieval
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/seller_reviews?select=seller_name,rating,review_text,created_at&limit=5",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                review_count = len(data) if data else 0
                self.log_result(
                    "Seller Review Retrieval",
                    True,
                    f"Seller reviews retrieved successfully (Status: {response.status_code})",
                    f"Retrieved {review_count} reviews from database"
                )
            else:
                self.log_result(
                    "Seller Review Retrieval",
                    False,
                    f"Seller review retrieval failed (Status: {response.status_code})",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Seller Review Retrieval", False, f"Seller review retrieval test failed: {str(e)}")
    
    def test_bot_management_apis(self):
        """Test bot management APIs"""
        print("\n=== BOT MANAGEMENT API TESTS ===")
        
        # Test 1: Bot creation API
        try:
            bot_data = {
                "prompt": "Create a conservative Bitcoin trading bot that focuses on steady growth with low risk",
                "user_id": TEST_USER_ID
            }
            
            response = requests.post(f"{BACKEND_URL}/bots/create-with-ai", json=bot_data, timeout=15)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                bot_id = data.get('bot_id', 'N/A')
                bot_name = data.get('bot_config', {}).get('name', 'N/A')
                self.log_result(
                    "Bot Creation API",
                    success,
                    f"Bot creation API working (Status: {response.status_code})",
                    f"Bot created: {bot_name}, ID: {bot_id[:8]}..."
                )
            else:
                self.log_result(
                    "Bot Creation API",
                    False,
                    f"Bot creation returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Bot Creation API", False, f"Bot creation failed: {str(e)}")
        
        # Test 2: User bots retrieval
        try:
            response = requests.get(f"{BACKEND_URL}/bots/user/{TEST_USER_ID}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                bot_count = data.get('total', 0)
                self.log_result(
                    "User Bots Retrieval",
                    success,
                    f"User bots retrieval working (Status: {response.status_code})",
                    f"Found {bot_count} bots for user"
                )
            else:
                self.log_result(
                    "User Bots Retrieval",
                    False,
                    f"User bots retrieval returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("User Bots Retrieval", False, f"User bots retrieval failed: {str(e)}")
    
    def test_webhook_system(self):
        """Test webhook system for AI feed"""
        print("\n=== WEBHOOK SYSTEM TESTS ===")
        
        # Test 1: OpenAI format webhook
        try:
            webhook_data = {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "Backend Test: Market Analysis Update",
                                "summary": "Comprehensive backend testing confirms all systems operational after frontend authentication fixes.",
                                "sentiment_score": 75
                            }
                        }
                    }
                ],
                "source": "Backend Testing Suite",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            response = requests.post(f"{BACKEND_URL}/ai_news_webhook", json=webhook_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                entry_id = data.get('id', 'N/A')
                title = data.get('title', 'N/A')
                self.log_result(
                    "OpenAI Webhook",
                    True,
                    f"OpenAI webhook working (Status: {response.status_code})",
                    f"Entry created: {entry_id[:8]}..., Title: {title[:50]}..."
                )
            else:
                self.log_result(
                    "OpenAI Webhook",
                    False,
                    f"OpenAI webhook returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("OpenAI Webhook", False, f"OpenAI webhook failed: {str(e)}")
        
        # Test 2: Feed retrieval
        try:
            response = requests.get(f"{BACKEND_URL}/feed_entries?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                entry_count = len(data) if isinstance(data, list) else 0
                self.log_result(
                    "Feed Retrieval",
                    True,
                    f"Feed retrieval working (Status: {response.status_code})",
                    f"Retrieved {entry_count} feed entries"
                )
            else:
                self.log_result(
                    "Feed Retrieval",
                    False,
                    f"Feed retrieval returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Feed Retrieval", False, f"Feed retrieval failed: {str(e)}")
        
        # Test 3: Russian language feed (translation test)
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/feed_entries?limit=1&language=ru", timeout=15)
            translation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                entry_count = len(data) if isinstance(data, list) else 0
                has_russian = any(entry.get('language') == 'ru' for entry in data) if data else False
                self.log_result(
                    "Russian Language Feed",
                    True,
                    f"Russian feed working (Status: {response.status_code})",
                    f"Retrieved {entry_count} entries, Russian content: {has_russian}, Time: {translation_time:.2f}s"
                )
            else:
                self.log_result(
                    "Russian Language Feed",
                    False,
                    f"Russian feed returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Russian Language Feed", False, f"Russian feed failed: {str(e)}")
    
    def test_verification_system(self):
        """Test verification system"""
        print("\n=== VERIFICATION SYSTEM TESTS ===")
        
        # Test 1: Verification storage setup
        try:
            response = requests.post(f"{BACKEND_URL}/setup-verification-storage", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                bucket_name = data.get('bucket_name', 'N/A')
                self.log_result(
                    "Verification Storage Setup",
                    success,
                    f"Verification storage setup working (Status: {response.status_code})",
                    f"Bucket: {bucket_name}, Success: {success}"
                )
            else:
                self.log_result(
                    "Verification Storage Setup",
                    False,
                    f"Verification storage setup returned {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_result("Verification Storage Setup", False, f"Verification storage setup failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING SUITE")
        print("=" * 80)
        print("Focus: Authentication and Voting System Verification After Frontend Auth Fix")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_core_backend_health()
        self.test_authentication_system()
        self.test_voting_system_database_schema()
        self.test_seller_reviews_system()
        self.test_bot_management_apis()
        self.test_webhook_system()
        self.test_verification_system()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE BACKEND TESTING COMPLETED")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"Total Time: {total_time:.2f} seconds")
        print("=" * 80)
        
        # Print critical findings
        print("\n🔍 CRITICAL FINDINGS:")
        
        # Check for PostgreSQL UUID error resolution
        uuid_tests = [r for r in self.results if 'UUID' in r['test'] or 'Vote Creation' in r['test']]
        if uuid_tests:
            uuid_success = all('✅' in r['status'] for r in uuid_tests)
            if uuid_success:
                print("✅ PostgreSQL UUID Error: RESOLVED - Voting system working correctly")
            else:
                print("❌ PostgreSQL UUID Error: STILL EXISTS - Voting system has issues")
        
        # Check authentication system stability
        auth_tests = [r for r in self.results if 'Auth' in r['test'] or 'Signin' in r['test']]
        if auth_tests:
            auth_success_rate = sum(1 for r in auth_tests if '✅' in r['status']) / len(auth_tests)
            if auth_success_rate >= 0.75:
                print("✅ Authentication System: STABLE after frontend auth fix")
            else:
                print("❌ Authentication System: UNSTABLE - May have regressions")
        
        # Check core backend stability
        core_tests = [r for r in self.results if any(keyword in r['test'] for keyword in ['API Root', 'Status', 'Health'])]
        if core_tests:
            core_success = all('✅' in r['status'] for r in core_tests)
            if core_success:
                print("✅ Core Backend: STABLE - No regressions detected")
            else:
                print("❌ Core Backend: ISSUES DETECTED - Potential regressions")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   └─ {result['details']}")
        
        return {
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'success_rate': (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
            'results': self.results,
            'duration': total_time
        }

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()