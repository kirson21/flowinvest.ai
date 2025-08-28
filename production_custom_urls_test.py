#!/usr/bin/env python3
"""
Production Custom URLs Backend API Testing
==========================================

This script tests the production Custom URLs backend API to diagnose why custom URLs aren't working.
Testing against production backend: https://flowinvest-ai.onrender.com

TESTING REQUIREMENTS:
1. Backend Health Check: Test /api/urls/health to verify custom URLs routes are loaded
2. API Availability: Check if custom_urls.py routes are accessible in production
3. Database Connectivity: Verify backend can connect to production Supabase database
4. Public URL Endpoints: Test public URL endpoints like /api/urls/public/user/Flow%20Invest
5. Environment Variables: Check if backend is using correct environment variables
6. Route Configuration: Verify custom URLs routes are properly registered in FastAPI

Production URLs:
- Backend: https://flowinvest-ai.onrender.com
- Frontend: https://f01i.app
"""

import requests
import json
import sys
from urllib.parse import quote
import time

# Production backend URL
BACKEND_URL = "https://flowinvest-ai.onrender.com"

class ProductionCustomURLsTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
        
    def log_test(self, test_name, passed, details="", error=""):
        """Log test results"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_backend_health_check(self):
        """Test 1: Backend Health Check - Test /api/urls/health"""
        try:
            response = requests.get(f"{self.backend_url}/api/urls/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Backend Health Check (/api/urls/health)",
                    True,
                    f"Status: {data.get('status', 'unknown')}, Features: {data.get('features', [])}"
                )
                return data
            else:
                self.log_test(
                    "Backend Health Check (/api/urls/health)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Backend Health Check (/api/urls/health)",
                False,
                "",
                str(e)
            )
            return None

    def test_main_api_health(self):
        """Test 2: Main API Health Check"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                self.log_test(
                    "Main API Health Check (/api/health)",
                    True,
                    f"Services: {services}"
                )
                return data
            else:
                self.log_test(
                    "Main API Health Check (/api/health)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Main API Health Check (/api/health)",
                False,
                "",
                str(e)
            )
            return None

    def test_root_endpoint(self):
        """Test 3: Root Endpoint to Check Features"""
        try:
            response = requests.get(f"{self.backend_url}/api/", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                self.log_test(
                    "Root API Endpoint (/api/)",
                    True,
                    f"Features: {features}, Version: {data.get('version', 'unknown')}"
                )
                return data
            else:
                self.log_test(
                    "Root API Endpoint (/api/)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Root API Endpoint (/api/)",
                False,
                "",
                str(e)
            )
            return None

    def test_custom_urls_route_availability(self):
        """Test 4: Custom URLs Route Availability"""
        endpoints_to_test = [
            ("GET", "/api/urls/reserved-words"),
            ("POST", "/api/urls/validate-slug", {"slug": "test-slug"}),
            ("POST", "/api/urls/generate-slug", {"text": "Test User"})
        ]
        
        available_endpoints = 0
        
        for method, endpoint, *payload in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                elif method == "POST":
                    data = payload[0] if payload else {}
                    response = requests.post(f"{self.backend_url}{endpoint}", json=data, timeout=15)
                
                if response.status_code in [200, 400, 422]:  # 400/422 might be expected for validation
                    available_endpoints += 1
                    print(f"   ✅ {method} {endpoint} - HTTP {response.status_code}")
                else:
                    print(f"   ❌ {method} {endpoint} - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {method} {endpoint} - Error: {str(e)[:100]}")
        
        success = available_endpoints >= 2  # At least 2 out of 3 should work
        self.log_test(
            "Custom URLs Route Availability",
            success,
            f"{available_endpoints}/{len(endpoints_to_test)} endpoints accessible"
        )

    def test_public_user_url_flow_invest(self):
        """Test 5: Public User URL - Flow Invest"""
        try:
            # Test the specific user mentioned in the request
            encoded_name = quote("Flow Invest")
            response = requests.get(f"{self.backend_url}/api/urls/public/user/{encoded_name}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Public User URL - Flow Invest",
                    True,
                    f"User found: {data.get('display_name', 'unknown')}"
                )
                return data
            elif response.status_code == 404:
                self.log_test(
                    "Public User URL - Flow Invest",
                    False,
                    "User 'Flow Invest' not found in database",
                    "This might be why custom URLs aren't working - user doesn't exist"
                )
                return None
            else:
                self.log_test(
                    "Public User URL - Flow Invest",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Public User URL - Flow Invest",
                False,
                "",
                str(e)
            )
            return None

    def test_database_connectivity(self):
        """Test 6: Database Connectivity via Reserved Words"""
        try:
            response = requests.get(f"{self.backend_url}/api/urls/reserved-words", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                reserved_words = data.get('reserved_words', [])
                categories = data.get('categories', {})
                
                if len(reserved_words) > 0:
                    self.log_test(
                        "Database Connectivity (Reserved Words)",
                        True,
                        f"Retrieved {len(reserved_words)} reserved words, Categories: {list(categories.keys())}"
                    )
                    return True
                else:
                    self.log_test(
                        "Database Connectivity (Reserved Words)",
                        False,
                        "No reserved words found - database might be empty"
                    )
                    return False
            else:
                self.log_test(
                    "Database Connectivity (Reserved Words)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Database Connectivity (Reserved Words)",
                False,
                "",
                str(e)
            )
            return False

    def test_slug_validation_system(self):
        """Test 7: Slug Validation System"""
        test_cases = [
            ("valid-slug", True),
            ("admin", False),  # Should be reserved
            ("flow-invest", True),
            ("", False)  # Invalid empty slug
        ]
        
        working_validations = 0
        
        for slug, expected_valid in test_cases:
            try:
                payload = {"slug": slug}
                response = requests.post(f"{self.backend_url}/api/urls/validate-slug", json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get('valid', False)
                    
                    if (is_valid and expected_valid) or (not is_valid and not expected_valid):
                        working_validations += 1
                        print(f"   ✅ '{slug}' - Expected: {expected_valid}, Got: {is_valid}")
                    else:
                        print(f"   ❌ '{slug}' - Expected: {expected_valid}, Got: {is_valid}")
                        if not is_valid:
                            print(f"      Error: {data.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ '{slug}' - HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ '{slug}' - Error: {str(e)[:50]}")
        
        success = working_validations >= 2
        self.log_test(
            "Slug Validation System",
            success,
            f"{working_validations}/{len(test_cases)} validations working correctly"
        )

    def test_slug_generation(self):
        """Test 8: Slug Generation System"""
        test_names = [
            "Flow Invest",
            "Test User 123",
            "Special@Characters#Here"
        ]
        
        successful_generations = 0
        
        for name in test_names:
            try:
                payload = {"text": name}
                response = requests.post(f"{self.backend_url}/api/urls/generate-slug", json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    generated_slug = data.get('slug', '')
                    
                    if generated_slug and len(generated_slug) > 0:
                        successful_generations += 1
                        print(f"   ✅ '{name}' -> '{generated_slug}'")
                    else:
                        print(f"   ❌ '{name}' -> Empty slug")
                else:
                    print(f"   ❌ '{name}' - HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ '{name}' - Error: {str(e)[:50]}")
        
        success = successful_generations >= 2
        self.log_test(
            "Slug Generation System",
            success,
            f"{successful_generations}/{len(test_names)} slug generations successful"
        )

    def test_cors_configuration(self):
        """Test 9: CORS Configuration for Frontend"""
        try:
            # Test with OPTIONS request to check CORS headers
            response = requests.options(
                f"{self.backend_url}/api/urls/health",
                headers={
                    'Origin': 'https://f01i.app',
                    'Access-Control-Request-Method': 'GET'
                },
                timeout=15
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            has_cors = any(cors_headers.values())
            
            self.log_test(
                "CORS Configuration",
                has_cors,
                f"CORS headers present: {has_cors}, Origin allowed: {cors_headers.get('Access-Control-Allow-Origin', 'Not set')}"
            )
            
        except Exception as e:
            self.log_test(
                "CORS Configuration",
                False,
                "",
                str(e)
            )

    def run_all_tests(self):
        """Run all production tests"""
        print("=" * 80)
        print("PRODUCTION CUSTOM URLS BACKEND API TESTING")
        print("=" * 80)
        print(f"Testing against: {self.backend_url}")
        print(f"Target frontend: https://f01i.app")
        print()
        
        # Run all tests
        self.test_backend_health_check()
        self.test_main_api_health()
        self.test_root_endpoint()
        self.test_custom_urls_route_availability()
        self.test_public_user_url_flow_invest()
        self.test_database_connectivity()
        self.test_slug_validation_system()
        self.test_slug_generation()
        self.test_cors_configuration()
        
        # Print summary
        print("=" * 80)
        print("PRODUCTION TESTING SUMMARY")
        print("=" * 80)
        print(f"Tests Passed: {self.passed_tests}/{self.total_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print()
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print("FAILED TESTS:")
            for test in failed_tests:
                print(f"❌ {test['test']}")
                if test['error']:
                    print(f"   Error: {test['error']}")
                if test['details']:
                    print(f"   Details: {test['details']}")
            print()
        
        # Diagnostic summary
        print("DIAGNOSTIC SUMMARY:")
        print("=" * 40)
        
        # Check if custom URLs routes are loaded
        health_passed = any(r['test'] == "Backend Health Check (/api/urls/health)" and r['passed'] for r in self.test_results)
        if health_passed:
            print("✅ Custom URLs routes are loaded in production")
        else:
            print("❌ Custom URLs routes may not be loaded in production")
        
        # Check database connectivity
        db_passed = any(r['test'] == "Database Connectivity (Reserved Words)" and r['passed'] for r in self.test_results)
        if db_passed:
            print("✅ Production database connectivity working")
        else:
            print("❌ Production database connectivity issues detected")
        
        # Check Flow Invest user
        flow_invest_passed = any(r['test'] == "Public User URL - Flow Invest" and r['passed'] for r in self.test_results)
        if flow_invest_passed:
            print("✅ 'Flow Invest' user exists in production database")
        else:
            print("❌ 'Flow Invest' user not found - this may be why custom URLs aren't working")
        
        # Check API availability
        routes_passed = any(r['test'] == "Custom URLs Route Availability" and r['passed'] for r in self.test_results)
        if routes_passed:
            print("✅ Custom URLs API endpoints are accessible")
        else:
            print("❌ Custom URLs API endpoints may not be accessible")
        
        return self.passed_tests, self.total_tests, failed_tests

if __name__ == "__main__":
    tester = ProductionCustomURLsTest()
    passed, total, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Production Custom URLs API is fully operational!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED - Production Custom URLs API has issues")
        sys.exit(1)