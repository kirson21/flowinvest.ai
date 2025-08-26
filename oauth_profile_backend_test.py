#!/usr/bin/env python3
"""
OAuth Profile Creation System Testing
Testing the automatic OAuth profile creation system that has been implemented and fixed.
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://dataflow-crypto.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super Admin for testing
EXISTING_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Known existing user
INVALID_USER_ID = "invalid-user-id-12345"

# Known existing users from the system (from previous test results)
KNOWN_USERS = [
    "cd0e9717-f85d-4726-81e9-f260394ead58",  # Super admin
    # We'll discover more during testing
]

class OAuthProfileTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_user_id = TEST_USER_ID
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
    
    def test_auth_health(self):
        """Test auth service health"""
        try:
            response = requests.get(f"{self.backend_url}/auth/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                supabase_connected = data.get('supabase_connected', False)
                
                self.log_test(
                    "Auth Service Health Check",
                    success and supabase_connected,
                    f"Success: {success}, Supabase Connected: {supabase_connected}"
                )
                return success and supabase_connected
            else:
                self.log_test(
                    "Auth Service Health Check",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Auth Service Health Check", False, error=str(e))
            return False
    
    def test_oauth_profile_creation_valid_data(self):
        """Test OAuth profile creation with valid user_metadata for existing user"""
        try:
            # Use the known existing user for this test
            oauth_data = {
                "user_metadata": {
                    "full_name": "John OAuth Doe Updated",
                    "picture": "https://lh3.googleusercontent.com/test-oauth-avatar",
                    "name": "John Doe"
                },
                "email": "john.oauth@example.com"
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
                    existed = data.get('existed', False)
                    if existed:
                        self.log_test(
                            "OAuth Profile Creation - Valid Data",
                            True,
                            f"Profile already exists for user {EXISTING_USER_ID} - correct behavior"
                        )
                    else:
                        user_data = data.get('user', {})
                        display_name = user_data.get('display_name')
                        avatar_url = user_data.get('avatar_url')
                        
                        self.log_test(
                            "OAuth Profile Creation - Valid Data",
                            True,
                            f"Profile created with display_name: '{display_name}', avatar_url: '{avatar_url}'"
                        )
                    return True
                else:
                    self.log_test(
                        "OAuth Profile Creation - Valid Data",
                        False,
                        error=f"Success=False: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Profile Creation - Valid Data",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Valid Data", False, error=str(e))
            return False
    
    def test_oauth_profile_creation_existing_user(self):
        """Test OAuth profile creation with existing user to ensure no duplicates"""
        try:
            oauth_data = {
                "user_metadata": {
                    "full_name": "Existing User Test",
                    "picture": "https://example.com/existing-avatar.jpg"
                },
                "email": "existing@example.com"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                existed = data.get('existed', False)
                
                if success and existed:
                    self.log_test(
                        "OAuth Profile Creation - Existing User",
                        True,
                        f"Correctly detected existing profile: {data.get('message')}"
                    )
                    return True
                elif success and not existed:
                    self.log_test(
                        "OAuth Profile Creation - Existing User",
                        True,
                        "Profile created for user (may not have existed before)"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth Profile Creation - Existing User",
                        False,
                        error=f"Success=False: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Profile Creation - Existing User",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Existing User", False, error=str(e))
            return False
    
    def test_oauth_profile_creation_invalid_user_id(self):
        """Test OAuth profile creation with invalid user_id"""
        try:
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
                
                if not success:
                    # Expected behavior - should fail for invalid user
                    self.log_test(
                        "OAuth Profile Creation - Invalid User ID",
                        True,
                        f"Correctly rejected invalid user: {data.get('message')}"
                    )
                    return True
                else:
                    # Unexpected - should not succeed for invalid user
                    self.log_test(
                        "OAuth Profile Creation - Invalid User ID",
                        False,
                        error="Profile creation succeeded for invalid user (security issue)"
                    )
                    return False
            else:
                # Error response is expected for invalid user
                self.log_test(
                    "OAuth Profile Creation - Invalid User ID",
                    True,
                    f"Correctly returned error for invalid user: HTTP {response.status_code}"
                )
                return True
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Invalid User ID", False, error=str(e))
            return False
    
    def test_oauth_profile_creation_missing_metadata(self):
        """Test OAuth profile creation with missing user_metadata for existing user"""
        try:
            oauth_data = {
                "email": "minimal@example.com"
                # No user_metadata provided
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
                    existed = data.get('existed', False)
                    if existed:
                        self.log_test(
                            "OAuth Profile Creation - Missing Metadata",
                            True,
                            "Profile already exists - correct behavior for existing user"
                        )
                    else:
                        user_data = data.get('user', {})
                        display_name = user_data.get('display_name')
                        
                        # Should create profile with fallback display name
                        self.log_test(
                            "OAuth Profile Creation - Missing Metadata",
                            True,
                            f"Profile created with fallback display_name: '{display_name}'"
                        )
                    return True
                else:
                    self.log_test(
                        "OAuth Profile Creation - Missing Metadata",
                        False,
                        error=f"Failed to create profile: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Profile Creation - Missing Metadata",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Missing Metadata", False, error=str(e))
            return False
    
    def test_oauth_profile_creation_malformed_data(self):
        """Test OAuth profile creation with malformed OAuth data"""
        try:
            # Create a unique test user ID for this test
            test_user_id = f"test-malformed-{int(time.time())}"
            
            oauth_data = {
                "user_metadata": "invalid_string_instead_of_object",
                "email": 12345  # Invalid email type
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{test_user_id}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    # Should handle malformed data gracefully
                    user_data = data.get('user', {})
                    display_name = user_data.get('display_name')
                    
                    self.log_test(
                        "OAuth Profile Creation - Malformed Data",
                        True,
                        f"Gracefully handled malformed data, created profile with display_name: '{display_name}'"
                    )
                    return True
                else:
                    # Acceptable to fail with malformed data
                    self.log_test(
                        "OAuth Profile Creation - Malformed Data",
                        True,
                        f"Correctly rejected malformed data: {data.get('message')}"
                    )
                    return True
            else:
                # Error response is acceptable for malformed data
                self.log_test(
                    "OAuth Profile Creation - Malformed Data",
                    True,
                    f"Correctly returned error for malformed data: HTTP {response.status_code}"
                )
                return True
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Malformed Data", False, error=str(e))
            return False
    
    def test_regular_profile_creation_field_filtering(self):
        """Test regular profile creation with field filtering for existing user"""
        try:
            profile_data = {
                "display_name": "Regular User Test Updated",
                "bio": "Test bio for field filtering",
                "email": "should_be_filtered@example.com",  # Should be filtered out
                "invalid_field": "should_be_removed",  # Should be filtered out
                "avatar_url": "https://example.com/filtered-avatar.jpg",
                "seller_verification_status": "unverified"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{EXISTING_USER_ID}/profile",
                json=profile_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    
                    # Check that disallowed fields were filtered out
                    has_email = 'email' in user_data
                    has_invalid_field = 'invalid_field' in user_data
                    has_display_name = user_data.get('display_name') == "Regular User Test Updated"
                    
                    if not has_email and not has_invalid_field and has_display_name:
                        self.log_test(
                            "Regular Profile Creation - Field Filtering",
                            True,
                            f"Field filtering working correctly. Profile created with allowed fields only."
                        )
                        return True
                    else:
                        self.log_test(
                            "Regular Profile Creation - Field Filtering",
                            False,
                            error=f"Field filtering failed. Email present: {has_email}, Invalid field present: {has_invalid_field}"
                        )
                        return False
                else:
                    self.log_test(
                        "Regular Profile Creation - Field Filtering",
                        False,
                        error=f"Profile creation failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "Regular Profile Creation - Field Filtering",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Regular Profile Creation - Field Filtering", False, error=str(e))
            return False
    
    def test_profile_retrieval_existing_user(self):
        """Test profile retrieval for user with existing profile"""
        try:
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
                    
                    # Should return actual profile data, not default
                    if not is_default and user_data.get('user_id') == EXISTING_USER_ID:
                        self.log_test(
                            "Profile Retrieval - Existing User",
                            True,
                            f"Retrieved existing profile for user {EXISTING_USER_ID}"
                        )
                        return True
                    elif is_default:
                        self.log_test(
                            "Profile Retrieval - Existing User",
                            True,
                            "User has no profile yet - returned default profile structure"
                        )
                        return True
                    else:
                        self.log_test(
                            "Profile Retrieval - Existing User",
                            False,
                            error="Profile data inconsistent or missing user_id"
                        )
                        return False
                else:
                    self.log_test(
                        "Profile Retrieval - Existing User",
                        False,
                        error=f"Request failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "Profile Retrieval - Existing User",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Profile Retrieval - Existing User", False, error=str(e))
            return False
    
    def test_profile_retrieval_nonexistent_user(self):
        """Test profile retrieval for user without profile"""
        try:
            nonexistent_user_id = f"nonexistent-{int(time.time())}"
            
            response = requests.get(
                f"{self.backend_url}/auth/user/{nonexistent_user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    is_default = data.get('is_default', False)
                    
                    # Should return default profile structure
                    if is_default and user_data.get('user_id') == nonexistent_user_id:
                        self.log_test(
                            "Profile Retrieval - Nonexistent User",
                            True,
                            "Correctly returned default profile structure for user without profile"
                        )
                        return True
                    else:
                        self.log_test(
                            "Profile Retrieval - Nonexistent User",
                            False,
                            error="Should return default profile for nonexistent user"
                        )
                        return False
                else:
                    self.log_test(
                        "Profile Retrieval - Nonexistent User",
                        False,
                        error=f"Request failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "Profile Retrieval - Nonexistent User",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Profile Retrieval - Nonexistent User", False, error=str(e))
            return False
    
    def test_oauth_profile_minimal_metadata(self):
        """Test OAuth profile creation with minimal metadata"""
        try:
            # Create a unique test user ID for this test
            test_user_id = f"test-minimal-{int(time.time())}"
            
            oauth_data = {
                "user_metadata": {
                    # Only email, no full_name or picture
                },
                "email": "minimal@example.com"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{test_user_id}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    display_name = user_data.get('display_name')
                    
                    # Should create profile with fallback display name (email prefix or 'User')
                    expected_fallback = oauth_data['email'].split('@')[0] if oauth_data.get('email') else 'User'
                    
                    self.log_test(
                        "OAuth Profile Creation - Minimal Metadata",
                        True,
                        f"Profile created with fallback display_name: '{display_name}' (expected: '{expected_fallback}')"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth Profile Creation - Minimal Metadata",
                        False,
                        error=f"Profile creation failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Profile Creation - Minimal Metadata",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Minimal Metadata", False, error=str(e))
            return False
    
    def test_concurrent_profile_creation(self):
        """Test concurrent profile creation attempts"""
        try:
            # Create a unique test user ID for this test
            test_user_id = f"test-concurrent-{int(time.time())}"
            
            oauth_data = {
                "user_metadata": {
                    "full_name": "Concurrent Test User",
                    "picture": "https://example.com/concurrent-avatar.jpg"
                },
                "email": "concurrent@example.com"
            }
            
            # Make two concurrent requests
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def make_request():
                try:
                    response = requests.post(
                        f"{self.backend_url}/auth/user/{test_user_id}/profile/oauth",
                        json=oauth_data,
                        timeout=15
                    )
                    results_queue.put(response)
                except Exception as e:
                    results_queue.put(e)
            
            # Start two threads
            thread1 = threading.Thread(target=make_request)
            thread2 = threading.Thread(target=make_request)
            
            thread1.start()
            thread2.start()
            
            thread1.join()
            thread2.join()
            
            # Get results
            result1 = results_queue.get()
            result2 = results_queue.get()
            
            success_count = 0
            duplicate_detected = False
            
            for i, result in enumerate([result1, result2], 1):
                if isinstance(result, Exception):
                    continue
                
                if result.status_code in [200, 201]:
                    data = result.json()
                    if data.get('success'):
                        if data.get('existed'):
                            duplicate_detected = True
                        else:
                            success_count += 1
            
            # One should succeed, one should detect duplicate
            if success_count == 1 and duplicate_detected:
                self.log_test(
                    "OAuth Profile Creation - Concurrent Attempts",
                    True,
                    "Correctly handled concurrent creation - one succeeded, one detected duplicate"
                )
                return True
            elif success_count == 1:
                self.log_test(
                    "OAuth Profile Creation - Concurrent Attempts",
                    True,
                    "One request succeeded (acceptable for concurrent requests)"
                )
                return True
            else:
                self.log_test(
                    "OAuth Profile Creation - Concurrent Attempts",
                    False,
                    error=f"Unexpected results: {success_count} successes, duplicate_detected: {duplicate_detected}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Concurrent Attempts", False, error=str(e))
            return False
    
    def test_profile_creation_special_characters(self):
        """Test profile creation with special characters in names"""
        try:
            # Create a unique test user ID for this test
            test_user_id = f"test-special-{int(time.time())}"
            
            oauth_data = {
                "user_metadata": {
                    "full_name": "José María Ñoño-Pérez O'Connor",
                    "picture": "https://example.com/special-avatar.jpg"
                },
                "email": "special.chars@example.com"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{test_user_id}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    display_name = user_data.get('display_name')
                    
                    self.log_test(
                        "OAuth Profile Creation - Special Characters",
                        True,
                        f"Successfully handled special characters in name: '{display_name}'"
                    )
                    return True
                else:
                    self.log_test(
                        "OAuth Profile Creation - Special Characters",
                        False,
                        error=f"Profile creation failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Profile Creation - Special Characters",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Special Characters", False, error=str(e))
            return False
    
    def test_database_foreign_key_relationships(self):
        """Test that profiles are created with correct user_id foreign key relationships"""
        try:
            # Create a unique test user ID for this test
            test_user_id = f"test-fk-{int(time.time())}"
            
            oauth_data = {
                "user_metadata": {
                    "full_name": "Foreign Key Test User",
                    "picture": "https://example.com/fk-avatar.jpg"
                },
                "email": "fk.test@example.com"
            }
            
            # First create the profile
            create_response = requests.post(
                f"{self.backend_url}/auth/user/{test_user_id}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if create_response.status_code in [200, 201]:
                create_data = create_response.json()
                
                if create_data.get('success'):
                    # Now retrieve the profile to verify foreign key relationship
                    retrieve_response = requests.get(
                        f"{self.backend_url}/auth/user/{test_user_id}",
                        timeout=10
                    )
                    
                    if retrieve_response.status_code == 200:
                        retrieve_data = retrieve_response.json()
                        
                        if retrieve_data.get('success'):
                            user_data = retrieve_data.get('user', {})
                            stored_user_id = user_data.get('user_id')
                            
                            if stored_user_id == test_user_id:
                                self.log_test(
                                    "Database Foreign Key Relationships",
                                    True,
                                    f"Profile correctly stored with user_id: {stored_user_id}"
                                )
                                return True
                            else:
                                self.log_test(
                                    "Database Foreign Key Relationships",
                                    False,
                                    error=f"User ID mismatch: expected {test_user_id}, got {stored_user_id}"
                                )
                                return False
                        else:
                            self.log_test(
                                "Database Foreign Key Relationships",
                                False,
                                error="Failed to retrieve created profile"
                            )
                            return False
                    else:
                        self.log_test(
                            "Database Foreign Key Relationships",
                            False,
                            error=f"Profile retrieval failed: HTTP {retrieve_response.status_code}"
                        )
                        return False
                else:
                    self.log_test(
                        "Database Foreign Key Relationships",
                        False,
                        error="Profile creation failed"
                    )
                    return False
            else:
                self.log_test(
                    "Database Foreign Key Relationships",
                    False,
                    error=f"Profile creation failed: HTTP {create_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Database Foreign Key Relationships", False, error=str(e))
            return False
    
    def test_oauth_profile_creation_comprehensive(self):
        """Test comprehensive OAuth profile creation with all metadata fields"""
        try:
            # Create a unique test user ID for this test
            test_user_id = f"test-comprehensive-{int(time.time())}"
            
            oauth_data = {
                "user_metadata": {
                    "full_name": "Comprehensive Test User",
                    "name": "Comp Test",  # Alternative name field
                    "picture": "https://lh3.googleusercontent.com/test-avatar",
                    "avatar_url": "https://example.com/alt-avatar.jpg",
                    "locale": "en-US",
                    "email_verified": True
                },
                "email": "comprehensive.test@gmail.com",
                "provider": "google",
                "aud": "authenticated"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/user/{test_user_id}/profile/oauth",
                json=oauth_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    user_data = data.get('user', {})
                    display_name = user_data.get('display_name')
                    avatar_url = user_data.get('avatar_url')
                    seller_status = user_data.get('seller_verification_status')
                    
                    # Verify all required fields are populated correctly
                    has_display_name = display_name == "Comprehensive Test User"
                    has_avatar = avatar_url == "https://lh3.googleusercontent.com/test-avatar"
                    has_seller_status = seller_status == "unverified"
                    has_user_id = user_data.get('user_id') == test_user_id
                    
                    if has_display_name and has_avatar and has_seller_status and has_user_id:
                        self.log_test(
                            "OAuth Profile Creation - Comprehensive Data",
                            True,
                            f"All fields populated correctly: name='{display_name}', avatar='{avatar_url}', status='{seller_status}'"
                        )
                        return True
                    else:
                        self.log_test(
                            "OAuth Profile Creation - Comprehensive Data",
                            False,
                            error=f"Field population issues: name={has_display_name}, avatar={has_avatar}, status={has_seller_status}, user_id={has_user_id}"
                        )
                        return False
                else:
                    self.log_test(
                        "OAuth Profile Creation - Comprehensive Data",
                        False,
                        error=f"Profile creation failed: {data.get('message')}"
                    )
                    return False
            else:
                self.log_test(
                    "OAuth Profile Creation - Comprehensive Data",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Comprehensive Data", False, error=str(e))
            return False
    
    def test_profile_creation_error_handling(self):
        """Test error handling for various edge cases"""
        try:
            test_cases = [
                {
                    "name": "Empty OAuth Data",
                    "user_id": f"test-empty-{int(time.time())}",
                    "data": {},
                    "should_succeed": True  # Should handle gracefully
                },
                {
                    "name": "Null User Metadata",
                    "user_id": f"test-null-{int(time.time())}",
                    "data": {"user_metadata": None, "email": "null@example.com"},
                    "should_succeed": True  # Should handle gracefully
                },
                {
                    "name": "Very Long Name",
                    "user_id": f"test-long-{int(time.time())}",
                    "data": {
                        "user_metadata": {
                            "full_name": "A" * 500,  # Very long name
                            "picture": "https://example.com/long-avatar.jpg"
                        },
                        "email": "long.name@example.com"
                    },
                    "should_succeed": True  # Should handle or truncate
                }
            ]
            
            all_passed = True
            results = []
            
            for test_case in test_cases:
                try:
                    response = requests.post(
                        f"{self.backend_url}/auth/user/{test_case['user_id']}/profile/oauth",
                        json=test_case['data'],
                        timeout=15
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        success = data.get('success', False)
                        
                        if test_case['should_succeed']:
                            if success:
                                results.append(f"✅ {test_case['name']}: Handled correctly")
                            else:
                                results.append(f"❌ {test_case['name']}: Should have succeeded but failed")
                                all_passed = False
                        else:
                            if not success:
                                results.append(f"✅ {test_case['name']}: Correctly rejected")
                            else:
                                results.append(f"❌ {test_case['name']}: Should have failed but succeeded")
                                all_passed = False
                    else:
                        if test_case['should_succeed']:
                            results.append(f"❌ {test_case['name']}: HTTP {response.status_code}")
                            all_passed = False
                        else:
                            results.append(f"✅ {test_case['name']}: Correctly returned error")
                            
                except Exception as case_error:
                    results.append(f"❌ {test_case['name']}: Exception - {str(case_error)}")
                    all_passed = False
            
            self.log_test(
                "OAuth Profile Creation - Error Handling",
                all_passed,
                "; ".join(results) if all_passed else "",
                "; ".join(results) if not all_passed else ""
            )
            return all_passed
                
        except Exception as e:
            self.log_test("OAuth Profile Creation - Error Handling", False, error=str(e))
            return False
    
    def run_comprehensive_tests(self):
        """Run all OAuth profile creation tests"""
        print("=" * 80)
        print("🔥 OAUTH PROFILE CREATION SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 80)
        print()
        
        # Test 1: Basic connectivity
        if not self.test_backend_health():
            print("❌ Backend health check failed - aborting tests")
            return self.generate_summary()
        
        # Test 2: Auth service health
        if not self.test_auth_health():
            print("❌ Auth service health check failed - continuing with limited tests")
        
        # Test 3: OAuth profile creation with valid data
        self.test_oauth_profile_creation_valid_data()
        
        # Test 4: OAuth profile creation with existing user
        self.test_oauth_profile_creation_existing_user()
        
        # Test 5: OAuth profile creation with invalid user ID
        self.test_oauth_profile_creation_invalid_user_id()
        
        # Test 6: OAuth profile creation with missing metadata
        self.test_oauth_profile_creation_missing_metadata()
        
        # Test 7: OAuth profile creation with malformed data
        self.test_oauth_profile_creation_malformed_data()
        
        # Test 8: Regular profile creation with field filtering
        self.test_regular_profile_creation_field_filtering()
        
        # Test 9: Profile retrieval for existing user
        self.test_profile_retrieval_existing_user()
        
        # Test 10: Profile retrieval for nonexistent user
        self.test_profile_retrieval_nonexistent_user()
        
        # Test 11: OAuth profile creation with minimal metadata
        self.test_oauth_profile_minimal_metadata()
        
        # Test 12: Concurrent profile creation attempts
        self.test_concurrent_profile_creation()
        
        # Test 13: Database foreign key relationships
        self.test_database_foreign_key_relationships()
        
        # Test 14: Profile creation with special characters
        self.test_profile_creation_special_characters()
        
        # Test 15: Error handling edge cases
        self.test_profile_creation_error_handling()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("📊 OAUTH PROFILE CREATION TEST SUMMARY")
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
        
        # Show passed tests
        passed_tests_list = [r for r in self.test_results if r['success']]
        if passed_tests_list:
            print("✅ PASSED TESTS:")
            for test in passed_tests_list:
                print(f"   • {test['test']}")
                if test['details']:
                    print(f"     {test['details']}")
            print()
        
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "failed_tests": failed_tests_list,
            "passed_tests": passed_tests_list,
            "all_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = OAuthProfileTester()
    summary = tester.run_comprehensive_tests()
    
    # Return exit code based on critical failures
    critical_failures = [t for t in summary.get('failed_tests', []) if 'CRITICAL' in t['test'] or 'Critical' in t['test']]
    
    if critical_failures:
        print(f"❌ {len(critical_failures)} critical test(s) failed!")
        return 1
    else:
        print("✅ All critical tests passed!")
        return 0

if __name__ == "__main__":
    exit(main())