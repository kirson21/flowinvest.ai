#!/usr/bin/env python3
"""
Frontend Custom URLs Integration Testing
========================================

This script tests the frontend integration to understand why custom URLs like 
https://f01i.app/Flow%20Invest aren't working despite the backend API being operational.

Testing both:
- Backend API: https://flowinvest-ai.onrender.com
- Frontend: https://f01i.app
"""

import requests
import json
import sys
from urllib.parse import quote
import time

# URLs
BACKEND_URL = "https://flowinvest-ai.onrender.com"
FRONTEND_URL = "https://f01i.app"

class FrontendCustomURLsTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.frontend_url = FRONTEND_URL
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

    def test_frontend_accessibility(self):
        """Test 1: Frontend Accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=30)
            
            if response.status_code == 200:
                content_length = len(response.text)
                has_react = "react" in response.text.lower() or "root" in response.text
                self.log_test(
                    "Frontend Accessibility",
                    True,
                    f"Frontend accessible, Content length: {content_length}, React app: {has_react}"
                )
                return True
            else:
                self.log_test(
                    "Frontend Accessibility",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Frontend Accessibility",
                False,
                "",
                str(e)
            )
            return False

    def test_custom_url_flow_invest(self):
        """Test 2: Custom URL - Flow Invest"""
        try:
            # Test the specific custom URL that should work
            response = requests.get(f"{self.frontend_url}/Flow%20Invest", timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                content = response.text
                # Check if it's showing the user profile or just the main app
                has_profile_content = any(keyword in content.lower() for keyword in [
                    "flow invest", "flowinvest", "profile", "bio", "seller"
                ])
                
                self.log_test(
                    "Custom URL - Flow Invest",
                    has_profile_content,
                    f"HTTP {response.status_code}, Profile content detected: {has_profile_content}"
                )
                return has_profile_content
            else:
                self.log_test(
                    "Custom URL - Flow Invest",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Custom URL - Flow Invest",
                False,
                "",
                str(e)
            )
            return False

    def test_frontend_backend_connection(self):
        """Test 3: Frontend-Backend Connection"""
        try:
            # Check if frontend can reach backend by testing a known working endpoint
            # This simulates what the frontend would do
            headers = {
                'Origin': self.frontend_url,
                'Referer': self.frontend_url
            }
            
            response = requests.get(
                f"{self.backend_url}/api/urls/public/user/Flow%20Invest", 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Frontend-Backend Connection",
                    True,
                    f"Backend accessible from frontend origin, User: {data.get('display_name', 'unknown')}"
                )
                return True
            else:
                self.log_test(
                    "Frontend-Backend Connection",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Frontend-Backend Connection",
                False,
                "",
                str(e)
            )
            return False

    def test_frontend_routing_system(self):
        """Test 4: Frontend Routing System"""
        test_routes = [
            "/",
            "/dashboard", 
            "/settings",
            "/marketplace"
        ]
        
        working_routes = 0
        
        for route in test_routes:
            try:
                response = requests.get(f"{self.frontend_url}{route}", timeout=15)
                
                if response.status_code == 200:
                    working_routes += 1
                    print(f"   ✅ {route} - HTTP {response.status_code}")
                else:
                    print(f"   ❌ {route} - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {route} - Error: {str(e)[:50]}")
        
        success = working_routes >= 2
        self.log_test(
            "Frontend Routing System",
            success,
            f"{working_routes}/{len(test_routes)} routes accessible"
        )

    def test_spa_routing_behavior(self):
        """Test 5: SPA Routing Behavior"""
        try:
            # Test if unknown routes return the main app (SPA behavior)
            response = requests.get(f"{self.frontend_url}/unknown-route-12345", timeout=30)
            
            if response.status_code == 200:
                content = response.text
                # Check if it returns the main React app instead of 404
                is_spa = any(keyword in content.lower() for keyword in [
                    "react", "root", "app", "div id", "script"
                ])
                
                self.log_test(
                    "SPA Routing Behavior",
                    is_spa,
                    f"Unknown route returns main app: {is_spa} (SPA routing working)"
                )
                return is_spa
            elif response.status_code == 404:
                self.log_test(
                    "SPA Routing Behavior",
                    False,
                    "Returns 404 for unknown routes - SPA routing may not be configured"
                )
                return False
            else:
                self.log_test(
                    "SPA Routing Behavior",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_test(
                "SPA Routing Behavior",
                False,
                "",
                str(e)
            )
            return False

    def test_backend_environment_variables(self):
        """Test 6: Backend Environment Variables"""
        try:
            # Check if backend has correct environment variables
            response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                supabase_connected = services.get('supabase') == 'connected'
                
                self.log_test(
                    "Backend Environment Variables",
                    supabase_connected,
                    f"Supabase connection: {services.get('supabase', 'unknown')}"
                )
                return supabase_connected
            else:
                self.log_test(
                    "Backend Environment Variables",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Backend Environment Variables",
                False,
                "",
                str(e)
            )
            return False

    def run_all_tests(self):
        """Run all frontend integration tests"""
        print("=" * 80)
        print("FRONTEND CUSTOM URLS INTEGRATION TESTING")
        print("=" * 80)
        print(f"Backend: {self.backend_url}")
        print(f"Frontend: {self.frontend_url}")
        print()
        
        # Run all tests
        self.test_frontend_accessibility()
        self.test_custom_url_flow_invest()
        self.test_frontend_backend_connection()
        self.test_frontend_routing_system()
        self.test_spa_routing_behavior()
        self.test_backend_environment_variables()
        
        # Print summary
        print("=" * 80)
        print("FRONTEND INTEGRATION TESTING SUMMARY")
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
        
        # Root cause analysis
        print("ROOT CAUSE ANALYSIS:")
        print("=" * 40)
        
        frontend_accessible = any(r['test'] == "Frontend Accessibility" and r['passed'] for r in self.test_results)
        custom_url_working = any(r['test'] == "Custom URL - Flow Invest" and r['passed'] for r in self.test_results)
        spa_routing = any(r['test'] == "SPA Routing Behavior" and r['passed'] for r in self.test_results)
        backend_connection = any(r['test'] == "Frontend-Backend Connection" and r['passed'] for r in self.test_results)
        
        if not frontend_accessible:
            print("❌ CRITICAL: Frontend is not accessible - this is the primary issue")
        elif not spa_routing:
            print("❌ LIKELY CAUSE: SPA routing not configured - custom URLs won't work without client-side routing")
        elif not backend_connection:
            print("❌ LIKELY CAUSE: Frontend cannot connect to backend - CORS or network issues")
        elif not custom_url_working:
            print("❌ LIKELY CAUSE: Frontend routing logic not implemented for custom URLs")
        else:
            print("✅ All systems operational - custom URLs should be working")
        
        print()
        print("RECOMMENDATIONS:")
        print("=" * 40)
        
        if not frontend_accessible:
            print("1. Check frontend deployment status on Vercel")
            print("2. Verify domain configuration for f01i.app")
            print("3. Check DNS settings")
        elif not spa_routing:
            print("1. Configure SPA routing in Vercel (rewrites for React Router)")
            print("2. Add _redirects or vercel.json configuration")
            print("3. Ensure all routes serve index.html")
        elif not backend_connection:
            print("1. Verify CORS configuration in backend")
            print("2. Check REACT_APP_BACKEND_URL in frontend environment")
            print("3. Test API calls from browser console")
        else:
            print("1. Check React Router configuration for custom URL patterns")
            print("2. Verify frontend logic for parsing custom URLs")
            print("3. Test custom URL detection in browser developer tools")
        
        return self.passed_tests, self.total_tests, failed_tests

if __name__ == "__main__":
    tester = FrontendCustomURLsTest()
    passed, total, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed >= total - 1:  # Allow 1 failure
        print(f"\n✅ MOSTLY SUCCESSFUL - {passed}/{total} tests passed")
        sys.exit(0)
    else:
        print(f"\n⚠️  MULTIPLE ISSUES DETECTED - {total - passed} tests failed")
        sys.exit(1)