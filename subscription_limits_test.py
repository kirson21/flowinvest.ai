#!/usr/bin/env python3
"""
Backend Testing Suite for Bot Creation Subscription Limits
Testing the subscription limit checking implementation for AI and manual bot creation.
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://investai-hub.preview.emergentagent.com/api"
SUPER_ADMIN_UUID = "cd0e9717-f85d-4726-81e9-f260394ead58"
TEST_USER_UUID = "test-user-12345"  # Regular user for testing

class BotSubscriptionLimitTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.super_admin_id = SUPER_ADMIN_UUID
        self.test_user_id = TEST_USER_UUID
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {}
        }
        
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        url = f"{self.backend_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}
                
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": response.status_code < 400
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
        except json.JSONDecodeError as e:
            return {"error": f"JSON decode error: {e}", "success": False}
    
    def test_backend_health(self):
        """Test basic backend connectivity"""
        print("=== BACKEND HEALTH CHECK ===")
        
        # Test API root
        result = self.make_request("GET", "/")
        if result.get("success") and result.get("status_code") == 200:
            self.log_test("Backend API Root", True, "API root endpoint accessible", result.get("data"))
        else:
            self.log_test("Backend API Root", False, f"API root failed: {result.get('error', 'Unknown error')}", result)
            
        # Test health endpoint
        result = self.make_request("GET", "/health")
        if result.get("success") and result.get("status_code") == 200:
            self.log_test("Backend Health Check", True, "Health endpoint working", result.get("data"))
        else:
            self.log_test("Backend Health Check", False, f"Health check failed: {result.get('error', 'Unknown error')}", result)
            
        # Test auth health
        result = self.make_request("GET", "/auth/health")
        if result.get("success") and result.get("status_code") == 200:
            data = result.get("data", {})
            supabase_connected = data.get("supabase_connected", False)
            self.log_test("Auth Health Check", True, f"Auth service healthy, Supabase connected: {supabase_connected}", data)
        else:
            self.log_test("Auth Health Check", False, f"Auth health failed: {result.get('error', 'Unknown error')}", result)
    
    def test_subscription_limits_endpoint(self):
        """Test subscription limits retrieval endpoint"""
        print("=== SUBSCRIPTION LIMITS ENDPOINT TESTS ===")
        
        # Test Super Admin limits
        result = self.make_request("GET", f"/auth/user/{self.super_admin_id}/subscription/limits")
        if result.get("success") and result.get("status_code") == 200:
            data = result.get("data", {})
            subscription = data.get("subscription", {})
            is_super_admin = subscription.get("is_super_admin", False)
            limits = subscription.get("limits")
            
            if is_super_admin and limits is None:
                self.log_test("Super Admin Subscription Limits", True, "Super Admin has unlimited access", data)
            else:
                self.log_test("Super Admin Subscription Limits", False, f"Super Admin limits incorrect: is_super_admin={is_super_admin}, limits={limits}", data)
        else:
            self.log_test("Super Admin Subscription Limits", False, f"Failed to get super admin limits: {result.get('error', 'Unknown error')}", result)
        
        # Test Regular User limits (should default to free plan)
        result = self.make_request("GET", f"/auth/user/{self.test_user_id}/subscription/limits")
        if result.get("success") and result.get("status_code") == 200:
            data = result.get("data", {})
            subscription = data.get("subscription", {})
            plan_type = subscription.get("plan_type")
            limits = subscription.get("limits", {})
            
            expected_free_limits = {"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1}
            
            if plan_type == "free" and limits.get("ai_bots") == 1 and limits.get("manual_bots") == 2:
                self.log_test("Regular User Free Plan Limits", True, "Free plan limits correctly set", data)
            else:
                self.log_test("Regular User Free Plan Limits", False, f"Free plan limits incorrect: plan={plan_type}, limits={limits}", data)
        else:
            self.log_test("Regular User Free Plan Limits", False, f"Failed to get regular user limits: {result.get('error', 'Unknown error')}", result)
    
    def test_ai_bot_limit_checking(self):
        """Test AI bot creation limit checking"""
        print("=== AI BOT LIMIT CHECKING TESTS ===")
        
        # Test scenarios for free user
        test_scenarios = [
            {"current_count": 0, "expected_can_create": True, "description": "Free user creating first AI bot (0/1)"},
            {"current_count": 1, "expected_can_create": False, "description": "Free user creating second AI bot (1/1) - should deny"}
        ]
        
        for scenario in test_scenarios:
            data = {
                "resource_type": "ai_bots",
                "current_count": scenario["current_count"]
            }
            
            result = self.make_request("POST", f"/auth/user/{self.test_user_id}/subscription/check-limit", data)
            
            if result.get("success") and result.get("status_code") == 200:
                response_data = result.get("data", {})
                can_create = response_data.get("can_create")
                limit_reached = response_data.get("limit_reached")
                current_count = response_data.get("current_count")
                limit = response_data.get("limit")
                
                if (can_create == scenario["expected_can_create"] and 
                    limit_reached == (not scenario["expected_can_create"]) and
                    current_count == scenario["current_count"] and
                    limit == 1):
                    self.log_test(f"AI Bot Limit Check - {scenario['description']}", True, 
                                f"Correct response: can_create={can_create}, limit_reached={limit_reached}", response_data)
                else:
                    self.log_test(f"AI Bot Limit Check - {scenario['description']}", False, 
                                f"Incorrect response: can_create={can_create}, expected={scenario['expected_can_create']}", response_data)
            else:
                self.log_test(f"AI Bot Limit Check - {scenario['description']}", False, 
                            f"Request failed: {result.get('error', 'Unknown error')}", result)
    
    def test_manual_bot_limit_checking(self):
        """Test manual bot creation limit checking"""
        print("=== MANUAL BOT LIMIT CHECKING TESTS ===")
        
        # Test scenarios for free user
        test_scenarios = [
            {"current_count": 0, "expected_can_create": True, "description": "Free user creating first manual bot (0/2)"},
            {"current_count": 1, "expected_can_create": True, "description": "Free user creating second manual bot (1/2)"},
            {"current_count": 2, "expected_can_create": False, "description": "Free user creating third manual bot (2/2) - should deny"}
        ]
        
        for scenario in test_scenarios:
            data = {
                "resource_type": "manual_bots",
                "current_count": scenario["current_count"]
            }
            
            result = self.make_request("POST", f"/auth/user/{self.test_user_id}/subscription/check-limit", data)
            
            if result.get("success") and result.get("status_code") == 200:
                response_data = result.get("data", {})
                can_create = response_data.get("can_create")
                limit_reached = response_data.get("limit_reached")
                current_count = response_data.get("current_count")
                limit = response_data.get("limit")
                
                if (can_create == scenario["expected_can_create"] and 
                    limit_reached == (not scenario["expected_can_create"]) and
                    current_count == scenario["current_count"] and
                    limit == 2):
                    self.log_test(f"Manual Bot Limit Check - {scenario['description']}", True, 
                                f"Correct response: can_create={can_create}, limit_reached={limit_reached}", response_data)
                else:
                    self.log_test(f"Manual Bot Limit Check - {scenario['description']}", False, 
                                f"Incorrect response: can_create={can_create}, expected={scenario['expected_can_create']}", response_data)
            else:
                self.log_test(f"Manual Bot Limit Check - {scenario['description']}", False, 
                            f"Request failed: {result.get('error', 'Unknown error')}", result)
    
    def test_super_admin_unlimited_access(self):
        """Test Super Admin unlimited bot creation access"""
        print("=== SUPER ADMIN UNLIMITED ACCESS TESTS ===")
        
        # Test AI bots for Super Admin with high count
        test_scenarios = [
            {"resource_type": "ai_bots", "current_count": 10, "description": "Super Admin creating 10th AI bot"},
            {"resource_type": "manual_bots", "current_count": 15, "description": "Super Admin creating 15th manual bot"}
        ]
        
        for scenario in test_scenarios:
            data = {
                "resource_type": scenario["resource_type"],
                "current_count": scenario["current_count"]
            }
            
            result = self.make_request("POST", f"/auth/user/{self.super_admin_id}/subscription/check-limit", data)
            
            if result.get("success") and result.get("status_code") == 200:
                response_data = result.get("data", {})
                can_create = response_data.get("can_create")
                limit_reached = response_data.get("limit_reached")
                limit = response_data.get("limit")
                is_super_admin = response_data.get("is_super_admin")
                
                if (can_create == True and 
                    limit_reached == False and
                    limit == -1 and
                    is_super_admin == True):
                    self.log_test(f"Super Admin Unlimited - {scenario['description']}", True, 
                                f"Super Admin has unlimited access: can_create={can_create}, limit={limit}", response_data)
                else:
                    self.log_test(f"Super Admin Unlimited - {scenario['description']}", False, 
                                f"Super Admin access incorrect: can_create={can_create}, limit={limit}, is_super_admin={is_super_admin}", response_data)
            else:
                self.log_test(f"Super Admin Unlimited - {scenario['description']}", False, 
                            f"Request failed: {result.get('error', 'Unknown error')}", result)
    
    def test_subscription_plans_endpoint(self):
        """Test subscription plans endpoint"""
        print("=== SUBSCRIPTION PLANS ENDPOINT TEST ===")
        
        result = self.make_request("GET", "/auth/subscription/plans")
        
        if result.get("success") and result.get("status_code") == 200:
            data = result.get("data", {})
            plans = data.get("plans", [])
            
            # Check if we have the expected plans
            plan_ids = [plan.get("id") for plan in plans]
            expected_plans = ["free", "plus", "pro"]
            
            if all(plan_id in plan_ids for plan_id in expected_plans):
                # Check free plan limits
                free_plan = next((plan for plan in plans if plan.get("id") == "free"), None)
                if free_plan:
                    limitations = free_plan.get("limitations", {})
                    if limitations.get("ai_bots") == 1 and limitations.get("manual_bots") == 2:
                        self.log_test("Subscription Plans Endpoint", True, 
                                    f"All expected plans available with correct free plan limits", data)
                    else:
                        self.log_test("Subscription Plans Endpoint", False, 
                                    f"Free plan limits incorrect: {limitations}", data)
                else:
                    self.log_test("Subscription Plans Endpoint", False, "Free plan not found", data)
            else:
                self.log_test("Subscription Plans Endpoint", False, 
                            f"Missing expected plans. Found: {plan_ids}, Expected: {expected_plans}", data)
        else:
            self.log_test("Subscription Plans Endpoint", False, 
                        f"Request failed: {result.get('error', 'Unknown error')}", result)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("=== EDGE CASES AND ERROR HANDLING ===")
        
        # Test with invalid user ID
        result = self.make_request("POST", "/auth/user/invalid-uuid/subscription/check-limit", 
                                 {"resource_type": "ai_bots", "current_count": 0})
        
        if result.get("success") and result.get("status_code") == 200:
            # Should still work and default to free plan
            data = result.get("data", {})
            if data.get("plan_type") == "free":
                self.log_test("Invalid User ID Edge Case", True, 
                            "Invalid user ID defaults to free plan", data)
            else:
                self.log_test("Invalid User ID Edge Case", False, 
                            f"Invalid user ID handling incorrect: {data}", data)
        else:
            self.log_test("Invalid User ID Edge Case", False, 
                        f"Request failed: {result.get('error', 'Unknown error')}", result)
        
        # Test with invalid resource type
        result = self.make_request("POST", f"/auth/user/{self.test_user_id}/subscription/check-limit", 
                                 {"resource_type": "invalid_resource", "current_count": 0})
        
        if result.get("success") and result.get("status_code") == 200:
            data = result.get("data", {})
            # Should default to limit of 1 for unknown resource types
            if data.get("limit") == 1:
                self.log_test("Invalid Resource Type Edge Case", True, 
                            "Invalid resource type defaults to limit of 1", data)
            else:
                self.log_test("Invalid Resource Type Edge Case", False, 
                            f"Invalid resource type handling incorrect: {data}", data)
        else:
            self.log_test("Invalid Resource Type Edge Case", False, 
                        f"Request failed: {result.get('error', 'Unknown error')}", result)
    
    def run_all_tests(self):
        """Run all subscription limit tests"""
        print("🚀 STARTING BOT CREATION SUBSCRIPTION LIMITS TESTING")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_backend_health()
        self.test_subscription_limits_endpoint()
        self.test_ai_bot_limit_checking()
        self.test_manual_bot_limit_checking()
        self.test_super_admin_unlimited_access()
        self.test_subscription_plans_endpoint()
        self.test_edge_cases()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("=" * 60)
        print("🏁 TESTING COMPLETE")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Results: {self.passed_tests}/{self.total_tests} tests passed")
        print(f"✅ Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("❌ SOME TESTS FAILED")
            failed_tests = [test for test in self.test_results if not test["success"]]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
            return False

def main():
    """Main test execution"""
    tester = BotSubscriptionLimitTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()