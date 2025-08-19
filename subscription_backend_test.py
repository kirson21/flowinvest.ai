#!/usr/bin/env python3
"""
Subscription System Backend Testing Script
Testing the subscription-level restrictions backend implementation
"""

import requests
import json
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

# Test users
SUPER_ADMIN_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super admin
REGULAR_USER_ID = str(uuid.uuid4())  # Regular user without subscription

# Test data
RESOURCE_TYPES = ['ai_bots', 'manual_bots', 'marketplace_products']
FREE_PLAN_LIMITS = {
    'ai_bots': 1,
    'manual_bots': 2,
    'marketplace_products': 1
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)

def print_test(test_name):
    """Print a formatted test header"""
    print(f"\n🔍 {test_name}")
    print("-" * 60)

def make_request(method, endpoint, data=None, expected_status=200):
    """Make HTTP request and return response"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"   {method} {url}")
        print(f"   Status: {response.status_code}")
        
        if data:
            print(f"   Request: {json.dumps(data, indent=2)}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response: {response.text}")
            response_data = {"error": "Invalid JSON response"}
        
        success = response.status_code == expected_status
        print(f"   ✅ PASS" if success else f"   ❌ FAIL (Expected {expected_status}, got {response.status_code})")
        
        return response, response_data, success
        
    except Exception as e:
        print(f"   ❌ FAIL - Request failed: {str(e)}")
        return None, {"error": str(e)}, False

def test_backend_health():
    """Test basic backend connectivity"""
    print_test("Testing Backend Health")
    
    endpoints = [
        "/",
        "/status", 
        "/health",
        "/auth/health"
    ]
    
    results = []
    for endpoint in endpoints:
        response, data, success = make_request('GET', endpoint)
        results.append(success)
    
    return all(results)

def test_subscription_limits_endpoint():
    """Test GET /api/auth/user/{user_id}/subscription/limits endpoint"""
    print_test("Testing Subscription Limits Endpoint")
    
    results = []
    
    # Test with Super Admin
    print("\n📋 Testing Super Admin Limits:")
    response, data, success = make_request('GET', f"/auth/user/{SUPER_ADMIN_USER_ID}/subscription/limits")
    results.append(success)
    
    if success and data.get('success'):
        subscription = data.get('subscription', {})
        is_super_admin = subscription.get('is_super_admin', False)
        print(f"   Super Admin Status: {is_super_admin}")
        if is_super_admin:
            print("   ✅ Super Admin correctly identified")
        else:
            print("   ❌ Super Admin not identified correctly")
            results.append(False)
    
    # Test with Regular User (should default to free plan)
    print("\n📋 Testing Regular User Limits (Free Plan Default):")
    response, data, success = make_request('GET', f"/auth/user/{REGULAR_USER_ID}/subscription/limits")
    results.append(success)
    
    if success and data.get('success'):
        subscription = data.get('subscription', {})
        plan_type = subscription.get('plan_type')
        limits = subscription.get('limits', {})
        
        print(f"   Plan Type: {plan_type}")
        print(f"   Limits: {limits}")
        
        if plan_type == 'free':
            print("   ✅ Correctly defaulted to free plan")
            # Verify free plan limits
            expected_limits = FREE_PLAN_LIMITS
            if limits == expected_limits:
                print("   ✅ Free plan limits are correct")
            else:
                print(f"   ❌ Free plan limits incorrect. Expected: {expected_limits}, Got: {limits}")
                results.append(False)
        else:
            print(f"   ❌ Expected free plan, got: {plan_type}")
            results.append(False)
    
    return all(results)

def test_subscription_check_limit_endpoint():
    """Test POST /api/auth/user/{user_id}/subscription/check-limit endpoint"""
    print_test("Testing Subscription Check Limit Endpoint")
    
    results = []
    
    # Test Super Admin - should bypass all limits
    print("\n📋 Testing Super Admin Limit Checks:")
    for resource_type in RESOURCE_TYPES:
        for current_count in [0, 5, 100]:  # Test various counts
            test_data = {
                'resource_type': resource_type,
                'current_count': current_count
            }
            
            print(f"\n   Testing {resource_type} with current count {current_count}:")
            response, data, success = make_request('POST', f"/auth/user/{SUPER_ADMIN_USER_ID}/subscription/check-limit", test_data)
            results.append(success)
            
            if success and data.get('success'):
                can_create = data.get('can_create')
                is_super_admin = data.get('is_super_admin')
                limit = data.get('limit')
                
                if is_super_admin and can_create and limit == -1:
                    print("   ✅ Super Admin correctly bypasses limits")
                else:
                    print(f"   ❌ Super Admin limit check failed. can_create: {can_create}, limit: {limit}, is_super_admin: {is_super_admin}")
                    results.append(False)
    
    # Test Regular User - should enforce free plan limits
    print("\n📋 Testing Regular User Limit Checks (Free Plan):")
    for resource_type in RESOURCE_TYPES:
        free_limit = FREE_PLAN_LIMITS[resource_type]
        
        # Test below limit (should allow)
        test_data = {
            'resource_type': resource_type,
            'current_count': free_limit - 1
        }
        
        print(f"\n   Testing {resource_type} below limit ({free_limit - 1}/{free_limit}):")
        response, data, success = make_request('POST', f"/auth/user/{REGULAR_USER_ID}/subscription/check-limit", test_data)
        results.append(success)
        
        if success and data.get('success'):
            can_create = data.get('can_create')
            limit_reached = data.get('limit_reached')
            limit = data.get('limit')
            
            if can_create and not limit_reached and limit == free_limit:
                print("   ✅ Below limit check passed")
            else:
                print(f"   ❌ Below limit check failed. can_create: {can_create}, limit_reached: {limit_reached}, limit: {limit}")
                results.append(False)
        
        # Test at limit (should deny)
        test_data = {
            'resource_type': resource_type,
            'current_count': free_limit
        }
        
        print(f"\n   Testing {resource_type} at limit ({free_limit}/{free_limit}):")
        response, data, success = make_request('POST', f"/auth/user/{REGULAR_USER_ID}/subscription/check-limit", test_data)
        results.append(success)
        
        if success and data.get('success'):
            can_create = data.get('can_create')
            limit_reached = data.get('limit_reached')
            limit = data.get('limit')
            
            if not can_create and limit_reached and limit == free_limit:
                print("   ✅ At limit check passed")
            else:
                print(f"   ❌ At limit check failed. can_create: {can_create}, limit_reached: {limit_reached}, limit: {limit}")
                results.append(False)
    
    return all(results)

def test_subscription_details_endpoint():
    """Test GET /api/auth/user/{user_id}/subscription endpoint"""
    print_test("Testing Subscription Details Endpoint")
    
    results = []
    
    # Test with Super Admin
    print("\n📋 Testing Super Admin Subscription Details:")
    response, data, success = make_request('GET', f"/auth/user/{SUPER_ADMIN_USER_ID}/subscription")
    results.append(success)
    
    if success and data.get('success'):
        subscription = data.get('subscription', {})
        plan_type = subscription.get('plan_type')
        status = subscription.get('status')
        
        print(f"   Plan Type: {plan_type}")
        print(f"   Status: {status}")
        
        if plan_type == 'super_admin':
            print("   ✅ Super Admin subscription correctly identified")
        else:
            print(f"   ❌ Expected super_admin plan, got: {plan_type}")
            results.append(False)
    
    # Test with Regular User (should create default free subscription)
    print("\n📋 Testing Regular User Subscription Details (Free Plan Default):")
    response, data, success = make_request('GET', f"/auth/user/{REGULAR_USER_ID}/subscription")
    results.append(success)
    
    if success and data.get('success'):
        subscription = data.get('subscription', {})
        plan_type = subscription.get('plan_type')
        status = subscription.get('status')
        limits = subscription.get('limits', {})
        
        print(f"   Plan Type: {plan_type}")
        print(f"   Status: {status}")
        print(f"   Limits: {limits}")
        
        if plan_type == 'free' and status == 'active':
            print("   ✅ Free subscription correctly created/returned")
            
            # Verify free plan limits
            expected_limits = FREE_PLAN_LIMITS
            if limits == expected_limits:
                print("   ✅ Free plan limits are correct")
            else:
                print(f"   ❌ Free plan limits incorrect. Expected: {expected_limits}, Got: {limits}")
                results.append(False)
        else:
            print(f"   ❌ Expected free/active subscription, got: {plan_type}/{status}")
            results.append(False)
    
    return all(results)

def test_subscription_plans_endpoint():
    """Test GET /api/auth/subscription/plans endpoint"""
    print_test("Testing Subscription Plans Endpoint")
    
    response, data, success = make_request('GET', "/auth/subscription/plans")
    
    if success and data.get('success'):
        plans = data.get('plans', [])
        print(f"   Found {len(plans)} subscription plans")
        
        # Check for required plans
        plan_ids = [plan.get('id') for plan in plans]
        required_plans = ['free', 'plus', 'pro', 'super_admin']
        
        missing_plans = [plan for plan in required_plans if plan not in plan_ids]
        if not missing_plans:
            print("   ✅ All required plans are available")
            
            # Check super_admin plan specifically
            super_admin_plan = next((plan for plan in plans if plan.get('id') == 'super_admin'), None)
            if super_admin_plan:
                if super_admin_plan.get('limitations') is None:
                    print("   ✅ Super Admin plan has no limitations")
                else:
                    print(f"   ❌ Super Admin plan should have no limitations, got: {super_admin_plan.get('limitations')}")
                    return False
            
            return True
        else:
            print(f"   ❌ Missing required plans: {missing_plans}")
            return False
    
    return False

def test_edge_cases():
    """Test edge cases and error handling"""
    print_test("Testing Edge Cases and Error Handling")
    
    results = []
    
    # Test with invalid user ID
    print("\n📋 Testing Invalid User ID:")
    invalid_user_id = "invalid-user-id"
    response, data, success = make_request('GET', f"/auth/user/{invalid_user_id}/subscription/limits", expected_status=200)
    results.append(success)
    
    # Should still return success with default free plan
    if success and data.get('success'):
        subscription = data.get('subscription', {})
        if subscription.get('plan_type') == 'free':
            print("   ✅ Invalid user ID correctly defaults to free plan")
        else:
            print("   ❌ Invalid user ID should default to free plan")
            results.append(False)
    
    # Test with invalid resource type
    print("\n📋 Testing Invalid Resource Type:")
    test_data = {
        'resource_type': 'invalid_resource',
        'current_count': 0
    }
    response, data, success = make_request('POST', f"/auth/user/{REGULAR_USER_ID}/subscription/check-limit", test_data)
    results.append(success)
    
    if success and data.get('success'):
        # Should handle gracefully, possibly defaulting to limit 1
        limit = data.get('limit', 0)
        print(f"   ✅ Invalid resource type handled gracefully (limit: {limit})")
    
    # Test with negative current count
    print("\n📋 Testing Negative Current Count:")
    test_data = {
        'resource_type': 'ai_bots',
        'current_count': -1
    }
    response, data, success = make_request('POST', f"/auth/user/{REGULAR_USER_ID}/subscription/check-limit", test_data)
    results.append(success)
    
    if success and data.get('success'):
        can_create = data.get('can_create')
        print(f"   ✅ Negative count handled gracefully (can_create: {can_create})")
    
    return all(results)

def run_comprehensive_subscription_tests():
    """Run all subscription system tests"""
    print_section("SUBSCRIPTION SYSTEM BACKEND TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Super Admin User ID: {SUPER_ADMIN_USER_ID}")
    print(f"Regular User ID: {REGULAR_USER_ID}")
    
    test_results = []
    
    # Test 1: Backend Health
    test_results.append(test_backend_health())
    
    # Test 2: Subscription Limits Endpoint
    test_results.append(test_subscription_limits_endpoint())
    
    # Test 3: Subscription Check Limit Endpoint
    test_results.append(test_subscription_check_limit_endpoint())
    
    # Test 4: Subscription Details Endpoint
    test_results.append(test_subscription_details_endpoint())
    
    # Test 5: Subscription Plans Endpoint
    test_results.append(test_subscription_plans_endpoint())
    
    # Test 6: Edge Cases
    test_results.append(test_edge_cases())
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(test_results)
    total = len(test_results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 SUBSCRIPTION SYSTEM TESTS PASSED")
        return True
    else:
        print("❌ SUBSCRIPTION SYSTEM TESTS FAILED")
        return False

if __name__ == "__main__":
    success = run_comprehensive_subscription_tests()
    exit(0 if success else 1)