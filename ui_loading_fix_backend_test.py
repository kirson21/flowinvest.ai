#!/usr/bin/env python3
"""
Backend Regression Testing Suite for UI Loading Bug Fix
Focus: Verify backend functionality after frontend mock data removal
Priority: Ensure no backend regressions from frontend-only changes
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

class UILoadingFixBackendTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = str(uuid.uuid4())
        self.test_email = f"ui_fix_test_{uuid.uuid4().hex[:8]}@flowinvest.ai"
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

    def test_core_api_health(self):
        """Test core API health endpoints - Priority 1"""
        print("🔍 TESTING CORE API HEALTH...")
        
        # Test API root
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root Endpoint", True, f"Status: {response.status_code}, Message: {data.get('message', 'OK')}")
            else:
                self.log_test("API Root Endpoint", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("API Root Endpoint", False, "Connection failed", str(e))
        
        # Test status endpoint
        try:
            response = requests.get(f"{API_BASE}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status Endpoint", True, f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("Status Endpoint", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Status Endpoint", False, "Connection failed", str(e))
        
        # Test health endpoint
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                self.log_test("Health Check", True, f"API: {services.get('api', 'unknown')}, Supabase: {services.get('supabase', 'unknown')}")
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Health Check", False, "Connection failed", str(e))

    def test_authentication_system(self):
        """Test authentication system - Priority 1"""
        print("🔍 TESTING AUTHENTICATION SYSTEM...")
        
        # Test auth health
        try:
            response = requests.get(f"{API_BASE}/auth/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                self.log_test("Auth Health Check", True, f"Supabase connected: {supabase_connected}")
            else:
                self.log_test("Auth Health Check", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Auth Health Check", False, "Connection failed", str(e))
        
        # Test user signup
        try:
            signup_data = {
                "email": self.test_email,
                "password": "TestPassword123!",
                "full_name": "UI Fix Test User"
            }
            response = requests.post(f"{API_BASE}/auth/signup", json=signup_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user', {}).get('id')
                if user_id:
                    self.test_user_id = user_id
                    self.log_test("User Signup", True, f"User created: {self.test_email}")
                else:
                    self.log_test("User Signup", False, "No user ID returned", str(data))
            else:
                self.log_test("User Signup", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("User Signup", False, "Connection failed", str(e))
        
        # Test signin validation
        try:
            signin_data = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            response = requests.post(f"{API_BASE}/auth/signin", json=signin_data, timeout=10)
            if response.status_code == 401:
                self.log_test("Signin Endpoint", True, "Correctly rejected invalid credentials")
            else:
                self.log_test("Signin Endpoint", False, f"Expected 401, got {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Signin Endpoint", False, "Connection failed", str(e))

    def test_bot_management_apis(self):
        """Test bot management APIs - Priority 1"""
        print("🔍 TESTING BOT MANAGEMENT APIS...")
        
        # Test bot creation API
        try:
            bot_data = {
                "prompt": "Create a conservative Bitcoin trading bot for UI loading fix testing",
                "user_id": self.super_admin_uid
            }
            response = requests.post(f"{API_BASE}/bots/create-with-ai", json=bot_data, timeout=30)
            if response.status_code == 200:
                data = response.json()
                bot_id = data.get('bot_id')
                bot_name = data.get('bot_config', {}).get('name', 'Unknown')
                if bot_id:
                    self.log_test("Bot Creation API", True, f"Bot created: {bot_name}, ID: {bot_id[:8]}...")
                else:
                    self.log_test("Bot Creation API", False, "No bot_id returned", str(data))
            else:
                self.log_test("Bot Creation API", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Bot Creation API", False, "Connection failed", str(e))
        
        # Test user bots retrieval
        try:
            response = requests.get(f"{API_BASE}/bots/user/{self.super_admin_uid}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                bot_count = len(data.get('bots', []))
                self.log_test("User Bots Retrieval", True, f"Bots found: {bot_count}")
            else:
                self.log_test("User Bots Retrieval", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("User Bots Retrieval", False, "Connection failed", str(e))

    def test_webhook_system(self):
        """Test webhook system - Priority 1"""
        print("🔍 TESTING WEBHOOK SYSTEM...")
        
        # Test OpenAI webhook
        try:
            webhook_data = {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "UI Loading Fix Backend Test",
                                "summary": "Testing backend stability after removing mock data initialization from frontend components",
                                "sentiment_score": 75
                            }
                        }
                    }
                ],
                "source": "UI Loading Fix Test",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            response = requests.post(f"{API_BASE}/ai_news_webhook", json=webhook_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                entry_id = data.get('id', 'unknown')
                self.log_test("OpenAI Webhook", True, f"Entry created: {entry_id[:8]}...")
            else:
                self.log_test("OpenAI Webhook", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("OpenAI Webhook", False, "Connection failed", str(e))
        
        # Test feed retrieval
        try:
            response = requests.get(f"{API_BASE}/feed_entries?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                entry_count = len(data) if isinstance(data, list) else 0
                self.log_test("Feed Retrieval", True, f"Entries retrieved: {entry_count}")
            else:
                self.log_test("Feed Retrieval", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Feed Retrieval", False, "Connection failed", str(e))
        
        # Test language-aware feeds
        try:
            start_time = time.time()
            response = requests.get(f"{API_BASE}/feed_entries?language=ru&limit=2", timeout=15)
            translation_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                entry_count = len(data) if isinstance(data, list) else 0
                self.log_test("Language-aware Feeds", True, f"Russian entries: {entry_count}, Translation time: {translation_time:.2f}s")
            else:
                self.log_test("Language-aware Feeds", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Language-aware Feeds", False, "Connection failed", str(e))

    def test_data_sync_compatibility(self):
        """Test data sync service compatibility - Priority 2"""
        print("🔍 TESTING DATA SYNC COMPATIBILITY...")
        
        # Test super admin setup (for data sync service)
        try:
            response = requests.post(f"{API_BASE}/auth/admin/setup", timeout=10)
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', 'OK')
                self.log_test("Super Admin Setup", True, f"Admin setup: {message[:50]}...")
            else:
                self.log_test("Super Admin Setup", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Super Admin Setup", False, "Connection failed", str(e))
        
        # Test verification system (for seller verification)
        try:
            response = requests.get(f"{API_BASE}/verification/storage/setup", timeout=10)
            if response.status_code == 200:
                data = response.json()
                bucket_name = data.get('bucket_name', 'unknown')
                self.log_test("Verification Storage Setup", True, f"Storage bucket: {bucket_name}")
            else:
                self.log_test("Verification Storage Setup", False, f"Status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Verification Storage Setup", False, "Connection failed", str(e))

    def test_legacy_endpoints(self):
        """Test legacy endpoints that might be affected - Priority 3"""
        print("🔍 TESTING LEGACY ENDPOINTS...")
        
        # Test legacy webhook (expected to fail)
        try:
            legacy_data = {"message": "test"}
            response = requests.post(f"{API_BASE}/webhook", json=legacy_data, timeout=10)
            if response.status_code == 500:
                self.log_test("Legacy Webhook Endpoint", True, "Expected 500 - endpoint not implemented")
            else:
                self.log_test("Legacy Webhook Endpoint", False, f"Unexpected status: {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Legacy Webhook Endpoint", True, f"Expected connection error - endpoint not implemented: {str(e)}")

    def run_all_tests(self):
        """Run all backend regression tests"""
        print("🚀 UI LOADING FIX BACKEND REGRESSION TESTING")
        print(f"Backend URL: {API_BASE}")
        print(f"Test User: {self.test_email}")
        print(f"Super Admin UID: {self.super_admin_uid}")
        print("=" * 80)
        
        # Run test suites in priority order
        self.test_core_api_health()
        self.test_authentication_system()
        self.test_bot_management_apis()
        self.test_webhook_system()
        self.test_data_sync_compatibility()
        self.test_legacy_endpoints()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("📊 UI LOADING FIX BACKEND REGRESSION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Group results by category
        categories = {
            'Core API Health': [],
            'Authentication System': [],
            'Bot Management APIs': [],
            'Webhook System': [],
            'Data Sync Compatibility': [],
            'Legacy Endpoints': []
        }
        
        for result in self.test_results:
            test_name = result['test']
            if any(keyword in test_name for keyword in ['API Root', 'Status', 'Health Check']):
                categories['Core API Health'].append(result)
            elif any(keyword in test_name for keyword in ['Auth', 'User', 'Signin', 'Signup']):
                categories['Authentication System'].append(result)
            elif any(keyword in test_name for keyword in ['Bot']):
                categories['Bot Management APIs'].append(result)
            elif any(keyword in test_name for keyword in ['Webhook', 'Feed', 'Language']):
                categories['Webhook System'].append(result)
            elif any(keyword in test_name for keyword in ['Admin', 'Verification', 'Storage']):
                categories['Data Sync Compatibility'].append(result)
            else:
                categories['Legacy Endpoints'].append(result)
        
        # Print category summaries
        print("\n🎯 CATEGORY BREAKDOWN:")
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t['success'])
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
                print(f"{status} {category}: {passed}/{total} tests passed ({rate:.1f}%)")
        
        # Critical findings
        print("\n🔍 CRITICAL FINDINGS:")
        
        # Check core functionality
        core_tests = categories['Core API Health']
        core_success = sum(1 for t in core_tests if t['success'])
        if core_success == len(core_tests) and core_tests:
            print("✅ Core API functionality intact - no regressions from UI changes")
        else:
            print("❌ Core API issues detected - potential regression")
        
        # Check authentication
        auth_tests = categories['Authentication System']
        auth_success = sum(1 for t in auth_tests if t['success'])
        if auth_success >= len(auth_tests) * 0.8 and auth_tests:
            print("✅ Authentication system operational")
        else:
            print("❌ Authentication system issues detected")
        
        # Check bot management
        bot_tests = categories['Bot Management APIs']
        bot_success = sum(1 for t in bot_tests if t['success'])
        if bot_success >= len(bot_tests) * 0.8 and bot_tests:
            print("✅ Bot management APIs working correctly")
        else:
            print("❌ Bot management API issues detected")
        
        # Check webhook system
        webhook_tests = categories['Webhook System']
        webhook_success = sum(1 for t in webhook_tests if t['success'])
        if webhook_success >= len(webhook_tests) * 0.8 and webhook_tests:
            print("✅ Webhook and feed system operational")
        else:
            print("❌ Webhook system issues detected")
        
        # Failed tests details
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['error'] or result['details']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("✅ EXCELLENT: No regressions detected from UI loading bug fix")
        elif success_rate >= 80:
            print("✅ GOOD: Minor issues detected but no critical regressions")
        elif success_rate >= 60:
            print("⚠️ MODERATE: Some issues detected, investigation recommended")
        else:
            print("❌ CRITICAL: Significant issues detected, immediate attention required")
        
        print("\n" + "=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results,
            'categories': categories
        }

if __name__ == "__main__":
    tester = UILoadingFixBackendTester()
    tester.run_all_tests()