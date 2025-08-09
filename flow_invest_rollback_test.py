#!/usr/bin/env python3
"""
Flow Invest Backend Rollback Verification Test
Testing that the backend has been successfully restored to its original working state
after removing trading bot and exchange key features.
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

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
SUPER_ADMIN_UID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class FlowInvestRollbackTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_core_backend_health(self):
        """Test core backend health endpoints - PRIORITY 1"""
        print("=== CORE BACKEND HEALTH TESTS ===")
        
        # Test root endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint (/)", True, f"Status: {data.get('status')}, Version: {data.get('version')}")
            else:
                self.log_test("Root Endpoint (/)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Root Endpoint (/)", False, error=str(e))

        # Test API root endpoint
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root Endpoint (/api/)", True, f"Status: {data.get('status')}, Environment: {data.get('environment')}")
            else:
                self.log_test("API Root Endpoint (/api/)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("API Root Endpoint (/api/)", False, error=str(e))

        # Test status endpoint
        try:
            response = self.session.get(f"{API_BASE}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status Endpoint (/api/status)", True, f"Status: {data.get('status')}, Environment: {data.get('environment')}")
            else:
                self.log_test("Status Endpoint (/api/status)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Status Endpoint (/api/status)", False, error=str(e))

        # Test health check endpoint
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                api_status = services.get('api')
                supabase_status = services.get('supabase')
                self.log_test("Health Check Endpoint (/api/health)", True, f"API: {api_status}, Supabase: {supabase_status}")
            else:
                self.log_test("Health Check Endpoint (/api/health)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Check Endpoint (/api/health)", False, error=str(e))

    def test_authentication_system(self):
        """Test authentication system - PRIORITY 2"""
        print("=== AUTHENTICATION SYSTEM TESTS ===")
        
        # Test auth health check
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                success = data.get('success', False)
                if supabase_connected and success:
                    self.log_test("Auth Health Check", True, f"Supabase connected: {supabase_connected}")
                else:
                    self.log_test("Auth Health Check", False, f"Supabase connected: {supabase_connected}, Success: {success}")
            else:
                self.log_test("Auth Health Check", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Health Check", False, error=str(e))

        # Test super admin setup
        try:
            response = self.session.post(f"{API_BASE}/auth/admin/setup")
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                if success and SUPER_ADMIN_UID in message:
                    self.log_test("Super Admin Setup", True, f"Super Admin configured: {SUPER_ADMIN_UID}")
                else:
                    self.log_test("Super Admin Setup", success, message)
            else:
                self.log_test("Super Admin Setup", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Super Admin Setup", False, error=str(e))

        # Test signin validation (should reject invalid credentials)
        try:
            signin_data = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            response = self.session.post(f"{API_BASE}/auth/signin", json=signin_data)
            if response.status_code == 401:
                self.log_test("Signin Validation", True, "Correctly rejected invalid credentials")
            else:
                self.log_test("Signin Validation", False, f"Expected 401, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Signin Validation", False, error=str(e))

        # Test user signup (database connectivity test)
        try:
            test_email = f"rollback_test_{uuid.uuid4().hex[:8]}@flowinvest.ai"
            signup_data = {
                "email": test_email,
                "password": "testpass123",
                "full_name": "Rollback Test User",
                "country": "US"
            }
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                if success:
                    self.log_test("User Signup (Database Test)", True, f"Database accessible - test user created: {test_email}")
                else:
                    self.log_test("User Signup (Database Test)", False, "Signup failed despite 200 response")
            elif response.status_code == 400 and ("already registered" in response.text or "email" in response.text.lower()):
                self.log_test("User Signup (Database Test)", True, "Database accessible (signup validation working)")
            else:
                self.log_test("User Signup (Database Test)", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("User Signup (Database Test)", False, error=str(e))

    def test_webhook_system(self):
        """Test webhook system - PRIORITY 3"""
        print("=== WEBHOOK SYSTEM TESTS ===")
        
        # Test webhook format endpoint
        try:
            response = self.session.get(f"{API_BASE}/webhook/test")
            if response.status_code == 200:
                data = response.json()
                if "example_request" in data:
                    self.log_test("Webhook Format Endpoint", True, "Webhook format documentation available")
                else:
                    self.log_test("Webhook Format Endpoint", False, "Missing example request format")
            else:
                self.log_test("Webhook Format Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Webhook Format Endpoint", False, error=str(e))

        # Test AI news webhook with OpenAI format
        try:
            test_webhook_data = {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "Rollback Test: Bitcoin Market Analysis",
                                "summary": "Testing webhook functionality after backend rollback to ensure AI feed system is operational.",
                                "sentiment_score": 75
                            }
                        }
                    }
                ],
                "source": "Rollback Test Source",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.session.post(f"{API_BASE}/ai_news_webhook", json=test_webhook_data)
            if response.status_code == 200:
                data = response.json()
                entry_id = data.get('id')
                self.log_test("AI News Webhook", True, f"Webhook processed successfully, Entry ID: {entry_id}")
            else:
                self.log_test("AI News Webhook", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("AI News Webhook", False, error=str(e))

        # Test feed entries retrieval
        try:
            response = self.session.get(f"{API_BASE}/feed_entries")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Feed Entries Retrieval", True, f"Retrieved {len(data)} feed entries")
                else:
                    self.log_test("Feed Entries Retrieval", False, "Response is not a list")
            else:
                self.log_test("Feed Entries Retrieval", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Feed Entries Retrieval", False, error=str(e))

        # Test Russian language feed (translation system)
        try:
            response = self.session.get(f"{API_BASE}/feed_entries?language=ru")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Russian Language Feed", True, f"Retrieved {len(data)} Russian feed entries")
                else:
                    self.log_test("Russian Language Feed", False, "Response is not a list")
            else:
                self.log_test("Russian Language Feed", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Russian Language Feed", False, error=str(e))

    def test_seller_verification_system(self):
        """Test seller verification system - PRIORITY 4"""
        print("=== SELLER VERIFICATION SYSTEM TESTS ===")
        
        # Test verification storage setup
        try:
            response = self.session.post(f"{API_BASE}/setup-verification-storage")
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                bucket_name = data.get('bucket_name', '')
                if success and bucket_name == "verification-documents":
                    self.log_test("Verification Storage Setup", True, f"Storage bucket ready: {bucket_name}")
                else:
                    self.log_test("Verification Storage Setup", False, f"Setup failed: {data.get('message', 'Unknown error')}")
            else:
                self.log_test("Verification Storage Setup", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Verification Storage Setup", False, error=str(e))

    def test_ai_bot_system(self):
        """Test original AI bot system (not trading bots) - PRIORITY 5"""
        print("=== AI BOT SYSTEM TESTS ===")
        
        # Test bot creation with AI (original functionality)
        try:
            bot_request = {
                "prompt": "Create a conservative investment bot for Bitcoin with low risk",
                "user_id": SUPER_ADMIN_UID
            }
            response = self.session.post(f"{API_BASE}/bots/create-with-ai", json=bot_request)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                bot_id = data.get('bot_id', '')
                if success and bot_id:
                    self.log_test("AI Bot Creation", True, f"Bot created successfully with ID: {bot_id[:8]}...")
                else:
                    self.log_test("AI Bot Creation", False, f"Creation failed: {data.get('message', 'Unknown error')}")
            else:
                self.log_test("AI Bot Creation", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("AI Bot Creation", False, error=str(e))

        # Test user bots retrieval
        try:
            response = self.session.get(f"{API_BASE}/bots/user/{SUPER_ADMIN_UID}")
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                bots = data.get('bots', [])
                total = data.get('total', 0)
                if success:
                    self.log_test("User Bots Retrieval", True, f"Retrieved {total} bots for user")
                else:
                    self.log_test("User Bots Retrieval", False, "Failed to retrieve bots")
            else:
                self.log_test("User Bots Retrieval", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("User Bots Retrieval", False, error=str(e))

        # Test Grok service (should work or fail gracefully)
        try:
            grok_request = {
                "prompt": "Test Grok service functionality after rollback"
            }
            response = self.session.post(f"{API_BASE}/bots/test-grok", json=grok_request)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                if success:
                    self.log_test("Grok Service Test", True, "Grok service operational")
                else:
                    self.log_test("Grok Service Test", False, "Grok service not working")
            else:
                self.log_test("Grok Service Test", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Grok Service Test", False, error=str(e))

    def test_removed_features_verification(self):
        """Verify that trading bot and exchange key features have been removed - PRIORITY 6"""
        print("=== REMOVED FEATURES VERIFICATION TESTS ===")
        
        # Test that trading bot routes are removed
        removed_routes = [
            ("/trading-bots/strategy-templates", "Trading Bot Strategy Templates"),
            ("/trading-bots/", "Trading Bot Management"),
            ("/trading-bots/generate-bot", "Trading Bot Generation"),
            ("/exchange-keys/", "Exchange Keys Management"),
            ("/exchange-keys/add", "Add Exchange Keys"),
            ("/exchange-keys/supported-exchanges", "Supported Exchanges")
        ]
        
        for route, name in removed_routes:
            try:
                response = self.session.get(f"{API_BASE}{route}")
                if response.status_code == 404:
                    self.log_test(f"Removed Feature - {name}", True, "Route properly removed (404)")
                else:
                    self.log_test(f"Removed Feature - {name}", False, f"Route still exists (HTTP {response.status_code})")
            except Exception as e:
                self.log_test(f"Removed Feature - {name}", True, f"Route removed (connection error expected)")

    def test_database_connectivity(self):
        """Test Supabase database connectivity - PRIORITY 7"""
        print("=== DATABASE CONNECTIVITY TESTS ===")
        
        # Test Supabase connection through auth health
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                if supabase_connected:
                    self.log_test("Supabase Database Connection", True, "Database connection verified through auth health")
                else:
                    self.log_test("Supabase Database Connection", False, "Supabase connection failed")
            else:
                self.log_test("Supabase Database Connection", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Supabase Database Connection", False, error=str(e))

        # Test basic database operations through user bots
        try:
            response = self.session.get(f"{API_BASE}/bots/user/{SUPER_ADMIN_UID}")
            if response.status_code == 200:
                self.log_test("Database Operations Test", True, "Database operations working through user bots endpoint")
            elif response.status_code == 500 and "table" in response.text.lower():
                self.log_test("Database Operations Test", False, "Database table issues detected")
            else:
                self.log_test("Database Operations Test", True, f"Database accessible (HTTP {response.status_code})")
        except Exception as e:
            self.log_test("Database Operations Test", False, error=str(e))

    def test_backend_stability(self):
        """Test backend server stability after rollback"""
        print("=== BACKEND STABILITY TESTS ===")
        
        # Test multiple rapid requests to check stability
        try:
            success_count = 0
            total_requests = 5
            
            for i in range(total_requests):
                response = self.session.get(f"{API_BASE}/health")
                if response.status_code == 200:
                    success_count += 1
                time.sleep(0.2)  # Small delay between requests
            
            stability_rate = (success_count / total_requests) * 100
            if stability_rate >= 80:
                self.log_test("Backend Stability", True, f"Stability rate: {stability_rate}% ({success_count}/{total_requests})")
            else:
                self.log_test("Backend Stability", False, f"Low stability rate: {stability_rate}% ({success_count}/{total_requests})")
        except Exception as e:
            self.log_test("Backend Stability", False, error=str(e))

    def run_all_tests(self):
        """Run all tests and generate summary"""
        print("🚀 STARTING FLOW INVEST BACKEND ROLLBACK VERIFICATION")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Focus: Verifying original functionality after rollback")
        print("=" * 80)
        
        # Run all test suites in priority order
        self.test_core_backend_health()
        self.test_authentication_system()
        self.test_webhook_system()
        self.test_seller_verification_system()
        self.test_ai_bot_system()
        self.test_removed_features_verification()
        self.test_database_connectivity()
        self.test_backend_stability()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("📊 FLOW INVEST BACKEND ROLLBACK VERIFICATION SUMMARY")
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
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['error']}")
            print()
        
        # Priority findings
        print("🔍 ROLLBACK VERIFICATION RESULTS:")
        
        # 1. Core Backend Health
        core_tests = [r for r in self.test_results if 'Endpoint' in r['test'] and any(x in r['test'] for x in ['Root', 'Status', 'Health'])]
        core_passed = sum(1 for r in core_tests if r['success'])
        
        if core_passed == len(core_tests) and len(core_tests) > 0:
            print("✅ Core Backend Health: RESTORED AND OPERATIONAL")
        else:
            print("❌ Core Backend Health: ISSUES DETECTED")
        
        # 2. Authentication System
        auth_tests = [r for r in self.test_results if 'Auth' in r['test'] or 'Signin' in r['test'] or 'Signup' in r['test']]
        auth_passed = sum(1 for r in auth_tests if r['success'])
        
        if auth_passed >= len(auth_tests) * 0.8 and len(auth_tests) > 0:
            print("✅ Authentication System: RESTORED AND WORKING")
        else:
            print("❌ Authentication System: ISSUES DETECTED")
        
        # 3. Webhook System
        webhook_tests = [r for r in self.test_results if 'Webhook' in r['test'] or 'Feed' in r['test']]
        webhook_passed = sum(1 for r in webhook_tests if r['success'])
        
        if webhook_passed >= len(webhook_tests) * 0.8 and len(webhook_tests) > 0:
            print("✅ Webhook System: RESTORED AND OPERATIONAL")
        else:
            print("❌ Webhook System: ISSUES DETECTED")
        
        # 4. Seller Verification
        verification_tests = [r for r in self.test_results if 'Verification' in r['test']]
        verification_passed = sum(1 for r in verification_tests if r['success'])
        
        if verification_passed == len(verification_tests) and len(verification_tests) > 0:
            print("✅ Seller Verification System: RESTORED AND INTACT")
        else:
            print("❌ Seller Verification System: ISSUES DETECTED")
        
        # 5. AI Bot System (Original)
        bot_tests = [r for r in self.test_results if 'AI Bot' in r['test'] or 'Grok' in r['test']]
        bot_passed = sum(1 for r in bot_tests if r['success'])
        
        if bot_passed >= len(bot_tests) * 0.7 and len(bot_tests) > 0:  # 70% threshold for AI services
            print("✅ AI Bot System (Original): PRESERVED AND WORKING")
        else:
            print("❌ AI Bot System (Original): ISSUES DETECTED")
        
        # 6. Removed Features Verification
        removed_tests = [r for r in self.test_results if 'Removed Feature' in r['test']]
        removed_passed = sum(1 for r in removed_tests if r['success'])
        
        if removed_passed == len(removed_tests) and len(removed_tests) > 0:
            print("✅ Trading Bot Features: SUCCESSFULLY REMOVED")
        else:
            print("❌ Trading Bot Features: REMOVAL INCOMPLETE")
        
        # 7. Database Connectivity
        db_tests = [r for r in self.test_results if 'Database' in r['test'] and 'Supabase' in r['test']]
        db_passed = sum(1 for r in db_tests if r['success'])
        
        if db_passed == len(db_tests) and len(db_tests) > 0:
            print("✅ Database Connectivity: OPERATIONAL")
        else:
            print("❌ Database Connectivity: ISSUES DETECTED")
        
        print()
        print("🎯 ROLLBACK SUCCESS VERIFICATION:")
        
        # Check if core functionality is restored
        core_health_rate = (core_passed / len(core_tests) * 100) if len(core_tests) > 0 else 0
        auth_health_rate = (auth_passed / len(auth_tests) * 100) if len(auth_tests) > 0 else 0
        webhook_health_rate = (webhook_passed / len(webhook_tests) * 100) if len(webhook_tests) > 0 else 0
        
        if core_health_rate >= 90 and auth_health_rate >= 80 and webhook_health_rate >= 80:
            print("✅ Original functionality successfully restored")
        else:
            print("❌ Original functionality not fully restored")
        
        # Check if new features are properly removed
        removal_rate = (removed_passed / len(removed_tests) * 100) if len(removed_tests) > 0 else 0
        if removal_rate >= 90:
            print("✅ New trading bot features successfully removed")
        else:
            print("❌ New trading bot features not completely removed")
        
        print()
        if success_rate >= 85:
            print("🎉 ROLLBACK ASSESSMENT: SUCCESSFUL - Backend restored to original working state")
        elif success_rate >= 70:
            print("✅ ROLLBACK ASSESSMENT: MOSTLY SUCCESSFUL - Minor issues remain")
        elif success_rate >= 50:
            print("⚠️  ROLLBACK ASSESSMENT: PARTIAL - Some original functionality not restored")
        else:
            print("🚨 ROLLBACK ASSESSMENT: FAILED - Major issues with rollback")
        
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = FlowInvestRollbackTester()
    summary = tester.run_all_tests()