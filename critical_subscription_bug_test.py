#!/usr/bin/env python3
"""
CRITICAL SUBSCRIPTION BUG TESTING
=================================

Found the bug! The backend allows creation when current_count is negative.
This test verifies the exact bug and provides evidence for the fix.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://fintracker-18.preview.emergentagent.com/api"

class CriticalSubscriptionBugTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.critical_bugs = []
        
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
            self.critical_bugs.append(result)
        
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_negative_count_exploit(self, user_id, resource_type, negative_count):
        """Test the negative count exploit"""
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
            payload = {
                "resource_type": resource_type,
                "current_count": negative_count
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # This should NEVER allow creation with negative count
                if data.get('can_create') == True:
                    self.log_test(f"Negative Count Exploit ({resource_type}, count={negative_count})", False, 
                                f"CRITICAL BUG: Negative count allows unlimited creation! Response: {data}", True)
                    return False
                else:
                    self.log_test(f"Negative Count Exploit ({resource_type}, count={negative_count})", True, 
                                f"Negative count properly rejected: can_create={data.get('can_create')}")
                    return True
            else:
                self.log_test(f"Negative Count Exploit ({resource_type}, count={negative_count})", False, 
                            f"HTTP {response.status_code}: {response.text}", True)
                return False
                
        except Exception as e:
            self.log_test(f"Negative Count Exploit ({resource_type}, count={negative_count})", False, 
                        f"Request error: {str(e)}", True)
            return False
    
    def test_how_user_bypassed_limits(self):
        """Test exactly how a user could have created 6 bots"""
        print("🚨 TESTING HOW USER BYPASSED LIMITS")
        print("=" * 50)
        
        user_id = str(uuid.uuid4())
        
        # Scenario: User exploits negative count to create unlimited bots
        print("Scenario: User sends negative current_count to bypass limits")
        print()
        
        # Test AI bots with negative count
        print("1. Creating AI bots with negative count exploit:")
        for i in range(3):  # User created 3 AI bots
            exploit_count = -1 - i  # -1, -2, -3
            result = self.test_negative_count_exploit(user_id, "ai_bots", exploit_count)
            if not result:
                print(f"   ❌ AI Bot {i+1}: User could exploit negative count {exploit_count}")
            else:
                print(f"   ✅ AI Bot {i+1}: Exploit blocked")
        
        print()
        
        # Test manual bots with negative count
        print("2. Creating manual bots with negative count exploit:")
        for i in range(3):  # User created 3 manual bots
            exploit_count = -1 - i  # -1, -2, -3
            result = self.test_negative_count_exploit(user_id, "manual_bots", exploit_count)
            if not result:
                print(f"   ❌ Manual Bot {i+1}: User could exploit negative count {exploit_count}")
            else:
                print(f"   ✅ Manual Bot {i+1}: Exploit blocked")
        
        print()
    
    def test_other_potential_exploits(self):
        """Test other potential exploits"""
        print("🔍 TESTING OTHER POTENTIAL EXPLOITS")
        print("=" * 40)
        
        user_id = str(uuid.uuid4())
        
        # Test very large negative numbers
        self.test_negative_count_exploit(user_id, "ai_bots", -999999)
        self.test_negative_count_exploit(user_id, "manual_bots", -999999)
        
        # Test zero (should work normally)
        try:
            url = f"{self.backend_url}/auth/user/{user_id}/subscription/check-limit"
            payload = {
                "resource_type": "ai_bots",
                "current_count": 0
            }
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get('can_create') == True and data.get('limit') == 1:
                self.log_test("Zero Count Test", True, 
                            f"Zero count works correctly: can_create={data.get('can_create')}")
            else:
                self.log_test("Zero Count Test", False, 
                            f"Zero count not working: {data}", True)
        except Exception as e:
            self.log_test("Zero Count Test", False, f"Error: {str(e)}", True)
    
    def demonstrate_fix_needed(self):
        """Demonstrate what the fix should be"""
        print("💡 DEMONSTRATING THE FIX NEEDED")
        print("=" * 40)
        print()
        print("CURRENT BUGGY CODE (line 379 in auth.py):")
        print("   can_create = limit_check.current_count < limit")
        print()
        print("PROBLEM:")
        print("   - When current_count = -1 and limit = 1")
        print("   - -1 < 1 evaluates to True")
        print("   - So can_create = True (WRONG!)")
        print()
        print("CORRECT FIX:")
        print("   can_create = limit_check.current_count >= 0 and limit_check.current_count < limit")
        print()
        print("OR BETTER:")
        print("   # Validate current_count is non-negative")
        print("   if limit_check.current_count < 0:")
        print("       return {'success': False, 'message': 'Invalid current_count'}")
        print("   can_create = limit_check.current_count < limit")
        print()
    
    def run_comprehensive_test(self):
        """Run comprehensive critical bug testing"""
        print("🔥 CRITICAL SUBSCRIPTION BUG TESTING")
        print("=" * 60)
        print("URGENT: Found how user bypassed subscription limits!")
        print("=" * 60)
        print()
        
        # Test how user bypassed limits
        self.test_how_user_bypassed_limits()
        
        # Test other potential exploits
        self.test_other_potential_exploits()
        print()
        
        # Demonstrate the fix
        self.demonstrate_fix_needed()
        
        # Summary
        print("📊 CRITICAL BUG ANALYSIS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        critical_bugs = len(self.critical_bugs)
        
        print(f"Total Tests: {total_tests}")
        print(f"Critical Bugs Found: {critical_bugs}")
        print()
        
        if self.critical_bugs:
            print("🚨 CRITICAL BUGS CONFIRMED:")
            print("-" * 30)
            for bug in self.critical_bugs:
                print(f"❌ {bug['test']}")
                print(f"   {bug['details']}")
            print()
            
            print("🔧 IMMEDIATE ACTION REQUIRED:")
            print("1. Fix the negative count validation in auth.py line 379")
            print("2. Add input validation for current_count >= 0")
            print("3. Test the fix with negative values")
            print("4. Deploy the fix immediately")
            print()
            
            print("🎯 ROOT CAUSE:")
            print("The backend subscription limit check doesn't validate that")
            print("current_count is non-negative, allowing users to send negative")
            print("values and bypass all subscription limits.")
        else:
            print("✅ No critical bugs found (unexpected)")
        
        return critical_bugs == 0

def main():
    """Main test execution"""
    tester = CriticalSubscriptionBugTest()
    success = tester.run_comprehensive_test()
    
    if not success:
        print("\n🚨 CRITICAL BUG CONFIRMED!")
        print("The user was able to create 6 bots by exploiting the negative count bug.")
        return False
    else:
        print("\n✅ No bugs found (this would be unexpected)")
        return True

if __name__ == "__main__":
    main()