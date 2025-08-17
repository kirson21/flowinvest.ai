#!/usr/bin/env python3
"""
Backend Balance System Testing Script
Testing the User Balance System Backend APIs comprehensively
"""

import requests
import json
import os
import uuid
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super admin test user

# Test data
TEST_AMOUNTS = {
    'topup': 100.00,
    'purchase': 50.00,
    'withdrawal': 25.00
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
        
        return all_healthy
        
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_get_user_balance(user_id):
    """Test GET /api/auth/user/{user_id}/balance endpoint"""
    print_test(f"Testing GET User Balance for {user_id}")
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}/balance"
        response = requests.get(url, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                balance = data.get('balance', 0)
                currency = data.get('currency', 'USD')
                print(f"  ✅ Balance retrieved successfully")
                print(f"     Balance: ${balance:.2f} {currency}")
                return True, balance, currency
            else:
                print(f"  ❌ Failed to get balance: {data.get('message')}")
                return False, 0, 'USD'
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, 0, 'USD'
            
    except Exception as e:
        print(f"  ❌ Error testing GET balance: {e}")
        return False, 0, 'USD'

def test_update_balance(user_id, amount, transaction_type):
    """Test POST /api/auth/user/{user_id}/update-balance endpoint"""
    print_test(f"Testing {transaction_type.upper()} Balance Update: ${amount}")
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}/update-balance"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "amount": amount,
            "transaction_type": transaction_type,
            "description": f"Test {transaction_type} of ${amount}"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ {transaction_type.title()} successful")
                print(f"     Previous Balance: ${data.get('previous_balance', 0):.2f}")
                print(f"     New Balance: ${data.get('new_balance', 0):.2f}")
                print(f"     Amount Changed: ${data.get('amount_changed', 0):.2f}")
                return True, data
            else:
                print(f"  ❌ {transaction_type.title()} failed: {data.get('message')}")
                return False, data
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, response.text
            
    except Exception as e:
        print(f"  ❌ Error testing {transaction_type}: {e}")
        return False, str(e)

def test_process_transaction(buyer_id, seller_id, product_id, amount):
    """Test POST /api/auth/user/{user_id}/process-transaction endpoint"""
    print_test(f"Testing Marketplace Purchase: ${amount}")
    
    try:
        url = f"{API_BASE}/auth/user/{buyer_id}/process-transaction"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "seller_id": seller_id,
            "product_id": product_id,
            "amount": amount,
            "description": f"Test marketplace purchase of ${amount}"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ Purchase successful")
                print(f"     Transaction ID: {data.get('transaction_id')}")
                print(f"     Amount Charged: ${data.get('amount_charged', 0):.2f}")
                print(f"     Platform Fee (10%): ${data.get('platform_fee', 0):.2f}")
                print(f"     Seller Received (90%): ${data.get('seller_received', 0):.2f}")
                print(f"     Buyer New Balance: ${data.get('buyer_new_balance', 0):.2f}")
                return True, data
            else:
                print(f"  ❌ Purchase failed: {data.get('message')}")
                print(f"     Error: {data.get('error', 'unknown')}")
                if 'current_balance' in data:
                    print(f"     Current Balance: ${data.get('current_balance', 0):.2f}")
                    print(f"     Required Amount: ${data.get('required_amount', 0):.2f}")
                return False, data
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, response.text
            
    except Exception as e:
        print(f"  ❌ Error testing marketplace purchase: {e}")
        return False, str(e)

def test_get_transactions(user_id, limit=10):
    """Test GET /api/auth/user/{user_id}/transactions endpoint"""
    print_test(f"Testing Transaction History for {user_id}")
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}/transactions?limit={limit}"
        response = requests.get(url, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                transactions = data.get('transactions', [])
                print(f"  ✅ Transaction history retrieved")
                print(f"     Found {len(transactions)} transactions")
                
                for i, tx in enumerate(transactions[:3]):  # Show first 3 transactions
                    print(f"     Transaction {i+1}:")
                    print(f"       ID: {tx.get('id')}")
                    print(f"       Type: {tx.get('transaction_type')}")
                    print(f"       Amount: ${tx.get('amount', 0):.2f}")
                    print(f"       Status: {tx.get('status')}")
                    print(f"       Date: {tx.get('created_at')}")
                
                return True, transactions
            else:
                print(f"  ❌ Failed to get transactions: {data.get('message')}")
                return False, []
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"  ❌ Error testing transaction history: {e}")
        return False, []

