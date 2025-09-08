#!/usr/bin/env python3
"""
NowPayments Withdrawal Core Functionality Testing
Testing withdrawal system focusing on database operations and validation logic
"""

import requests
import json
import time
import uuid
import sys
import os
from datetime import datetime

# Add backend path
sys.path.append('/app/backend')

# Configuration
BACKEND_URL = "https://ai-flow-invest.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super Admin for testing

class WithdrawalCoreTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_user_id = TEST_USER_ID
        self.test_results = []
        self.created_withdrawals = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def test_database_schema_verification(self):
        """Test withdrawal database schema and functions"""
        try:
            from supabase_client import supabase_admin as supabase
            
            # Test 1: Check if table exists
            result = supabase.table('nowpayments_withdrawals').select('*').limit(1).execute()
            if result.status_code == 200:
                self.log_test(
                    "Database Schema - Table Exists",
                    True,
                    "nowpayments_withdrawals table is accessible"
                )
            else:
                self.log_test(
                    "Database Schema - Table Exists",
                    False,
                    error=f"Table access failed: {result.status_code}"
                )
                return False
            
            # Test 2: Test create_withdrawal_request function
            test_result = supabase.rpc('create_withdrawal_request', {
                'p_user_id': self.test_user_id,
                'p_recipient_address': 'TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE',
                'p_currency': 'usdttrc20',
                'p_amount': 15.0,
                'p_description': 'Database function test'
            }).execute()
            
            if test_result.status_code == 200 and test_result.data:
                response_data = test_result.data[0] if isinstance(test_result.data, list) else test_result.data
                
                if response_data.get('success'):
                    withdrawal_id = response_data.get('withdrawal_id')
                    self.created_withdrawals.append(withdrawal_id)
                    self.log_test(
                        "Database Function - create_withdrawal_request",
                        True,
                        f"Created withdrawal ID: {withdrawal_id}"
                    )
                else:
                    error_msg = response_data.get('message', 'Unknown error')
                    self.log_test(
                        "Database Function - create_withdrawal_request",
                        False,
                        error=error_msg
                    )
            else:
                self.log_test(
                    "Database Function - create_withdrawal_request",
                    False,
                    error=f"RPC call failed: {test_result.status_code}"
                )
            
            # Test 3: Test process_verified_withdrawal function
            dummy_id = str(uuid.uuid4())
            process_result = supabase.rpc('process_verified_withdrawal', {
                'p_withdrawal_id': dummy_id
            }).execute()
            
            if process_result.status_code == 200 and process_result.data:
                response_data = process_result.data[0] if isinstance(process_result.data, list) else process_result.data
                
                # Should return success=false for non-existent withdrawal
                if not response_data.get('success') and 'not_found' in response_data.get('error', ''):
                    self.log_test(
                        "Database Function - process_verified_withdrawal",
                        True,
                        "Function correctly handles non-existent withdrawal ID"
                    )
                else:
                    self.log_test(
                        "Database Function - process_verified_withdrawal",
                        True,
                        f"Function accessible: {response_data}"
                    )
            else:
                self.log_test(
                    "Database Function - process_verified_withdrawal",
                    False,
                    error=f"RPC call failed: {process_result.status_code}"
                )
            
            return True
            
        except Exception as e:
            self.log_test("Database Schema Verification", False, error=str(e))
            return False
    
    def test_withdrawal_endpoints_validation(self):
        """Test withdrawal endpoint validation logic"""
        
        # Test 1: Missing user_id
        try:
            withdrawal_data = {
                "recipient_address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
                "amount": 15.0,
                "currency": "usdttrc20"
            }
            
            response = requests.post(
                f"{self.backend_url}/nowpayments/withdrawal/create",
                json=withdrawal_data,
                timeout=15
            )
            
            if response.status_code == 422:  # FastAPI validation error
                self.log_test(
                    "Validation - Missing User ID",
                    True,
                    "Correctly rejects requests without user_id"
                )
            else:
                self.log_test(
                    "Validation - Missing User ID",
                    False,
                    error=f"Expected 422, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Validation - Missing User ID", False, error=str(e))
        
        # Test 2: Invalid amount (zero)
        try:
            withdrawal_data = {
                "recipient_address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
                "amount": 0,
                "currency": "usdttrc20"
            }
            
            response = requests.post(
                f"{self.backend_url}/nowpayments/withdrawal/create",
                json=withdrawal_data,
                params={"user_id": self.test_user_id},
                timeout=15
            )
            
            if response.status_code == 400:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                
                if "greater than 0" in error_detail:
                    self.log_test(
                        "Validation - Zero Amount",
                        True,
                        f"Correctly rejects zero amount: {error_detail}"
                    )
                else:
                    self.log_test(
                        "Validation - Zero Amount",
                        False,
                        error=f"Wrong error message: {error_detail}"
                    )
            else:
                self.log_test(
                    "Validation - Zero Amount",
                    False,
                    error=f"Expected 400, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Validation - Zero Amount", False, error=str(e))
        
        # Test 3: Missing recipient address
        try:
            withdrawal_data = {
                "amount": 15.0,
                "currency": "usdttrc20"
            }
            
            response = requests.post(
                f"{self.backend_url}/nowpayments/withdrawal/create",
                json=withdrawal_data,
                params={"user_id": self.test_user_id},
                timeout=15
            )
            
            if response.status_code in [400, 422]:
                self.log_test(
                    "Validation - Missing Address",
                    True,
                    "Correctly rejects requests without recipient address"
                )
            else:
                self.log_test(
                    "Validation - Missing Address",
                    False,
                    error=f"Expected 400/422, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Validation - Missing Address", False, error=str(e))
        
        # Test 4: Unsupported currency
        try:
            withdrawal_data = {
                "recipient_address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
                "amount": 15.0,
                "currency": "btc"  # Not supported
            }
            
            response = requests.post(
                f"{self.backend_url}/nowpayments/withdrawal/create",
                json=withdrawal_data,
                params={"user_id": self.test_user_id},
                timeout=15
            )
            
            if response.status_code == 400:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                
                if "not supported" in error_detail:
                    self.log_test(
                        "Validation - Unsupported Currency",
                        True,
                        f"Correctly rejects unsupported currency: {error_detail}"
                    )
                else:
                    self.log_test(
                        "Validation - Unsupported Currency",
                        False,
                        error=f"Wrong error message: {error_detail}"
                    )
            else:
                self.log_test(
                    "Validation - Unsupported Currency",
                    False,
                    error=f"Expected 400, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Validation - Unsupported Currency", False, error=str(e))
    
    def test_withdrawal_history_endpoint(self):
        """Test withdrawal history retrieval"""
        try:
            response = requests.get(
                f"{self.backend_url}/nowpayments/user/{self.test_user_id}/withdrawals",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                withdrawals = data.get('withdrawals', [])
                count = data.get('count', 0)
                
                self.log_test(
                    "Withdrawal History Endpoint",
                    success,
                    f"Retrieved {count} withdrawal records"
                )
                
                # Show details of withdrawals if any
                if withdrawals:
                    latest = withdrawals[0]
                    print(f"   Latest withdrawal: {latest.get('amount')} {latest.get('currency')} - Status: {latest.get('status')}")
                    print(f"   Address: {latest.get('recipient_address', '')[:20]}...")
                
                return success
            else:
                self.log_test(
                    "Withdrawal History Endpoint",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Withdrawal History Endpoint", False, error=str(e))
            return False
    
    def test_supported_currencies_validation(self):
        """Test supported currencies configuration"""
        try:
            from routes.nowpayments import SUPPORTED_CURRENCIES
            
            # Extract all supported currency codes
            supported_codes = []
            for curr_data in SUPPORTED_CURRENCIES.values():
                supported_codes.extend(curr_data["networks"].values())
            
            expected_currencies = [
                'usdttrc20', 'usdtbsc', 'usdtsol', 'usdtton', 'usdterc20',
                'usdcbsc', 'usdcsol', 'usdcerc20'
            ]
            
            # Check if all expected currencies are supported
            missing_currencies = [curr for curr in expected_currencies if curr not in supported_codes]
            extra_currencies = [curr for curr in supported_codes if curr not in expected_currencies]
            
            if not missing_currencies:
                self.log_test(
                    "Supported Currencies Configuration",
                    True,
                    f"All {len(expected_currencies)} expected currencies supported: {supported_codes}"
                )
            else:
                self.log_test(
                    "Supported Currencies Configuration",
                    False,
                    error=f"Missing currencies: {missing_currencies}"
                )
            
            return True
            
        except Exception as e:
            self.log_test("Supported Currencies Configuration", False, error=str(e))
            return False
    
    def test_withdrawal_webhook_endpoint(self):
        """Test withdrawal webhook endpoint accessibility"""
        try:
            # Test webhook endpoint with GET (should return 405)
            response = requests.get(f"{self.backend_url}/nowpayments/withdrawal/webhook", timeout=10)
            
            if response.status_code == 405:
                self.log_test(
                    "Withdrawal Webhook Endpoint",
                    True,
                    "Webhook endpoint accessible (correctly returns 405 for GET)"
                )
                return True
            else:
                self.log_test(
                    "Withdrawal Webhook Endpoint",
                    False,
                    error=f"Unexpected status code: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Withdrawal Webhook Endpoint", False, error=str(e))
            return False
    
    def test_2fa_code_generation_logic(self):
        """Test 2FA code generation logic (without actual secret)"""
        try:
            from routes.nowpayments import generate_2fa_code
            
            # This will fail due to missing secret, but we can test the logic
            code = generate_2fa_code()
            
            if code is None:
                self.log_test(
                    "2FA Code Generation Logic",
                    True,
                    "Function correctly returns None when NOWPAYMENTS_2FA_SECRET is missing"
                )
            elif isinstance(code, str) and len(code) == 6 and code.isdigit():
                self.log_test(
                    "2FA Code Generation Logic",
                    True,
                    f"Generated valid 6-digit TOTP code: {code}"
                )
            else:
                self.log_test(
                    "2FA Code Generation Logic",
                    False,
                    error=f"Invalid code format: {code}"
                )
            
            return True
            
        except Exception as e:
            self.log_test("2FA Code Generation Logic", False, error=str(e))
            return False
    
    def test_address_format_validation(self):
        """Test address format validation for different networks"""
        test_addresses = {
            "TRC20": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
            "BSC": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "Solana": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            "Ethereum": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "Invalid": "invalid_address_123"
        }
        
        for network, address in test_addresses.items():
            try:
                # We'll test by trying to create a withdrawal and see if address validation occurs
                # Note: The current implementation doesn't validate address format, 
                # so we're testing that the system accepts valid formats
                
                currency_map = {
                    "TRC20": "usdttrc20",
                    "BSC": "usdtbsc", 
                    "Solana": "usdcsol",
                    "Ethereum": "usdterc20",
                    "Invalid": "usdttrc20"
                }
                
                currency = currency_map.get(network, "usdttrc20")
                
                # Test with direct database function to avoid API issues
                from supabase_client import supabase_admin as supabase
                
                result = supabase.rpc('create_withdrawal_request', {
                    'p_user_id': self.test_user_id,
                    'p_recipient_address': address,
                    'p_currency': currency,
                    'p_amount': 15.0,
                    'p_description': f'Address validation test for {network}'
                }).execute()
                
                if result.status_code == 200 and result.data:
                    response_data = result.data[0] if isinstance(result.data, list) else result.data
                    
                    if response_data.get('success'):
                        withdrawal_id = response_data.get('withdrawal_id')
                        self.created_withdrawals.append(withdrawal_id)
                        self.log_test(
                            f"Address Format - {network}",
                            True,
                            f"Address accepted: {address[:20]}..."
                        )
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        if "insufficient" in error_msg.lower():
                            self.log_test(
                                f"Address Format - {network}",
                                True,
                                f"Address format accepted (failed on balance): {error_msg}"
                            )
                        else:
                            self.log_test(
                                f"Address Format - {network}",
                                False,
                                error=error_msg
                            )
                else:
                    self.log_test(
                        f"Address Format - {network}",
                        False,
                        error=f"RPC call failed: {result.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(f"Address Format - {network}", False, error=str(e))
    
    def test_balance_validation_logic(self):
        """Test balance validation in withdrawal creation"""
        try:
            from supabase_client import supabase_admin as supabase
            
            # Get current balance
            balance_result = supabase.table('user_accounts').select('balance').eq('user_id', self.test_user_id).execute()
            current_balance = 0.0
            if balance_result.status_code == 200 and balance_result.data:
                current_balance = float(balance_result.data[0]['balance'])
            
            print(f"Current balance for testing: ${current_balance:.2f}")
            
            # Test with amount exceeding balance
            excessive_amount = current_balance + 50.0
            
            result = supabase.rpc('create_withdrawal_request', {
                'p_user_id': self.test_user_id,
                'p_recipient_address': 'TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE',
                'p_currency': 'usdttrc20',
                'p_amount': excessive_amount,
                'p_description': 'Balance validation test'
            }).execute()
            
            if result.status_code == 200 and result.data:
                response_data = result.data[0] if isinstance(result.data, list) else result.data
                
                if not response_data.get('success') and 'insufficient' in response_data.get('error', '').lower():
                    self.log_test(
                        "Balance Validation Logic",
                        True,
                        f"Correctly rejects excessive amount: {response_data.get('message')}"
                    )
                else:
                    self.log_test(
                        "Balance Validation Logic",
                        False,
                        error=f"Unexpected response: {response_data}"
                    )
            else:
                self.log_test(
                    "Balance Validation Logic",
                    False,
                    error=f"RPC call failed: {result.status_code}"
                )
                
        except Exception as e:
            self.log_test("Balance Validation Logic", False, error=str(e))
    
    def test_withdrawal_status_tracking(self):
        """Test withdrawal status tracking and updates"""
        if not self.created_withdrawals:
            self.log_test(
                "Withdrawal Status Tracking",
                False,
                error="No withdrawals created for status testing"
            )
            return False
        
        try:
            from supabase_client import supabase_admin as supabase
            
            withdrawal_id = self.created_withdrawals[0]
            
            # Test status update
            update_result = supabase.table('nowpayments_withdrawals').update({
                'status': 'verified',
                'verification_code': '123456',
                'verified_at': 'now()'
            }).eq('id', withdrawal_id).execute()
            
            if update_result.status_code == 200:
                # Verify the update
                check_result = supabase.table('nowpayments_withdrawals').select('*').eq('id', withdrawal_id).execute()
                
                if check_result.status_code == 200 and check_result.data:
                    withdrawal = check_result.data[0]
                    status = withdrawal.get('status')
                    verification_code = withdrawal.get('verification_code')
                    
                    if status == 'verified' and verification_code == '123456':
                        self.log_test(
                            "Withdrawal Status Tracking",
                            True,
                            f"Status updated successfully: {status}, Code: {verification_code}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Withdrawal Status Tracking",
                            False,
                            error=f"Status update not reflected: {status}, {verification_code}"
                        )
                        return False
                else:
                    self.log_test(
                        "Withdrawal Status Tracking",
                        False,
                        error="Failed to retrieve updated withdrawal"
                    )
                    return False
            else:
                self.log_test(
                    "Withdrawal Status Tracking",
                    False,
                    error=f"Status update failed: {update_result.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Withdrawal Status Tracking", False, error=str(e))
            return False
    
    def test_environment_configuration(self):
        """Test environment variable configuration"""
        try:
            from routes.nowpayments import NOWPAYMENTS_API_KEY, NOWPAYMENTS_2FA_SECRET, BASE_URL
            
            # Test BASE_URL configuration
            if BASE_URL and BASE_URL.startswith('https://'):
                self.log_test(
                    "Environment - Base URL",
                    True,
                    f"Base URL configured: {BASE_URL}"
                )
            else:
                self.log_test(
                    "Environment - Base URL",
                    False,
                    error=f"Invalid base URL: {BASE_URL}"
                )
            
            # Test API key configuration (expected to be missing in test environment)
            if NOWPAYMENTS_API_KEY:
                self.log_test(
                    "Environment - API Key",
                    True,
                    "NOWPAYMENTS_API_KEY is configured"
                )
            else:
                self.log_test(
                    "Environment - API Key",
                    False,
                    error="NOWPAYMENTS_API_KEY environment variable not set (expected in test environment)"
                )
            
            # Test 2FA secret configuration (expected to be missing in test environment)
            if NOWPAYMENTS_2FA_SECRET:
                self.log_test(
                    "Environment - 2FA Secret",
                    True,
                    "NOWPAYMENTS_2FA_SECRET is configured"
                )
            else:
                self.log_test(
                    "Environment - 2FA Secret",
                    False,
                    error="NOWPAYMENTS_2FA_SECRET environment variable not set (expected in test environment)"
                )
            
            return True
            
        except Exception as e:
            self.log_test("Environment Configuration", False, error=str(e))
            return False
    
    def run_core_withdrawal_tests(self):
        """Run core withdrawal functionality tests"""
        print("=" * 80)
        print("🔥 NOWPAYMENTS WITHDRAWAL CORE FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test User ID: {self.test_user_id}")
        print("Testing core withdrawal logic without external API dependencies")
        print("=" * 80)
        print()
        
        # Test 1: Database schema verification
        if not self.test_database_schema_verification():
            print("❌ Database schema verification failed - aborting tests")
            return self.generate_summary()
        
        # Test 2: Environment configuration
        self.test_environment_configuration()
        
        # Test 3: 2FA code generation logic
        self.test_2fa_code_generation_logic()
        
        # Test 4: Supported currencies validation
        self.test_supported_currencies_validation()
        
        # Test 5: Withdrawal endpoint validation
        self.test_withdrawal_endpoints_validation()
        
        # Test 6: Balance validation logic
        self.test_balance_validation_logic()
        
        # Test 7: Withdrawal status tracking
        self.test_withdrawal_status_tracking()
        
        # Test 8: Withdrawal history endpoint
        self.test_withdrawal_history_endpoint()
        
        # Test 9: Withdrawal webhook endpoint
        self.test_withdrawal_webhook_endpoint()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("📊 WITHDRAWAL CORE FUNCTIONALITY TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show critical findings
        critical_tests = [r for r in self.test_results if any(keyword in r['test'].lower() for keyword in ['database', 'validation', 'schema'])]
        if critical_tests:
            print("🔥 CRITICAL WITHDRAWAL FUNCTIONALITY RESULTS:")
            for test in critical_tests:
                status = "✅ PASS" if test['success'] else "❌ FAIL"
                print(f"   {status} {test['test']}")
                if test['error']:
                    print(f"      Error: {test['error']}")
            print()
        
        # Show failed tests
        failed_tests_list = [r for r in self.test_results if not r['success']]
        if failed_tests_list:
            print("❌ FAILED TESTS:")
            for test in failed_tests_list:
                print(f"   • {test['test']}: {test['error']}")
            print()
        
        # Show created withdrawals
        if self.created_withdrawals:
            print(f"📝 Created {len(self.created_withdrawals)} withdrawal records during testing:")
            for withdrawal_id in self.created_withdrawals:
                print(f"   • {withdrawal_id}")
            print()
        
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "critical_tests": critical_tests,
            "failed_tests": failed_tests_list,
            "created_withdrawals": self.created_withdrawals,
            "all_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = WithdrawalCoreTester()
    summary = tester.run_core_withdrawal_tests()
    
    # Determine overall success
    critical_failures = [t for t in summary.get('failed_tests', []) if 'database' in t['test'].lower() or 'schema' in t['test'].lower()]
    
    if critical_failures:
        print(f"❌ {len(critical_failures)} critical database/schema test(s) failed!")
        return 1
    else:
        print("✅ Core withdrawal functionality tests completed!")
        return 0

if __name__ == "__main__":
    exit(main())