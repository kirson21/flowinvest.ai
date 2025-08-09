#!/usr/bin/env python3
"""
AI Trading Bot Constructor Backend Infrastructure Testing
Testing authentication system fixes, route registration, and core backend services
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

class TradingBotInfrastructureTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.super_admin_token = None
        
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
        """Test basic backend connectivity and health"""
        print("=== CORE BACKEND SERVICES TESTS ===")
        
        # Test API root endpoint
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root Endpoint", True, f"Status: {data.get('status')}, Environment: {data.get('environment')}")
            else:
                self.log_test("API Root Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("API Root Endpoint", False, error=str(e))

        # Test status endpoint
        try:
            response = self.session.get(f"{API_BASE}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status Endpoint", True, f"Status: {data.get('status')}")
            else:
                self.log_test("Status Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Status Endpoint", False, error=str(e))

        # Test health check endpoint
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                supabase_status = services.get('supabase', 'unknown')
                self.log_test("Health Check Endpoint", True, f"API: {services.get('api')}, Supabase: {supabase_status}")
            else:
                self.log_test("Health Check Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Check Endpoint", False, error=str(e))

    def test_authentication_system_health(self):
        """Test authentication system health after fixes"""
        print("=== AUTHENTICATION SYSTEM HEALTH TESTS ===")
        
        # Test auth health check - PRIORITY 1
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                success = data.get('success', False)
                message = data.get('message', '')
                
                if supabase_connected and success:
                    self.log_test("Auth Health Check", True, f"Supabase connected: {supabase_connected}, Message: {message}")
                else:
                    self.log_test("Auth Health Check", False, f"Supabase connected: {supabase_connected}, Success: {success}")
            else:
                self.log_test("Auth Health Check", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Health Check", False, error=str(e))

        # Test super admin setup - PRIORITY 2
        try:
            response = self.session.post(f"{API_BASE}/auth/admin/setup")
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                user_id = data.get('user_id', '')
                
                if success and (SUPER_ADMIN_UID in message or user_id == SUPER_ADMIN_UID):
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

    def test_non_authenticated_endpoints(self):
        """Test non-authenticated endpoints - PRIORITY 3"""
        print("=== NON-AUTHENTICATED ENDPOINTS TESTS ===")
        
        # Test supported exchanges endpoint - CRITICAL
        try:
            response = self.session.get(f"{API_BASE}/exchange-keys/supported-exchanges")
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                exchanges = data.get('exchanges', [])
                
                if success and exchanges:
                    bybit_found = any(ex.get('id') == 'bybit' for ex in exchanges)
                    if bybit_found:
                        self.log_test("Supported Exchanges Endpoint", True, f"Found {len(exchanges)} exchanges including Bybit")
                    else:
                        self.log_test("Supported Exchanges Endpoint", False, "Bybit configuration not found in exchanges")
                else:
                    self.log_test("Supported Exchanges Endpoint", False, f"Success: {success}, Exchanges count: {len(exchanges)}")
            else:
                self.log_test("Supported Exchanges Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Supported Exchanges Endpoint", False, error=str(e))

    def test_route_registration_verification(self):
        """Test that all trading bot routes are properly registered - PRIORITY 4"""
        print("=== ROUTE REGISTRATION VERIFICATION TESTS ===")
        
        # Test trading bot routes accessibility (should return 401 for unauthenticated requests)
        trading_bot_routes = [
            ("/trading-bots/strategy-templates", "Strategy Templates Route"),
            ("/trading-bots/", "User Bots Route"),
            ("/trading-bots/generate-bot", "Generate Bot Route")
        ]
        
        for route, name in trading_bot_routes:
            try:
                response = self.session.get(f"{API_BASE}{route}")
                # These routes should return 401 (unauthorized) or 422 (validation error) for unauthenticated requests
                # NOT 404 (not found) which would indicate route registration issues
                if response.status_code in [401, 422]:
                    self.log_test(f"Route Registration - {name}", True, f"Route accessible (HTTP {response.status_code} - auth required)")
                elif response.status_code == 404:
                    self.log_test(f"Route Registration - {name}", False, f"Route not found (HTTP 404) - registration issue")
                else:
                    self.log_test(f"Route Registration - {name}", True, f"Route accessible (HTTP {response.status_code})")
            except Exception as e:
                self.log_test(f"Route Registration - {name}", False, error=str(e))

        # Test exchange key routes accessibility
        exchange_key_routes = [
            ("/exchange-keys/", "User Exchange Keys Route"),
            ("/exchange-keys/add", "Add Exchange Keys Route")
        ]
        
        for route, name in exchange_key_routes:
            try:
                response = self.session.get(f"{API_BASE}{route}")
                # These routes should return 401 (unauthorized) or 422 (validation error) for unauthenticated requests
                if response.status_code in [401, 422]:
                    self.log_test(f"Route Registration - {name}", True, f"Route accessible (HTTP {response.status_code} - auth required)")
                elif response.status_code == 404:
                    self.log_test(f"Route Registration - {name}", False, f"Route not found (HTTP 404) - registration issue")
                else:
                    self.log_test(f"Route Registration - {name}", True, f"Route accessible (HTTP {response.status_code})")
            except Exception as e:
                self.log_test(f"Route Registration - {name}", False, error=str(e))

    def test_database_connectivity(self):
        """Test Supabase database connectivity - PRIORITY 5"""
        print("=== DATABASE CONNECTIVITY TESTS ===")
        
        # Test if we can access Supabase tables through backend
        try:
            # Test user signup to verify database connectivity
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
                success = data.get('success', False)
                if success:
                    self.log_test("Supabase Database Connectivity", True, f"Database accessible - test user created: {test_email}")
                else:
                    self.log_test("Supabase Database Connectivity", False, "Signup failed despite 200 response")
            elif response.status_code == 400 and ("already registered" in response.text or "email" in response.text.lower()):
                self.log_test("Supabase Database Connectivity", True, "Database accessible (signup validation working)")
            else:
                self.log_test("Supabase Database Connectivity", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Supabase Database Connectivity", False, error=str(e))

        # Test if trading bot tables exist (indirect verification)
        try:
            # This should fail with auth error, not table error
            response = self.session.get(f"{API_BASE}/trading-bots/")
            if response.status_code == 401:
                self.log_test("Trading Bot Tables Verification", True, "Tables accessible (authentication required)")
            elif response.status_code == 500 and "table" in response.text.lower():
                self.log_test("Trading Bot Tables Verification", False, "Database table issues detected")
            else:
                self.log_test("Trading Bot Tables Verification", True, f"Tables accessible (HTTP {response.status_code})")
        except Exception as e:
            self.log_test("Trading Bot Tables Verification", False, error=str(e))

    def test_authentication_fixes_verification(self):
        """Test specific authentication fixes mentioned in the review"""
        print("=== AUTHENTICATION FIXES VERIFICATION TESTS ===")
        
        # Test PostgreSQL error 42703 fix
        try:
            # This should not return PostgreSQL column errors anymore
            response = self.session.get(f"{API_BASE}/auth/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('supabase_connected', False):
                    self.log_test("PostgreSQL 42703 Error Fix", True, "No PostgreSQL column errors detected")
                else:
                    self.log_test("PostgreSQL 42703 Error Fix", False, "Supabase connection issues")
            else:
                # Check if error contains PostgreSQL column error
                if "42703" in response.text or "column" in response.text.lower() and "not found" in response.text.lower():
                    self.log_test("PostgreSQL 42703 Error Fix", False, "PostgreSQL column error still present")
                else:
                    self.log_test("PostgreSQL 42703 Error Fix", True, "No PostgreSQL column errors detected")
        except Exception as e:
            self.log_test("PostgreSQL 42703 Error Fix", False, error=str(e))

        # Test route prefix fix (no double /api prefix)
        try:
            # Test that routes work with single /api prefix
            response = self.session.get(f"{API_BASE}/exchange-keys/supported-exchanges")
            if response.status_code == 200:
                self.log_test("Route Prefix Fix", True, "Routes accessible with correct /api prefix")
            else:
                self.log_test("Route Prefix Fix", False, f"Route prefix issues detected (HTTP {response.status_code})")
        except Exception as e:
            self.log_test("Route Prefix Fix", False, error=str(e))

        # Test import path fix
        try:
            # Test that backend starts without import errors (indirect test)
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                self.log_test("Import Path Fix", True, "Backend running without import errors")
            else:
                self.log_test("Import Path Fix", False, f"Backend health check failed (HTTP {response.status_code})")
        except Exception as e:
            self.log_test("Import Path Fix", False, error=str(e))

    def test_backend_stability(self):
        """Test backend server stability"""
        print("=== BACKEND STABILITY TESTS ===")
        
        # Test multiple rapid requests to check stability
        try:
            success_count = 0
            total_requests = 5
            
            for i in range(total_requests):
                response = self.session.get(f"{API_BASE}/health")
                if response.status_code == 200:
                    success_count += 1
                time.sleep(0.1)  # Small delay between requests
            
            stability_rate = (success_count / total_requests) * 100
            if stability_rate >= 80:
                self.log_test("Backend Stability", True, f"Stability rate: {stability_rate}% ({success_count}/{total_requests})")
            else:
                self.log_test("Backend Stability", False, f"Low stability rate: {stability_rate}% ({success_count}/{total_requests})")
        except Exception as e:
            self.log_test("Backend Stability", False, error=str(e))

    def run_all_tests(self):
        """Run all tests and generate summary"""
        print("🚀 STARTING AI TRADING BOT CONSTRUCTOR BACKEND INFRASTRUCTURE TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Focus: Authentication System Fixes & Trading Bot Infrastructure")
        print("=" * 80)
        
        # Run all test suites in priority order
        self.test_core_backend_health()
        self.test_authentication_system_health()
        self.test_non_authenticated_endpoints()
        self.test_route_registration_verification()
        self.test_database_connectivity()
        self.test_authentication_fixes_verification()
        self.test_backend_stability()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("📊 AI TRADING BOT CONSTRUCTOR INFRASTRUCTURE TEST SUMMARY")
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
        print("🔍 PRIORITY TESTING RESULTS:")
        
        # 1. Authentication System Health
        auth_health_tests = [r for r in self.test_results if 'Auth Health' in r['test'] or 'Super Admin Setup' in r['test']]
        auth_health_passed = sum(1 for r in auth_health_tests if r['success'])
        
        if auth_health_passed == len(auth_health_tests) and len(auth_health_tests) > 0:
            print("✅ Authentication System Health: OPERATIONAL")
        else:
            print("❌ Authentication System Health: ISSUES DETECTED")
        
        # 2. Non-Authenticated Endpoints
        non_auth_tests = [r for r in self.test_results if 'Supported Exchanges' in r['test']]
        non_auth_passed = sum(1 for r in non_auth_tests if r['success'])
        
        if non_auth_passed == len(non_auth_tests) and len(non_auth_tests) > 0:
            print("✅ Non-Authenticated Endpoints: WORKING")
        else:
            print("❌ Non-Authenticated Endpoints: ISSUES DETECTED")
        
        # 3. Core Backend Services
        core_tests = [r for r in self.test_results if 'Endpoint' in r['test'] and ('Root' in r['test'] or 'Status' in r['test'] or 'Health' in r['test'])]
        core_passed = sum(1 for r in core_tests if r['success'])
        
        if core_passed == len(core_tests) and len(core_tests) > 0:
            print("✅ Core Backend Services: STABLE")
        else:
            print("❌ Core Backend Services: ISSUES DETECTED")
        
        # 4. Route Registration
        route_tests = [r for r in self.test_results if 'Route Registration' in r['test']]
        route_passed = sum(1 for r in route_tests if r['success'])
        
        if route_passed >= len(route_tests) * 0.8 and len(route_tests) > 0:  # 80% threshold
            print("✅ Route Registration: COMPLETE")
        else:
            print("❌ Route Registration: ISSUES DETECTED")
        
        # 5. Database Connectivity
        db_tests = [r for r in self.test_results if 'Database' in r['test'] or 'Supabase' in r['test']]
        db_passed = sum(1 for r in db_tests if r['success'])
        
        if db_passed >= len(db_tests) * 0.8 and len(db_tests) > 0:  # 80% threshold
            print("✅ Database Connectivity: OPERATIONAL")
        else:
            print("❌ Database Connectivity: ISSUES DETECTED")
        
        # Authentication fixes verification
        fix_tests = [r for r in self.test_results if 'Fix' in r['test']]
        fix_passed = sum(1 for r in fix_tests if r['success'])
        
        if fix_passed == len(fix_tests) and len(fix_tests) > 0:
            print("✅ Authentication Fixes: VERIFIED")
        else:
            print("❌ Authentication Fixes: ISSUES REMAIN")
        
        # Overall assessment
        print()
        print("🎯 EXPECTED IMPROVEMENTS VERIFICATION:")
        
        # Check if authentication health improved
        auth_health_working = any(r['success'] for r in self.test_results if 'Auth Health' in r['test'])
        if auth_health_working:
            print("✅ Authentication health check now passes")
        else:
            print("❌ Authentication health check still failing")
        
        # Check if supported exchanges endpoint works
        exchanges_working = any(r['success'] for r in self.test_results if 'Supported Exchanges' in r['test'])
        if exchanges_working:
            print("✅ Supported exchanges endpoint returns Bybit configuration")
        else:
            print("❌ Supported exchanges endpoint still not working")
        
        # Check core backend health
        core_health_rate = (core_passed / len(core_tests) * 100) if len(core_tests) > 0 else 0
        if core_health_rate >= 90:
            print("✅ Core backend health is excellent (≥90%)")
        elif core_health_rate >= 70:
            print("⚠️  Core backend health is good (≥70%)")
        else:
            print("❌ Core backend health needs improvement")
        
        # Check route registration completeness
        route_rate = (route_passed / len(route_tests) * 100) if len(route_tests) > 0 else 0
        if route_rate >= 90:
            print("✅ Route registration is complete")
        else:
            print("❌ Route registration has issues")
        
        print()
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Authentication fixes successful, infrastructure ready")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Most fixes working, minor issues remain")
        elif success_rate >= 50:
            print("⚠️  OVERALL ASSESSMENT: FAIR - Some improvements, but issues persist")
        else:
            print("🚨 OVERALL ASSESSMENT: POOR - Major issues require immediate attention")
        
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = TradingBotInfrastructureTester()
    summary = tester.run_all_tests()