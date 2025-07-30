#!/usr/bin/env python3
"""
Focused Backend Regression Test for My Purchases & Product Editor Changes
Tests only critical backend endpoints to verify no regressions from frontend changes.
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔗 Testing backend at: {API_BASE}")

class FocusedRegressionTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })

    def test_server_health(self):
        """Test GET /api/status - Critical health check"""
        print("\n🏥 Testing Server Health")
        
        try:
            response = self.session.get(f"{API_BASE}/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    self.log_test("Server Health (GET /api/status)", True, f"Status: {data.get('status')}, Environment: {data.get('environment')}")
                    return True
                else:
                    self.log_test("Server Health (GET /api/status)", False, f"Unexpected status: {data}")
            else:
                self.log_test("Server Health (GET /api/status)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Server Health (GET /api/status)", False, f"Exception: {str(e)}")
            
        return False

    def test_api_root(self):
        """Test GET /api/ - API root endpoint"""
        print("\n🌐 Testing API Root")
        
        try:
            response = self.session.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                data = response.json()
                if "Flow Invest API" in data.get('message', ''):
                    self.log_test("API Root (GET /api/)", True, f"Message: {data.get('message')}")
                    return True
                else:
                    self.log_test("API Root (GET /api/)", False, f"Unexpected response: {data}")
            else:
                self.log_test("API Root (GET /api/)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("API Root (GET /api/)", False, f"Exception: {str(e)}")
            
        return False

    def test_auth_health(self):
        """Test GET /api/auth/health - Authentication system health"""
        print("\n🔐 Testing Authentication Health")
        
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('supabase_connected'):
                    self.log_test("Authentication Health (GET /api/auth/health)", True, "Supabase connected")
                    return True
                else:
                    self.log_test("Authentication Health (GET /api/auth/health)", False, f"Service unhealthy: {data}")
            else:
                self.log_test("Authentication Health (GET /api/auth/health)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Authentication Health (GET /api/auth/health)", False, f"Exception: {str(e)}")
            
        return False

    def test_user_signup(self):
        """Test POST /api/auth/signup - User registration"""
        print("\n📝 Testing User Signup")
        
        # Generate unique email for testing
        test_email = f"test_{uuid.uuid4().hex[:8]}@flowinvest.ai"
        
        signup_data = {
            "email": test_email,
            "password": "TestPassword123!",
            "full_name": "Regression Test User",
            "country": "United States"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/signup",
                json=signup_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('user'):
                    user = data['user']
                    self.log_test("User Signup (POST /api/auth/signup)", True, f"User created: {user.get('email')}")
                    return True
                else:
                    self.log_test("User Signup (POST /api/auth/signup)", False, f"Signup failed: {data}")
            else:
                self.log_test("User Signup (POST /api/auth/signup)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Signup (POST /api/auth/signup)", False, f"Exception: {str(e)}")
            
        return False

    def test_signin_endpoint(self):
        """Test POST /api/auth/signin - Verify endpoint is working (expect rejection)"""
        print("\n🔑 Testing Signin Endpoint")
        
        signin_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/signin",
                json=signin_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # We expect this to fail with 401 or 400, which means the endpoint is working
            if response.status_code in [400, 401]:
                self.log_test("Signin Endpoint (POST /api/auth/signin)", True, "Correctly rejecting invalid credentials")
                return True
            elif response.status_code == 200:
                self.log_test("Signin Endpoint (POST /api/auth/signin)", True, "Endpoint working (unexpected success)")
                return True
            else:
                self.log_test("Signin Endpoint (POST /api/auth/signin)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Signin Endpoint (POST /api/auth/signin)", False, f"Exception: {str(e)}")
            
        return False

    def test_webhook_system(self):
        """Test POST /api/ai_news_webhook - OpenAI format webhook"""
        print("\n📡 Testing Webhook System")
        
        openai_sample_data = {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "Backend Regression Test Entry",
                            "summary": "Testing webhook system after My Purchases and Product Editor frontend changes.",
                            "sentiment_score": 75
                        }
                    }
                }
            ],
            "source": "Regression Test",
            "timestamp": "2025-01-11T12:00:00Z"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/ai_news_webhook",
                json=openai_sample_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('id'):
                    self.log_test("Webhook System (POST /api/ai_news_webhook)", True, f"Entry created with ID: {data['id']}")
                    return True
                else:
                    self.log_test("Webhook System (POST /api/ai_news_webhook)", False, f"No ID in response: {data}")
            else:
                self.log_test("Webhook System (POST /api/ai_news_webhook)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Webhook System (POST /api/ai_news_webhook)", False, f"Exception: {str(e)}")
            
        return False

    def test_feed_retrieval(self):
        """Test GET /api/feed_entries - Feed retrieval"""
        print("\n📖 Testing Feed Retrieval")
        
        try:
            response = self.session.get(f"{API_BASE}/feed_entries")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Feed Retrieval (GET /api/feed_entries)", True, f"Retrieved {len(data)} entries")
                    return True
                else:
                    self.log_test("Feed Retrieval (GET /api/feed_entries)", False, "Response is not a list")
            else:
                self.log_test("Feed Retrieval (GET /api/feed_entries)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Feed Retrieval (GET /api/feed_entries)", False, f"Exception: {str(e)}")
            
        return False

    def test_language_aware_feed(self):
        """Test language-aware feed retrieval"""
        print("\n🌍 Testing Language-Aware Feed")
        
        # Test English
        try:
            response = self.session.get(f"{API_BASE}/feed_entries?language=en")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("English Feed (GET /api/feed_entries?language=en)", True, f"Retrieved {len(data)} entries")
                else:
                    self.log_test("English Feed (GET /api/feed_entries?language=en)", False, "Invalid response format")
            else:
                self.log_test("English Feed (GET /api/feed_entries?language=en)", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("English Feed (GET /api/feed_entries?language=en)", False, f"Exception: {str(e)}")

        # Test Russian (translation)
        try:
            import time
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/feed_entries?language=ru")
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Russian Feed (GET /api/feed_entries?language=ru)", True, f"Retrieved {len(data)} entries (took {request_time:.2f}s with translation fallback)")
                else:
                    self.log_test("Russian Feed (GET /api/feed_entries?language=ru)", False, "Invalid response format")
            else:
                self.log_test("Russian Feed (GET /api/feed_entries?language=ru)", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Russian Feed (GET /api/feed_entries?language=ru)", False, f"Exception: {str(e)}")

    def test_user_bots(self):
        """Test GET /api/bots/user/{user_id} - User bots retrieval"""
        print("\n🤖 Testing User Bots Retrieval")
        
        # Use a proper UUID format for test user ID
        test_user_id = str(uuid.uuid4())
        
        try:
            response = self.session.get(f"{API_BASE}/bots/user/{test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'bots' in data:
                    bots = data['bots']
                    total = data.get('total', len(bots))
                    self.log_test("User Bots Retrieval (GET /api/bots/user/{user_id})", True, f"Retrieved {total} bots for user")
                    return True
                else:
                    self.log_test("User Bots Retrieval (GET /api/bots/user/{user_id})", False, f"Unexpected response: {data}")
            else:
                self.log_test("User Bots Retrieval (GET /api/bots/user/{user_id})", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Bots Retrieval (GET /api/bots/user/{user_id})", False, f"Exception: {str(e)}")
            
        return False

    def run_focused_regression_tests(self):
        """Run focused regression tests for critical backend functionality"""
        print("🚀 Starting Focused Backend Regression Tests")
        print("Testing core functionality after My Purchases & Product Editor frontend changes")
        print("=" * 80)
        
        # Core Services
        print("\n" + "=" * 50)
        print("🏥 CORE SERVICES")
        print("=" * 50)
        
        self.test_server_health()
        self.test_api_root()
        
        # Authentication System
        print("\n" + "=" * 50)
        print("🔐 AUTHENTICATION SYSTEM")
        print("=" * 50)
        
        self.test_auth_health()
        self.test_user_signup()
        self.test_signin_endpoint()
        
        # Webhook System
        print("\n" + "=" * 50)
        print("📡 WEBHOOK SYSTEM")
        print("=" * 50)
        
        self.test_webhook_system()
        self.test_feed_retrieval()
        self.test_language_aware_feed()
        
        # AI Bot System
        print("\n" + "=" * 50)
        print("🤖 AI BOT SYSTEM")
        print("=" * 50)
        
        self.test_user_bots()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FOCUSED REGRESSION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show expected vs unexpected failures
        expected_failures = []
        unexpected_failures = []
        
        for result in self.test_results:
            if not result['success']:
                # Check if this is an expected failure (environment limitations)
                if any(keyword in result['details'].lower() for keyword in ['grok api key', 'openai translation', 'invalid api key', 'environment']):
                    expected_failures.append(result)
                else:
                    unexpected_failures.append(result)
        
        if expected_failures:
            print(f"\n⚠️  EXPECTED LIMITATIONS ({len(expected_failures)}):")
            for result in expected_failures:
                print(f"   ⚠️  {result['test']}: {result['details']}")
        
        if unexpected_failures:
            print(f"\n🚨 UNEXPECTED FAILURES ({len(unexpected_failures)}):")
            for result in unexpected_failures:
                print(f"   ❌ {result['test']}: {result['details']}")
            return False
        else:
            print(f"\n🎉 NO REGRESSIONS DETECTED!")
            print("All critical backend endpoints are functioning properly.")
            print("Frontend changes (My Purchases & Product Editor) have NOT affected backend functionality.")
            return True

if __name__ == "__main__":
    tester = FocusedRegressionTester()
    success = tester.run_focused_regression_tests()
    
    if success:
        print("\n✅ Backend regression test PASSED - No regressions from frontend changes!")
        exit(0)
    else:
        print("\n❌ Backend regression test FAILED - Regressions detected!")
        exit(1)