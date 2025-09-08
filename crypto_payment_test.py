#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Crypto Payment Reference System
Testing Agent - Crypto Payment Reference System Implementation
"""

import requests
import json
import time
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://ai-flow-invest.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super Admin for testing
ADMIN_KEY = "admin123"

class CryptoPaymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CryptoPaymentTester/1.0'
        })
        self.test_results = []
        self.test_references = []  # Track generated references for cleanup
        
    def log_test(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def test_backend_health(self):
        """Test basic backend health endpoints"""
        print("=== TESTING BACKEND HEALTH ===")
        
        # Test API root
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root Endpoint", True, f"Status: {response.status_code}, Features: {data.get('features', [])}")
            else:
                self.log_test("API Root Endpoint", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                self.log_test("Health Check", True, f"Status: {response.status_code}, Services: {services}")
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
        
        # Test crypto health
        try:
            response = self.session.get(f"{BACKEND_URL}/crypto/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Crypto Health Check", True, f"Status: {response.status_code}, Mode: {data.get('mode')}")
            else:
                self.log_test("Crypto Health Check", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Crypto Health Check", False, f"Exception: {str(e)}")

    def test_supported_currencies(self):
        """Test supported currencies endpoint"""
        print("=== TESTING SUPPORTED CURRENCIES ===")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/crypto/supported-currencies")
            if response.status_code == 200:
                data = response.json()
                currencies = data.get('currencies', [])
                networks = data.get('networks', {})
                
                # Verify expected currencies
                expected_currencies = ['USDT', 'USDC']
                found_currencies = [c['code'] for c in currencies]
                
                if all(curr in found_currencies for curr in expected_currencies):
                    self.log_test("Supported Currencies", True, f"Found currencies: {found_currencies}, Networks: {list(networks.keys())}")
                else:
                    self.log_test("Supported Currencies", False, f"Missing currencies. Expected: {expected_currencies}, Found: {found_currencies}")
            else:
                self.log_test("Supported Currencies", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Supported Currencies", False, f"Exception: {str(e)}")

    def test_deposit_address_generation(self):
        """Test crypto deposit address generation with unique payment references"""
        print("=== TESTING DEPOSIT ADDRESS GENERATION ===")
        
        test_cases = [
            {"currency": "USDT", "network": "ERC20"},
            {"currency": "USDT", "network": "TRC20"},
            {"currency": "USDC", "network": "ERC20"}
        ]
        
        generated_references = []
        
        for case in test_cases:
            try:
                payload = {
                    "currency": case["currency"],
                    "network": case["network"]
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/crypto/deposit/address",
                    json=payload,
                    params={"user_id": TEST_USER_ID}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        reference = data.get('deposit_reference')
                        address = data.get('address')
                        transaction_id = data.get('transaction_id')
                        
                        # Verify unique reference generation
                        if reference and reference not in generated_references:
                            generated_references.append(reference)
                            self.test_references.append(reference)
                            
                            # Verify address is returned
                            if address:
                                self.log_test(
                                    f"Deposit Address - {case['currency']} {case['network']}", 
                                    True, 
                                    f"Reference: {reference}, Address: {address[:10]}...{address[-10:]}, TX ID: {transaction_id}"
                                )
                            else:
                                self.log_test(f"Deposit Address - {case['currency']} {case['network']}", False, "No address returned", data)
                        else:
                            self.log_test(f"Deposit Address - {case['currency']} {case['network']}", False, f"Duplicate or missing reference: {reference}")
                    else:
                        self.log_test(f"Deposit Address - {case['currency']} {case['network']}", False, f"API returned success=false: {data.get('detail')}")
                else:
                    self.log_test(f"Deposit Address - {case['currency']} {case['network']}", False, f"Status: {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_test(f"Deposit Address - {case['currency']} {case['network']}", False, f"Exception: {str(e)}")
        
        # Test uniqueness of references
        if len(generated_references) == len(set(generated_references)) and len(generated_references) > 0:
            self.log_test("Payment Reference Uniqueness", True, f"All {len(generated_references)} references are unique")
        else:
            self.log_test("Payment Reference Uniqueness", False, f"Duplicate references found in {generated_references}")

    def test_invalid_deposit_requests(self):
        """Test invalid deposit request scenarios"""
        print("=== TESTING INVALID DEPOSIT REQUESTS ===")
        
        invalid_cases = [
            {"currency": "BTC", "network": "ERC20", "expected_error": "Unsupported currency"},
            {"currency": "USDT", "network": "BSC", "expected_error": "Unsupported network"},
            {"currency": "USDC", "network": "TRC20", "expected_error": "USDC only supports ERC20 network"}
        ]
        
        for case in invalid_cases:
            try:
                payload = {
                    "currency": case["currency"],
                    "network": case["network"]
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/crypto/deposit/address",
                    json=payload,
                    params={"user_id": TEST_USER_ID}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success') and case["expected_error"] in data.get('detail', ''):
                        self.log_test(f"Invalid Request - {case['currency']} {case['network']}", True, f"Correctly rejected: {data.get('detail')}")
                    else:
                        self.log_test(f"Invalid Request - {case['currency']} {case['network']}", False, f"Should have been rejected: {data}")
                else:
                    self.log_test(f"Invalid Request - {case['currency']} {case['network']}", False, f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Invalid Request - {case['currency']} {case['network']}", False, f"Exception: {str(e)}")

    def test_manual_confirmation_system(self):
        """Test manual confirmation system for admin testing"""
        print("=== TESTING MANUAL CONFIRMATION SYSTEM ===")
        
        # First create a deposit to confirm
        try:
            payload = {"currency": "USDT", "network": "ERC20"}
            response = self.session.post(
                f"{BACKEND_URL}/crypto/deposit/address",
                json=payload,
                params={"user_id": TEST_USER_ID}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    reference = data.get('deposit_reference')
                    transaction_id = data.get('transaction_id')
                    
                    # Now test manual confirmation
                    confirm_response = self.session.post(
                        f"{BACKEND_URL}/crypto/deposit/manual-confirm",
                        params={
                            "deposit_reference": reference,
                            "transaction_hash": f"0x{'a' * 64}",  # Mock transaction hash
                            "amount": 100.50,
                            "admin_key": ADMIN_KEY
                        }
                    )
                    
                    if confirm_response.status_code == 200:
                        confirm_data = confirm_response.json()
                        if confirm_data.get('success'):
                            self.log_test(
                                "Manual Confirmation", 
                                True, 
                                f"Confirmed deposit: {reference}, Amount: ${confirm_data.get('amount')}, User: {confirm_data.get('user_id')}"
                            )
                        else:
                            self.log_test("Manual Confirmation", False, f"Confirmation failed: {confirm_data.get('detail')}")
                    else:
                        self.log_test("Manual Confirmation", False, f"Status: {confirm_response.status_code}")
                else:
                    self.log_test("Manual Confirmation Setup", False, "Failed to create deposit for testing")
            else:
                self.log_test("Manual Confirmation Setup", False, f"Failed to create deposit: {response.status_code}")
                
        except Exception as e:
            self.log_test("Manual Confirmation", False, f"Exception: {str(e)}")
        
        # Test invalid confirmation scenarios
        invalid_cases = [
            {"reference": "INVALID_REF", "admin_key": ADMIN_KEY, "expected": "Transaction not found"},
            {"reference": "VALID_REF", "admin_key": "wrong_key", "expected": "Unauthorized"}
        ]
        
        for case in invalid_cases:
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/crypto/deposit/manual-confirm",
                    params={
                        "deposit_reference": case["reference"],
                        "transaction_hash": f"0x{'b' * 64}",
                        "amount": 50.0,
                        "admin_key": case["admin_key"]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success') and case["expected"] in data.get('detail', ''):
                        self.log_test(f"Invalid Confirmation - {case['reference'][:10]}", True, f"Correctly rejected: {data.get('detail')}")
                    else:
                        self.log_test(f"Invalid Confirmation - {case['reference'][:10]}", False, f"Should have been rejected: {data}")
                        
            except Exception as e:
                self.log_test(f"Invalid Confirmation - {case['reference'][:10]}", False, f"Exception: {str(e)}")

    def test_webhook_processing(self):
        """Test webhook processing for deposit confirmations"""
        print("=== TESTING WEBHOOK PROCESSING ===")
        
        # First create a deposit to process via webhook
        try:
            payload = {"currency": "USDT", "network": "TRC20"}
            response = self.session.post(
                f"{BACKEND_URL}/crypto/deposit/address",
                json=payload,
                params={"user_id": TEST_USER_ID}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    reference = data.get('deposit_reference')
                    
                    # Simulate Capitalist webhook callback
                    webhook_payload = {
                        "payment_reference": reference,
                        "amount": 75.25,
                        "transaction_hash": f"0x{'c' * 64}",
                        "status": "confirmed"
                    }
                    
                    webhook_response = self.session.post(
                        f"{BACKEND_URL}/crypto/webhook/capitalist",
                        json=webhook_payload
                    )
                    
                    if webhook_response.status_code == 200:
                        webhook_data = webhook_response.json()
                        if webhook_data.get('success'):
                            self.log_test(
                                "Webhook Processing", 
                                True, 
                                f"Processed webhook: Reference {reference}, Amount: ${webhook_data.get('amount')}, User: {webhook_data.get('user_id')}"
                            )
                        else:
                            self.log_test("Webhook Processing", False, f"Webhook failed: {webhook_data.get('detail')}")
                    else:
                        self.log_test("Webhook Processing", False, f"Status: {webhook_response.status_code}")
                else:
                    self.log_test("Webhook Setup", False, "Failed to create deposit for webhook testing")
            else:
                self.log_test("Webhook Setup", False, f"Failed to create deposit: {response.status_code}")
                
        except Exception as e:
            self.log_test("Webhook Processing", False, f"Exception: {str(e)}")
        
        # Test invalid webhook scenarios
        invalid_webhooks = [
            {"payment_reference": "", "amount": 100, "expected": "Invalid callback data"},
            {"payment_reference": "NONEXISTENT", "amount": 100, "expected": "Transaction not found"},
            {"payment_reference": "VALID", "amount": 0, "expected": "Invalid callback data"}
        ]
        
        for case in invalid_webhooks:
            try:
                webhook_payload = {
                    "payment_reference": case["payment_reference"],
                    "amount": case["amount"],
                    "transaction_hash": f"0x{'d' * 64}",
                    "status": "confirmed"
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/crypto/webhook/capitalist",
                    json=webhook_payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success') and case["expected"] in data.get('detail', ''):
                        self.log_test(f"Invalid Webhook - {case['payment_reference'] or 'Empty'}", True, f"Correctly rejected: {data.get('detail')}")
                    else:
                        self.log_test(f"Invalid Webhook - {case['payment_reference'] or 'Empty'}", False, f"Should have been rejected: {data}")
                        
            except Exception as e:
                self.log_test(f"Invalid Webhook - {case['payment_reference'] or 'Empty'}", False, f"Exception: {str(e)}")

    def test_transaction_management(self):
        """Test transaction management endpoints"""
        print("=== TESTING TRANSACTION MANAGEMENT ===")
        
        # Test get crypto transactions
        try:
            response = self.session.get(
                f"{BACKEND_URL}/crypto/transactions",
                params={"user_id": TEST_USER_ID, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    transactions = data.get('transactions', [])
                    self.log_test("Get Crypto Transactions", True, f"Retrieved {len(transactions)} transactions")
                else:
                    self.log_test("Get Crypto Transactions", False, f"API returned success=false: {data.get('detail')}")
            else:
                self.log_test("Get Crypto Transactions", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Crypto Transactions", False, f"Exception: {str(e)}")
        
        # Test get user deposits
        try:
            response = self.session.get(f"{BACKEND_URL}/crypto/deposits/user/{TEST_USER_ID}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    deposits = data.get('deposits', [])
                    self.log_test("Get User Deposits", True, f"Retrieved {len(deposits)} deposits")
                else:
                    self.log_test("Get User Deposits", False, f"API returned success=false: {data.get('detail')}")
            else:
                self.log_test("Get User Deposits", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get User Deposits", False, f"Exception: {str(e)}")
        
        # Test get pending deposits (admin)
        try:
            response = self.session.get(
                f"{BACKEND_URL}/crypto/deposits/pending",
                params={"admin_key": ADMIN_KEY}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pending = data.get('pending_deposits', [])
                    self.log_test("Get Pending Deposits", True, f"Retrieved {len(pending)} pending deposits")
                else:
                    self.log_test("Get Pending Deposits", False, f"API returned success=false: {data.get('detail')}")
            else:
                self.log_test("Get Pending Deposits", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Pending Deposits", False, f"Exception: {str(e)}")

    def test_transaction_status(self):
        """Test individual transaction status retrieval"""
        print("=== TESTING TRANSACTION STATUS ===")
        
        # First create a transaction to check status
        try:
            payload = {"currency": "USDC", "network": "ERC20"}
            response = self.session.post(
                f"{BACKEND_URL}/crypto/deposit/address",
                json=payload,
                params={"user_id": TEST_USER_ID}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    transaction_id = data.get('transaction_id')
                    
                    # Check transaction status
                    status_response = self.session.get(
                        f"{BACKEND_URL}/crypto/status/{transaction_id}",
                        params={"user_id": TEST_USER_ID}
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get('success'):
                            transaction = status_data.get('transaction', {})
                            self.log_test(
                                "Transaction Status", 
                                True, 
                                f"Status: {transaction.get('status')}, Currency: {transaction.get('currency')}, Reference: {transaction.get('reference')}"
                            )
                        else:
                            self.log_test("Transaction Status", False, f"Status check failed: {status_data.get('detail')}")
                    else:
                        self.log_test("Transaction Status", False, f"Status: {status_response.status_code}")
                else:
                    self.log_test("Transaction Status Setup", False, "Failed to create transaction for status testing")
            else:
                self.log_test("Transaction Status Setup", False, f"Failed to create transaction: {response.status_code}")
                
        except Exception as e:
            self.log_test("Transaction Status", False, f"Exception: {str(e)}")
        
        # Test invalid transaction ID
        try:
            response = self.session.get(
                f"{BACKEND_URL}/crypto/status/invalid-id",
                params={"user_id": TEST_USER_ID}
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('success') and "not found" in data.get('detail', '').lower():
                    self.log_test("Invalid Transaction Status", True, f"Correctly rejected invalid ID: {data.get('detail')}")
                else:
                    self.log_test("Invalid Transaction Status", False, f"Should have been rejected: {data}")
                    
        except Exception as e:
            self.log_test("Invalid Transaction Status", False, f"Exception: {str(e)}")

    def test_withdrawal_system(self):
        """Test withdrawal system with balance validation"""
        print("=== TESTING WITHDRAWAL SYSTEM ===")
        
        # Test withdrawal fees endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/crypto/fees")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    fees = data.get('fees', {})
                    limits = data.get('limits', {})
                    self.log_test("Withdrawal Fees", True, f"Min fee: ${fees.get('withdrawal', {}).get('minimum_fee')}, Limits: {limits}")
                else:
                    self.log_test("Withdrawal Fees", False, f"API returned success=false")
            else:
                self.log_test("Withdrawal Fees", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Withdrawal Fees", False, f"Exception: {str(e)}")
        
        # Test withdrawal with insufficient balance (expected to fail)
        try:
            withdrawal_payload = {
                "recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C87",
                "amount": 999999.99,  # Very high amount to trigger insufficient balance
                "currency": "USDT",
                "network": "ERC20",
                "memo": "Test withdrawal"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/crypto/withdrawal",
                json=withdrawal_payload,
                params={"user_id": TEST_USER_ID}
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('success') and "insufficient balance" in data.get('detail', '').lower():
                    self.log_test("Insufficient Balance Withdrawal", True, f"Correctly rejected: {data.get('detail')}")
                else:
                    self.log_test("Insufficient Balance Withdrawal", False, f"Should have been rejected for insufficient balance: {data}")
            else:
                self.log_test("Insufficient Balance Withdrawal", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Insufficient Balance Withdrawal", False, f"Exception: {str(e)}")
        
        # Test withdrawal with invalid parameters
        invalid_withdrawals = [
            {"recipient_address": "invalid", "amount": 100, "currency": "USDT", "network": "ERC20", "expected": "Invalid recipient address"},
            {"recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C87", "amount": -10, "currency": "USDT", "network": "ERC20", "expected": "Invalid amount"},
            {"recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C87", "amount": 100, "currency": "BTC", "network": "ERC20", "expected": "Unsupported currency"}
        ]
        
        for case in invalid_withdrawals:
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/crypto/withdrawal",
                    json=case,
                    params={"user_id": TEST_USER_ID}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success') and case["expected"].lower() in data.get('detail', '').lower():
                        self.log_test(f"Invalid Withdrawal - {case['expected'][:20]}", True, f"Correctly rejected: {data.get('detail')}")
                    else:
                        self.log_test(f"Invalid Withdrawal - {case['expected'][:20]}", False, f"Should have been rejected: {data}")
                        
            except Exception as e:
                self.log_test(f"Invalid Withdrawal - {case['expected'][:20]}", False, f"Exception: {str(e)}")

    def test_database_integration(self):
        """Test database integration and data persistence"""
        print("=== TESTING DATABASE INTEGRATION ===")
        
        # Create a deposit and verify it's stored in database
        try:
            payload = {"currency": "USDT", "network": "ERC20"}
            response = self.session.post(
                f"{BACKEND_URL}/crypto/deposit/address",
                json=payload,
                params={"user_id": TEST_USER_ID}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    reference = data.get('deposit_reference')
                    transaction_id = data.get('transaction_id')
                    
                    # Verify transaction appears in user's transaction list
                    time.sleep(1)  # Brief delay for database consistency
                    
                    transactions_response = self.session.get(
                        f"{BACKEND_URL}/crypto/transactions",
                        params={"user_id": TEST_USER_ID, "limit": 50}
                    )
                    
                    if transactions_response.status_code == 200:
                        tx_data = transactions_response.json()
                        if tx_data.get('success'):
                            transactions = tx_data.get('transactions', [])
                            
                            # Look for our transaction
                            found_tx = None
                            for tx in transactions:
                                if tx.get('reference') == reference:
                                    found_tx = tx
                                    break
                            
                            if found_tx:
                                self.log_test(
                                    "Database Integration", 
                                    True, 
                                    f"Transaction stored and retrieved: ID {found_tx.get('id')}, Reference: {found_tx.get('reference')}, Status: {found_tx.get('status')}"
                                )
                            else:
                                self.log_test("Database Integration", False, f"Transaction with reference {reference} not found in database")
                        else:
                            self.log_test("Database Integration", False, f"Failed to retrieve transactions: {tx_data.get('detail')}")
                    else:
                        self.log_test("Database Integration", False, f"Failed to retrieve transactions: {transactions_response.status_code}")
                else:
                    self.log_test("Database Integration Setup", False, "Failed to create transaction for database testing")
            else:
                self.log_test("Database Integration Setup", False, f"Failed to create transaction: {response.status_code}")
                
        except Exception as e:
            self.log_test("Database Integration", False, f"Exception: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all crypto payment reference system tests"""
        print("🚀 STARTING COMPREHENSIVE CRYPTO PAYMENT REFERENCE SYSTEM TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {TEST_USER_ID}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_backend_health()
        self.test_supported_currencies()
        self.test_deposit_address_generation()
        self.test_invalid_deposit_requests()
        self.test_manual_confirmation_system()
        self.test_webhook_processing()
        self.test_transaction_management()
        self.test_transaction_status()
        self.test_withdrawal_system()
        self.test_database_integration()
        
        # Calculate results
        end_time = time.time()
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("🏁 CRYPTO PAYMENT REFERENCE SYSTEM TESTING COMPLETE")
        print(f"⏱️  Total Time: {end_time - start_time:.2f} seconds")
        print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test_name']}: {result['details']}")
        
        print(f"\n📝 Generated {len(self.test_references)} unique payment references during testing")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results,
            'generated_references': self.test_references
        }

def main():
    """Main testing function"""
    tester = CryptoPaymentTester()
    results = tester.run_comprehensive_tests()
    
    # Return exit code based on results
    if results['failed_tests'] == 0:
        print("\n🎉 ALL TESTS PASSED! Crypto payment reference system is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {results['failed_tests']} tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())