def test_insufficient_funds_scenario(user_id):
    """Test insufficient funds scenario"""
    print_test("Testing Insufficient Funds Scenario")
    
    # First get current balance
    success, current_balance, currency = test_get_user_balance(user_id)
    if not success:
        print("  ❌ Cannot test insufficient funds - failed to get current balance")
        return False
    
    # Try to purchase something more expensive than current balance
    excessive_amount = current_balance + 1000.00
    fake_seller_id = str(uuid.uuid4())
    fake_product_id = str(uuid.uuid4())
    
    print(f"  Attempting purchase of ${excessive_amount:.2f} with balance ${current_balance:.2f}")
    
    success, result = test_process_transaction(user_id, fake_seller_id, fake_product_id, excessive_amount)
    
    if not success and isinstance(result, dict):
        if result.get('error') == 'insufficient_funds':
            print(f"  ✅ Insufficient funds properly detected")
            print(f"     Error message: {result.get('message')}")
            return True
        else:
            print(f"  ❌ Wrong error type: {result.get('error')}")
            return False
    else:
        print(f"  ❌ Purchase should have failed due to insufficient funds")
        return False

def test_invalid_amounts():
    """Test invalid amount scenarios"""
    print_test("Testing Invalid Amount Scenarios")
    
    invalid_amounts = [0, -10, -100]
    results = []
    
    for amount in invalid_amounts:
        print(f"\n  Testing amount: ${amount}")
        success, result = test_update_balance(TEST_USER_ID, amount, "topup")
        
        if not success:
            print(f"    ✅ Correctly rejected invalid amount ${amount}")
            results.append(True)
        else:
            print(f"    ❌ Should have rejected invalid amount ${amount}")
            results.append(False)
    
    return all(results)

def test_withdrawal_insufficient_funds():
    """Test withdrawal with insufficient funds"""
    print_test("Testing Withdrawal with Insufficient Funds")
    
    # Get current balance
    success, current_balance, currency = test_get_user_balance(TEST_USER_ID)
    if not success:
        print("  ❌ Cannot test withdrawal - failed to get current balance")
        return False
    
    # Try to withdraw more than available
    excessive_withdrawal = current_balance + 100.00
    
    print(f"  Attempting withdrawal of ${excessive_withdrawal:.2f} with balance ${current_balance:.2f}")
    
    success, result = test_update_balance(TEST_USER_ID, excessive_withdrawal, "withdrawal")
    
    if not success and isinstance(result, dict):
        if "insufficient funds" in result.get('message', '').lower():
            print(f"  ✅ Insufficient funds for withdrawal properly detected")
            print(f"     Error message: {result.get('message')}")
            return True
        else:
            print(f"  ❌ Wrong error message: {result.get('message')}")
            return False
    else:
        print(f"  ❌ Withdrawal should have failed due to insufficient funds")
        return False

def test_platform_fee_calculation():
    """Test that platform fee is calculated correctly (10%)"""
    print_test("Testing Platform Fee Calculation (10%)")
    
    # First ensure we have sufficient balance
    topup_success, _ = test_update_balance(TEST_USER_ID, 200.00, "topup")
    if not topup_success:
        print("  ❌ Failed to top up for platform fee test")
        return False
    
    # Create fake seller and product IDs
    fake_seller_id = str(uuid.uuid4())
    fake_product_id = str(uuid.uuid4())
    test_amount = 100.00
    expected_fee = test_amount * 0.10  # 10%
    expected_seller_amount = test_amount * 0.90  # 90%
    
    success, result = test_process_transaction(TEST_USER_ID, fake_seller_id, fake_product_id, test_amount)
    
    if success and isinstance(result, dict):
        actual_fee = result.get('platform_fee', 0)
        actual_seller_amount = result.get('seller_received', 0)
        
        fee_correct = abs(actual_fee - expected_fee) < 0.01
        seller_amount_correct = abs(actual_seller_amount - expected_seller_amount) < 0.01
        
        print(f"  Expected Platform Fee: ${expected_fee:.2f}")
        print(f"  Actual Platform Fee: ${actual_fee:.2f}")
        print(f"  Expected Seller Amount: ${expected_seller_amount:.2f}")
        print(f"  Actual Seller Amount: ${actual_seller_amount:.2f}")
        
        if fee_correct and seller_amount_correct:
            print(f"  ✅ Platform fee calculation is correct (10%)")
            return True
        else:
            print(f"  ❌ Platform fee calculation is incorrect")
            return False
    else:
        print(f"  ❌ Failed to test platform fee calculation")
        return False

