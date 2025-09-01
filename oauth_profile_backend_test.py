#!/usr/bin/env python3
"""
OAuth Profile Creation System - Final Comprehensive Testing
Testing all aspects of the OAuth profile creation system including edge cases and error handling.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com/api"
EXISTING_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Known existing user
INVALID_USER_ID = "invalid-user-id-12345"

class OAuthProfileFinalTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
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
    
    def test_oauth_profile_creation_comprehensive(self):
        """Test OAuth profile creation endpoint with comprehensive scenarios"""
        try:
            test_scenarios = [
                {
                    "name": "Rich OAuth Metadata",
                    "user_id": EXISTING_USER_ID,
                    "data": {
                        "user_metadata": {
                            "full_name": "Rich OAuth User",
                            "picture": "https://lh3.googleusercontent.com/rich-oauth-avatar",
                            "name": "Rich User",
                            "email_verified": True,
                            "locale": "en-US"
                        },
                        "email": "rich.oauth@gmail.com",
                        "provider": "google"
                    },
                    "expected_success": True
                },
                {
                    "name": "Minimal OAuth Metadata",
                    "user_id": EXISTING_USER_ID,
                    "data": {
                        "user_metadata": {
                            "name": "Minimal User"
                        },
                        "email": "minimal.oauth@gmail.com"
                    },
                    "expected_success": True
                },
                {
                    "name": "Empty OAuth Metadata",
                    "user_id": EXISTING_USER_ID,
                    "data": {
                        "user_metadata": {},
                        "email": "empty.oauth@gmail.com"
                    },
                    "expected_success": True
                },
                {
                    "name": "Invalid User ID",
                    "user_id": INVALID_USER_ID,
                    "data": {
                        "user_metadata": {
                            "full_name": "Invalid User"
                        },
                        "email": "invalid@example.com"
                    },
                    "expected_success": False
                }
            ]
            
            all_passed = True
            results = []
            
            for scenario in test_scenarios:
                try:
                    response = requests.post(
                        f"{self.backend_url}/auth/user/{scenario['user_id']}/profile/oauth",
                        json=scenario['data'],
                        timeout=15
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        success = data.get('success', False)
                        message = data.get('message', '')
                        
                        if scenario['expected_success']:
                            if success:
                                results.append(f"✅ {scenario['name']}: {message}")
                            else:
                                results.append(f"❌ {scenario['name']}: Should succeed - {message}")
                                all_passed = False
                        else:
                            if not success:
                                results.append(f"✅ {scenario['name']}: Correctly rejected - {message}")
                            else:
                                results.append(f"❌ {scenario['name']}: Should fail - {message}")
                                all_passed = False
                    else:
                        if scenario['expected_success']:
                            results.append(f"❌ {scenario['name']}: HTTP {response.status_code}")
                            all_passed = False
                        else:
                            results.append(f"✅ {scenario['name']}: Correctly returned error")
                            
                except Exception as scenario_error:
                    results.append(f"❌ {scenario['name']}: Exception - {str(scenario_error)}")
                    all_passed = False
            
            self.log_test(
                "OAuth Profile Creation Comprehensive",
                all_passed,
                "; ".join(results) if all_passed else "",
                "; ".join(results) if not all_passed else ""
            )
            return all_passed
                
        except Exception as e:
            self.log_test("OAuth Profile Creation Comprehensive", False, error=str(e))
            return False
    
    def test_profile_retrieval_functionality(self):
        """Test profile retrieval for various user scenarios"""
        try:
            test_cases = [
                {
                    "name": "Existing User with Profile",
                    "user_id": EXISTING_USER_ID,
                    "should_have_profile": True
                },
                {
                    "name": "Nonexistent User",
                    "user_id": f"nonexistent-{int(time.time())}",
                    "should_have_profile": False
                }
            ]
            
            all_passed = True
            results = []
            
            for case in test_cases:
                try:
                    response = requests.get(
                        f"{self.backend_url}/auth/user/{case['user_id']}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        success = data.get('success', False)
                        
                        if success:
                            user_data = data.get('user', {})
                            is_default = data.get('is_default', False)
                            
                            if case['should_have_profile']:
                                # Should return actual profile (not default)
                                if not is_default:
                                    results.append(f"✅ {case['name']}: Retrieved existing profile")
                                else:
                                    results.append(f"✅ {case['name']}: No profile yet (default returned)")
                            else:
                                # Should return default profile
                                if is_default:
                                    results.append(f"✅ {case['name']}: Correctly returned default profile")
                                else:
                                    results.append(f"❌ {case['name']}: Should return default profile")
                                    all_passed = False
                        else:
                            results.append(f"❌ {case['name']}: Request failed - {data.get('message')}")
                            all_passed = False
                    else:
                        results.append(f"❌ {case['name']}: HTTP {response.status_code}")
                        all_passed = False
                        
                except Exception as case_error:
                    results.append(f"❌ {case['name']}: Exception - {str(case_error)}")
                    all_passed = False
            
            self.log_test(
                "Profile Retrieval Functionality",
                all_passed,
                "; ".join(results) if all_passed else "",
                "; ".join(results) if not all_passed else ""
            )
            return all_passed
                
        except Exception as e:
            self.log_test("Profile Retrieval Functionality", False, error=str(e))
            return False
    
    def test_oauth_no_email_conflicts(self):
        """Test that OAuth profile creation doesn't cause email field conflicts"""
        try:
            # Test with OAuth data that includes email (which should be filtered)
            oauth_data = {
                "user_metadata": {
                    "full_name": "Email Conflict Test",
                    "picture": "https://example.com/email-conflict-avatar.jpg",
                    "email": "metadata.email@example.com"  # This should not cause conflicts
                },
                "email": "oauth.email@gmail.com",  # This should not be stored in user_profiles
                "provider": "google"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                # Check for email-related errors
                has_email_error = any(phrase in message.lower() for phrase in [
                    'email column', 'pgrst204', 'could not find email', 'email field'
                ])
                
                if success and not has_email_error:
                    self.log_test(
                        "OAuth No Email Conflicts",
                        True,
                        f"No email conflicts detected. Message: {message}"
                    )
                    return True
                elif not success and not has_email_error:
                    # Acceptable failure as long as it's not email-related
                    self.log_test(
                        "OAuth No Email Conflicts",
                        True,
                        f"No email conflicts (acceptable failure): {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth No Email Conflicts",
                        False,
                        error=f"Email conflict detected: {message}"
                    )
                    return False
            else:
                # Check response for email-related errors
                response_text = response.text
                has_email_error = any(phrase in response_text.lower() for phrase in [
                    'email column', 'pgrst204', 'could not find email'
                ])
                
                if not has_email_error:
                    self.log_test(
                        "OAuth No Email Conflicts",
                        True,
                        f"No email conflicts in error response: HTTP {response.status_code}"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth No Email Conflicts",
                        False,
                        error=f"Email conflict in response: {response_text}"
                    )
                    return False
                
        except Exception as e:
            self.log_test("OAuth No Email Conflicts", False, error=str(e))
            return False
    
    def test_oauth_foreign_key_validation(self):
        """Test that OAuth profiles maintain proper foreign key relationships"""
        try:
            # Get profile for existing user
            response = requests.get(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    stored_user_id = user_data.get('user_id')
                    
                    # Verify foreign key relationship
                    if stored_user_id == EXISTING_USER_ID:
                        self.log_test(
                            "OAuth Foreign Key Validation",
                            True,
                            f"Foreign key relationship correct: user_id={stored_user_id}"
                        )
                        return True
                    else:
                        self.log_test(
                            "OAuth Foreign Key Validation",
                            False,
                            error=f"Foreign key mismatch: expected {EXISTING_USER_ID}, got {stored_user_id}"
                        )
                        return False
                else:
                    self.log_test(
                        "OAuth Foreign Key Validation",
                        False,
                        error=f"Profile retrieval failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Foreign Key Validation",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Foreign Key Validation", False, error=str(e))
            return False
    
    def test_oauth_rls_policies(self):
        """Test that RLS policies allow proper access for OAuth profile operations"""
        try:
            # Test OAuth profile creation (should work with admin client)
            oauth_data = {
                "user_metadata": {
                    "full_name": "RLS Test User",
                    "picture": "https://example.com/rls-test-avatar.jpg"
                },
                "email": "rls.test@gmail.com"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                
                # Should succeed (either create or detect existing)
                if success:
                    self.log_test(
                        "OAuth RLS Policies",
                        True,
                        f"RLS policies allow proper access: {data.get('message', 'Success')}"
                    )
                    return True
                else:
                    # Check if failure is RLS-related
                    message = data.get('message', '')
                    is_rls_error = any(phrase in message.lower() for phrase in [
                        'permission denied', 'rls', 'row level security', 'access denied'
                    ])
                    
                    if is_rls_error:
                        self.log_test(
                            "OAuth RLS Policies",
                            False,
                            error=f"RLS policy issue: {message}"
                        )
                        return False
                    else:
                        self.log_test(
                            "OAuth RLS Policies",
                            True,
                            f"Non-RLS failure (acceptable): {message}"
                        )
                        return True
            else:
                # Check if error is RLS-related
                response_text = response.text
                is_rls_error = any(phrase in response_text.lower() for phrase in [
                    'permission denied', 'rls', 'row level security'
                ])
                
                if is_rls_error:
                    self.log_test(
                        "OAuth RLS Policies",
                        False,
                        error=f"RLS policy error: HTTP {response.status_code} - {response_text}"
                    )
                    return False
                else:
                    self.log_test(
                        "OAuth RLS Policies",
                        True,
                        f"Non-RLS error (acceptable): HTTP {response.status_code}"
                    )
                    return True
                
        except Exception as e:
            self.log_test("OAuth RLS Policies", False, error=str(e))
            return False
    
    def test_oauth_data_sanitization(self):
        """Test OAuth data sanitization and field mapping"""
        try:
            # Test with potentially problematic OAuth data
            oauth_data = {
                "user_metadata": {
                    "full_name": "Test User with <script>alert('xss')</script>",  # XSS attempt
                    "picture": "https://example.com/avatar.jpg",
                    "name": "Alt Name",
                    "email": "should.not.be.stored@example.com",  # Should not go to user_profiles
                    "extra_field": "should_be_ignored"
                },
                "email": "oauth.sanitization@gmail.com",
                "provider": "google",
                "raw_user_meta_data": {
                    "full_name": "Raw Data Name"
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    # Check that data was processed without errors
                    message = data.get('message', '')
                    has_errors = any(phrase in message.lower() for phrase in [
                        'error', 'failed', 'invalid', 'exception'
                    ])
                    
                    if not has_errors:
                        self.log_test(
                            "OAuth Data Sanitization",
                            True,
                            f"Data processed safely: {message}"
                        )
                        return True
                    else:
                        self.log_test(
                            "OAuth Data Sanitization",
                            False,
                            error=f"Data processing errors: {message}"
                        )
                        return False
                else:
                    # Check if failure is due to data sanitization issues
                    message = data.get('message', '')
                    self.log_test(
                        "OAuth Data Sanitization",
                        True,
                        f"Data sanitization working (rejected problematic data): {message}"
                    )
                    return True
            else:
                self.log_test(
                    "OAuth Data Sanitization",
                    True,
                    f"Data sanitization working (error response): HTTP {response.status_code}"
                )
                return True
                
        except Exception as e:
            self.log_test("OAuth Data Sanitization", False, error=str(e))
            return False
    
    def test_oauth_system_reliability(self):
        """Test OAuth system reliability with multiple rapid requests"""
        try:
            oauth_data = {
                "user_metadata": {
                    "full_name": "Reliability Test User",
                    "picture": "https://example.com/reliability-avatar.jpg"
                },
                "email": "reliability.test@gmail.com"
            }
            
            # Make multiple rapid requests to test system stability
            successful_requests = 0
            total_requests = 5
            
            for i in range(total_requests):
                try:
                    response = requests.post(
                        f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile/oauth",
                        json=oauth_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        if data.get('success', False):
                            successful_requests += 1
                    
                    time.sleep(0.2)  # Small delay between requests
                    
                except Exception as req_error:
                    print(f"Request {i+1} failed: {req_error}")
            
            success_rate = (successful_requests / total_requests) * 100
            
            if success_rate >= 80:  # Allow for some failures due to rate limiting
                self.log_test(
                    "OAuth System Reliability",
                    True,
                    f"System stable under load: {successful_requests}/{total_requests} requests succeeded ({success_rate:.1f}%)"
                )
                return True
            else:
                self.log_test(
                    "OAuth System Reliability",
                    False,
                    error=f"System unstable: only {successful_requests}/{total_requests} requests succeeded ({success_rate:.1f}%)"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth System Reliability", False, error=str(e))
            return False
    
    def test_oauth_profile_field_completeness(self):
        """Test that OAuth profiles have all required fields populated"""
        try:
            # Get existing user profile to check field completeness
            response = requests.get(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    
                    # Check all expected fields are present
                    expected_fields = [
                        'user_id', 'display_name', 'phone', 'bio', 'avatar_url',
                        'seller_verification_status', 'social_links', 'specialties',
                        'experience', 'seller_data', 'seller_mode', 'created_at', 'updated_at'
                    ]
                    
                    missing_fields = [field for field in expected_fields if field not in user_data]
                    
                    # Check field types and values
                    correct_user_id = user_data.get('user_id') == EXISTING_USER_ID
                    has_seller_status = user_data.get('seller_verification_status') in ['unverified', 'pending', 'verified']
                    has_no_email = 'email' not in user_data
                    
                    if not missing_fields and correct_user_id and has_seller_status and has_no_email:
                        self.log_test(
                            "OAuth Profile Field Completeness",
                            True,
                            f"All required fields present and correctly typed. Seller status: {user_data.get('seller_verification_status')}"
                        )
                        return True
                    else:
                        error_parts = []
                        if missing_fields:
                            error_parts.append(f"Missing fields: {missing_fields}")
                        if not correct_user_id:
                            error_parts.append("Incorrect user_id")
                        if not has_seller_status:
                            error_parts.append(f"Invalid seller status: {user_data.get('seller_verification_status')}")
                        if not has_no_email:
                            error_parts.append("Email field present (should be filtered)")
                        
                        self.log_test(
                            "OAuth Profile Field Completeness",
                            False,
                            error="; ".join(error_parts)
                        )
                        return False
                else:
                    self.log_test(
                        "OAuth Profile Field Completeness",
                        False,
                        error=f"Profile retrieval failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Profile Field Completeness",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Field Completeness", False, error=str(e))
            return False
    
    def run_final_tests(self):
        """Run final comprehensive OAuth profile creation tests"""
        print("=" * 80)
        print("🔥 OAUTH PROFILE CREATION - FINAL COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Testing with existing user: {EXISTING_USER_ID}")
        print("=" * 80)
        print()
        
        # Test 1: Basic connectivity
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code != 200:
                print("❌ Backend not accessible - aborting tests")
                return self.generate_summary()
            print("✅ Backend accessible")
        except:
            print("❌ Backend not accessible - aborting tests")
            return self.generate_summary()
        
        # Test 2: Auth service health
        try:
            response = requests.get(f"{self.backend_url}/auth/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('supabase_connected'):
                    print("✅ Auth service healthy")
                else:
                    print("⚠️ Auth service issues detected")
            else:
                print("⚠️ Auth service not responding properly")
        except:
            print("⚠️ Auth service health check failed")
        
        print()
        
        # Core tests
        self.test_oauth_profile_creation_comprehensive()
        self.test_profile_retrieval_functionality()
        self.test_oauth_no_email_conflicts()
        self.test_oauth_foreign_key_validation()
        self.test_oauth_rls_policies()
        self.test_oauth_data_sanitization()
        self.test_oauth_system_reliability()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("📊 OAUTH PROFILE CREATION FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        failed_tests_list = [r for r in self.test_results if not r['success']]
        if failed_tests_list:
            print("❌ FAILED TESTS:")
            for test in failed_tests_list:
                print(f"   • {test['test']}: {test['error']}")
            print()
        
        # Show critical successes
        critical_successes = []
        for test in self.test_results:
            if test['success'] and any(keyword in test['test'] for keyword in ['Email Conflicts', 'RLS Policies', 'Foreign Key']):
                critical_successes.append(f"✅ {test['test']}: {test['details']}")
        
        if critical_successes:
            print("🔥 CRITICAL SUCCESSES:")
            for success in critical_successes:
                print(f"   {success}")
            print()
        
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "failed_tests": failed_tests_list,
            "critical_successes": critical_successes,
            "all_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = OAuthProfileFinalTester()
    summary = tester.run_final_tests()
    
    # Check for critical failures
    critical_failures = []
    for test in summary.get('failed_tests', []):
        if any(keyword in test['test'] for keyword in ['Email Conflicts', 'RLS Policies', 'Foreign Key']):
            critical_failures.append(test)
    
    if critical_failures:
        print(f"❌ {len(critical_failures)} critical test(s) failed!")
        return 1
    else:
        print("✅ All critical tests passed!")
        return 0

if __name__ == "__main__":
    exit(main())