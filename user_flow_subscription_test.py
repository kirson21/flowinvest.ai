#!/usr/bin/env python3
"""
USER FLOW SUBSCRIPTION LIMITS TESTING
=====================================

Testing the actual user flow that might be bypassing subscription limits.
This test simulates how a user might have been able to create 6 bots.
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://crypto-payment-fix-2.preview.emergentagent.com/api"

class UserFlowSubscriptionTest:
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
    
    def test_user_subscription_creation(self, user_id):
        """Test if user gets proper subscription on first access"""
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    subscription = data.get('subscription', {})
                    plan_type = subscription.get('plan_type')
                    limits = subscription.get('limits', {})
                    
                    if plan_type == 'free' and limits.get('ai_bots') == 1 and limits.get('manual_bots') == 2:
                        self.log_test("User Subscription Creation", True, 
                                    f"Free plan created with correct limits: AI={limits.get('ai_bots')}, Manual={limits.get('manual_bots')}")
                        return True
                    else:
                        self.log_test("User Subscription Creation", False, 
                                    f"Incorrect subscription: plan={plan_type}, limits={limits}", True)
                        return False
                else:
                    self.log_test("User Subscription Creation", False, 
                                f"API error: {data.get('message')}", True)
                    return False
            else:
                self.log_test("User Subscription Creation", False, 
                            f"HTTP {response.status_code}: {response.text}", True)
                return False
                
        except Exception as e:
            self.log_test("User Subscription Creation", False, 
                        f"Request error: {str(e)}", True)
            return False
    
    def test_super_admin_bypass(self):
        """Test if super admin UUID bypasses limits correctly"""
        super_admin_id = "cd0e9717-f85d-4726-81e9-f260394ead58"
        
        try:
            url = f"{self.backend_url}/auth/user/{super_admin_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots",
                "current_count": 10  # Way over normal limits
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('can_create') == True and data.get('limit') == -1 and data.get('plan_type') == 'super_admin':
                    self.log_test("Super Admin Bypass", True, 
                                f"Super admin correctly bypasses limits: can_create={data.get('can_create')}, limit={data.get('limit')}")
                    return True
                else:
                    self.log_test("Super Admin Bypass", False, 
                                f"Super admin not working correctly: {data}", True)
                    return False
            else:
                self.log_test("Super Admin Bypass", False, 
                            f"HTTP {response.status_code}: {response.text}", True)
                return False
                
        except Exception as e:
            self.log_test("Super Admin Bypass", False, 
                        f"Request error: {str(e)}", True)
            return False
    
    def test_potential_bypass_scenarios(self, user_id):
        """Test potential ways users might bypass limits"""
        
        # Test 1: What if frontend doesn't send current_count?
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots"
                # Missing current_count
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current_count = data.get('current_count', 'missing')
                
                if current_count == 0:  # Default value
                    self.log_test("Missing current_count Test", True, 
                                f"Backend defaults to current_count=0 when missing")
                else:
                    self.log_test("Missing current_count Test", False, 
                                f"Unexpected current_count handling: {current_count}", True)
            else:
                self.log_test("Missing current_count Test", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Missing current_count Test", False, 
                        f"Request error: {str(e)}")
        
        # Test 2: What if frontend sends negative current_count?
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots",
                "current_count": -1
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                can_create = data.get('can_create')
                
                if can_create == True:  # This would be a bug
                    self.log_test("Negative current_count Test", False, 
                                f"CRITICAL: Negative count allows creation: {data}", True)
                else:
                    self.log_test("Negative current_count Test", True, 
                                f"Negative count properly handled: can_create={can_create}")
            else:
                self.log_test("Negative current_count Test", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Negative current_count Test", False, 
                        f"Request error: {str(e)}")
        
        # Test 3: What if user has no subscription record?
        new_user_id = str(uuid.uuid4())
        try:
            url = f"{self.backend_url}/auth/user/{new_user_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots",
                "current_count": 5  # Way over limit
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('plan_type') == 'free' and data.get('limit') == 1 and data.get('can_create') == False:
                    self.log_test("No Subscription Record Test", True, 
                                f"New user defaults to free plan with proper limits")
                else:
                    self.log_test("No Subscription Record Test", False, 
                                f"New user not handled correctly: {data}", True)
            else:
                self.log_test("No Subscription Record Test", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("No Subscription Record Test", False, 
                        f"Request error: {str(e)}")
    
    def test_realistic_user_scenario(self):
        """Test with a realistic user scenario"""
        # Create a realistic user ID
        realistic_user_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        
        print("🧪 Testing Realistic User Scenario")
        print("-" * 40)
        
        # Step 1: Check if user gets proper subscription
        self.test_user_subscription_creation(realistic_user_id)
        
        # Step 2: Test creating first AI bot (should be allowed)
        try:
            url = f"{self.backend_url}/auth/user/{realistic_user_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots",
                "current_count": 0
            }
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get('can_create') == True:
                self.log_test("First AI Bot Creation", True, 
                            f"User can create first AI bot: {data.get('can_create')}")
            else:
                self.log_test("First AI Bot Creation", False, 
                            f"User cannot create first AI bot: {data}", True)
        except Exception as e:
            self.log_test("First AI Bot Creation", False, f"Error: {str(e)}", True)
        
        # Step 3: Test creating second AI bot (should be denied)
        try:
            url = f"{self.backend_url}/auth/user/{realistic_user_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots",
                "current_count": 1
            }
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get('can_create') == False and data.get('limit_reached') == True:
                self.log_test("Second AI Bot Creation", True, 
                            f"User correctly denied second AI bot: can_create={data.get('can_create')}")
            else:
                self.log_test("Second AI Bot Creation", False, 
                            f"CRITICAL: User allowed second AI bot: {data}", True)
        except Exception as e:
            self.log_test("Second AI Bot Creation", False, f"Error: {str(e)}", True)
        
        # Step 4: Test manual bots (should allow 2)
        for count in [0, 1, 2]:
            try:
                url = f"{self.backend_url}/auth/user/{realistic_user_id}/subscription/check-limit"
                payload = {
                    "resource_type": "manual_bots",
                    "current_count": count
                }
                
                response = requests.post(url, json=payload, timeout=10)
                data = response.json()
                
                expected_can_create = count < 2
                if data.get('can_create') == expected_can_create:
                    self.log_test(f"Manual Bot {count+1} Creation", True, 
                                f"Manual bot creation correctly handled: can_create={data.get('can_create')}")
                else:
                    self.log_test(f"Manual Bot {count+1} Creation", False, 
                                f"CRITICAL: Manual bot logic wrong: {data}", True)
            except Exception as e:
                self.log_test(f"Manual Bot {count+1} Creation", False, f"Error: {str(e)}", True)
    
    def run_comprehensive_test(self):
        """Run comprehensive user flow testing"""
        print("🔍 USER FLOW SUBSCRIPTION LIMITS TESTING")
        print("=" * 60)
        print("Testing how a user might have bypassed subscription limits")
        print("=" * 60)
        print()
        
        # Test super admin bypass
        self.test_super_admin_bypass()
        print()
        
        # Test realistic user scenario
        self.test_realistic_user_scenario()
        print()
        
        # Test potential bypass scenarios
        test_user_id = str(uuid.uuid4())
        print("🔍 Testing Potential Bypass Scenarios")
        print("-" * 40)
        self.test_potential_bypass_scenarios(test_user_id)
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
        else:
            print("✅ No critical issues found in backend logic")
            print("🤔 The issue might be in frontend implementation or user flow")
        
        return critical_failures == 0

def main():
    """Main test execution"""
    tester = UserFlowSubscriptionTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ BACKEND LOGIC IS CORRECT")
        print("💡 The issue is likely in the frontend implementation:")
        print("   - Frontend might not be calling the check-limit endpoint")
        print("   - Frontend might be ignoring the can_create response")
        print("   - Frontend might have a bug in counting current bots")
        print("   - User might be using super admin account unknowingly")
    else:
        print("\n❌ CRITICAL BACKEND ISSUES FOUND")
    
    return success

if __name__ == "__main__":
    main()