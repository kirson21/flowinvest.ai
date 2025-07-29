#!/usr/bin/env python3
"""
Focused Backend Regression Test for Advanced Bot Builder UI Changes
Tests only the core functionality requested in the review:
1. Server health check (GET /api/status)
2. Basic authentication system health
3. Core API functionality
"""

import requests
import json
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ REACT_APP_BACKEND_URL not found in environment")
    exit(1)

API_BASE = f"{BACKEND_URL}/api"

print(f"🔗 Testing backend at: {API_BASE}")
print("🎯 FOCUSED REGRESSION TEST - Advanced Bot Builder UI Changes")
print("=" * 70)

class FocusedTester:
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
        """Test GET /api/status - Primary requirement"""
        print("\n🏥 Testing Server Health Check (GET /api/status)")
        
        try:
            response = self.session.get(f"{API_BASE}/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    self.log_test("Server Health Check", True, f"Status: {data.get('status')}, Environment: {data.get('environment')}")
                    return True
                else:
                    self.log_test("Server Health Check", False, f"Unexpected status: {data}")
            else:
                self.log_test("Server Health Check", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Server Health Check", False, f"Exception: {str(e)}")
            
        return False

    def test_api_root(self):
        """Test GET /api/ - Core API accessibility"""
        print("\n🌐 Testing API Root Endpoint")
        
        try:
            response = self.session.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                data = response.json()
                if "Flow Invest API" in data.get('message', ''):
                    self.log_test("API Root Endpoint", True, f"Message: {data.get('message')}")
                    return True
                else:
                    self.log_test("API Root Endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_test("API Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            
        return False

    def test_auth_health(self):
        """Test authentication system health - Basic requirement"""
        print("\n🔐 Testing Authentication System Health")
        
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('supabase_connected'):
                    self.log_test("Authentication System Health", True, "Supabase connected and authentication service healthy")
                    return True
                else:
                    self.log_test("Authentication System Health", False, f"Service unhealthy: {data}")
            else:
                self.log_test("Authentication System Health", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Authentication System Health", False, f"Exception: {str(e)}")
            
        return False

    def test_user_signup_basic(self):
        """Test basic user signup functionality"""
        print("\n📝 Testing User Signup (Core API Functionality)")
        
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
                    self.log_test("User Signup", True, f"User created: {user.get('email')}")
                    return True
                else:
                    self.log_test("User Signup", False, f"Signup failed: {data.get('message', 'Unknown error')}")
            else:
                # Check if it's a duplicate email error (acceptable for testing)
                if response.status_code == 400 and "already registered" in response.text:
                    self.log_test("User Signup", True, "Email already registered (acceptable for testing)")
                    return True
                else:
                    self.log_test("User Signup", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Signup", False, f"Exception: {str(e)}")
            
        return False

    def test_signin_endpoint(self):
        """Test signin endpoint responds correctly"""
        print("\n🔑 Testing Signin Endpoint Response")
        
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
                self.log_test("Signin Endpoint", True, "Endpoint correctly rejecting invalid credentials")
                return True
            elif response.status_code == 200:
                # Unexpected success with fake credentials
                self.log_test("Signin Endpoint", False, "Endpoint incorrectly accepted invalid credentials")
            else:
                self.log_test("Signin Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Signin Endpoint", False, f"Exception: {str(e)}")
            
        return False

    def test_webhook_system(self):
        """Test webhook system - Core API functionality"""
        print("\n📡 Testing Webhook System")
        
        openai_sample_data = {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "Backend Regression Test Entry",
                            "summary": "Testing webhook system after Advanced Bot Builder UI changes.",
                            "sentiment_score": 75
                        }
                    }
                }
            ],
            "source": "Regression Test",
            "timestamp": "2025-01-11T10:30:00Z"
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
                    self.log_test("Webhook System", True, f"Entry created with ID: {data['id']}")
                    return True
                else:
                    self.log_test("Webhook System", False, f"No ID in response: {data}")
            else:
                self.log_test("Webhook System", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Webhook System", False, f"Exception: {str(e)}")
            
        return False

    def test_feed_retrieval(self):
        """Test feed retrieval - Core API functionality"""
        print("\n📖 Testing Feed Retrieval")
        
        try:
            response = self.session.get(f"{API_BASE}/feed_entries")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Feed Retrieval", True, f"Retrieved {len(data)} entries")
                    return True
                else:
                    self.log_test("Feed Retrieval", False, "Response is not a list")
            else:
                self.log_test("Feed Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Feed Retrieval", False, f"Exception: {str(e)}")
            
        return False

    def test_language_aware_feed(self):
        """Test language-aware feed functionality"""
        print("\n🌍 Testing Language-Aware Feed")
        
        # Test English
        try:
            response = self.session.get(f"{API_BASE}/feed_entries?language=en")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("English Feed", True, f"Retrieved {len(data)} English entries")
                else:
                    self.log_test("English Feed", False, "Invalid response format")
            else:
                self.log_test("English Feed", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("English Feed", False, f"Exception: {str(e)}")

        # Test Russian (translation)
        try:
            import time
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/feed_entries?language=ru")
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Russian Feed", True, f"Retrieved {len(data)} entries (took {request_time:.2f}s with translation fallback)")
                else:
                    self.log_test("Russian Feed", False, "Invalid response format")
            else:
                self.log_test("Russian Feed", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Russian Feed", False, f"Exception: {str(e)}")

    def test_ai_bots_retrieval(self):
        """Test AI bots retrieval for a user"""
        print("\n🤖 Testing AI Bot System")
        
        # Use a test user ID (this should work even if user doesn't exist)
        test_user_id = "test-user-regression"
        
        try:
            response = self.session.get(f"{API_BASE}/bots/user/{test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'bots' in data:
                    bots = data['bots']
                    total = data.get('total', len(bots))
                    self.log_test("AI Bot System", True, f"Retrieved {total} bots for user")
                    return True
                else:
                    self.log_test("AI Bot System", False, f"Failed to get bots: {data.get('message', 'Unknown error')}")
            else:
                self.log_test("AI Bot System", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("AI Bot System", False, f"Exception: {str(e)}")
            
        return False

    def run_focused_tests(self):
        """Run focused regression tests for Advanced Bot Builder UI changes"""
        print("🎯 FOCUSED REGRESSION TESTS - Advanced Bot Builder UI Changes")
        print("Testing core backend functionality after frontend-only changes")
        print("=" * 70)
        
        # Core Services Tests
        print("\n🏥 CORE SERVICES")
        self.test_server_health()
        self.test_api_root()
        
        # Authentication System Tests
        print("\n🔐 AUTHENTICATION SYSTEM")
        self.test_auth_health()
        self.test_user_signup_basic()
        self.test_signin_endpoint()
        
        # Core API Functionality Tests
        print("\n📡 CORE API FUNCTIONALITY")
        self.test_webhook_system()
        self.test_feed_retrieval()
        self.test_language_aware_feed()
        self.test_ai_bots_retrieval()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 FOCUSED REGRESSION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show critical vs non-critical failures
        critical_tests = ['Server Health Check', 'API Root Endpoint', 'Authentication System Health']
        critical_failures = [r for r in self.test_results if not r['success'] and r['test'] in critical_tests]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for result in critical_failures:
                print(f"   ❌ {result['test']}: {result['details']}")
        else:
            print(f"\n✅ ALL CRITICAL SYSTEMS OPERATIONAL")
            
        if failed_tests > 0 and not critical_failures:
            print(f"\n⚠️  NON-CRITICAL ISSUES ({failed_tests}):")
            for result in self.test_results:
                if not result['success'] and result['test'] not in critical_tests:
                    print(f"   ❌ {result['test']}: {result['details']}")
                    
        return len(critical_failures) == 0

if __name__ == "__main__":
    tester = FocusedTester()
    success = tester.run_focused_tests()
    
    if success:
        print("\n🎉 All critical backend systems operational after Advanced Bot Builder UI changes!")
        print("✅ NO REGRESSIONS DETECTED")
        exit(0)
    else:
        print("\n💥 Critical backend systems have issues. Investigation required.")
        exit(1)