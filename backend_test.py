#!/usr/bin/env python3
"""
Comprehensive NowPayments Integration Backend Testing
Tests all NowPayments functionality including API connectivity, invoice creation, 
database integration, and webhook processing.
"""

import asyncio
import httpx
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Test configuration
BACKEND_URL = "https://crypto-payment-fix-2.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super Admin
NOWPAYMENTS_API_KEY = "DHGG9K5-VAQ4QFP-NDHHDQ7-M4ZQCHM"

class NowPaymentsBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_user_id = TEST_USER_ID
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()

    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple:
        """Make HTTP request to backend"""
        url = f"{self.backend_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params or {})
                elif method.upper() == "POST":
                    response = await client.post(url, json=data or {})
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data or {})
                elif method.upper() == "DELETE":
                    response = await client.delete(url)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return response.status_code, response_data
                
            except Exception as e:
                return 0, {"error": str(e)}

    async def test_nowpayments_health(self):
        """Test NowPayments API connectivity and health check"""
        status_code, response = await self.make_request("GET", "/nowpayments/health")
        
        if status_code == 200 and response.get("status") == "healthy":
            self.log_test(
                "NowPayments Health Check",
                True,
                f"API connected: {response.get('api_connected')}, Supported currencies: {response.get('supported_currencies')}"
            )
            return True
        else:
            self.log_test(
                "NowPayments Health Check",
                False,
                f"Status: {status_code}",
                response
            )
            return False

    async def test_supported_currencies(self):
        """Test supported currencies endpoint"""
        status_code, response = await self.make_request("GET", "/nowpayments/currencies")
        
        if status_code == 200 and response.get("success"):
            currencies = response.get("currencies", {})
            total_networks = response.get("total_networks", 0)
            
            # Check for required currencies
            usdt_networks = len(currencies.get("USDT", {}).get("networks", []))
            usdc_networks = len(currencies.get("USDC", {}).get("networks", []))
            
            self.log_test(
                "Supported Currencies",
                True,
                f"USDT networks: {usdt_networks}, USDC networks: {usdc_networks}, Total: {total_networks}"
            )
            return currencies
        else:
            self.log_test(
                "Supported Currencies",
                False,
                f"Status: {status_code}",
                response
            )
            return None

    async def test_price_estimation(self):
        """Test price estimation for various currency pairs"""
        test_cases = [
            {"amount": 10, "currency_to": "usdttrc20", "name": "USDT TRC20"},
            {"amount": 25, "currency_to": "usdtbsc", "name": "USDT BSC"},
            {"amount": 100, "currency_to": "usdcerc20", "name": "USDC ERC20"}
        ]
        
        all_passed = True
        for case in test_cases:
            params = {
                "amount": case["amount"],
                "currency_from": "usd",
                "currency_to": case["currency_to"]
            }
            
            status_code, response = await self.make_request("GET", "/nowpayments/estimate", params=params)
            
            if status_code == 200 and response.get("success"):
                estimate = response.get("estimate", {})
                estimated_amount = estimate.get("estimated_amount", 0)
                
                self.log_test(
                    f"Price Estimation - {case['name']}",
                    True,
                    f"${case['amount']} USD = {estimated_amount} {case['currency_to'].upper()}"
                )
            else:
                self.log_test(
                    f"Price Estimation - {case['name']}",
                    False,
                    f"Status: {status_code}",
                    response
                )
                all_passed = False
        
        return all_passed

    async def test_invoice_creation(self):
        """Test invoice creation with different amounts and currencies"""
        test_cases = [
            {"amount": 10.0, "pay_currency": "usdttrc20", "description": "Test $10 USDT TRC20"},
            {"amount": 25.0, "pay_currency": "usdtbsc", "description": "Test $25 USDT BSC"},
            {"amount": 100.0, "pay_currency": "usdcerc20", "description": "Test $100 USDC ERC20"}
        ]
        
        created_invoices = []
        all_passed = True
        
        for case in test_cases:
            invoice_data = {
                "amount": case["amount"],
                "currency": "usd",
                "pay_currency": case["pay_currency"],
                "description": case["description"],
                "user_email": "test@f01i.ai"
            }
            
            # Add user_id as query parameter
            endpoint = f"/nowpayments/invoice?user_id={self.test_user_id}"
            status_code, response = await self.make_request("POST", endpoint, invoice_data)
            
            if status_code == 200 and response.get("success"):
                invoice_id = response.get("invoice_id")
                invoice_url = response.get("invoice_url")
                order_id = response.get("order_id")
                
                created_invoices.append({
                    "invoice_id": invoice_id,
                    "order_id": order_id,
                    "amount": case["amount"],
                    "currency": case["pay_currency"]
                })
                
                self.log_test(
                    f"Invoice Creation - {case['description']}",
                    True,
                    f"Invoice ID: {invoice_id}, Order ID: {order_id}, URL: {invoice_url[:50]}..."
                )
            else:
                self.log_test(
                    f"Invoice Creation - {case['description']}",
                    False,
                    f"Status: {status_code}",
                    response
                )
                all_passed = False
        
        return all_passed, created_invoices

    async def test_payment_status(self, created_invoices):
        """Test payment status retrieval for created invoices"""
        if not created_invoices:
            self.log_test(
                "Payment Status Check",
                False,
                "No invoices available to test"
            )
            return False
        
        all_passed = True
        for invoice in created_invoices:
            invoice_id = invoice["invoice_id"]
            endpoint = f"/nowpayments/payment/{invoice_id}?user_id={self.test_user_id}"
            
            status_code, response = await self.make_request("GET", endpoint)
            
            if status_code == 200 and response.get("success"):
                payment_data = response.get("payment", {})
                payment_status = payment_data.get("payment_status", "unknown")
                
                self.log_test(
                    f"Payment Status - Invoice {invoice_id[:8]}...",
                    True,
                    f"Status: {payment_status}, Amount: ${invoice['amount']}"
                )
            else:
                self.log_test(
                    f"Payment Status - Invoice {invoice_id[:8]}...",
                    False,
                    f"Status: {status_code}",
                    response
                )
                all_passed = False
        
        return all_passed

    async def test_user_payment_history(self):
        """Test user payment history retrieval"""
        endpoint = f"/nowpayments/user/{self.test_user_id}/payments"
        status_code, response = await self.make_request("GET", endpoint)
        
        if status_code == 200 and response.get("success"):
            payments = response.get("payments", [])
            count = response.get("count", 0)
            
            self.log_test(
                "User Payment History",
                True,
                f"Found {count} payment records for user {self.test_user_id[:8]}..."
            )
            return True
        else:
            self.log_test(
                "User Payment History",
                False,
                f"Status: {status_code}",
                response
            )
            return False

    async def test_webhook_endpoint(self):
        """Test webhook endpoint with mock data"""
        mock_webhook_data = {
            "payment_id": "test_payment_123",
            "payment_status": "finished",
            "order_id": f"f01i_{self.test_user_id}_{int(time.time())}",
            "actually_paid": 50.0,
            "pay_currency": "usdttrc20",
            "outcome_amount": 50.0,
            "outcome_currency": "usd"
        }
        
        # Note: This will likely fail because we don't have a real invoice
        # but we can test if the endpoint exists and handles the request
        status_code, response = await self.make_request("POST", "/nowpayments/webhook", mock_webhook_data)
        
        # Webhook should return success even if invoice not found (to avoid retries)
        if status_code == 200:
            self.log_test(
                "Webhook Endpoint",
                True,
                f"Webhook processed, Response: {response}"
            )
            return True
        else:
            self.log_test(
                "Webhook Endpoint",
                False,
                f"Status: {status_code}",
                response
            )
            return False

    async def test_subscription_plan_creation(self):
        """Test subscription plan creation"""
        plan_data = {
            "title": "Test Plan",
            "interval_days": 30,
            "amount": 19.99,
            "currency": "usd"
        }
        
        status_code, response = await self.make_request("POST", "/nowpayments/subscription/plan", plan_data)
        
        # This might fail due to authentication requirements
        if status_code in [200, 201] and response.get("success"):
            plan = response.get("plan", {})
            self.log_test(
                "Subscription Plan Creation",
                True,
                f"Plan created: {plan.get('title', 'Unknown')}"
            )
            return True
        else:
            # Expected to fail due to authentication
            self.log_test(
                "Subscription Plan Creation",
                False,
                f"Status: {status_code} (Expected - requires JWT auth)",
                response
            )
            return False

    async def test_subscription_creation(self):
        """Test subscription creation"""
        subscription_data = {
            "plan_id": "1",  # Assuming plan ID 1 exists
            "user_email": "test@f01i.ai"
        }
        
        endpoint = f"/nowpayments/subscription?user_id={self.test_user_id}"
        status_code, response = await self.make_request("POST", endpoint, subscription_data)
        
        # This might fail due to authentication or missing plan
        if status_code in [200, 201] and response.get("success"):
            subscription = response.get("subscription", {})
            self.log_test(
                "Subscription Creation",
                True,
                f"Subscription created: {subscription.get('id', 'Unknown')}"
            )
            return True
        else:
            # Expected to fail due to authentication or missing plan
            self.log_test(
                "Subscription Creation",
                False,
                f"Status: {status_code} (Expected - requires JWT auth or valid plan)",
                response
            )
            return False

    async def test_database_integration(self):
        """Test database integration by checking if tables exist"""
        # We'll test this indirectly by trying to create an invoice
        # If database tables don't exist, invoice creation will fail
        
        invoice_data = {
            "amount": 1.0,
            "currency": "usd",
            "pay_currency": "usdttrc20",
            "description": "Database integration test",
            "user_email": "test@f01i.ai"
        }
        
        endpoint = f"/nowpayments/invoice?user_id={self.test_user_id}"
        status_code, response = await self.make_request("POST", endpoint, invoice_data)
        
        if status_code == 200 and response.get("success"):
            self.log_test(
                "Database Integration",
                True,
                "Invoice created successfully - database tables exist and working"
            )
            return True
        elif "relation" in str(response).lower() and "does not exist" in str(response).lower():
            self.log_test(
                "Database Integration",
                False,
                "Database tables do not exist - schema not applied",
                response
            )
            return False
        else:
            self.log_test(
                "Database Integration",
                False,
                f"Status: {status_code} - Unknown database issue",
                response
            )
            return False

    async def test_error_handling(self):
        """Test error handling with invalid requests"""
        test_cases = [
            {
                "name": "Invalid Amount",
                "data": {"amount": -10, "currency": "usd"},
                "endpoint": f"/nowpayments/invoice?user_id={self.test_user_id}"
            },
            {
                "name": "Invalid Currency",
                "data": {"amount": 10, "currency": "invalid_currency"},
                "endpoint": f"/nowpayments/invoice?user_id={self.test_user_id}"
            },
            {
                "name": "Missing Payment ID",
                "data": {},
                "endpoint": "/nowpayments/payment/invalid_id"
            }
        ]
        
        all_passed = True
        for case in test_cases:
            if case["endpoint"].startswith("/nowpayments/payment/"):
                status_code, response = await self.make_request("GET", case["endpoint"])
            else:
                status_code, response = await self.make_request("POST", case["endpoint"], case["data"])
            
            # Error handling is good if we get 4xx status codes
            if 400 <= status_code < 500:
                self.log_test(
                    f"Error Handling - {case['name']}",
                    True,
                    f"Properly returned {status_code} error"
                )
            else:
                self.log_test(
                    f"Error Handling - {case['name']}",
                    False,
                    f"Expected 4xx error, got {status_code}",
                    response
                )
                all_passed = False
        
        return all_passed

    async def run_all_tests(self):
        """Run all NowPayments backend tests"""
        print("🚀 STARTING COMPREHENSIVE NOWPAYMENTS BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"NowPayments API Key: {NOWPAYMENTS_API_KEY}")
        print("=" * 80)
        print()

        # Test 1: Health Check
        await self.test_nowpayments_health()
        
        # Test 2: Supported Currencies
        currencies = await self.test_supported_currencies()
        
        # Test 3: Price Estimation
        await self.test_price_estimation()
        
        # Test 4: Database Integration (Critical)
        await self.test_database_integration()
        
        # Test 5: Invoice Creation (Critical)
        invoice_success, created_invoices = await self.test_invoice_creation()
        
        # Test 6: Payment Status
        if created_invoices:
            await self.test_payment_status(created_invoices)
        
        # Test 7: User Payment History
        await self.test_user_payment_history()
        
        # Test 8: Webhook Endpoint
        await self.test_webhook_endpoint()
        
        # Test 9: Subscription Plan Creation
        await self.test_subscription_plan_creation()
        
        # Test 10: Subscription Creation
        await self.test_subscription_creation()
        
        # Test 11: Error Handling
        await self.test_error_handling()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("🏁 NOWPAYMENTS BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        # Print passed tests
        passed_tests = [r for r in self.results if r["success"]]
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        # Critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        # Check for database issues
        db_test = next((r for r in self.results if "Database Integration" in r["test"]), None)
        if db_test and not db_test["success"]:
            print("   🚨 DATABASE SCHEMA NOT APPLIED - NowPayments tables do not exist")
        elif db_test and db_test["success"]:
            print("   ✅ Database schema successfully applied - all tables working")
        
        # Check for API connectivity
        health_test = next((r for r in self.results if "Health Check" in r["test"]), None)
        if health_test and health_test["success"]:
            print("   ✅ NowPayments API connectivity confirmed")
        else:
            print("   🚨 NowPayments API connectivity issues")
        
        # Check for invoice creation
        invoice_tests = [r for r in self.results if "Invoice Creation" in r["test"]]
        successful_invoices = [r for r in invoice_tests if r["success"]]
        if successful_invoices:
            print(f"   ✅ Invoice creation working - {len(successful_invoices)}/{len(invoice_tests)} currencies tested")
        else:
            print("   🚨 Invoice creation failing for all currencies")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = NowPaymentsBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())