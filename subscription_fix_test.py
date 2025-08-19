#!/usr/bin/env python3
"""
Subscription Fixes Testing Script
Testing the two critical subscription fixes:
1. Super Admin Plan Removal from GET /api/auth/subscription/plans
2. Subscription Limit Checking for marketplace products
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
SUPER_ADMIN_UUID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)

def print_test(test_name):
    """Print a formatted test header"""
    print(f"\n🔍 {test_name}")
    print("-" * 60)

def test_subscription_plans_endpoint():
    """Test 1: GET /api/auth/subscription/plans - Verify Super Admin plan is removed"""
    print_test("Testing GET /api/auth/subscription/plans")
    
    try:
        url = f"{API_BASE}/auth/subscription/plans"
        response = requests.get(url, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                plans = data.get('plans', [])
                plan_ids = [plan.get('id') for plan in plans]
                
                print(f"  ✅ Plans endpoint working")
                print(f"     Found {len(plans)} plans: {plan_ids}")
                
                # Check that super_admin plan is NOT included
                if 'super_admin' in plan_ids:
                    print(f"  ❌ CRITICAL: Super Admin plan still present in response!")
                    return False, f"Super Admin plan found in plans: {plan_ids}"
                
                # Check that only expected plans are present
                expected_plans = ['free', 'plus', 'pro']
                if set(plan_ids) == set(expected_plans):
                    print(f"  ✅ CRITICAL FIX VERIFIED: Super Admin plan successfully removed")
                    print(f"     Only expected plans present: {plan_ids}")
                    return True, f"Plans correctly limited to: {plan_ids}"
                else:
                    print(f"  ⚠️  Unexpected plans found")
                    print(f"     Expected: {expected_plans}")
                    print(f"     Found: {plan_ids}")
                    return True, f"Super Admin removed but unexpected plans: {plan_ids}"
            else:
                print(f"  ❌ API returned success=false: {data.get('message')}")
                return False, data.get('message', 'Unknown error')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        print(f"  ❌ Error testing subscription plans: {e}")
        return False, str(e)

def test_subscription_limit_free_user_allowed():
    """Test 2a: Free user with 0 products should be allowed to create 1"""
    print_test("Testing Free User Limit Check - Should Allow (0/1)")
    
    # Create a fake free user ID for testing
    fake_free_user_id = "11111111-1111-1111-1111-111111111111"
    
    try:
        url = f"{API_BASE}/auth/user/{fake_free_user_id}/subscription/check-limit"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "resource_type": "marketplace_products",
            "current_count": 0
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                can_create = data.get('can_create')
                limit_reached = data.get('limit_reached')
                current_count = data.get('current_count')
                limit = data.get('limit')
                plan_type = data.get('plan_type')
                
                print(f"  ✅ Limit check endpoint working")
                print(f"     Plan Type: {plan_type}")
                print(f"     Current Count: {current_count}")
                print(f"     Limit: {limit}")
                print(f"     Can Create: {can_create}")
                print(f"     Limit Reached: {limit_reached}")
                
                # Free user with 0 products should be allowed to create 1
                if can_create and not limit_reached and limit == 1 and plan_type == 'free':
                    print(f"  ✅ CRITICAL FIX VERIFIED: Free user correctly allowed to create first product")
                    return True, f"Free user (0/1) correctly allowed"
                else:
                    print(f"  ❌ CRITICAL: Free user limit check failed")
                    return False, f"Expected: can_create=True, limit=1, got: can_create={can_create}, limit={limit}"
            else:
                print(f"  ❌ API returned success=false: {data.get('message')}")
                return False, data.get('message', 'Unknown error')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        print(f"  ❌ Error testing free user limit (allowed): {e}")
        return False, str(e)

def test_subscription_limit_free_user_denied():
    """Test 2b: Free user with 1 product should be denied creating another"""
    print_test("Testing Free User Limit Check - Should Deny (1/1)")
    
    # Create a fake free user ID for testing
    fake_free_user_id = "22222222-2222-2222-2222-222222222222"
    
    try:
        url = f"{API_BASE}/auth/user/{fake_free_user_id}/subscription/check-limit"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "resource_type": "marketplace_products",
            "current_count": 1
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                can_create = data.get('can_create')
                limit_reached = data.get('limit_reached')
                current_count = data.get('current_count')
                limit = data.get('limit')
                plan_type = data.get('plan_type')
                
                print(f"  ✅ Limit check endpoint working")
                print(f"     Plan Type: {plan_type}")
                print(f"     Current Count: {current_count}")
                print(f"     Limit: {limit}")
                print(f"     Can Create: {can_create}")
                print(f"     Limit Reached: {limit_reached}")
                
                # Free user with 1 product should be denied creating another
                if not can_create and limit_reached and limit == 1 and plan_type == 'free':
                    print(f"  ✅ CRITICAL FIX VERIFIED: Free user correctly denied second product")
                    return True, f"Free user (1/1) correctly denied"
                else:
                    print(f"  ❌ CRITICAL: Free user limit enforcement failed")
                    return False, f"Expected: can_create=False, limit_reached=True, got: can_create={can_create}, limit_reached={limit_reached}"
            else:
                print(f"  ❌ API returned success=false: {data.get('message')}")
                return False, data.get('message', 'Unknown error')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        print(f"  ❌ Error testing free user limit (denied): {e}")
        return False, str(e)

def test_subscription_limit_super_admin_unlimited():
    """Test 2c: Super Admin should have unlimited access"""
    print_test("Testing Super Admin Limit Check - Should Allow Unlimited")
    
    try:
        url = f"{API_BASE}/auth/user/{SUPER_ADMIN_UUID}/subscription/check-limit"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "resource_type": "marketplace_products",
            "current_count": 10  # High number to test unlimited
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                can_create = data.get('can_create')
                limit_reached = data.get('limit_reached')
                current_count = data.get('current_count')
                limit = data.get('limit')
                plan_type = data.get('plan_type')
                is_super_admin = data.get('is_super_admin')
                
                print(f"  ✅ Limit check endpoint working")
                print(f"     Plan Type: {plan_type}")
                print(f"     Is Super Admin: {is_super_admin}")
                print(f"     Current Count: {current_count}")
                print(f"     Limit: {limit}")
                print(f"     Can Create: {can_create}")
                print(f"     Limit Reached: {limit_reached}")
                
                # Super admin should have unlimited access
                if can_create and not limit_reached and limit == -1 and is_super_admin:
                    print(f"  ✅ CRITICAL FIX VERIFIED: Super Admin has unlimited access")
                    return True, f"Super Admin unlimited access confirmed"
                else:
                    print(f"  ❌ CRITICAL: Super Admin limit check failed")
                    return False, f"Expected: unlimited access, got: can_create={can_create}, limit={limit}, is_super_admin={is_super_admin}"
            else:
                print(f"  ❌ API returned success=false: {data.get('message')}")
                return False, data.get('message', 'Unknown error')
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        print(f"  ❌ Error testing super admin limit: {e}")
        return False, str(e)

def test_backend_health():
    """Test basic backend connectivity"""
    print_test("Testing Backend Health")
    
    try:
        endpoints = [
            f"{API_BASE}/",
            f"{API_BASE}/status", 
            f"{API_BASE}/health",
            f"{API_BASE}/auth/health"
        ]
        
        all_healthy = True
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"  {status} {endpoint}: {response.status_code}")
                if response.status_code != 200:
                    print(f"     Response: {response.text[:200]}")
                    all_healthy = False
            except Exception as e:
                print(f"  ❌ {endpoint}: {str(e)}")
                all_healthy = False
        
        return all_healthy, "Backend health check completed"
        
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False, str(e)

def run_subscription_fix_tests():
    """Run comprehensive subscription fix tests"""
    print_section("SUBSCRIPTION FIXES TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Super Admin UUID: {SUPER_ADMIN_UUID}")
    
    test_results = {}
    
    # Test 0: Backend Health
    print_section("0. BACKEND HEALTH CHECK")
    test_results['backend_health'], _ = test_backend_health()
    
    if not test_results['backend_health']:
        print("\n❌ Backend health check failed. Cannot proceed with testing.")
        return test_results
    
    # Test 1: Subscription Plans Endpoint (Super Admin Plan Removal)
    print_section("1. SUBSCRIPTION PLANS ENDPOINT TEST")
    test_results['plans_endpoint'], plans_message = test_subscription_plans_endpoint()
    
    # Test 2a: Free User Limit Check - Should Allow (0/1)
    print_section("2A. FREE USER LIMIT CHECK - SHOULD ALLOW")
    test_results['free_user_allowed'], free_allowed_message = test_subscription_limit_free_user_allowed()
    
    # Test 2b: Free User Limit Check - Should Deny (1/1)
    print_section("2B. FREE USER LIMIT CHECK - SHOULD DENY")
    test_results['free_user_denied'], free_denied_message = test_subscription_limit_free_user_denied()
    
    # Test 2c: Super Admin Limit Check - Should Allow Unlimited
    print_section("2C. SUPER ADMIN LIMIT CHECK - UNLIMITED")
    test_results['super_admin_unlimited'], super_admin_message = test_subscription_limit_super_admin_unlimited()
    
    return test_results

def print_test_summary(test_results):
    """Print comprehensive test summary"""
    print_section("SUBSCRIPTION FIXES TEST SUMMARY")
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 OVERALL RESULTS:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print()
    
    print("📋 DETAILED RESULTS:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    print()
    
    # Critical fixes verification
    critical_tests = ['plans_endpoint', 'free_user_allowed', 'free_user_denied', 'super_admin_unlimited']
    critical_failures = [test for test in critical_tests if not test_results.get(test, False)]
    
    if critical_failures:
        print("🚨 CRITICAL SUBSCRIPTION FIXES NOT WORKING:")
        for failure in critical_failures:
            print(f"   ❌ {failure.replace('_', ' ').title()}")
        print()
        print("⚠️  REQUIRED ACTIONS:")
        if 'plans_endpoint' in critical_failures:
            print("   - Super Admin plan is still being returned in GET /api/auth/subscription/plans")
        if 'free_user_allowed' in critical_failures:
            print("   - Free users cannot create their first marketplace product")
        if 'free_user_denied' in critical_failures:
            print("   - Free users are not being limited to 1 marketplace product")
        if 'super_admin_unlimited' in critical_failures:
            print("   - Super Admin does not have unlimited marketplace product access")
    else:
        print("✅ ALL CRITICAL SUBSCRIPTION FIXES WORKING CORRECTLY!")
        print("   ✅ Super Admin plan removed from public plans endpoint")
        print("   ✅ Free user marketplace product limits enforced (1 product max)")
        print("   ✅ Super Admin has unlimited marketplace product access")
    
    print()
    
    # Overall assessment
    if success_rate == 100:
        print("🎉 EXCELLENT! All subscription fixes verified successfully!")
    elif success_rate >= 80:
        print("✅ GOOD! Most subscription fixes working, minor issues detected.")
    else:
        print("⚠️  ATTENTION NEEDED! Multiple subscription fixes require investigation.")

def main():
    """Main testing function"""
    try:
        test_results = run_subscription_fix_tests()
        print_test_summary(test_results)
        
        # Return success status for automation
        critical_tests = ['plans_endpoint', 'free_user_allowed', 'free_user_denied', 'super_admin_unlimited']
        critical_success = all(test_results.get(test, False) for test in critical_tests)
        
        return critical_success
        
    except Exception as e:
        print(f"\n❌ SUBSCRIPTION TESTING FAILED WITH EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)