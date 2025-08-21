#!/usr/bin/env python3
"""
CRITICAL BYPASS ENDPOINT FIX TESTING
====================================

This test specifically verifies the critical fix for the /trading-bots/create endpoint
that was previously allowing unlimited bot creation without subscription limit checking.

CRITICAL TESTING FOCUS:
- POST /api/trading-bots/create endpoint subscription limit enforcement
- Free user limits: 1 AI bot, 2 manual bots
- Super Admin unlimited access
- Proper 403 error responses when limits exceeded
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://botfolio-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test constants
SUPER_ADMIN_UUID = "cd0e9717-f85d-4726-81e9-f260394ead58"
TEST_USER_UUID = str(uuid.uuid4())

class CriticalBypassEndpointTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, details="", expected_status=None, actual_status=None):
        """Log test result with detailed information"""
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
            "expected_status": expected_status,
            "actual_status": actual_status
        }
        self.results.append(result)
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if expected_status and actual_status:
            print(f"   Expected: {expected_status}, Got: {actual_status}")
        print()

    def test_backend_health(self):
        """Test basic backend connectivity"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            success = response.status_code == 200
            self.log_result(
                "Backend Health Check",
                success,
                f"Backend connectivity verified" if success else f"Backend unreachable",
                200,
                response.status_code
            )
            return success
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Connection error: {str(e)}")
            return False

    def create_bot_payload(self, bot_name, ai_model="grok-4", user_id=None):
        """Create standardized bot creation payload"""
        return {
            "bot_name": bot_name,
            "description": "Test bot for subscription limit checking",
            "ai_model": ai_model,
            "bot_config": {
                "strategy": "test_strategy",
                "risk_level": "medium",
                "max_position_size": 1000
            },
            "user_id": user_id or TEST_USER_UUID
        }

    def test_free_user_first_ai_bot(self):
        """Test: Free user creating 1st AI bot should work"""
        payload = self.create_bot_payload("Test AI Bot 1", "grok-4")
        
        try:
            response = requests.post(f"{API_BASE}/trading-bots/create", json=payload, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"AI bot created successfully: {data.get('message', 'No message')}"
            else:
                details = f"Failed to create AI bot: {response.text}"
                
            self.log_result(
                "Free User - 1st AI Bot Creation",
                success,
                details,
                200,
                response.status_code
            )
            return success
            
        except Exception as e:
            self.log_result("Free User - 1st AI Bot Creation", False, f"Request error: {str(e)}")
            return False

    def test_free_user_second_ai_bot_blocked(self):
        """Test: Free user creating 2nd AI bot should be BLOCKED with 403"""
        payload = self.create_bot_payload("Test AI Bot 2", "grok-4")
        
        try:
            response = requests.post(f"{API_BASE}/trading-bots/create", json=payload, timeout=15)
            success = response.status_code == 403
            
            if success:
                data = response.json()
                details = f"Correctly blocked with 403: {data.get('detail', 'No detail')}"
            else:
                details = f"SECURITY ISSUE: Should have been blocked but got {response.status_code}: {response.text}"
                
            self.log_result(
                "Free User - 2nd AI Bot BLOCKED",
                success,
                details,
                403,
                response.status_code
            )
            return success
            
        except Exception as e:
            self.log_result("Free User - 2nd AI Bot BLOCKED", False, f"Request error: {str(e)}")
            return False

    def test_free_user_first_manual_bot(self):
        """Test: Free user creating 1st manual bot should work"""
        payload = self.create_bot_payload("Test Manual Bot 1", "manual")
        
        try:
            response = requests.post(f"{API_BASE}/trading-bots/create", json=payload, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Manual bot created successfully: {data.get('message', 'No message')}"
            else:
                details = f"Failed to create manual bot: {response.text}"
                
            self.log_result(
                "Free User - 1st Manual Bot Creation",
                success,
                details,
                200,
                response.status_code
            )
            return success
            
        except Exception as e:
            self.log_result("Free User - 1st Manual Bot Creation", False, f"Request error: {str(e)}")
            return False

    def test_free_user_second_manual_bot(self):
        """Test: Free user creating 2nd manual bot should work (limit is 2)"""
        payload = self.create_bot_payload("Test Manual Bot 2", "manual")
        
        try:
            response = requests.post(f"{API_BASE}/trading-bots/create", json=payload, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"2nd manual bot created successfully: {data.get('message', 'No message')}"
            else:
                details = f"Failed to create 2nd manual bot: {response.text}"
                
            self.log_result(
                "Free User - 2nd Manual Bot Creation",
                success,
                details,
                200,
                response.status_code
            )
            return success
            
        except Exception as e:
            self.log_result("Free User - 2nd Manual Bot Creation", False, f"Request error: {str(e)}")
            return False

    def test_free_user_third_manual_bot_blocked(self):
        """Test: Free user creating 3rd manual bot should be BLOCKED with 403"""
        payload = self.create_bot_payload("Test Manual Bot 3", "manual")
        
        try:
            response = requests.post(f"{API_BASE}/trading-bots/create", json=payload, timeout=15)
            success = response.status_code == 403
            
            if success:
                data = response.json()
                details = f"Correctly blocked with 403: {data.get('detail', 'No detail')}"
            else:
                details = f"SECURITY ISSUE: Should have been blocked but got {response.status_code}: {response.text}"
                
            self.log_result(
                "Free User - 3rd Manual Bot BLOCKED",
                success,
                details,
                403,
                response.status_code
            )
            return success
            
        except Exception as e:
            self.log_result("Free User - 3rd Manual Bot BLOCKED", False, f"Request error: {str(e)}")
            return False

    def test_super_admin_unlimited_access(self):
        """Test: Super Admin should have unlimited access"""
        payload = self.create_bot_payload("Super Admin Test Bot", "grok-4", SUPER_ADMIN_UUID)
        
        try:
            response = requests.post(f"{API_BASE}/trading-bots/create", json=payload, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Super Admin bot created successfully: {data.get('message', 'No message')}"
            else:
                details = f"Super Admin bot creation failed: {response.text}"
                
            self.log_result(
                "Super Admin - Unlimited Access",
                success,
                details,
                200,
                response.status_code
            )
            return success
            
        except Exception as e:
            self.log_result("Super Admin - Unlimited Access", False, f"Request error: {str(e)}")
            return False

    def test_payload_validation(self):
        """Test: Endpoint should validate required payload fields"""
        invalid_payload = {"bot_name": "Test"}  # Missing required fields
        
        try:
            response = requests.post(f"{API_BASE}/trading-bots/create", json=invalid_payload, timeout=15)
            success = response.status_code == 400
            
            if success:
                data = response.json()
                details = f"Correctly rejected invalid payload: {data.get('detail', 'No detail')}"
            else:
                details = f"Should have rejected invalid payload but got {response.status_code}: {response.text}"
                
            self.log_result(
                "Payload Validation",
                success,
                details,
                400,
                response.status_code
            )
            return success
            
        except Exception as e:
            self.log_result("Payload Validation", False, f"Request error: {str(e)}")
            return False

    def run_critical_tests(self):
        """Run all critical bypass endpoint tests"""
        print("=" * 80)
        print("🚨 CRITICAL BYPASS ENDPOINT FIX TESTING")
        print("=" * 80)
        print(f"Testing endpoint: POST {API_BASE}/trading-bots/create")
        print(f"Test User UUID: {TEST_USER_UUID}")
        print(f"Super Admin UUID: {SUPER_ADMIN_UUID}")
        print("=" * 80)
        print()

        # Test sequence
        tests = [
            self.test_backend_health,
            self.test_payload_validation,
            self.test_free_user_first_ai_bot,
            self.test_free_user_second_ai_bot_blocked,
            self.test_free_user_first_manual_bot,
            self.test_free_user_second_manual_bot,
            self.test_free_user_third_manual_bot_blocked,
            self.test_super_admin_unlimited_access
        ]

        for test in tests:
            test()

        # Summary
        print("=" * 80)
        print("🔍 CRITICAL TEST RESULTS SUMMARY")
        print("=" * 80)
        
        critical_security_tests = [
            "Free User - 2nd AI Bot BLOCKED",
            "Free User - 3rd Manual Bot BLOCKED"
        ]
        
        security_passed = 0
        for result in self.results:
            if result["test"] in critical_security_tests and result["success"]:
                security_passed += 1
        
        print(f"Overall Success Rate: {self.passed_tests}/{self.total_tests} ({(self.passed_tests/self.total_tests)*100:.1f}%)")
        print(f"Critical Security Tests: {security_passed}/{len(critical_security_tests)} passed")
        print()
        
        if security_passed == len(critical_security_tests):
            print("🔒 SECURITY STATUS: BYPASS VULNERABILITY FIXED ✅")
        else:
            print("🚨 SECURITY STATUS: BYPASS VULNERABILITY STILL EXISTS ❌")
        
        print()
        print("Detailed Results:")
        for result in self.results:
            print(f"  {result['status']}: {result['test']}")
            if result['details']:
                print(f"     {result['details']}")
        
        return self.passed_tests, self.total_tests

def main():
    """Main test execution"""
    tester = CriticalBypassEndpointTester()
    passed, total = tester.run_critical_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - BYPASS VULNERABILITY SUCCESSFULLY FIXED!")
        exit(0)
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED - REVIEW REQUIRED")
        exit(1)

if __name__ == "__main__":
    main()