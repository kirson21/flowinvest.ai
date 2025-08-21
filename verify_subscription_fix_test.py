#!/usr/bin/env python3
"""
VERIFY SUBSCRIPTION FIX TEST
============================

Verify that the subscription limits bug has been fixed.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://botfolio-1.preview.emergentagent.com/api"

class VerifySubscriptionFixTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_negative_count_blocked(self, user_id, resource_type, negative_count):
        """Test that negative counts are now blocked"""
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
            payload = {
                "resource_type": resource_type,
                "current_count": negative_count
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should now return success=False and can_create=False
                if (data.get('success') == False and 
                    data.get('can_create') == False and 
                    'Invalid current_count' in data.get('message', '')):
                    self.log_test(f"Negative Count Blocked ({resource_type}, count={negative_count})", True, 
                                f"Negative count properly blocked: {data.get('message')}")
                    return True
                else:
                    self.log_test(f"Negative Count Blocked ({resource_type}, count={negative_count})", False, 
                                f"Fix not working: {data}")
                    return False
            else:
                self.log_test(f"Negative Count Blocked ({resource_type}, count={negative_count})", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"Negative Count Blocked ({resource_type}, count={negative_count})", False, 
                        f"Request error: {str(e)}")
            return False
    
    def test_normal_limits_still_work(self, user_id):
        """Test that normal subscription limits still work correctly"""
        
        # Test AI bots - should allow 0, block 1+
        test_cases = [
            ("ai_bots", 0, True),   # Should allow
            ("ai_bots", 1, False),  # Should block
            ("manual_bots", 0, True),   # Should allow
            ("manual_bots", 1, True),   # Should allow
            ("manual_bots", 2, False),  # Should block
        ]
        
        all_passed = True
        for resource_type, current_count, expected_can_create in test_cases:
            try:
                url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
                payload = {
                    "resource_type": resource_type,
                    "current_count": current_count
                }
                
                response = requests.post(url, json=payload, timeout=10)
                data = response.json()
                
                actual_can_create = data.get('can_create')
                if actual_can_create == expected_can_create:
                    self.log_test(f"Normal Limits ({resource_type}, count={current_count})", True, 
                                f"can_create={actual_can_create} (expected {expected_can_create})")
                else:
                    self.log_test(f"Normal Limits ({resource_type}, count={current_count})", False, 
                                f"can_create={actual_can_create}, expected {expected_can_create}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Normal Limits ({resource_type}, count={current_count})", False, 
                            f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_verification_test(self):
        """Run verification test"""
        print("🔧 VERIFYING SUBSCRIPTION LIMITS FIX")
        print("=" * 50)
        print("Testing that the negative count exploit has been fixed")
        print("=" * 50)
        print()
        
        user_id = str(uuid.uuid4())
        
        # Test that negative counts are blocked
        print("1. Testing Negative Count Blocking:")
        negative_tests = [
            ("ai_bots", -1),
            ("ai_bots", -999),
            ("manual_bots", -1),
            ("manual_bots", -999),
        ]
        
        negative_blocked = True
        for resource_type, negative_count in negative_tests:
            if not self.test_negative_count_blocked(user_id, resource_type, negative_count):
                negative_blocked = False
        
        print()
        
        # Test that normal limits still work
        print("2. Testing Normal Limits Still Work:")
        normal_limits_work = self.test_normal_limits_still_work(user_id)
        
        print()
        
        # Summary
        print("📊 VERIFICATION SUMMARY")
        print("=" * 30)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if negative_blocked and normal_limits_work:
            print("✅ FIX VERIFIED SUCCESSFULLY!")
            print("🔒 Negative count exploit has been blocked")
            print("✅ Normal subscription limits still work correctly")
            print("🎯 Users can no longer bypass subscription limits")
            return True
        else:
            print("❌ FIX VERIFICATION FAILED!")
            if not negative_blocked:
                print("🚨 Negative count exploit still works")
            if not normal_limits_work:
                print("🚨 Normal limits are broken")
            return False

def main():
    """Main test execution"""
    tester = VerifySubscriptionFixTest()
    success = tester.run_verification_test()
    
    if success:
        print("\n🎉 SUBSCRIPTION LIMITS BUG SUCCESSFULLY FIXED!")
        print("The critical security vulnerability has been resolved.")
    else:
        print("\n❌ FIX VERIFICATION FAILED")
        print("The bug may still exist or the fix broke normal functionality.")
    
    return success

if __name__ == "__main__":
    main()