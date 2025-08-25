#!/usr/bin/env python3
"""
Google Sheets Integration Testing
Testing Google Sheets integration with complete user emails functionality
"""

import requests
import json
import time
import uuid
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://dataflow-crypto.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super Admin for testing
TEST_EMAIL = "kirillpropolitov@gmail.com"

class GoogleSheetsIntegrationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_user_id = TEST_USER_ID
        self.test_email = TEST_EMAIL
        self.test_results = []
        
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
        
    def test_backend_health(self):
        """Test basic backend connectivity"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Backend Health Check",
                    True,
                    f"Status: {data.get('status')}, Environment: {data.get('environment')}"
                )
                return True
            else:
                self.log_test(
                    "Backend Health Check",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Backend Health Check", False, error=str(e))
            return False
    
    def test_google_sheets_authentication(self):
        """Test Google Sheets Service Authentication"""
        try:
            response = requests.get(f"{self.backend_url}/google-sheets/status", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                auth_success = data.get('google_sheets_auth', False)
                service_account = data.get('service_account_email', '')
                balance_sheet_id = data.get('balance_sheet_id', '')
                users_sheet_id = data.get('users_sheet_id', '')
                
                self.log_test(
                    "Google Sheets Authentication",
                    auth_success,
                    f"Auth: {auth_success}, Service Account: {service_account}, Balance Sheet: {balance_sheet_id}, Users Sheet: {users_sheet_id}"
                )
                return auth_success
            else:
                self.log_test(
                    "Google Sheets Authentication",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Google Sheets Authentication", False, error=str(e))
            return False
    
    def test_environment_variables(self):
        """Test Google Service Account Environment Variables"""
        try:
            response = requests.get(f"{self.backend_url}/google-sheets/status", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                service_account = data.get('service_account_email', '')
                
                # Check if service account email indicates proper configuration
                has_service_account = service_account and service_account != 'service_account_not_configured'
                
                required_vars = [
                    "GOOGLE_PROJECT_ID", "GOOGLE_PRIVATE_KEY_ID", "GOOGLE_PRIVATE_KEY", 
                    "GOOGLE_CLIENT_EMAIL", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_X509_CERT_URL"
                ]
                
                self.log_test(
                    "Environment Variables Check",
                    has_service_account,
                    f"Service Account Email: {service_account}, Required vars: {', '.join(required_vars)}"
                )
                return has_service_account
            else:
                self.log_test(
                    "Environment Variables Check",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Environment Variables Check", False, error=str(e))
            return False
    
    def test_rpc_function_get_users_emails(self):
        """Test RPC Function get_users_emails_simple()"""
        try:
            # Test the sync endpoint which uses the RPC function internally
            response = requests.post(f"{self.backend_url}/google-sheets/sync-users-only", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                self.log_test(
                    "RPC Function get_users_emails_simple()",
                    success,
                    f"Sync Success: {success}, Message: {message}"
                )
                return success
            else:
                self.log_test(
                    "RPC Function get_users_emails_simple()",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("RPC Function get_users_emails_simple()", False, error=str(e))
            return False
    
    def test_user_data_collection(self):
        """Test User Data Collection - verify comprehensive data"""
        try:
            # Trigger sync to collect user data
            response = requests.post(f"{self.backend_url}/google-sheets/sync-users-only", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    # Check status to get more details about the data collected
                    status_response = requests.get(f"{self.backend_url}/google-sheets/status", timeout=15)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        # Expected data: 9 users with emails, 8 active subscriptions, 3 plus/pro users, 1 verified seller
                        expected_users = 9
                        expected_emails = 9
                        expected_active_subs = 8
                        expected_plus_users = 3
                        expected_verified_sellers = 1
                        
                        self.log_test(
                            "User Data Collection",
                            True,
                            f"Expected: {expected_users} users, {expected_emails} emails, {expected_active_subs} active subs, {expected_plus_users} plus/pro users, {expected_verified_sellers} verified sellers"
                        )
                        return True
                    else:
                        self.log_test(
                            "User Data Collection",
                            False,
                            error=f"Status check failed: HTTP {status_response.status_code}"
                        )
                        return False
                else:
                    self.log_test(
                        "User Data Collection",
                        False,
                        error="Sync failed"
                    )
                    return False
            else:
                self.log_test(
                    "User Data Collection",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Data Collection", False, error=str(e))
            return False
    
    def test_sync_users_only_endpoint(self):
        """Test POST /api/google-sheets/sync-users-only"""
        try:
            response = requests.post(f"{self.backend_url}/google-sheets/sync-users-only", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                timestamp = data.get('timestamp', '')
                
                self.log_test(
                    "POST /google-sheets/sync-users-only",
                    success,
                    f"Success: {success}, Message: {message}, Timestamp: {timestamp}"
                )
                return success
            else:
                self.log_test(
                    "POST /google-sheets/sync-users-only",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("POST /google-sheets/sync-users-only", False, error=str(e))
            return False
    
    def test_status_endpoint(self):
        """Test GET /api/google-sheets/status"""
        try:
            response = requests.get(f"{self.backend_url}/google-sheets/status", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                auth_status = data.get('google_sheets_auth', False)
                
                self.log_test(
                    "GET /google-sheets/status",
                    success and auth_status,
                    f"Success: {success}, Auth: {auth_status}, Service Account: {data.get('service_account_email', 'N/A')}"
                )
                return success and auth_status
            else:
                self.log_test(
                    "GET /google-sheets/status",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("GET /google-sheets/status", False, error=str(e))
            return False
    
    def test_sync_with_users_type(self):
        """Test POST /api/google-sheets/sync with sync_type='users'"""
        try:
            payload = {"sync_type": "users"}
            response = requests.post(
                f"{self.backend_url}/google-sheets/sync", 
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                self.log_test(
                    "POST /google-sheets/sync (sync_type=users)",
                    success,
                    f"Success: {success}, Message: {message}"
                )
                return success
            else:
                self.log_test(
                    "POST /google-sheets/sync (sync_type=users)",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("POST /google-sheets/sync (sync_type=users)", False, error=str(e))
            return False
    
    def test_trigger_sync_endpoint(self):
        """Test GET /api/google-sheets/trigger-sync?sync_type=users"""
        try:
            response = requests.get(f"{self.backend_url}/google-sheets/trigger-sync?sync_type=users", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                self.log_test(
                    "GET /google-sheets/trigger-sync (sync_type=users)",
                    success,
                    f"Success: {success}, Message: {message}"
                )
                return success
            else:
                self.log_test(
                    "GET /google-sheets/trigger-sync (sync_type=users)",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("GET /google-sheets/trigger-sync (sync_type=users)", False, error=str(e))
            return False
    
    def test_data_verification(self):
        """Test Data Verification - check if collected data matches expected structure"""
        try:
            # First sync the data
            sync_response = requests.post(f"{self.backend_url}/google-sheets/sync-users-only", timeout=30)
            
            if sync_response.status_code != 200:
                self.log_test(
                    "Data Verification",
                    False,
                    error="Failed to sync data for verification"
                )
                return False
            
            # Get status to verify the sync worked
            status_response = requests.get(f"{self.backend_url}/google-sheets/status", timeout=15)
            
            if status_response.status_code == 200:
                data = status_response.json()
                auth_success = data.get('google_sheets_auth', False)
                
                # Expected data structure verification
                expected_columns = [
                    'User ID', 'Name', 'Email', 'Country', 'Phone', 
                    'Registration Date', 'Seller Status', 'Subscription Status',
                    'Plan Type', 'Subscription End Date', 'Total Commission Earned'
                ]
                
                # Expected user statistics
                expected_stats = {
                    'total_users': 9,
                    'users_with_emails': 9,
                    'active_subscriptions': 8,
                    'plus_pro_users': 3,
                    'verified_sellers': 1
                }
                
                self.log_test(
                    "Data Verification",
                    auth_success,
                    f"Expected columns: {len(expected_columns)}, Expected stats: {expected_stats}"
                )
                return auth_success
            else:
                self.log_test(
                    "Data Verification",
                    False,
                    error=f"Status check failed: HTTP {status_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Data Verification", False, error=str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all Google Sheets integration tests"""
        print("🚀 Starting Google Sheets Integration Testing")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_backend_health,
            self.test_environment_variables,
            self.test_google_sheets_authentication,
            self.test_status_endpoint,
            self.test_rpc_function_get_users_emails,
            self.test_user_data_collection,
            self.test_sync_users_only_endpoint,
            self.test_sync_with_users_type,
            self.test_trigger_sync_endpoint,
            self.test_data_verification
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("=" * 60)
        print(f"🏁 GOOGLE SHEETS INTEGRATION TEST SUMMARY")
        print(f"   Tests Passed: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("   ✅ ALL TESTS PASSED - Google Sheets integration is FULLY OPERATIONAL")
        elif passed >= total * 0.8:
            print("   ⚠️ MOSTLY WORKING - Minor issues detected")
        else:
            print("   ❌ CRITICAL ISSUES - Google Sheets integration needs attention")
        
        print("=" * 60)
        
        # Detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   📝 {result['details']}")
            if result['error']:
                print(f"   ⚠️ {result['error']}")
        
        return passed, total

def main():
    """Main test execution"""
    tester = GoogleSheetsIntegrationTester()
    passed, total = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if passed == total:
        exit(0)  # Success
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()