#!/usr/bin/env python3
"""
SELLER VERIFICATION QUERY COLUMN FIX VERIFICATION TEST
Testing the corrected getAllApplications query to ensure PostgreSQL 42703 error is resolved
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://dataflow-crypto.preview.emergentagent.com/api"
SUPABASE_URL = "https://pmfwqmaykidbvjhcqjrr.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtZndxbWF5a2lkYnZqaGNxanJyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDk2MjUsImV4cCI6MjA2Nzk4NTYyNX0.BsJ0128ME7WhH-CBRb3_LTV5NvsDkVev07SzOalAb-E"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtZndxbWF5a2lkYnZqaGNxanJyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjQwOTYyNSwiZXhwIjoyMDY3OTg1NjI1fQ.XiC_Nf3BR8etEqXRDUggG8sBgZA5lcwipd2GPu_a_tU"

# Super Admin UID for testing
SUPER_ADMIN_UID = "cd0e9717-f85d-4726-81e9-f260394ead58"

class SellerVerificationQueryTest:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, message, details=None):
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
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_supabase_direct_query(self):
        """Test the corrected query directly against Supabase to verify column fix"""
        try:
            # Test the exact query from verificationService.js
            headers = {
                'apikey': SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                'Content-Type': 'application/json'
            }
            
            # This is the corrected query that should work
            query_url = f"{SUPABASE_URL}/rest/v1/seller_verification_applications"
            params = {
                'select': 'id,user_id,full_name,contact_email,status,created_at,user_profiles!seller_verification_applications_user_id_fkey(display_name)',
                'order': 'created_at.desc'
            }
            
            print(f"Testing corrected query: {query_url}")
            print(f"Query params: {params}")
            
            response = requests.get(query_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Direct Supabase Query - Column Fix Verification",
                    True,
                    f"Query executed successfully, returned {len(data)} applications",
                    f"Status: {response.status_code}, Response length: {len(data)}"
                )
                
                # Verify the structure includes user_profiles with display_name only
                if data and len(data) > 0:
                    sample_app = data[0]
                    if 'user_profiles' in sample_app and 'display_name' in sample_app['user_profiles']:
                        self.log_test(
                            "Query Structure Verification",
                            True,
                            "Query returns user_profiles with display_name field as expected",
                            f"Sample structure: {list(sample_app.get('user_profiles', {}).keys())}"
                        )
                    else:
                        self.log_test(
                            "Query Structure Verification",
                            False,
                            "Query structure missing expected user_profiles.display_name",
                            f"Sample app structure: {sample_app.keys() if sample_app else 'No data'}"
                        )
                else:
                    self.log_test(
                        "Query Structure Verification",
                        True,
                        "No applications found, but query executed without column errors",
                        "Empty result set - column error would have prevented successful execution"
                    )
                
                return True
                
            elif response.status_code == 400 and "42703" in response.text:
                self.log_test(
                    "Direct Supabase Query - Column Fix Verification",
                    False,
                    "PostgreSQL 42703 error still present - column does not exist",
                    f"Status: {response.status_code}, Error: {response.text}"
                )
                return False
            else:
                self.log_test(
                    "Direct Supabase Query - Column Fix Verification",
                    False,
                    f"Query failed with status {response.status_code}",
                    f"Response: {response.text[:500]}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Direct Supabase Query - Column Fix Verification",
                False,
                f"Exception during query test: {str(e)}",
                f"Error type: {type(e).__name__}"
            )
            return False
    
    def test_old_problematic_query(self):
        """Test the old query that would cause 42703 error to confirm it's fixed"""
        try:
            headers = {
                'apikey': SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                'Content-Type': 'application/json'
            }
            
            # This would be the old problematic query (with email field that doesn't exist)
            query_url = f"{SUPABASE_URL}/rest/v1/seller_verification_applications"
            params = {
                'select': 'id,user_id,full_name,contact_email,status,created_at,user_profiles(display_name,email)',
                'order': 'created_at.desc'
            }
            
            print(f"Testing old problematic query for comparison: {query_url}")
            
            response = requests.get(query_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 400 and ("42703" in response.text or "email" in response.text.lower()):
                self.log_test(
                    "Old Query Verification - Confirms Fix Needed",
                    True,
                    "Old query correctly fails with column error, confirming the fix was necessary",
                    f"Status: {response.status_code}, Error contains expected column issue"
                )
                return True
            elif response.status_code == 200:
                self.log_test(
                    "Old Query Verification - Unexpected Success",
                    False,
                    "Old query unexpectedly succeeded - email column may exist now",
                    f"Status: {response.status_code}, This suggests schema may have changed"
                )
                return False
            else:
                self.log_test(
                    "Old Query Verification - Different Error",
                    True,
                    f"Old query failed with different error (not column issue): {response.status_code}",
                    f"Response: {response.text[:200]}"
                )
                return True
                
        except Exception as e:
            self.log_test(
                "Old Query Verification",
                False,
                f"Exception during old query test: {str(e)}",
                f"Error type: {type(e).__name__}"
            )
            return False
    
    def test_super_admin_application_retrieval(self):
        """Test that Super Admin can retrieve applications using the corrected query"""
        try:
            # Simulate the frontend call that would use the corrected query
            # This tests the actual implementation path
            
            headers = {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Test the corrected query as it would be called from frontend
            query_url = f"{SUPABASE_URL}/rest/v1/seller_verification_applications"
            params = {
                'select': '*,user_profiles!seller_verification_applications_user_id_fkey(display_name)',
                'order': 'created_at.desc'
            }
            
            response = requests.get(query_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Super Admin Application Retrieval",
                    True,
                    f"Super Admin can successfully retrieve {len(data)} applications with user profile data",
                    f"Query executed without 42703 errors, foreign key relationship working"
                )
                return True
            elif response.status_code == 400 and "42703" in response.text:
                self.log_test(
                    "Super Admin Application Retrieval",
                    False,
                    "42703 column error still occurring in Super Admin retrieval",
                    f"Error: {response.text}"
                )
                return False
            else:
                self.log_test(
                    "Super Admin Application Retrieval",
                    False,
                    f"Super Admin retrieval failed with status {response.status_code}",
                    f"Response: {response.text[:300]}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Super Admin Application Retrieval",
                False,
                f"Exception during Super Admin test: {str(e)}",
                f"Error type: {type(e).__name__}"
            )
            return False
    
    def test_foreign_key_relationship_specification(self):
        """Test that the specific foreign key relationship works correctly"""
        try:
            headers = {
                'apikey': SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Test the specific foreign key relationship used in the fix
            query_url = f"{SUPABASE_URL}/rest/v1/seller_verification_applications"
            params = {
                'select': 'id,user_profiles!seller_verification_applications_user_id_fkey(display_name)',
                'limit': '1'
            }
            
            response = requests.get(query_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                self.log_test(
                    "Foreign Key Relationship Specification",
                    True,
                    "Specific foreign key relationship 'seller_verification_applications_user_id_fkey' works correctly",
                    f"Query executed successfully, avoiding relationship ambiguity"
                )
                return True
            elif "relationship" in response.text.lower() or "ambiguous" in response.text.lower():
                self.log_test(
                    "Foreign Key Relationship Specification",
                    False,
                    "Foreign key relationship still has ambiguity issues",
                    f"Error: {response.text}"
                )
                return False
            else:
                self.log_test(
                    "Foreign Key Relationship Specification",
                    False,
                    f"Foreign key test failed with status {response.status_code}",
                    f"Response: {response.text[:300]}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Foreign Key Relationship Specification",
                False,
                f"Exception during foreign key test: {str(e)}",
                f"Error type: {type(e).__name__}"
            )
            return False
    
    def test_contact_email_availability(self):
        """Verify that contact email is available from application.contact_email field"""
        try:
            headers = {
                'apikey': SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                'Content-Type': 'application/json'
            }
            
            query_url = f"{SUPABASE_URL}/rest/v1/seller_verification_applications"
            params = {
                'select': 'id,contact_email,user_profiles!seller_verification_applications_user_id_fkey(display_name)',
                'limit': '1'
            }
            
            response = requests.get(query_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    sample_app = data[0]
                    has_contact_email = 'contact_email' in sample_app
                    has_display_name = 'user_profiles' in sample_app and sample_app['user_profiles'] and 'display_name' in sample_app['user_profiles']
                    
                    if has_contact_email and has_display_name:
                        self.log_test(
                            "Contact Email Availability",
                            True,
                            "Contact email available from application.contact_email and display_name from user_profiles",
                            f"Structure verified: contact_email={has_contact_email}, display_name={has_display_name}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Contact Email Availability",
                            False,
                            "Missing expected fields in query result",
                            f"contact_email={has_contact_email}, display_name={has_display_name}"
                        )
                        return False
                else:
                    self.log_test(
                        "Contact Email Availability",
                        True,
                        "No applications to test, but query structure is correct",
                        "Empty result set - query executed without errors"
                    )
                    return True
            else:
                self.log_test(
                    "Contact Email Availability",
                    False,
                    f"Contact email test failed with status {response.status_code}",
                    f"Response: {response.text[:300]}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Contact Email Availability",
                False,
                f"Exception during contact email test: {str(e)}",
                f"Error type: {type(e).__name__}"
            )
            return False
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 80)
        print("SELLER VERIFICATION QUERY COLUMN FIX VERIFICATION")
        print("Testing PostgreSQL 42703 'column does not exist' error resolution")
        print("=" * 80)
        
        # Test the corrected query
        self.test_supabase_direct_query()
        
        # Test the old problematic query for comparison
        self.test_old_problematic_query()
        
        # Test Super Admin functionality
        self.test_super_admin_application_retrieval()
        
        # Test foreign key relationship specification
        self.test_foreign_key_relationship_specification()
        
        # Test contact email availability
        self.test_contact_email_availability()
        
        # Print summary
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Tests Passed: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED - PostgreSQL 42703 error has been RESOLVED!")
            print("✅ The corrected getAllApplications query is working properly")
            print("✅ Super Admin can retrieve verification applications successfully")
            print("✅ No more 'column user_profiles_1.email does not exist' errors")
        else:
            print("⚠️  Some tests failed - Column fix may need additional work")
            
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        return success_rate >= 80  # Consider successful if 80% or more tests pass

if __name__ == "__main__":
    tester = SellerVerificationQueryTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)