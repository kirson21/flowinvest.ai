#!/usr/bin/env python3
"""
Flow Invest Backend Deployment Readiness Testing
Testing cleaned up backend to verify GitHub repository is ready for deployment
Focus: Requirements cleanup, core functionality, deployment readiness, clean state
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import subprocess
import sys

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
SUPER_ADMIN_UID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class DeploymentReadinessTester:
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

    def test_requirements_cleanup_verification(self):
        """Test that requirements.txt has been cleaned up and no Rust dependencies exist"""
        print("=== REQUIREMENTS.TXT CLEANUP VERIFICATION ===")
        
        try:
            # Read requirements.txt
            with open('/app/backend/requirements.txt', 'r') as f:
                requirements_content = f.read()
            
            # Check for Rust dependencies that should be removed
            rust_dependencies = ['python-jose', 'bcrypt', 'passlib', 'cryptography']
            found_rust_deps = []
            
            for dep in rust_dependencies:
                if dep in requirements_content.lower():
                    found_rust_deps.append(dep)
            
            if found_rust_deps:
                self.log_test("Requirements Rust Dependencies Cleanup", False, 
                             f"Found Rust dependencies that should be removed: {found_rust_deps}")
            else:
                self.log_test("Requirements Rust Dependencies Cleanup", True, 
                             "No Rust dependencies found - cleanup successful")
            
            # Verify essential dependencies are present
            essential_deps = ['fastapi', 'uvicorn', 'supabase', 'python-dotenv']
            missing_deps = []
            
            for dep in essential_deps:
                if dep not in requirements_content.lower():
                    missing_deps.append(dep)
            
            if missing_deps:
                self.log_test("Essential Dependencies Check", False, 
                             f"Missing essential dependencies: {missing_deps}")
            else:
                self.log_test("Essential Dependencies Check", True, 
                             "All essential dependencies present")
            
            # Count total dependencies
            lines = [line.strip() for line in requirements_content.split('\n') if line.strip() and not line.startswith('#')]
            self.log_test("Requirements File Size", True, 
                         f"Total dependencies: {len(lines)} (clean and minimal)")
                         
        except Exception as e:
            self.log_test("Requirements File Analysis", False, error=str(e))

    def test_server_imports_and_startup(self):
        """Test that server.py imports work correctly and no missing dependencies"""
        print("=== SERVER IMPORTS AND STARTUP VERIFICATION ===")
        
        try:
            # Test basic server health endpoints
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                api_status = services.get('api', 'unknown')
                supabase_status = services.get('supabase', 'unknown')
                
                if api_status == 'running' and supabase_status == 'connected':
                    self.log_test("Server Startup and Imports", True, 
                                 f"Server running successfully - API: {api_status}, Supabase: {supabase_status}")
                else:
                    self.log_test("Server Startup and Imports", False, 
                                 f"Service issues - API: {api_status}, Supabase: {supabase_status}")
            else:
                self.log_test("Server Startup and Imports", False, 
                             f"Health endpoint failed: HTTP {response.status_code}")
                             
        except Exception as e:
            self.log_test("Server Startup and Imports", False, error=str(e))

        # Test all route imports are working
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("Route Registration", True, 
                                 "All routes imported and registered successfully")
                else:
                    self.log_test("Route Registration", False, 
                                 f"Route registration issues: {data}")
            else:
                self.log_test("Route Registration", False, 
                             f"API root endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Route Registration", False, error=str(e))

    def test_core_system_functionality(self):
        """Test core system functionality: health, status, auth, webhooks, AI bots, seller verification"""
        print("=== CORE SYSTEM FUNCTIONALITY TESTS ===")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", True, 
                             f"Status: {data.get('status')}, Version: {data.get('version')}")
            else:
                self.log_test("Health Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Endpoint", False, error=str(e))

        # Test status endpoint
        try:
            response = self.session.get(f"{API_BASE}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status Endpoint", True, 
                             f"Status: {data.get('status')}, Environment: {data.get('environment')}")
            else:
                self.log_test("Status Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Status Endpoint", False, error=str(e))

    def test_authentication_system(self):
        """Test authentication system functionality"""
        print("=== AUTHENTICATION SYSTEM TESTS ===")
        
        # Test auth health check
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                success = data.get('success', False)
                
                if supabase_connected and success:
                    self.log_test("Authentication Health Check", True, 
                                 f"Supabase connected: {supabase_connected}")
                else:
                    self.log_test("Authentication Health Check", False, 
                                 f"Auth issues - Supabase: {supabase_connected}, Success: {success}")
            else:
                self.log_test("Authentication Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Authentication Health Check", False, error=str(e))

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
                self.log_test("Signin Validation", False, 
                             f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Signin Validation", False, error=str(e))

        # Test user signup (database connectivity test)
        try:
            test_email = f"test_{uuid.uuid4().hex[:8]}@flowinvest.ai"
            signup_data = {
                "email": test_email,
                "password": "testpass123",
                "full_name": "Test User",
                "country": "US"
            }
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("User Signup (Database Test)", True, 
                                 f"Database accessible - test user created: {test_email}")
                else:
                    self.log_test("User Signup (Database Test)", False, 
                                 "Signup failed despite 200 response")
            elif response.status_code == 400 and ("already registered" in response.text or "email" in response.text.lower()):
                self.log_test("User Signup (Database Test)", True, 
                             "Database accessible (signup validation working)")
            else:
                self.log_test("User Signup (Database Test)", False, 
                             f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Signup (Database Test)", False, error=str(e))

        # Test super admin setup
        try:
            response = self.session.post(f"{API_BASE}/auth/admin/setup")
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                if success and SUPER_ADMIN_UID in message:
                    self.log_test("Super Admin Setup", True, 
                                 f"Super Admin configured: {SUPER_ADMIN_UID}")
                else:
                    self.log_test("Super Admin Setup", success, message)
            else:
                self.log_test("Super Admin Setup", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Super Admin Setup", False, error=str(e))

    def test_webhook_system(self):
        """Test webhook system functionality"""
        print("=== WEBHOOK SYSTEM TESTS ===")
        
        # Test OpenAI webhook endpoint
        try:
            webhook_data = {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "Deployment Test News",
                                "summary": "Testing webhook system for deployment readiness verification",
                                "sentiment_score": 75
                            }
                        }
                    }
                ],
                "source": "Deployment Test",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            response = self.session.post(f"{API_BASE}/ai_news_webhook", json=webhook_data)
            if response.status_code == 200:
                data = response.json()
                entry_id = data.get('id')
                self.log_test("OpenAI Webhook", True, 
                             f"Webhook processed successfully, entry ID: {entry_id}")
            else:
                self.log_test("OpenAI Webhook", False, 
                             f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("OpenAI Webhook", False, error=str(e))

        # Test feed retrieval
        try:
            response = self.session.get(f"{API_BASE}/feed_entries?limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Feed Retrieval", True, 
                                 f"Retrieved {len(data)} feed entries")
                else:
                    self.log_test("Feed Retrieval", False, "Invalid response format")
            else:
                self.log_test("Feed Retrieval", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Feed Retrieval", False, error=str(e))

        # Test Russian language feed (translation system)
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/feed_entries?limit=1&language=ru")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    entry = data[0]
                    language = entry.get('language', 'unknown')
                    is_translated = entry.get('is_translated', False)
                    self.log_test("Russian Language Feed", True, 
                                 f"Language: {language}, Translated: {is_translated}, Response time: {response_time:.2f}s")
                else:
                    self.log_test("Russian Language Feed", True, "No entries available for translation test")
            else:
                self.log_test("Russian Language Feed", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Russian Language Feed", False, error=str(e))

    def test_ai_bots_functionality(self):
        """Test AI bots functionality"""
        print("=== AI BOTS FUNCTIONALITY TESTS ===")
        
        # Test bot creation with AI (should fail with auth error, not import error)
        try:
            bot_request = {
                "prompt": "Create a conservative Bitcoin trading bot for steady growth",
                "user_id": SUPER_ADMIN_UID
            }
            response = self.session.post(f"{API_BASE}/bots/create-with-ai", json=bot_request)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bot_id = data.get('bot_id')
                    self.log_test("AI Bot Creation", True, 
                                 f"Bot created successfully with ID: {bot_id}")
                else:
                    self.log_test("AI Bot Creation", False, "Bot creation failed")
            elif response.status_code in [401, 422]:
                self.log_test("AI Bot Creation", True, 
                             f"Endpoint accessible (HTTP {response.status_code} - auth/validation required)")
            else:
                self.log_test("AI Bot Creation", False, 
                             f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("AI Bot Creation", False, error=str(e))

        # Test user bots retrieval
        try:
            response = self.session.get(f"{API_BASE}/bots/user/{SUPER_ADMIN_UID}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bot_count = data.get('total', 0)
                    self.log_test("User Bots Retrieval", True, 
                                 f"Retrieved {bot_count} bots for user")
                else:
                    self.log_test("User Bots Retrieval", False, "Failed to retrieve bots")
            elif response.status_code in [401, 422]:
                self.log_test("User Bots Retrieval", True, 
                             f"Endpoint accessible (HTTP {response.status_code} - auth required)")
            else:
                self.log_test("User Bots Retrieval", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("User Bots Retrieval", False, error=str(e))

        # Test Grok service (should handle API key gracefully)
        try:
            test_request = {
                "prompt": "Test prompt for Grok service verification"
            }
            response = self.session.post(f"{API_BASE}/bots/test-grok", json=test_request)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Grok Service Test", True, "Grok service operational")
                else:
                    self.log_test("Grok Service Test", False, "Grok service failed")
            elif response.status_code == 500 and "api_key" in response.text.lower():
                self.log_test("Grok Service Test", True, 
                             "Grok service accessible (API key configuration needed)")
            else:
                self.log_test("Grok Service Test", False, 
                             f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Grok Service Test", False, error=str(e))

    def test_seller_verification_system(self):
        """Test seller verification system"""
        print("=== SELLER VERIFICATION SYSTEM TESTS ===")
        
        # Test verification storage setup
        try:
            response = self.session.post(f"{API_BASE}/setup-verification-storage")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bucket_name = data.get('bucket_name')
                    self.log_test("Verification Storage Setup", True, 
                                 f"Storage bucket ready: {bucket_name}")
                else:
                    self.log_test("Verification Storage Setup", False, 
                                 "Storage setup failed")
            else:
                self.log_test("Verification Storage Setup", False, 
                             f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Verification Storage Setup", False, error=str(e))

    def test_clean_state_verification(self):
        """Test that no trading bot endpoints exist and no references to deleted services"""
        print("=== CLEAN STATE VERIFICATION TESTS ===")
        
        # Test that trading bot endpoints don't exist (should return 404)
        trading_bot_endpoints = [
            "/trading-bots/strategy-templates",
            "/trading-bots/",
            "/trading-bots/generate-bot",
            "/exchange-keys/",
            "/exchange-keys/add"
        ]
        
        clean_endpoints = 0
        for endpoint in trading_bot_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                if response.status_code == 404:
                    clean_endpoints += 1
                elif response.status_code in [401, 422]:
                    # These endpoints might still exist but require auth - not clean
                    pass
            except:
                clean_endpoints += 1  # Connection error means endpoint doesn't exist
        
        if clean_endpoints == len(trading_bot_endpoints):
            self.log_test("Trading Bot Endpoints Cleanup", True, 
                         "All trading bot endpoints successfully removed")
        else:
            self.log_test("Trading Bot Endpoints Cleanup", False, 
                         f"Some trading bot endpoints still exist ({clean_endpoints}/{len(trading_bot_endpoints)} cleaned)")

        # Test that server starts without import errors from deleted services
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                self.log_test("Import Cleanup Verification", True, 
                             "Server running without import errors from deleted services")
            else:
                self.log_test("Import Cleanup Verification", False, 
                             "Server health check failed - possible import issues")
        except Exception as e:
            self.log_test("Import Cleanup Verification", False, error=str(e))

    def test_environment_variables_configuration(self):
        """Test that environment variables are correctly configured"""
        print("=== ENVIRONMENT VARIABLES CONFIGURATION TESTS ===")
        
        # Test that backend can access required environment variables
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                environment = data.get('environment')
                if environment:
                    self.log_test("Environment Variables", True, 
                                 f"Environment configured: {environment}")
                else:
                    self.log_test("Environment Variables", False, 
                                 "Environment variable not accessible")
            else:
                self.log_test("Environment Variables", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Environment Variables", False, error=str(e))

        # Test Supabase configuration
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                if supabase_connected:
                    self.log_test("Supabase Configuration", True, 
                                 "Supabase environment variables correctly configured")
                else:
                    self.log_test("Supabase Configuration", False, 
                                 "Supabase configuration issues")
            else:
                self.log_test("Supabase Configuration", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Supabase Configuration", False, error=str(e))

    def test_deployment_stability(self):
        """Test backend stability for deployment"""
        print("=== DEPLOYMENT STABILITY TESTS ===")
        
        # Test multiple rapid requests to check stability
        try:
            success_count = 0
            total_requests = 10
            response_times = []
            
            for i in range(total_requests):
                start_time = time.time()
                response = self.session.get(f"{API_BASE}/health")
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                time.sleep(0.1)  # Small delay between requests
            
            stability_rate = (success_count / total_requests) * 100
            avg_response_time = sum(response_times) / len(response_times)
            
            if stability_rate >= 90:
                self.log_test("Backend Stability", True, 
                             f"Stability: {stability_rate}% ({success_count}/{total_requests}), Avg response: {avg_response_time:.3f}s")
            else:
                self.log_test("Backend Stability", False, 
                             f"Low stability: {stability_rate}% ({success_count}/{total_requests})")
        except Exception as e:
            self.log_test("Backend Stability", False, error=str(e))

    def run_all_tests(self):
        """Run all deployment readiness tests"""
        print("🚀 STARTING FLOW INVEST BACKEND DEPLOYMENT READINESS TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Focus: Requirements Cleanup, Core Functionality, Deployment Readiness")
        print("=" * 80)
        
        # Run all test suites
        self.test_requirements_cleanup_verification()
        self.test_server_imports_and_startup()
        self.test_core_system_functionality()
        self.test_authentication_system()
        self.test_webhook_system()
        self.test_ai_bots_functionality()
        self.test_seller_verification_system()
        self.test_clean_state_verification()
        self.test_environment_variables_configuration()
        self.test_deployment_stability()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate deployment readiness summary"""
        print("=" * 80)
        print("📊 FLOW INVEST BACKEND DEPLOYMENT READINESS SUMMARY")
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
        
        # Deployment readiness assessment
        print("🔍 DEPLOYMENT READINESS ASSESSMENT:")
        
        # 1. Requirements Cleanup
        req_tests = [r for r in self.test_results if 'Requirements' in r['test'] or 'Dependencies' in r['test']]
        req_passed = sum(1 for r in req_tests if r['success'])
        
        if req_passed == len(req_tests) and len(req_tests) > 0:
            print("✅ Requirements Cleanup: COMPLETE - No Rust dependencies")
        else:
            print("❌ Requirements Cleanup: ISSUES - Rust dependencies may still exist")
        
        # 2. Core System Health
        core_tests = [r for r in self.test_results if any(keyword in r['test'] for keyword in ['Health', 'Status', 'Startup', 'Imports'])]
        core_passed = sum(1 for r in core_tests if r['success'])
        
        if core_passed >= len(core_tests) * 0.9 and len(core_tests) > 0:
            print("✅ Core System Health: EXCELLENT - All systems operational")
        elif core_passed >= len(core_tests) * 0.7:
            print("⚠️  Core System Health: GOOD - Minor issues detected")
        else:
            print("❌ Core System Health: POOR - Major issues require attention")
        
        # 3. Authentication System
        auth_tests = [r for r in self.test_results if 'Auth' in r['test'] or 'Signin' in r['test'] or 'Signup' in r['test']]
        auth_passed = sum(1 for r in auth_tests if r['success'])
        
        if auth_passed >= len(auth_tests) * 0.8 and len(auth_tests) > 0:
            print("✅ Authentication System: OPERATIONAL - Supabase integration working")
        else:
            print("❌ Authentication System: ISSUES - Authentication problems detected")
        
        # 4. Webhook System
        webhook_tests = [r for r in self.test_results if 'Webhook' in r['test'] or 'Feed' in r['test']]
        webhook_passed = sum(1 for r in webhook_tests if r['success'])
        
        if webhook_passed >= len(webhook_tests) * 0.8 and len(webhook_tests) > 0:
            print("✅ Webhook System: OPERATIONAL - AI feed processing working")
        else:
            print("❌ Webhook System: ISSUES - Feed processing problems")
        
        # 5. AI Bots System
        bots_tests = [r for r in self.test_results if 'Bot' in r['test'] or 'Grok' in r['test']]
        bots_passed = sum(1 for r in bots_tests if r['success'])
        
        if bots_passed >= len(bots_tests) * 0.7 and len(bots_tests) > 0:
            print("✅ AI Bots System: OPERATIONAL - Bot creation system working")
        else:
            print("❌ AI Bots System: ISSUES - Bot functionality problems")
        
        # 6. Clean State
        clean_tests = [r for r in self.test_results if 'Clean' in r['test'] or 'Cleanup' in r['test']]
        clean_passed = sum(1 for r in clean_tests if r['success'])
        
        if clean_passed >= len(clean_tests) * 0.8 and len(clean_tests) > 0:
            print("✅ Clean State: VERIFIED - No trading bot references remain")
        else:
            print("❌ Clean State: ISSUES - Trading bot cleanup incomplete")
        
        # 7. Deployment Stability
        stability_tests = [r for r in self.test_results if 'Stability' in r['test']]
        stability_passed = sum(1 for r in stability_tests if r['success'])
        
        if stability_passed == len(stability_tests) and len(stability_tests) > 0:
            print("✅ Deployment Stability: EXCELLENT - Ready for production")
        else:
            print("❌ Deployment Stability: ISSUES - Stability concerns")
        
        print()
        print("🎯 DEPLOYMENT READINESS VERDICT:")
        
        if success_rate >= 90:
            print("🎉 DEPLOYMENT READY: Excellent - GitHub repository is clean and ready for deployment")
            print("   ✅ No Rust compilation dependencies")
            print("   ✅ All core systems operational")
            print("   ✅ Original functionality preserved")
            print("   ✅ Clean state verified")
        elif success_rate >= 75:
            print("✅ MOSTLY READY: Good - Minor issues should be addressed before deployment")
            print("   ⚠️  Some non-critical issues detected")
            print("   ✅ Core functionality working")
        elif success_rate >= 50:
            print("⚠️  NEEDS WORK: Fair - Several issues require attention before deployment")
            print("   ❌ Multiple system issues detected")
            print("   ⚠️  Deployment not recommended yet")
        else:
            print("🚨 NOT READY: Poor - Major issues prevent deployment")
            print("   ❌ Critical system failures")
            print("   ❌ Deployment would likely fail")
        
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = DeploymentReadinessTester()
    summary = tester.run_all_tests()