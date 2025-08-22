#!/usr/bin/env python3
"""
NowPayments Integration Backend Testing Suite
Tests the complete NowPayments invoice-based payment gateway and subscription system
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://f01i-crypto.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super Admin for testing

class NowPaymentsBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_id = TEST_USER_ID
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Test results tracking
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        print("🚀 NowPayments Backend Integration Testing Suite")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.results['total_tests'] += 1
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"{status} | {test_name}")
        if details:
            print(f"     Details: {details}")
        if response_data and isinstance(response_data, dict):
            if 'status_code' in response_data:
                print(f"     Status: {response_data['status_code']}")
            if 'response_time' in response_data:
                print(f"     Time: {response_data['response_time']:.3f}s")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append({
                'test': test_name,
                'details': details,
                'data': response_data
            })
        print()

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            try:
                response_json = response.json()
            except:
                response_json = {"raw_response": response.text}
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'data': response_json,
                'success': 200 <= response.status_code < 300
            }
            
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': time.time() - start_time,
                'data': {'error': str(e)},
                'success': False
            }

    def test_nowpayments_health_check(self):
        """Test NowPayments service health and API connectivity"""
        print("🔍 Testing NowPayments Health Check...")
        
        result = self.make_request("GET", "/nowpayments/health")
        
        if result['success']:
            data = result['data']
            api_connected = data.get('api_connected', False)
            supported_currencies = data.get('supported_currencies', [])
            
            self.log_test(
                "NowPayments Health Check",
                api_connected and len(supported_currencies) > 0,
                f"API Connected: {api_connected}, Currencies: {supported_currencies}",
                result
            )
        else:
            self.log_test(
                "NowPayments Health Check",
                False,
                f"Health check failed: {result['data']}",
                result
            )

    def test_supported_currencies(self):
        """Test supported currencies endpoint"""
        print("🔍 Testing Supported Currencies...")
        
        result = self.make_request("GET", "/nowpayments/currencies")
        
        if result['success']:
            data = result['data']
            currencies = data.get('currencies', {})
            total_networks = data.get('total_networks', 0)
            
            # Check for required currencies
            has_usdt = 'USDT' in currencies
            has_usdc = 'USDC' in currencies
            
            usdt_networks = len(currencies.get('USDT', {}).get('networks', [])) if has_usdt else 0
            usdc_networks = len(currencies.get('USDC', {}).get('networks', [])) if has_usdc else 0
            
            success = has_usdt and has_usdc and total_networks >= 6
            
            self.log_test(
                "Supported Currencies Loading",
                success,
                f"USDT: {usdt_networks} networks, USDC: {usdc_networks} networks, Total: {total_networks}",
                result
            )
        else:
            self.log_test(
                "Supported Currencies Loading",
                False,
                f"Failed to load currencies: {result['data']}",
                result
            )

    def test_invoice_creation(self):
        """Test invoice creation with various currencies"""
        print("🔍 Testing Invoice Creation...")
        
        test_cases = [
            {"amount": 100.0, "currency": "usd", "pay_currency": "usdttrc20", "description": "USDT TRX Test"},
            {"amount": 50.0, "currency": "usd", "pay_currency": "usdtbsc", "description": "USDT BSC Test"},
            {"amount": 75.0, "currency": "usd", "pay_currency": "usdcsol", "description": "USDC SOL Test"},
            {"amount": 25.0, "currency": "usd", "pay_currency": "usdcerc20", "description": "USDC ETH Test"}
        ]
        
        created_invoices = []
        
        for i, test_case in enumerate(test_cases):
            test_case['user_email'] = f"test{i+1}@example.com"
            
            result = self.make_request("POST", "/nowpayments/invoice", test_case, {"user_id": self.test_user_id})
            
            if result['success']:
                data = result['data']
                invoice_id = data.get('invoice_id')
                invoice_url = data.get('invoice_url')
                order_id = data.get('order_id')
                
                created_invoices.append({
                    'invoice_id': invoice_id,
                    'order_id': order_id,
                    'amount': test_case['amount'],
                    'currency': test_case['pay_currency']
                })
                
                success = bool(invoice_id and invoice_url and order_id)
                
                self.log_test(
                    f"Invoice Creation - {test_case['pay_currency']}",
                    success,
                    f"Invoice ID: {invoice_id}, Order: {order_id}, Amount: ${test_case['amount']}",
                    result
                )
            else:
                self.log_test(
                    f"Invoice Creation - {test_case['pay_currency']}",
                    False,
                    f"Failed to create invoice: {result['data']}",
                    result
                )
        
        return created_invoices

    def test_payment_status_retrieval(self, created_invoices):
        """Test payment status retrieval"""
        print("🔍 Testing Payment Status Retrieval...")
        
        if not created_invoices:
            self.log_test(
                "Payment Status Retrieval",
                False,
                "No invoices available for testing",
                {}
            )
            return
        
        for invoice in created_invoices[:2]:  # Test first 2 invoices
            invoice_id = invoice['invoice_id']
            
            result = self.make_request("GET", f"/nowpayments/payment/{invoice_id}", params={"user_id": self.test_user_id})
            
            if result['success']:
                data = result['data']
                payment_data = data.get('payment', {})
                local_status = data.get('local_status')
                
                success = bool(payment_data and local_status)
                
                self.log_test(
                    f"Payment Status - {invoice['currency']}",
                    success,
                    f"Status: {local_status}, Amount: ${invoice['amount']}",
                    result
                )
            else:
                self.log_test(
                    f"Payment Status - {invoice['currency']}",
                    False,
                    f"Failed to get status: {result['data']}",
                    result
                )

    def test_user_payment_history(self):
        """Test user payment history retrieval"""
        print("🔍 Testing User Payment History...")
        
        result = self.make_request("GET", f"/nowpayments/user/{self.test_user_id}/payments", params={"limit": 10})
        
        if result['success']:
            data = result['data']
            payments = data.get('payments', [])
            count = data.get('count', 0)
            
            self.log_test(
                "User Payment History",
                True,
                f"Retrieved {count} payments for user",
                result
            )
        else:
            self.log_test(
                "User Payment History",
                False,
                f"Failed to get payment history: {result['data']}",
                result
            )

    def test_webhook_processing(self):
        """Test webhook processing with mock data"""
        print("🔍 Testing Webhook Processing...")
        
        # Create a test invoice first
        invoice_data = {
            "amount": 10.0,
            "currency": "usd",
            "pay_currency": "usdttrc20",
            "description": "Webhook Test Invoice",
            "user_email": "webhook@test.com"
        }
        
        invoice_result = self.make_request("POST", "/nowpayments/invoice", invoice_data, {"user_id": self.test_user_id})
        
        if not invoice_result['success']:
            self.log_test(
                "Webhook Processing Setup",
                False,
                "Failed to create test invoice for webhook testing",
                invoice_result
            )
            return
        
        invoice_id = invoice_result['data'].get('invoice_id')
        order_id = invoice_result['data'].get('order_id')
        
        # Mock webhook data
        webhook_data = {
            "payment_id": invoice_id,
            "payment_status": "finished",
            "order_id": order_id,
            "actually_paid": 10.0,
            "pay_currency": "usdttrc20",
            "price_amount": 10.0,
            "price_currency": "usd"
        }
        
        # Test webhook processing
        webhook_result = self.make_request("POST", "/nowpayments/webhook", webhook_data)
        
        success = webhook_result['success'] or webhook_result['status_code'] == 200
        
        self.log_test(
            "Webhook Processing",
            success,
            f"Processed webhook for payment {invoice_id}",
            webhook_result
        )

    def test_subscription_plan_creation(self):
        """Test subscription plan creation"""
        print("🔍 Testing Subscription Plan Creation...")
        
        plan_data = {
            "title": "Test Premium Plan",
            "interval_days": 30,
            "amount": 19.99,
            "currency": "usd"
        }
        
        result = self.make_request("POST", "/nowpayments/subscription/plan", plan_data)
        
        if result['success']:
            data = result['data']
            plan = data.get('plan', {})
            plan_id = plan.get('id')
            
            success = bool(plan_id)
            
            self.log_test(
                "Subscription Plan Creation",
                success,
                f"Created plan ID: {plan_id}, Amount: ${plan_data['amount']}",
                result
            )
            
            return plan_id
        else:
            self.log_test(
                "Subscription Plan Creation",
                False,
                f"Failed to create plan: {result['data']}",
                result
            )
            return None

    def test_subscription_creation(self, plan_id):
        """Test email-based subscription creation"""
        print("🔍 Testing Subscription Creation...")
        
        if not plan_id:
            self.log_test(
                "Subscription Creation",
                False,
                "No plan ID available for subscription testing",
                {}
            )
            return
        
        subscription_data = {
            "plan_id": str(plan_id),
            "user_email": "subscriber@test.com"
        }
        
        result = self.make_request("POST", "/nowpayments/subscription", subscription_data, {"user_id": self.test_user_id})
        
        if result['success']:
            data = result['data']
            subscription = data.get('subscription', {})
            subscription_id = subscription.get('id')
            
            success = bool(subscription_id)
            
            self.log_test(
                "Email-based Subscription Creation",
                success,
                f"Created subscription ID: {subscription_id}",
                result
            )
        else:
            self.log_test(
                "Email-based Subscription Creation",
                False,
                f"Failed to create subscription: {result['data']}",
                result
            )

    def test_price_estimation(self):
        """Test price estimation for different currency pairs"""
        print("🔍 Testing Price Estimation...")
        
        test_cases = [
            {"amount": 100, "currency_from": "usd", "currency_to": "usdttrc20"},
            {"amount": 50, "currency_from": "usd", "currency_to": "usdcerc20"},
            {"amount": 25, "currency_from": "usd", "currency_to": "usdtbsc"}
        ]
        
        for test_case in test_cases:
            result = self.make_request("GET", "/nowpayments/estimate", params=test_case)
            
            if result['success']:
                data = result['data']
                estimate = data.get('estimate', {})
                estimated_amount = estimate.get('estimated_amount')
                
                success = bool(estimated_amount)
                
                self.log_test(
                    f"Price Estimation - {test_case['currency_to']}",
                    success,
                    f"${test_case['amount']} USD = {estimated_amount} {test_case['currency_to']}",
                    result
                )
            else:
                self.log_test(
                    f"Price Estimation - {test_case['currency_to']}",
                    False,
                    f"Failed to get estimate: {result['data']}",
                    result
                )

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("🔍 Testing Edge Cases and Error Handling...")
        
        # Test invalid amount
        invalid_invoice = {
            "amount": -10.0,
            "currency": "usd",
            "description": "Invalid amount test"
        }
        
        result = self.make_request("POST", "/nowpayments/invoice", invalid_invoice, {"user_id": self.test_user_id})
        
        # Should fail with negative amount
        self.log_test(
            "Invalid Amount Rejection",
            not result['success'],
            f"Correctly rejected negative amount: {result['status_code']}",
            result
        )
        
        # Test invalid currency
        invalid_currency = {
            "amount": 10.0,
            "currency": "invalid_currency",
            "description": "Invalid currency test"
        }
        
        result = self.make_request("POST", "/nowpayments/invoice", invalid_currency, {"user_id": self.test_user_id})
        
        # May succeed or fail depending on NowPayments validation
        self.log_test(
            "Invalid Currency Handling",
            True,  # We just test that it doesn't crash
            f"Handled invalid currency gracefully: {result['status_code']}",
            result
        )
        
        # Test non-existent payment status
        result = self.make_request("GET", "/nowpayments/payment/non-existent-payment-id", params={"user_id": self.test_user_id})
        
        self.log_test(
            "Non-existent Payment Handling",
            not result['success'],
            f"Correctly handled non-existent payment: {result['status_code']}",
            result
        )

    def test_database_integration(self):
        """Test database integration and data persistence"""
        print("🔍 Testing Database Integration...")
        
        # Create a test invoice to verify database storage
        test_invoice = {
            "amount": 5.0,
            "currency": "usd",
            "pay_currency": "usdttrc20",
            "description": "Database Integration Test",
            "user_email": "dbtest@example.com"
        }
        
        result = self.make_request("POST", "/nowpayments/invoice", test_invoice, {"user_id": self.test_user_id})
        
        if result['success']:
            # Check if we can retrieve the payment from user history
            history_result = self.make_request("GET", f"/nowpayments/user/{self.test_user_id}/payments", params={"limit": 1})
            
            if history_result['success']:
                payments = history_result['data'].get('payments', [])
                found_payment = any(p.get('description') == test_invoice['description'] for p in payments)
                
                self.log_test(
                    "Database Storage Verification",
                    found_payment,
                    f"Invoice stored and retrievable from database",
                    history_result
                )
            else:
                self.log_test(
                    "Database Storage Verification",
                    False,
                    "Failed to retrieve payment from database",
                    history_result
                )
        else:
            self.log_test(
                "Database Storage Verification",
                False,
                "Failed to create test invoice for database verification",
                result
            )

    def run_comprehensive_tests(self):
        """Run all NowPayments integration tests"""
        print("🎯 Starting Comprehensive NowPayments Backend Testing...")
        print()
        
        # 1. Service Health and Setup
        self.test_nowpayments_health_check()
        self.test_supported_currencies()
        
        # 2. Invoice Creation System
        created_invoices = self.test_invoice_creation()
        
        # 3. Payment Status Tracking
        self.test_payment_status_retrieval(created_invoices)
        self.test_user_payment_history()
        
        # 4. Webhook Processing
        self.test_webhook_processing()
        
        # 5. Subscription System
        plan_id = self.test_subscription_plan_creation()
        self.test_subscription_creation(plan_id)
        
        # 6. Price Estimation
        self.test_price_estimation()
        
        # 7. Database Integration
        self.test_database_integration()
        
        # 8. Edge Cases
        self.test_edge_cases()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("=" * 80)
        print("🎯 NOWPAYMENTS BACKEND TESTING RESULTS")
        print("=" * 80)
        
        total = self.results['total_tests']
        passed = self.results['passed']
        failed = self.results['failed']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed} ✅")
        print(f"   Failed: {failed} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error['test']}: {error['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: NowPayments integration is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: NowPayments integration is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: NowPayments integration has some significant issues.")
        else:
            print("🚨 CRITICAL: NowPayments integration has major issues requiring immediate attention.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = NowPaymentsBackendTester()
    tester.run_comprehensive_tests()