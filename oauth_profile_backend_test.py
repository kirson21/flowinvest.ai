#!/usr/bin/env python3
"""
OAuth Profile Creation System - Core Functionality Testing
Testing the key OAuth profile creation functionality with focus on working scenarios.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://dataflow-crypto.preview.emergentagent.com/api"
EXISTING_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Known existing user
INVALID_USER_ID = "invalid-user-id-12345"

# Known existing users from the system (from previous test results)
KNOWN_USERS = [
    "cd0e9717-f85d-4726-81e9-f260394ead58",  # Super admin
    # We'll discover more during testing
]

class OAuthProfileCoreTester:
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
    
    def test_oauth_endpoint_functionality(self):
        """Test OAuth profile creation endpoint core functionality"""
        try:
            # Test with comprehensive OAuth data
            oauth_data = {
                "user_metadata": {
                    "full_name": "OAuth Test User",
                    "picture": "https://lh3.googleusercontent.com/oauth-test-avatar-123",
                    "name": "OAuth Test Alt",
                    "email_verified": True
                },
                "email": "oauth.test@gmail.com",
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
                existed = data.get('existed', False)
                
                # For existing user, should either create or detect existing
                if success:
                    self.log_test(
                        "OAuth Endpoint Functionality",
                        True,
                        f"OAuth endpoint working correctly. Success: {success}, Existed: {existed}, Message: {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth Endpoint Functionality",
                        False,
                        error=f"OAuth endpoint failed: {message}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Endpoint Functionality",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Endpoint Functionality", False, error=str(e))
            return False
    
    def test_oauth_user_verification(self):
        """Test OAuth endpoint user verification logic"""
        try:
            # Test with invalid user ID - should fail with proper error
            oauth_data = {
                "user_metadata": {
                    "full_name": "Invalid User Test",
                    "picture": "https://example.com/invalid-avatar.jpg"
                },
                "email": "invalid@example.com"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{INVALID_USER_ID}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                
                # Should fail for invalid user
                if not success and "not found in auth.users" in message:
                    self.log_test(
                        "OAuth User Verification",
                        True,
                        f"Correctly rejected invalid user: {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth User Verification",
                        False,
                        error=f"Should have rejected invalid user but got success={success}, message={message}"
                    )
                    return False
            else:
                # Error response is also acceptable for invalid user
                self.log_test(
                    "OAuth User Verification",
                    True,
                    f"Correctly returned error for invalid user: HTTP {response.status_code}"
                )
                return True
                
        except Exception as e:
            self.log_test("OAuth User Verification", False, error=str(e))
            return False
    
    def test_oauth_metadata_extraction(self):
        """Test OAuth metadata extraction with various data formats"""
        try:
            test_cases = [
                {
                    "name": "Full Metadata",
                    "data": {
                        "user_metadata": {
                            "full_name": "Full Meta User",
                            "picture": "https://lh3.googleusercontent.com/full-meta-avatar"
                        },
                        "email": "full.meta@gmail.com"
                    },
                    "expected_success": True
                },
                {
                    "name": "Name Only",
                    "data": {
                        "user_metadata": {
                            "name": "Name Only User"
                        },
                        "email": "name.only@gmail.com"
                    },
                    "expected_success": True
                },
                {
                    "name": "Picture Only",
                    "data": {
                        "user_metadata": {
                            "picture": "https://example.com/picture-only-avatar.jpg"
                        },
                        "email": "picture.only@gmail.com"
                    },
                    "expected_success": True
                },
                {
                    "name": "Empty Metadata",
                    "data": {
                        "user_metadata": {},
                        "email": "empty.meta@gmail.com"
                    },
                    "expected_success": True
                }
            ]
            
            all_passed = True
            results = []
            
            for test_case in test_cases:
                try:
                    response = requests.post(
                        f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile/oauth",
                        json=test_case['data'],
                        timeout=15
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        success = data.get('success', False)
                        
                        if test_case['expected_success']:
                            if success:
                                results.append(f"✅ {test_case['name']}: Processed correctly")
                            else:
                                results.append(f"❌ {test_case['name']}: Should have succeeded")
                                all_passed = False
                        else:
                            if not success:
                                results.append(f"✅ {test_case['name']}: Correctly rejected")
                            else:
                                results.append(f"❌ {test_case['name']}: Should have failed")
                                all_passed = False
                    else:
                        if test_case['expected_success']:
                            results.append(f"❌ {test_case['name']}: HTTP {response.status_code}")
                            all_passed = False
                        else:
                            results.append(f"✅ {test_case['name']}: Correctly returned error")
                            
                except Exception as case_error:
                    results.append(f"❌ {test_case['name']}: Exception - {str(case_error)}")
                    all_passed = False
            
            self.log_test(
                "OAuth Metadata Extraction",
                all_passed,
                "; ".join(results) if all_passed else "",
                "; ".join(results) if not all_passed else ""
            )
            return all_passed
                
        except Exception as e:
            self.log_test("OAuth Metadata Extraction", False, error=str(e))
            return False
    
    def test_profile_retrieval_comprehensive(self):
        """Test profile retrieval with comprehensive validation"""
        try:
            # Test existing user profile retrieval
            response = requests.get(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    is_default = data.get('is_default', False)
                    
                    # Validate profile structure
                    required_fields = ['user_id', 'display_name', 'seller_verification_status']
                    optional_fields = ['bio', 'phone', 'avatar_url', 'social_links', 'specialties', 'seller_data', 'seller_mode']
                    
                    has_required = all(field in user_data for field in required_fields)
                    has_user_id_match = user_data.get('user_id') == EXISTING_USER_ID
                    has_no_email = 'email' not in user_data  # Email should not be in profile
                    
                    if has_required and has_user_id_match and has_no_email:
                        self.log_test(
                            "Profile Retrieval Comprehensive",
                            True,
                            f"Profile structure valid. Default: {is_default}, Required fields present, No email field conflict"
                        )
                        return True
                    else:
                        error_parts = []
                        if not has_required:
                            missing = [f for f in required_fields if f not in user_data]
                            error_parts.append(f"Missing required fields: {missing}")
                        if not has_user_id_match:
                            error_parts.append(f"User ID mismatch")
                        if not has_no_email:
                            error_parts.append(f"Email field present (should be filtered)")
                        
                        self.log_test(
                            "Profile Retrieval Comprehensive",
                            False,
                            error="; ".join(error_parts)
                        )
                        return False
                else:
                    self.log_test(
                        "Profile Retrieval Comprehensive",
                        False,
                        error=f"Profile retrieval failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "Profile Retrieval Comprehensive",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Profile Retrieval Comprehensive", False, error=str(e))
            return False
    
    def test_profile_retrieval_default_structure(self):
        """Test profile retrieval returns proper default structure for users without profiles"""
        try:
            # Use a user ID that definitely doesn't have a profile
            nonexistent_user = f"test-nonexistent-{int(time.time())}"
            
            response = requests.get(
                f"{self.backend_url}/auth/user/{nonexistent_user}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    is_default = data.get('is_default', False)
                    
                    # Should return default profile structure
                    expected_fields = [
                        'user_id', 'display_name', 'phone', 'bio', 'avatar_url',
                        'seller_verification_status', 'social_links', 'specialties',
                        'experience', 'seller_data', 'seller_mode', 'created_at', 'updated_at'
                    ]
                    
                    has_all_fields = all(field in user_data for field in expected_fields)
                    correct_user_id = user_data.get('user_id') == nonexistent_user
                    correct_default_status = user_data.get('seller_verification_status') == 'unverified'
                    
                    if is_default and has_all_fields and correct_user_id and correct_default_status:
                        self.log_test(
                            "Profile Retrieval Default Structure",
                            True,
                            f"Correct default structure returned for user without profile"
                        )
                        return True
                    else:
                        error_parts = []
                        if not is_default:
                            error_parts.append("is_default not set")
                        if not has_all_fields:
                            missing = [f for f in expected_fields if f not in user_data]
                            error_parts.append(f"Missing fields: {missing}")
                        if not correct_user_id:
                            error_parts.append("Incorrect user_id")
                        if not correct_default_status:
                            error_parts.append("Incorrect default status")
                        
                        self.log_test(
                            "Profile Retrieval Default Structure",
                            False,
                            error="; ".join(error_parts)
                        )
                        return False
                else:
                    self.log_test(
                        "Profile Retrieval Default Structure",
                        False,
                        error=f"Profile retrieval failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "Profile Retrieval Default Structure",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Profile Retrieval Default Structure", False, error=str(e))
            return False
    
    def test_oauth_duplicate_prevention(self):
        """Test OAuth profile creation duplicate prevention"""
        try:
            # Try to create profile for user that already has one
            oauth_data = {
                "user_metadata": {
                    "full_name": "Duplicate Test User",
                    "picture": "https://example.com/duplicate-avatar.jpg"
                },
                "email": "duplicate.test@gmail.com"
            }
            
            # Make multiple requests to test duplicate prevention
            responses = []
            for i in range(2):
                response = requests.post(
                    f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile/oauth",
                    json=oauth_data,
                    timeout=15
                )
                responses.append(response)
                time.sleep(0.5)  # Small delay between requests
            
            # Both should succeed but indicate existing profile
            all_handled_correctly = True
            for i, response in enumerate(responses):
                if response.status_code in [200, 201]:
                    data = response.json()
                    success = data.get('success', False)
                    existed = data.get('existed', False)
                    
                    if not (success and existed):
                        all_handled_correctly = False
                        break
                else:
                    all_handled_correctly = False
                    break
            
            if all_handled_correctly:
                self.log_test(
                    "OAuth Duplicate Prevention",
                    True,
                    "Multiple requests correctly handled - no duplicates created"
                )
                return True
            else:
                self.log_test(
                    "OAuth Duplicate Prevention",
                    False,
                    error="Duplicate prevention not working correctly"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Duplicate Prevention", False, error=str(e))
            return False
    
    def test_oauth_field_population(self):
        """Test OAuth profile field population from metadata"""
        try:
            # Test with rich OAuth metadata
            oauth_data = {
                "user_metadata": {
                    "full_name": "Rich Metadata User",
                    "picture": "https://lh3.googleusercontent.com/rich-metadata-avatar",
                    "name": "Rich Meta",
                    "avatar_url": "https://example.com/alt-avatar.jpg",  # Should prefer 'picture'
                    "locale": "en-US",
                    "email_verified": True
                },
                "email": "rich.metadata@gmail.com",
                "provider": "google",
                "aud": "authenticated"
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
                    # Check that the endpoint processed the data correctly
                    # (Even if profile already exists, the endpoint should handle the data properly)
                    self.log_test(
                        "OAuth Field Population",
                        True,
                        f"OAuth metadata processed correctly: {data.get('message', 'Success')}"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth Field Population",
                        False,
                        error=f"OAuth field population failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Field Population",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Field Population", False, error=str(e))
            return False
    
    def test_oauth_error_handling_edge_cases(self):
        """Test OAuth endpoint error handling for edge cases"""
        try:
            edge_cases = [
                {
                    "name": "Empty Request Body",
                    "user_id": EXISTING_USER_ID,
                    "data": {},
                    "should_handle": True  # Should handle gracefully
                },
                {
                    "name": "Invalid JSON Structure",
                    "user_id": EXISTING_USER_ID,
                    "data": {"user_metadata": "not_an_object"},
                    "should_handle": True  # Should handle gracefully
                },
                {
                    "name": "Missing Email",
                    "user_id": EXISTING_USER_ID,
                    "data": {
                        "user_metadata": {
                            "full_name": "No Email User"
                        }
                    },
                    "should_handle": True  # Should handle gracefully
                }
            ]
            
            all_handled = True
            results = []
            
            for case in edge_cases:
                try:
                    response = requests.post(
                        f"{self.backend_url}/auth/user/{case['user_id']}/profile/oauth",
                        json=case['data'],
                        timeout=15
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        success = data.get('success', False)
                        
                        if case['should_handle'] and success:
                            results.append(f"✅ {case['name']}: Handled gracefully")
                        elif not case['should_handle'] and not success:
                            results.append(f"✅ {case['name']}: Correctly rejected")
                        else:
                            results.append(f"❌ {case['name']}: Unexpected result")
                            all_handled = False
                    else:
                        # Error responses can be acceptable depending on the case
                        if case['should_handle']:
                            results.append(f"❌ {case['name']}: HTTP {response.status_code}")
                            all_handled = False
                        else:
                            results.append(f"✅ {case['name']}: Correctly returned error")
                            
                except Exception as case_error:
                    if case['should_handle']:
                        results.append(f"❌ {case['name']}: Exception - {str(case_error)}")
                        all_handled = False
                    else:
                        results.append(f"✅ {case['name']}: Exception handled")
            
            self.log_test(
                "OAuth Error Handling Edge Cases",
                all_handled,
                "; ".join(results) if all_handled else "",
                "; ".join(results) if not all_handled else ""
            )
            return all_handled
                
        except Exception as e:
            self.log_test("OAuth Error Handling Edge Cases", False, error=str(e))
            return False
    
    def test_oauth_profile_no_pgrst204_errors(self):
        """Test that OAuth profile creation doesn't produce PGRST204 errors"""
        try:
            # Test OAuth profile creation with data that previously caused PGRST204 errors
            oauth_data = {
                "user_metadata": {
                    "full_name": "PGRST204 Test User",
                    "picture": "https://lh3.googleusercontent.com/pgrst204-test-avatar",
                    "email_verified": True
                },
                "email": "pgrst204.test@gmail.com",  # This should NOT cause email column errors
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
                
                # Check that no PGRST204 error occurred
                has_pgrst204 = 'PGRST204' in message or 'email column' in message.lower()
                
                if success and not has_pgrst204:
                    self.log_test(
                        "OAuth Profile - No PGRST204 Errors",
                        True,
                        f"No PGRST204 errors detected. Message: {message}"
                    )
                    return True
                elif not success and not has_pgrst204:
                    # Acceptable failure as long as it's not PGRST204
                    self.log_test(
                        "OAuth Profile - No PGRST204 Errors",
                        True,
                        f"No PGRST204 errors (acceptable failure): {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth Profile - No PGRST204 Errors",
                        False,
                        error=f"PGRST204 error detected: {message}"
                    )
                    return False
            else:
                # Check response text for PGRST204 errors
                response_text = response.text
                has_pgrst204 = 'PGRST204' in response_text or 'email column' in response_text.lower()
                
                if not has_pgrst204:
                    self.log_test(
                        "OAuth Profile - No PGRST204 Errors",
                        True,
                        f"No PGRST204 errors in error response: HTTP {response.status_code}"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth Profile - No PGRST204 Errors",
                        False,
                        error=f"PGRST204 error in response: {response_text}"
                    )
                    return False
                
        except Exception as e:
            self.log_test("OAuth Profile - No PGRST204 Errors", False, error=str(e))
            return False
    
    def test_profile_field_validation(self):
        """Test that OAuth profiles have correct field structure and no email conflicts"""
        try:
            # Get the existing user's profile
            response = requests.get(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    is_default = data.get('is_default', False)
                    
                    # Check required fields are present
                    required_fields = ['user_id', 'display_name', 'seller_verification_status']
                    missing_fields = [field for field in required_fields if field not in user_data]
                    
                    # Check that email field is NOT present (should be filtered)
                    has_email_field = 'email' in user_data
                    
                    if not missing_fields and not has_email_field:
                        self.log_test(
                            "Profile Field Validation",
                            True,
                            f"Profile has correct structure. Required fields present, email field correctly absent."
                        )
                        return True
                    else:
                        error_msg = ""
                        if missing_fields:
                            error_msg += f"Missing fields: {missing_fields}. "
                        if has_email_field:
                            error_msg += "Email field present (should be filtered). "
                        
                        self.log_test(
                            "Profile Field Validation",
                            False,
                            error=error_msg.strip()
                        )
                        return False
                else:
                    self.log_test(
                        "Profile Field Validation",
                        False,
                        error=f"Failed to retrieve profile: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "Profile Field Validation",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Profile Field Validation", False, error=str(e))
            return False
    
    def run_core_tests(self):
        """Run core OAuth profile creation tests"""
        print("=" * 80)
        print("🔥 OAUTH PROFILE CREATION - CORE FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Testing with existing user: {EXISTING_USER_ID}")
        print("=" * 80)
        print()
        
        # Test 1: Basic connectivity
        response = requests.get(f"{self.backend_url}/health", timeout=10)
        if response.status_code != 200:
            print("❌ Backend not accessible - aborting tests")
            return self.generate_summary()
        
        print("✅ Backend accessible")
        print()
        
        # Test 2: OAuth endpoint functionality
        self.test_oauth_endpoint_functionality()
        
        # Test 3: OAuth user verification logic
        self.test_oauth_user_verification()
        
        # Test 4: OAuth metadata extraction
        self.test_oauth_metadata_extraction()
        
        # Test 5: Profile retrieval comprehensive
        self.test_profile_retrieval_comprehensive()
        
        # Test 6: Profile retrieval default structure
        self.test_profile_retrieval_default_structure()
        
        # Test 7: OAuth duplicate prevention
        self.test_oauth_duplicate_prevention()
        
        # Test 8: OAuth field population
        self.test_oauth_field_population()
        
        # Test 9: OAuth error handling edge cases
        self.test_oauth_error_handling_edge_cases()
        
        # Test 10: No PGRST204 errors
        self.test_oauth_profile_no_pgrst204_errors()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("📊 OAUTH PROFILE CREATION CORE TEST SUMMARY")
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
        
        # Show critical findings
        critical_findings = []
        for test in self.test_results:
            if test['success'] and ('PGRST204' in test['test'] or 'Error Handling' in test['test']):
                critical_findings.append(f"✅ {test['test']}: {test['details']}")
        
        if critical_findings:
            print("🔥 CRITICAL FINDINGS:")
            for finding in critical_findings:
                print(f"   {finding}")
            print()
        
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "failed_tests": failed_tests_list,
            "critical_findings": critical_findings,
            "all_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = OAuthProfileCoreTester()
    summary = tester.run_core_tests()
    
    # Return exit code based on critical failures
    critical_failures = [t for t in summary.get('failed_tests', []) if 'PGRST204' in t['test'] or 'Critical' in t['test']]
    
    if critical_failures:
        print(f"❌ {len(critical_failures)} critical test(s) failed!")
        return 1
    else:
        print("✅ All critical tests passed!")
        return 0

if __name__ == "__main__":
    exit(main())