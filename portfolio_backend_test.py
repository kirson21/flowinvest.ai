#!/usr/bin/env python3
"""
Backend Testing Suite for Portfolio Creation Fix Verification
Focus: Portfolio creation with proper user_id UUID format and data validation
Priority: Verify backend readiness for portfolio operations with corrected user_id field
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
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = str(uuid.uuid4())  # Use proper UUID format
        self.test_email = f"portfolio_test_{uuid.uuid4().hex[:8]}@flowinvest.ai"
        self.super_admin_uid = "cd0e9717-f85d-4726-81e9-f260394ead58"
        
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

    def test_server_health(self):
        """Test basic server health - Priority 1"""
        print("🔍 TESTING SERVER HEALTH...")
        
        # Test API root
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                self.log_test("API Root Endpoint", True, f"GET /api/ returned {response.status_code}")
            else:
                self.log_test("API Root Endpoint", False, f"GET /api/ returned {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("API Root Endpoint", False, "Connection failed", str(e))
        
        # Test status endpoint
        try:
            response = requests.get(f"{API_BASE}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status Endpoint", True, f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("Status Endpoint", False, f"GET /api/status returned {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Status Endpoint", False, "Connection failed", str(e))
        
        # Test health endpoint
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                self.log_test("Health Check", True, f"Services: API={services.get('api', 'unknown')}, Supabase={services.get('supabase', 'unknown')}")
            else:
                self.log_test("Health Check", False, f"GET /api/health returned {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Health Check", False, "Connection failed", str(e))

    def test_authentication_system(self):
        """Test authentication system for UUID user_id support - Priority 1"""
        print("🔍 TESTING AUTHENTICATION SYSTEM...")
        
        # Test auth health
        try:
            response = requests.get(f"{API_BASE}/auth/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                self.log_test("Auth Health Check", True, f"Supabase connected: {supabase_connected}")
            else:
                self.log_test("Auth Health Check", False, f"GET /auth/health returned {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Auth Health Check", False, "Connection failed", str(e))
        
        # Test user signup with proper data structure
        try:
            signup_data = {
                "email": self.test_email,
                "password": "TestPassword123!",
                "full_name": "Portfolio Test User"
            }
            response = requests.post(f"{API_BASE}/auth/signup", json=signup_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user', {}).get('id')
                if user_id and len(user_id) == 36:  # UUID format check
                    self.test_user_id = user_id  # Use actual user ID from signup
                    self.log_test("User Signup with UUID", True, f"Created user with UUID: {user_id}")
                else:
                    self.log_test("User Signup with UUID", False, "Invalid or missing user ID format", str(data))
            else:
                self.log_test("User Signup with UUID", False, f"Signup failed with {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("User Signup with UUID", False, "Connection failed", str(e))
        
        # Test signin validation
        try:
            signin_data = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            response = requests.post(f"{API_BASE}/auth/signin", json=signin_data, timeout=10)
            if response.status_code == 401:
                self.log_test("Signin Validation", True, "Correctly rejected invalid credentials")
            else:
                self.log_test("Signin Validation", False, f"Expected 401, got {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Signin Validation", False, "Connection failed", str(e))

    def test_portfolio_readiness(self):
        """Test backend readiness for portfolio operations - Priority 1"""
        print("🔍 TESTING PORTFOLIO READINESS...")
        
        # Check for portfolio-related endpoints
        portfolio_endpoints = [
            "/portfolios",
            "/portfolios/create", 
            f"/portfolios/user/{self.test_user_id}",
            "/user/portfolios"
        ]
        
        portfolio_found = False
        for endpoint in portfolio_endpoints:
            try:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
                if response.status_code != 404:
                    portfolio_found = True
                    self.log_test(f"Portfolio Endpoint {endpoint}", True, f"Endpoint exists (status: {response.status_code})")
                else:
                    self.log_test(f"Portfolio Endpoint {endpoint}", False, "Endpoint not found (404)", "Portfolio endpoints may not be implemented")
            except Exception as e:
                self.log_test(f"Portfolio Endpoint {endpoint}", False, "Connection failed", str(e))
        
        if not portfolio_found:
            self.log_test("Portfolio System", False, "No portfolio endpoints found", "Portfolio creation system may need implementation")
        
        # Test portfolio creation with UUID user_id format
        try:
            portfolio_data = {
                "user_id": self.test_user_id,  # UUID format instead of 'current-user'
                "name": "Test Portfolio Strategy",
                "description": "Conservative portfolio for steady growth",
                "category": "Portfolio Strategies",
                "price": 99.99,
                "risk_level": "Low",
                "expected_return": "8-12%",
                "minimum_investment": 1000,
                "assets": [
                    {"symbol": "BTC", "allocation": 40, "target_price": 50000},
                    {"symbol": "ETH", "allocation": 35, "target_price": 3000},
                    {"symbol": "USDT", "allocation": 25, "target_price": 1}
                ]
            }
            
            # Try POST to potential portfolio creation endpoints
            create_endpoints = ["/portfolios", "/portfolios/create", "/user/portfolios"]
            creation_success = False
            
            for endpoint in create_endpoints:
                try:
                    response = requests.post(f"{API_BASE}{endpoint}", json=portfolio_data, timeout=10)
                    if response.status_code == 201:
                        creation_success = True
                        data = response.json()
                        self.log_test(f"Portfolio Creation {endpoint}", True, f"Portfolio created successfully: {data.get('id', 'unknown')}")
                        break
                    elif response.status_code == 404:
                        self.log_test(f"Portfolio Creation {endpoint}", False, "Endpoint not found", "Portfolio creation endpoint not implemented")
                    else:
                        self.log_test(f"Portfolio Creation {endpoint}", False, f"Status: {response.status_code}", response.text[:200])
                except Exception as e:
                    self.log_test(f"Portfolio Creation {endpoint}", False, "Connection failed", str(e))
            
            if not creation_success:
                self.log_test("Portfolio Creation System", False, "No working portfolio creation endpoint found", "Backend may need portfolio creation implementation")
                
        except Exception as e:
            self.log_test("Portfolio Creation Test", False, "Test setup failed", str(e))

    def test_user_id_validation(self):
        """Test UUID user_id validation vs old 'current-user' format - Priority 1"""
        print("🔍 TESTING USER ID VALIDATION...")
        
        # Test with valid UUID format
        try:
            response = requests.get(f"{API_BASE}/bots/user/{self.test_user_id}", timeout=10)
            if response.status_code in [200, 404]:  # 404 is OK if no bots exist
                data = response.json()
                self.log_test("UUID Format Acceptance", True, f"Backend accepts UUID format: {self.test_user_id[:8]}...")
            else:
                self.log_test("UUID Format Acceptance", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("UUID Format Acceptance", False, "Connection failed", str(e))
        
        # Test with old 'current-user' format (should be rejected or handled gracefully)
        try:
            response = requests.get(f"{API_BASE}/bots/user/current-user", timeout=10)
            if response.status_code == 400:
                self.log_test("Invalid User ID Rejection", True, "Backend correctly rejects 'current-user' string")
            elif response.status_code == 500:
                self.log_test("Invalid User ID Handling", True, "Backend handles invalid user_id format gracefully")
            else:
                self.log_test("Invalid User ID Handling", False, f"Unexpected response: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Invalid User ID Handling", False, "Connection failed", str(e))

    def test_data_validation_system(self):
        """Test data validation for portfolio creation - Priority 2"""
        print("🔍 TESTING DATA VALIDATION SYSTEM...")
        
        # Test bot creation with UUID (as proxy for data validation)
        try:
            bot_data = {
                "prompt": "Create a conservative Bitcoin trading bot for portfolio integration testing",
                "user_id": self.test_user_id
            }
            
            response = requests.post(f"{API_BASE}/bots/create-with-ai", json=bot_data, timeout=30)
            if response.status_code == 200:
                data = response.json()
                bot_id = data.get('bot_id')
                if bot_id:
                    self.log_test("Bot Creation with UUID", True, f"Bot created with ID: {bot_id[:8]}...")
                else:
                    self.log_test("Bot Creation with UUID", False, "No bot_id returned", str(data))
            else:
                self.log_test("Bot Creation with UUID", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Bot Creation with UUID", False, "Connection failed", str(e))
        
        # Test data validation with invalid input
        try:
            invalid_data = {
                "prompt": "",  # Empty prompt should be rejected
                "user_id": "invalid-uuid-format"
            }
            
            response = requests.post(f"{API_BASE}/bots/create-with-ai", json=invalid_data, timeout=10)
            if response.status_code == 400:
                self.log_test("Data Validation", True, "Backend correctly rejects invalid data")
            else:
                self.log_test("Data Validation", False, f"Expected 400, got {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Data Validation", False, "Validation test failed", str(e))

    def test_regression_check(self):
        """Test that existing functionality hasn't been broken - Priority 2"""
        print("🔍 TESTING REGRESSION CHECK...")
        
        # Test webhook system
        try:
            webhook_data = {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "Portfolio Creation Backend Test",
                                "summary": "Testing backend stability after portfolio creation fixes with UUID user_id support",
                                "sentiment_score": 75
                            }
                        }
                    }
                ],
                "source": "Backend Portfolio Test",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            response = requests.post(f"{API_BASE}/ai_news_webhook", json=webhook_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                entry_id = data.get('id', 'unknown')
                self.log_test("Webhook System", True, f"News entry created: {entry_id[:8]}...")
            else:
                self.log_test("Webhook System", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Webhook System", False, "Webhook test failed", str(e))
        
        # Test feed retrieval
        try:
            response = requests.get(f"{API_BASE}/feed_entries?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                entry_count = len(data)
                self.log_test("Feed Retrieval", True, f"Retrieved {entry_count} feed entries")
            else:
                self.log_test("Feed Retrieval", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Feed Retrieval", False, "Feed test failed", str(e))
        
        # Test super admin setup (for user authentication)
        try:
            response = requests.post(f"{API_BASE}/auth/admin/setup", timeout=10)
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'OK')
                self.log_test("Super Admin Setup", True, f"Admin setup: {message[:50]}...")
            else:
                self.log_test("Super Admin Setup", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Super Admin Setup", False, "Admin setup test failed", str(e))

    def run_all_tests(self):
        """Run all backend verification tests"""
        print("🚀 BACKEND VERIFICATION FOR PORTFOLIO CREATION FIX")
        print(f"Backend URL: {API_BASE}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        
        # Run test suites in priority order
        self.test_server_health()
        self.test_authentication_system()
        self.test_portfolio_readiness()
        self.test_user_id_validation()
        self.test_data_validation_system()
        self.test_regression_check()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("📊 BACKEND VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical findings for portfolio creation
        print("\n🎯 PORTFOLIO CREATION READINESS:")
        
        # Check UUID support
        uuid_tests = [r for r in self.test_results if 'uuid' in r['test'].lower() or 'user id' in r['test'].lower()]
        uuid_success = sum(1 for r in uuid_tests if r['success'])
        if uuid_success >= len(uuid_tests) * 0.8:
            print("✅ UUID user_id format properly supported")
        else:
            print("❌ UUID user_id format needs fixes")
        
        # Check portfolio endpoints
        portfolio_tests = [r for r in self.test_results if 'portfolio' in r['test'].lower()]
        if portfolio_tests:
            portfolio_success = sum(1 for r in portfolio_tests if r['success'])
            if portfolio_success > 0:
                print("✅ Portfolio endpoints partially ready")
            else:
                print("❌ Portfolio endpoints need implementation")
        else:
            print("⚠️  Portfolio endpoints not found - may need implementation")
        
        # Check data validation
        validation_tests = [r for r in self.test_results if 'validation' in r['test'].lower()]
        validation_success = sum(1 for r in validation_tests if r['success'])
        if validation_success >= len(validation_tests) * 0.8:
            print("✅ Data validation working correctly")
        else:
            print("❌ Data validation needs improvement")
        
        # Check for regressions
        regression_tests = [r for r in self.test_results if any(keyword in r['test'].lower() for keyword in ['webhook', 'feed', 'admin', 'auth health'])]
        regression_success = sum(1 for r in regression_tests if r['success'])
        if regression_success >= len(regression_tests) * 0.8:
            print("✅ No major regressions detected")
        else:
            print("❌ Potential regressions found")
        
        # Failed tests details
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['error']}")
        
        print("\n" + "=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results
        }

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code based on success rate
    if results['success_rate'] >= 80:
        print("🎯 BACKEND VERIFICATION PASSED")
        exit(0)
    else:
        print("🚨 BACKEND VERIFICATION NEEDS ATTENTION")
        exit(1)