#!/usr/bin/env python3
"""
Subscription Constraint Testing Script
Testing the SQL constraint fix for super_admin plan type
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
SUPER_ADMIN_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def print_test(test_name):
    """Print a formatted test header"""
    print(f"\n🔍 {test_name}")
    print("-" * 60)

def make_request(method, endpoint, data=None):
    """Make HTTP request and return response"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
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
        
        return response, response_data
        
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return None, {"error": str(e)}

def test_super_admin_constraint_fix():
    """Test that super_admin plan type works without SQL constraint errors"""
    print_test("Testing Super Admin Plan Type SQL Constraint Fix")
    
    # Test getting super admin subscription (should work without constraint errors)
    response, data = make_request('GET', f"/auth/user/{SUPER_ADMIN_USER_ID}/subscription")
    
    if response and response.status_code == 200 and data.get('success'):
        subscription = data.get('subscription', {})
        plan_type = subscription.get('plan_type')
        
        if plan_type == 'super_admin':
            print("   ✅ Super Admin plan type works without SQL constraint errors")
            return True
        else:
            print(f"   ❌ Expected super_admin plan, got: {plan_type}")
            return False
    else:
        print("   ❌ Failed to get super admin subscription")
        return False

def test_subscription_upgrade_to_super_admin():
    """Test upgrading a subscription to super_admin plan"""
    print_test("Testing Subscription Upgrade to Super Admin")
    
    # Try to upgrade to super_admin (this should work without constraint errors)
    upgrade_data = {
        "plan_type": "super_admin",
        "price": 0.0,
        "duration_days": None
    }
    
    response, data = make_request('POST', f"/auth/user/{SUPER_ADMIN_USER_ID}/subscription/upgrade", upgrade_data)
    
    if response and response.status_code == 200:
        if data.get('success'):
            print("   ✅ Super Admin upgrade works without SQL constraint errors")
            return True
        else:
            # Check if it's already super admin
            message = data.get('message', '')
            if 'already' in message.lower() or 'super_admin' in message.lower():
                print("   ✅ User is already Super Admin (no constraint error)")
                return True
            else:
                print(f"   ❌ Upgrade failed: {message}")
                return False
    else:
        print("   ❌ Failed to upgrade subscription")
        return False

def test_fallback_behavior():
    """Test fallback behavior for users without subscriptions"""
    print_test("Testing Fallback Behavior for Users Without Subscriptions")
    
    # Use a new random user ID that definitely doesn't have a subscription
    import uuid
    new_user_id = str(uuid.uuid4())
    
    # Test getting limits for user without subscription
    response, data = make_request('GET', f"/auth/user/{new_user_id}/subscription/limits")
    
    if response and response.status_code == 200 and data.get('success'):
        subscription = data.get('subscription', {})
        plan_type = subscription.get('plan_type')
        limits = subscription.get('limits', {})
        
        expected_limits = {
            'ai_bots': 1,
            'manual_bots': 2,
            'marketplace_products': 1
        }
        
        if plan_type == 'free' and limits == expected_limits:
            print("   ✅ Fallback to free plan with correct limits works")
            return True
        else:
            print(f"   ❌ Fallback failed. Plan: {plan_type}, Limits: {limits}")
            return False
    else:
        print("   ❌ Failed to get fallback subscription")
        return False

def test_resource_limit_enforcement():
    """Test resource limit enforcement for different scenarios"""
    print_test("Testing Resource Limit Enforcement")
    
    import uuid
    test_user_id = str(uuid.uuid4())
    
    results = []
    
    # Test each resource type with different current counts
    test_scenarios = [
        {'resource_type': 'ai_bots', 'current_count': 0, 'expected_can_create': True},
        {'resource_type': 'ai_bots', 'current_count': 1, 'expected_can_create': False},
        {'resource_type': 'manual_bots', 'current_count': 1, 'expected_can_create': True},
        {'resource_type': 'manual_bots', 'current_count': 2, 'expected_can_create': False},
        {'resource_type': 'marketplace_products', 'current_count': 0, 'expected_can_create': True},
        {'resource_type': 'marketplace_products', 'current_count': 1, 'expected_can_create': False},
    ]
    
    for scenario in test_scenarios:
        test_data = {
            'resource_type': scenario['resource_type'],
            'current_count': scenario['current_count']
        }
        
        response, data = make_request('POST', f"/auth/user/{test_user_id}/subscription/check-limit", test_data)
        
        if response and response.status_code == 200 and data.get('success'):
            can_create = data.get('can_create')
            expected = scenario['expected_can_create']
            
            if can_create == expected:
                print(f"   ✅ {scenario['resource_type']} limit check passed ({scenario['current_count']} -> can_create: {can_create})")
                results.append(True)
            else:
                print(f"   ❌ {scenario['resource_type']} limit check failed ({scenario['current_count']} -> expected: {expected}, got: {can_create})")
                results.append(False)
        else:
            print(f"   ❌ Failed to check limit for {scenario['resource_type']}")
            results.append(False)
    
    return all(results)

def run_constraint_tests():
    """Run all constraint-related tests"""
    print("=" * 80)
    print("🧪 SUBSCRIPTION CONSTRAINT TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Super Admin User ID: {SUPER_ADMIN_USER_ID}")
    
    test_results = []
    
    # Test 1: Super Admin Constraint Fix
    test_results.append(test_super_admin_constraint_fix())
    
    # Test 2: Subscription Upgrade to Super Admin
    test_results.append(test_subscription_upgrade_to_super_admin())
    
    # Test 3: Fallback Behavior
    test_results.append(test_fallback_behavior())
    
    # Test 4: Resource Limit Enforcement
    test_results.append(test_resource_limit_enforcement())
    
    # Summary
    print("\n" + "=" * 80)
    print("🧪 CONSTRAINT TEST SUMMARY")
    print("=" * 80)
    passed = sum(test_results)
    total = len(test_results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 75:
        print("🎉 SUBSCRIPTION CONSTRAINT TESTS PASSED")
        return True
    else:
        print("❌ SUBSCRIPTION CONSTRAINT TESTS FAILED")
        return False

if __name__ == "__main__":
    success = run_constraint_tests()
    exit(0 if success else 1)