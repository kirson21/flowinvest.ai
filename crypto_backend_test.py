#!/usr/bin/env python3
"""
Comprehensive Backend Testing for f01i.ai Crypto Payment System
Testing Agent - Crypto Payment System Implementation
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://f01i-crypto.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CryptoPaymentTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'response_data': response_data
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def test_crypto_health_check(self):
        """Test /api/crypto/health endpoint"""
        try:
            response = requests.get(f"{API_BASE}/crypto/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ['status', 'mode', 'supported_currencies', 'supported_networks']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Crypto Health Check",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Verify expected values
                if data['status'] != 'healthy':
                    self.log_result(
                        "Crypto Health Check",
                        False,
                        f"Expected status 'healthy', got '{data['status']}'",
                        data
                    )
                    return
                
                if 'USDT' not in data['supported_currencies'] or 'USDC' not in data['supported_currencies']:
                    self.log_result(
                        "Crypto Health Check",
                        False,
                        f"Missing USDT or USDC in supported currencies: {data['supported_currencies']}",
                        data
                    )
                    return
                
                self.log_result(
                    "Crypto Health Check",
                    True,
                    f"Service healthy, mode: {data['mode']}, currencies: {data['supported_currencies']}"
                )
            else:
                self.log_result(
                    "Crypto Health Check",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Crypto Health Check",
                False,
                f"Request failed: {str(e)}"
            )

    def test_supported_currencies(self):
        """Test /api/crypto/supported-currencies endpoint"""
        try:
            response = requests.get(f"{API_BASE}/crypto/supported-currencies", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure
                if not data.get('success'):
                    self.log_result(
                        "Supported Currencies",
                        False,
                        "Response success field is False or missing",
                        data
                    )
                    return
                
                currencies = data.get('currencies', [])
                networks = data.get('networks', {})
                
                # Check for USDT and USDC
                currency_codes = [c['code'] for c in currencies]
                if 'USDT' not in currency_codes or 'USDC' not in currency_codes:
                    self.log_result(
                        "Supported Currencies",
                        False,
                        f"Missing USDT or USDC in currencies: {currency_codes}",
                        data
                    )
                    return
                
                # Verify USDT supports both ERC20 and TRC20
                usdt_currency = next((c for c in currencies if c['code'] == 'USDT'), None)
                if not usdt_currency or 'ERC20' not in usdt_currency['networks'] or 'TRC20' not in usdt_currency['networks']:
                    self.log_result(
                        "Supported Currencies",
                        False,
                        f"USDT should support both ERC20 and TRC20 networks: {usdt_currency}",
                        data
                    )
                    return
                
                # Verify USDC supports only ERC20
                usdc_currency = next((c for c in currencies if c['code'] == 'USDC'), None)
                if not usdc_currency or usdc_currency['networks'] != ['ERC20']:
                    self.log_result(
                        "Supported Currencies",
                        False,
                        f"USDC should support only ERC20 network: {usdc_currency}",
                        data
                    )
                    return
                
                # Verify network information
                if 'ERC20' not in networks or 'TRC20' not in networks:
                    self.log_result(
                        "Supported Currencies",
                        False,
                        f"Missing network information: {list(networks.keys())}",
                        data
                    )
                    return
                
                self.log_result(
                    "Supported Currencies",
                    True,
                    f"Found {len(currencies)} currencies with proper network support"
                )
            else:
                self.log_result(
                    "Supported Currencies",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Supported Currencies",
                False,
                f"Request failed: {str(e)}"
            )

    def test_deposit_address_generation(self):
        """Test /api/crypto/deposit/address endpoint"""
        test_cases = [
            {"currency": "USDT", "network": "ERC20", "should_succeed": True},
            {"currency": "USDT", "network": "TRC20", "should_succeed": True},
            {"currency": "USDC", "network": "ERC20", "should_succeed": True},
            {"currency": "USDC", "network": "TRC20", "should_succeed": False},  # Should fail
            {"currency": "BTC", "network": "ERC20", "should_succeed": False},   # Should fail
            {"currency": "USDT", "network": "BSC", "should_succeed": False},    # Should fail
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "currency": case["currency"],
                    "network": case["network"]
                }
                
                response = requests.post(
                    f"{API_BASE}/crypto/deposit/address",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if case["should_succeed"]:
                        if data.get('success'):
                            # Verify address format
                            address = data.get('address', '')
                            if case["network"] == "ERC20" and not address.startswith('0x'):
                                self.log_result(
                                    f"Deposit Address - {case['currency']} {case['network']}",
                                    False,
                                    f"ERC20 address should start with 0x: {address}",
                                    data
                                )
                                continue
                            elif case["network"] == "TRC20" and not address.startswith('T'):
                                self.log_result(
                                    f"Deposit Address - {case['currency']} {case['network']}",
                                    False,
                                    f"TRC20 address should start with T: {address}",
                                    data
                                )
                                continue
                            
                            self.log_result(
                                f"Deposit Address - {case['currency']} {case['network']}",
                                True,
                                f"Generated address: {address[:10]}...{address[-10:]}"
                            )
                        else:
                            self.log_result(
                                f"Deposit Address - {case['currency']} {case['network']}",
                                False,
                                f"Expected success but got failure: {data.get('detail', 'Unknown error')}",
                                data
                            )
                    else:
                        if not data.get('success'):
                            self.log_result(
                                f"Deposit Address - {case['currency']} {case['network']} (Invalid)",
                                True,
                                f"Correctly rejected invalid request: {data.get('detail', 'Unknown error')}"
                            )
                        else:
                            self.log_result(
                                f"Deposit Address - {case['currency']} {case['network']} (Invalid)",
                                False,
                                "Should have rejected invalid currency/network combination",
                                data
                            )
                else:
                    self.log_result(
                        f"Deposit Address - {case['currency']} {case['network']}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Deposit Address - {case['currency']} {case['network']}",
                    False,
                    f"Request failed: {str(e)}"
                )

    def test_withdrawal_fees(self):
        """Test /api/crypto/fees endpoint"""
        try:
            response = requests.get(f"{API_BASE}/crypto/fees", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_result(
                        "Withdrawal Fees",
                        False,
                        "Response success field is False or missing",
                        data
                    )
                    return
                
                # Verify fee structure
                fees = data.get('fees', {})
                limits = data.get('limits', {})
                
                required_fee_fields = ['withdrawal', 'deposit']
                required_limit_fields = ['min_withdrawal', 'max_withdrawal', 'min_deposit']
                
                missing_fee_fields = [field for field in required_fee_fields if field not in fees]
                missing_limit_fields = [field for field in required_limit_fields if field not in limits]
                
                if missing_fee_fields or missing_limit_fields:
                    self.log_result(
                        "Withdrawal Fees",
                        False,
                        f"Missing fields - fees: {missing_fee_fields}, limits: {missing_limit_fields}",
                        data
                    )
                    return
                
                # Verify withdrawal fee structure
                withdrawal_fee = fees.get('withdrawal', {})
                if 'minimum_fee' not in withdrawal_fee or 'percentage_fee' not in withdrawal_fee:
                    self.log_result(
                        "Withdrawal Fees",
                        False,
                        "Missing minimum_fee or percentage_fee in withdrawal fees",
                        data
                    )
                    return
                
                self.log_result(
                    "Withdrawal Fees",
                    True,
                    f"Fee structure: min ${withdrawal_fee['minimum_fee']}, {withdrawal_fee['percentage_fee']*100}% of amount"
                )
            else:
                self.log_result(
                    "Withdrawal Fees",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Withdrawal Fees",
                False,
                f"Request failed: {str(e)}"
            )

    def test_mock_withdrawal(self):
        """Test /api/crypto/withdrawal endpoint"""
        test_cases = [
            {
                "recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF",
                "amount": 100.0,
                "currency": "USDT",
                "network": "ERC20",
                "should_succeed": True
            },
            {
                "recipient_address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5oNDMnt",
                "amount": 50.0,
                "currency": "USDT",
                "network": "TRC20",
                "should_succeed": True
            },
            {
                "recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF",
                "amount": 25.0,
                "currency": "USDC",
                "network": "ERC20",
                "should_succeed": True
            },
            {
                "recipient_address": "invalid_address",
                "amount": 100.0,
                "currency": "USDT",
                "network": "ERC20",
                "should_succeed": False
            },
            {
                "recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF",
                "amount": -10.0,
                "currency": "USDT",
                "network": "ERC20",
                "should_succeed": False
            },
            {
                "recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4CAF",
                "amount": 100.0,
                "currency": "BTC",
                "network": "ERC20",
                "should_succeed": False
            }
        ]
        
        for i, case in enumerate(test_cases):
            try:
                response = requests.post(
                    f"{API_BASE}/crypto/withdrawal",
                    json=case,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if case["should_succeed"]:
                        if data.get('success'):
                            # Verify response structure
                            required_fields = ['crypto_transaction_id', 'amount', 'fee', 'total_deducted', 'status']
                            missing_fields = [field for field in required_fields if field not in data]
                            
                            if missing_fields:
                                self.log_result(
                                    f"Mock Withdrawal {i+1} - {case['currency']} {case['network']}",
                                    False,
                                    f"Missing fields in response: {missing_fields}",
                                    data
                                )
                                continue
                            
                            # Verify fee calculation
                            expected_fee = max(5.0, case['amount'] * 0.02)
                            actual_fee = data.get('fee', 0)
                            
                            if abs(actual_fee - expected_fee) > 0.01:
                                self.log_result(
                                    f"Mock Withdrawal {i+1} - {case['currency']} {case['network']}",
                                    False,
                                    f"Fee calculation incorrect. Expected: ${expected_fee}, Got: ${actual_fee}",
                                    data
                                )
                                continue
                            
                            self.log_result(
                                f"Mock Withdrawal {i+1} - {case['currency']} {case['network']}",
                                True,
                                f"Withdrawal ${case['amount']} with fee ${actual_fee}, TX: {data['crypto_transaction_id'][:8]}..."
                            )
                        else:
                            self.log_result(
                                f"Mock Withdrawal {i+1} - {case['currency']} {case['network']}",
                                False,
                                f"Expected success but got failure: {data.get('detail', 'Unknown error')}",
                                data
                            )
                    else:
                        if not data.get('success'):
                            self.log_result(
                                f"Mock Withdrawal {i+1} - Invalid Request",
                                True,
                                f"Correctly rejected invalid request: {data.get('detail', 'Unknown error')}"
                            )
                        else:
                            self.log_result(
                                f"Mock Withdrawal {i+1} - Invalid Request",
                                False,
                                "Should have rejected invalid withdrawal request",
                                data
                            )
                else:
                    self.log_result(
                        f"Mock Withdrawal {i+1}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Mock Withdrawal {i+1}",
                    False,
                    f"Request failed: {str(e)}"
                )

    def test_transaction_history(self):
        """Test /api/crypto/transactions endpoint"""
        try:
            response = requests.get(f"{API_BASE}/crypto/transactions", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_result(
                        "Transaction History",
                        False,
                        "Response success field is False or missing",
                        data
                    )
                    return
                
                transactions = data.get('transactions', [])
                count = data.get('count', 0)
                
                if not isinstance(transactions, list):
                    self.log_result(
                        "Transaction History",
                        False,
                        "Transactions should be a list",
                        data
                    )
                    return
                
                # Verify transaction structure
                if transactions:
                    first_tx = transactions[0]
                    required_fields = ['id', 'transaction_type', 'currency', 'network', 'amount', 'status', 'created_at']
                    missing_fields = [field for field in required_fields if field not in first_tx]
                    
                    if missing_fields:
                        self.log_result(
                            "Transaction History",
                            False,
                            f"Missing fields in transaction: {missing_fields}",
                            first_tx
                        )
                        return
                
                self.log_result(
                    "Transaction History",
                    True,
                    f"Retrieved {len(transactions)} transactions, total count: {count}"
                )
            else:
                self.log_result(
                    "Transaction History",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Transaction History",
                False,
                f"Request failed: {str(e)}"
            )

    def test_transaction_status(self):
        """Test /api/crypto/status/{transaction_id} endpoint"""
        # Test with a mock transaction ID
        test_transaction_id = str(uuid.uuid4())
        
        try:
            response = requests.get(f"{API_BASE}/crypto/status/{test_transaction_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_result(
                        "Transaction Status",
                        False,
                        "Response success field is False or missing",
                        data
                    )
                    return
                
                transaction = data.get('transaction', {})
                
                # Verify transaction structure
                required_fields = ['id', 'transaction_type', 'currency', 'network', 'amount', 'status', 'created_at']
                missing_fields = [field for field in required_fields if field not in transaction]
                
                if missing_fields:
                    self.log_result(
                        "Transaction Status",
                        False,
                        f"Missing fields in transaction: {missing_fields}",
                        data
                    )
                    return
                
                # Verify the transaction ID matches
                if transaction.get('id') != test_transaction_id:
                    self.log_result(
                        "Transaction Status",
                        False,
                        f"Transaction ID mismatch. Expected: {test_transaction_id}, Got: {transaction.get('id')}",
                        data
                    )
                    return
                
                self.log_result(
                    "Transaction Status",
                    True,
                    f"Status: {transaction['status']}, Type: {transaction['transaction_type']}, Amount: ${transaction['amount']}"
                )
            else:
                self.log_result(
                    "Transaction Status",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Transaction Status",
                False,
                f"Request failed: {str(e)}"
            )

    def run_all_tests(self):
        """Run all crypto payment system tests"""
        print("=" * 80)
        print("🚀 CRYPTO PAYMENT SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        # Run all tests
        self.test_crypto_health_check()
        self.test_supported_currencies()
        self.test_deposit_address_generation()
        self.test_withdrawal_fees()
        self.test_mock_withdrawal()
        self.test_transaction_history()
        self.test_transaction_status()
        
        # Print summary
        print("=" * 80)
        print("📊 CRYPTO PAYMENT SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("🔍 DETAILED FINDINGS:")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        successes = []
        
        for result in self.results:
            if result['success']:
                successes.append(result)
            elif any(keyword in result['test'].lower() for keyword in ['health', 'currencies', 'withdrawal', 'transaction']):
                critical_failures.append(result)
            else:
                minor_issues.append(result)
        
        if critical_failures:
            print("\n🚨 CRITICAL ISSUES:")
            for result in critical_failures:
                print(f"   • {result['test']}: {result['details']}")
        
        if minor_issues:
            print("\n⚠️ MINOR ISSUES:")
            for result in minor_issues:
                print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ SUCCESSFUL TESTS: {len(successes)}")
        
        return self.passed_tests, self.failed_tests, self.total_tests

def main():
    """Main test execution"""
    tester = CryptoPaymentTester()
    passed, failed, total = tester.run_all_tests()
    
    # Return appropriate exit code
    if failed == 0:
        print("🎉 ALL CRYPTO PAYMENT TESTS PASSED!")
        return 0
    else:
        print(f"⚠️ {failed} TESTS FAILED OUT OF {total}")
        return 1

if __name__ == "__main__":
    exit(main())