def run_comprehensive_balance_tests():
    """Run comprehensive balance system tests"""
    print_section("COMPREHENSIVE USER BALANCE SYSTEM TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    
    test_results = {}
    
    # Test 1: Backend Health
    print_section("1. BACKEND HEALTH CHECK")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        print("\n❌ Backend health check failed. Cannot proceed with testing.")
        return test_results
    
    # Test 2: Get Initial Balance
    print_section("2. BALANCE RETRIEVAL TEST")
    balance_success, initial_balance, currency = test_get_user_balance(TEST_USER_ID)
    test_results['get_balance'] = balance_success
    
    # Test 3: Top Up Balance
    print_section("3. BALANCE TOP-UP TEST")
    topup_success, topup_result = test_update_balance(TEST_USER_ID, TEST_AMOUNTS['topup'], "topup")
    test_results['topup'] = topup_success
    
    # Test 4: Get Updated Balance
    print_section("4. BALANCE VERIFICATION AFTER TOP-UP")
    balance_after_topup_success, balance_after_topup, _ = test_get_user_balance(TEST_USER_ID)
    test_results['balance_after_topup'] = balance_after_topup_success
    
    # Test 5: Marketplace Purchase with Sufficient Funds
    print_section("5. MARKETPLACE PURCHASE TEST (SUFFICIENT FUNDS)")
    fake_seller_id = str(uuid.uuid4())
    fake_product_id = str(uuid.uuid4())
    purchase_success, purchase_result = test_process_transaction(
        TEST_USER_ID, fake_seller_id, fake_product_id, TEST_AMOUNTS['purchase']
    )
    test_results['marketplace_purchase'] = purchase_success
    
    # Test 6: Platform Fee Calculation
    print_section("6. PLATFORM FEE CALCULATION TEST")
    test_results['platform_fee'] = test_platform_fee_calculation()
    
    # Test 7: Withdrawal Test
    print_section("7. BALANCE WITHDRAWAL TEST")
    withdrawal_success, withdrawal_result = test_update_balance(TEST_USER_ID, TEST_AMOUNTS['withdrawal'], "withdrawal")
    test_results['withdrawal'] = withdrawal_success
    
    # Test 8: Transaction History
    print_section("8. TRANSACTION HISTORY TEST")
    history_success, transactions = test_get_transactions(TEST_USER_ID)
    test_results['transaction_history'] = history_success
    
    # Test 9: Insufficient Funds Scenarios
    print_section("9. INSUFFICIENT FUNDS SCENARIOS")
    test_results['insufficient_funds_purchase'] = test_insufficient_funds_scenario(TEST_USER_ID)
    test_results['insufficient_funds_withdrawal'] = test_withdrawal_insufficient_funds()
    
    # Test 10: Invalid Amount Scenarios
    print_section("10. INVALID AMOUNT SCENARIOS")
    test_results['invalid_amounts'] = test_invalid_amounts()
    
    # Test 11: Final Balance Check
    print_section("11. FINAL BALANCE VERIFICATION")
    final_balance_success, final_balance, _ = test_get_user_balance(TEST_USER_ID)
    test_results['final_balance'] = final_balance_success
    
    return test_results

def print_test_summary(test_results):
    """Print comprehensive test summary"""
    print_section("TEST SUMMARY")
    
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
    
    # Critical issues
    critical_tests = ['backend_health', 'get_balance', 'topup', 'marketplace_purchase', 'platform_fee']
    critical_failures = [test for test in critical_tests if not test_results.get(test, False)]
    
    if critical_failures:
        print("🚨 CRITICAL ISSUES DETECTED:")
        for failure in critical_failures:
            print(f"   ❌ {failure.replace('_', ' ').title()}")
    else:
        print("✅ ALL CRITICAL BALANCE SYSTEM FUNCTIONS WORKING")
    
    print()
    
    # Recommendations
    if success_rate < 80:
        print("⚠️  RECOMMENDATIONS:")
        print("   - Review failed tests and fix critical issues")
        print("   - Check database schema and function implementations")
        print("   - Verify API endpoint configurations")
    elif success_rate < 100:
        print("⚠️  MINOR ISSUES DETECTED:")
        print("   - Review failed tests for edge case handling")
        print("   - Consider improving error messages and validation")
    else:
        print("🎉 EXCELLENT! All balance system tests passed successfully!")

def main():
    """Main testing function"""
    try:
        test_results = run_comprehensive_balance_tests()
        print_test_summary(test_results)
        
        # Return success status for automation
        critical_tests = ['backend_health', 'get_balance', 'topup', 'marketplace_purchase', 'platform_fee']
        critical_success = all(test_results.get(test, False) for test in critical_tests)
        
        return critical_success
        
    except Exception as e:
        print(f"\n❌ TESTING FAILED WITH EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)