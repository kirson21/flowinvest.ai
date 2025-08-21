#!/usr/bin/env python3
"""
URGENT SUBSCRIPTION LIMITS TESTING
===================================

Testing the critical subscription limits bug where a free user was able to create 
6 bots (3 AI + 3 manual) when they should only be allowed 1 AI + 2 manual.

This test will verify:
1. Backend subscription limit checking endpoints
2. Free plan limits enforcement (1 AI bot, 2 manual bots)
3. Proper can_create and limit_reached responses
4. Edge cases with different current_count values
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://f01i-crypto.preview.emergentagent.com/api"

class SubscriptionLimitsTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.critical_issues = []
        
    def log_test(self, test_name, success, details, is_critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "critical": is_critical
        }
        self.test_results.append(result)
        
        if is_critical and not success:
            self.critical_issues.append(result)
        
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_backend_health(self):
        """Test basic backend connectivity"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"HTTP {response.status_code}", True)
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}", True)
            return False
    
    def test_subscription_limit_endpoint_ai_bots(self, user_id, current_count):
        """Test AI bots limit checking"""
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots",
                "current_count": current_count
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # For free users, AI bots limit should be 1
                expected_limit = 1
                expected_can_create = current_count < expected_limit
                expected_limit_reached = current_count >= expected_limit
                
                # Verify response structure
                required_fields = ['success', 'can_create', 'limit_reached', 'current_count', 'limit', 'plan_type']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(f"AI Bots Limit Check (count={current_count})", False, 
                                f"Missing fields: {missing_fields}", True)
                    return False
                
                # Verify logic
                issues = []
                if data.get('limit') != expected_limit:
                    issues.append(f"Expected limit {expected_limit}, got {data.get('limit')}")
                
                if data.get('can_create') != expected_can_create:
                    issues.append(f"Expected can_create {expected_can_create}, got {data.get('can_create')}")
                
                if data.get('limit_reached') != expected_limit_reached:
                    issues.append(f"Expected limit_reached {expected_limit_reached}, got {data.get('limit_reached')}")
                
                if data.get('current_count') != current_count:
                    issues.append(f"Expected current_count {current_count}, got {data.get('current_count')}")
                
                if data.get('plan_type') != 'free':
                    issues.append(f"Expected plan_type 'free', got {data.get('plan_type')}")
                
                if issues:
                    self.log_test(f"AI Bots Limit Check (count={current_count})", False, 
                                f"Logic errors: {'; '.join(issues)}", True)
                    return False
                else:
                    self.log_test(f"AI Bots Limit Check (count={current_count})", True, 
                                f"can_create={data.get('can_create')}, limit_reached={data.get('limit_reached')}, limit={data.get('limit')}")
                    return True
            else:
                self.log_test(f"AI Bots Limit Check (count={current_count})", False, 
                            f"HTTP {response.status_code}: {response.text}", True)
                return False
                
        except Exception as e:
            self.log_test(f"AI Bots Limit Check (count={current_count})", False, 
                        f"Request error: {str(e)}", True)
            return False
    
    def test_subscription_limit_endpoint_manual_bots(self, user_id, current_count):
        """Test manual bots limit checking"""
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
            payload = {
                "resource_type": "manual_bots",
                "current_count": current_count
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # For free users, manual bots limit should be 2
                expected_limit = 2
                expected_can_create = current_count < expected_limit
                expected_limit_reached = current_count >= expected_limit
                
                # Verify response structure
                required_fields = ['success', 'can_create', 'limit_reached', 'current_count', 'limit', 'plan_type']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(f"Manual Bots Limit Check (count={current_count})", False, 
                                f"Missing fields: {missing_fields}", True)
                    return False
                
                # Verify logic
                issues = []
                if data.get('limit') != expected_limit:
                    issues.append(f"Expected limit {expected_limit}, got {data.get('limit')}")
                
                if data.get('can_create') != expected_can_create:
                    issues.append(f"Expected can_create {expected_can_create}, got {data.get('can_create')}")
                
                if data.get('limit_reached') != expected_limit_reached:
                    issues.append(f"Expected limit_reached {expected_limit_reached}, got {data.get('limit_reached')}")
                
                if data.get('current_count') != current_count:
                    issues.append(f"Expected current_count {current_count}, got {data.get('current_count')}")
                
                if data.get('plan_type') != 'free':
                    issues.append(f"Expected plan_type 'free', got {data.get('plan_type')}")
                
                if issues:
                    self.log_test(f"Manual Bots Limit Check (count={current_count})", False, 
                                f"Logic errors: {'; '.join(issues)}", True)
                    return False
                else:
                    self.log_test(f"Manual Bots Limit Check (count={current_count})", True, 
                                f"can_create={data.get('can_create')}, limit_reached={data.get('limit_reached')}, limit={data.get('limit')}")
                    return True
            else:
                self.log_test(f"Manual Bots Limit Check (count={current_count})", False, 
                            f"HTTP {response.status_code}: {response.text}", True)
                return False
                
        except Exception as e:
            self.log_test(f"Manual Bots Limit Check (count={current_count})", False, 
                        f"Request error: {str(e)}", True)
            return False
    
    def test_subscription_limits_overview(self, user_id):
        """Test subscription limits overview endpoint"""
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/limits"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Subscription Limits Overview", False, 
                                f"API returned success=false: {data.get('message')}", True)
                    return False
                
                subscription = data.get('subscription', {})
                limits = subscription.get('limits', {})
                
                # For free users, verify default limits
                expected_limits = {
                    "ai_bots": 1,
                    "manual_bots": 2,
                    "marketplace_products": 1
                }
                
                issues = []
                for resource, expected_limit in expected_limits.items():
                    actual_limit = limits.get(resource)
                    if actual_limit != expected_limit:
                        issues.append(f"{resource}: expected {expected_limit}, got {actual_limit}")
                
                if subscription.get('plan_type') != 'free':
                    issues.append(f"Expected plan_type 'free', got {subscription.get('plan_type')}")
                
                if issues:
                    self.log_test("Subscription Limits Overview", False, 
                                f"Limit errors: {'; '.join(issues)}", True)
                    return False
                else:
                    self.log_test("Subscription Limits Overview", True, 
                                f"Free plan limits: AI={limits.get('ai_bots')}, Manual={limits.get('manual_bots')}")
                    return True
            else:
                self.log_test("Subscription Limits Overview", False, 
                            f"HTTP {response.status_code}: {response.text}", True)
                return False
                
        except Exception as e:
            self.log_test("Subscription Limits Overview", False, 
                        f"Request error: {str(e)}", True)
            return False
    
    def test_edge_cases(self, user_id):
        """Test edge cases and boundary conditions"""
        print("🔍 Testing Edge Cases and Boundary Conditions")
        print("=" * 60)
        
        # Test AI bots at boundary conditions
        test_cases = [
            (0, True, False),   # 0 bots - should allow creation
            (1, False, True),   # 1 bot - should NOT allow creation (limit reached)
            (2, False, True),   # 2 bots - should NOT allow creation (over limit)
            (3, False, True),   # 3 bots - should NOT allow creation (way over limit)
        ]
        
        ai_success = True
        for current_count, expected_can_create, expected_limit_reached in test_cases:
            if not self.test_subscription_limit_endpoint_ai_bots(user_id, current_count):
                ai_success = False
        
        # Test manual bots at boundary conditions
        manual_test_cases = [
            (0, True, False),   # 0 bots - should allow creation
            (1, True, False),   # 1 bot - should allow creation
            (2, False, True),   # 2 bots - should NOT allow creation (limit reached)
            (3, False, True),   # 3 bots - should NOT allow creation (over limit)
        ]
        
        manual_success = True
        for current_count, expected_can_create, expected_limit_reached in manual_test_cases:
            if not self.test_subscription_limit_endpoint_manual_bots(user_id, current_count):
                manual_success = False
        
        return ai_success and manual_success
    
    def test_problematic_user_scenario(self):
        """Test the exact scenario reported: user with 6 bots (3 AI + 3 manual)"""
        print("🚨 Testing Problematic User Scenario: 6 Bots Created")
        print("=" * 60)
        
        # Create a test user ID (simulating the problematic user)
        test_user_id = str(uuid.uuid4())
        
        # Test with the reported counts
        ai_result = self.test_subscription_limit_endpoint_ai_bots(test_user_id, 3)  # 3 AI bots
        manual_result = self.test_subscription_limit_endpoint_manual_bots(test_user_id, 3)  # 3 manual bots
        
        # Both should return can_create=False and limit_reached=True
        return ai_result and manual_result
    
    def run_comprehensive_test(self):
        """Run comprehensive subscription limits testing"""
        print("🔥 URGENT: SUBSCRIPTION LIMITS TESTING")
        print("=" * 60)
        print("Testing critical bug: Free user created 6 bots instead of max 3")
        print("Expected limits: 1 AI bot + 2 manual bots = 3 total")
        print("=" * 60)
        print()
        
        # Test backend connectivity first
        if not self.test_backend_health():
            print("❌ Backend not accessible - cannot continue testing")
            return False
        
        # Create test user
        test_user_id = str(uuid.uuid4())
        print(f"🧪 Using test user ID: {test_user_id}")
        print()
        
        # Test subscription limits overview
        print("📋 Testing Subscription Limits Overview")
        print("-" * 40)
        self.test_subscription_limits_overview(test_user_id)
        print()
        
        # Test edge cases
        edge_cases_success = self.test_edge_cases(test_user_id)
        print()
        
        # Test problematic scenario
        problematic_scenario_success = self.test_problematic_user_scenario()
        print()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        critical_failures = len(self.critical_issues)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Critical Failures: {critical_failures}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if self.critical_issues:
            print("🚨 CRITICAL ISSUES FOUND:")
            print("-" * 30)
            for issue in self.critical_issues:
                print(f"❌ {issue['test']}: {issue['details']}")
            print()
        
        # Detailed results
        print("📋 DETAILED RESULTS:")
        print("-" * 30)
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        return critical_failures == 0

def main():
    """Main test execution"""
    tester = SubscriptionLimitsTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ ALL TESTS PASSED - Subscription limits are working correctly")
        exit(0)
    else:
        print("\n❌ CRITICAL ISSUES FOUND - Subscription limits are broken")
        exit(1)

if __name__ == "__main__":
    main()