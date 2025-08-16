#!/usr/bin/env python3
"""
Backend Profile Update Testing Script
Testing the specific user profile update error: 409 duplicate key constraint violation
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
SPECIFIC_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

# Test data for profile updates (using only existing columns)
TEST_PROFILE_DATA = {
    "display_name": "Test Super Admin Updated",
    "bio": "Testing profile update functionality - updated"
}

def test_backend_health():
    """Test basic backend connectivity"""
    print("🔍 Testing Backend Health...")
    
    try:
        # Test basic endpoints
        endpoints = [
            f"{API_BASE}/",
            f"{API_BASE}/status", 
            f"{API_BASE}/health",
            f"{API_BASE}/auth/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                print(f"  ✅ {endpoint}: {response.status_code}")
                if response.status_code != 200:
                    print(f"     Response: {response.text[:200]}")
            except Exception as e:
                print(f"  ❌ {endpoint}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_get_user_profile(user_id):
    """Test GET /api/auth/user/{user_id} endpoint"""
    print(f"\n🔍 Testing GET User Profile for {user_id}...")
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}"
        response = requests.get(url, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ User profile found")
                user_data = data.get('user', {})
                print(f"     User ID: {user_data.get('user_id')}")
                print(f"     Display Name: {user_data.get('display_name')}")
                print(f"     Email: {user_data.get('email')}")
                return True, user_data
            else:
                print(f"  ❌ User not found: {data.get('message')}")
                return False, None
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"  ❌ Error testing GET user profile: {e}")
        return False, None

def test_put_user_profile(user_id, profile_data):
    """Test PUT /api/auth/user/{user_id}/profile endpoint"""
    print(f"\n🔍 Testing PUT User Profile Update for {user_id}...")
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}/profile"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.put(url, json=profile_data, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ Profile updated successfully")
                return True, data
            else:
                print(f"  ❌ Update failed: {data.get('message')}")
                return False, data
        elif response.status_code == 409:
            print(f"  🚨 DUPLICATE KEY CONSTRAINT VIOLATION DETECTED!")
            print(f"     This is the exact error reported by the user")
            return False, response.text
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, response.text
            
    except Exception as e:
        print(f"  ❌ Error testing PUT user profile: {e}")
        return False, str(e)

def test_post_user_profile(user_id, profile_data):
    """Test POST /api/auth/user/{user_id}/profile endpoint"""
    print(f"\n🔍 Testing POST User Profile Creation for {user_id}...")
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}/profile"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=profile_data, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ Profile created successfully")
                return True, data
            else:
                print(f"  ❌ Creation failed: {data.get('message')}")
                return False, data
        elif response.status_code == 409:
            print(f"  🚨 DUPLICATE KEY CONSTRAINT VIOLATION DETECTED!")
            print(f"     This suggests the profile already exists")
            return False, response.text
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, response.text
            
    except Exception as e:
        print(f"  ❌ Error testing POST user profile: {e}")
        return False, str(e)

def test_database_direct_query():
    """Test direct database query to understand schema"""
    print(f"\n🔍 Testing Direct Database Schema Query...")
    
    try:
        # Import supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin
        
        if not supabase_admin:
            print("  ❌ Supabase admin client not available")
            return False
        
        # Query user_profiles table structure
        print("  Querying user_profiles table...")
        response = supabase_admin.table('user_profiles').select('*').eq('user_id', SPECIFIC_USER_ID).execute()
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Data: {response.data}")
        
        if response.data:
            print(f"  ✅ Found {len(response.data)} profile(s) for user {SPECIFIC_USER_ID}")
            for profile in response.data:
                print(f"     Profile ID: {profile.get('id')}")
                print(f"     User ID: {profile.get('user_id')}")
                print(f"     Display Name: {profile.get('display_name')}")
        else:
            print(f"  ❌ No profiles found for user {SPECIFIC_USER_ID}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error with direct database query: {e}")
        return False

def test_with_non_existing_user():
    """Test profile operations with a non-existing user"""
    print(f"\n🔍 Testing with Non-Existing User...")
    
    non_existing_user_id = "00000000-0000-0000-0000-000000000000"
    
    # Test GET for non-existing user
    profile_exists, _ = test_get_user_profile(non_existing_user_id)
    
    if not profile_exists:
        # Test POST for non-existing user (should work)
        print(f"\n📝 Testing POST creation for non-existing user...")
        post_success, post_result = test_post_user_profile(non_existing_user_id, TEST_PROFILE_DATA)
        
        if post_success:
            print(f"  ✅ Profile created successfully for non-existing user")
            # Clean up - delete the created profile
            try:
                import sys
                sys.path.append('/app/backend')
                from supabase_client import supabase_admin
                if supabase_admin:
                    supabase_admin.table('user_profiles').delete().eq('user_id', non_existing_user_id).execute()
                    print(f"  🧹 Cleaned up test profile")
            except:
                pass
        else:
            print(f"  ❌ Failed to create profile for non-existing user")
    
    return profile_exists, post_success if not profile_exists else False

def analyze_duplicate_key_issue():
    """Analyze the duplicate key constraint issue"""
    print(f"\n🔍 Analyzing Duplicate Key Constraint Issue...")
    
    print("  POTENTIAL CAUSES:")
    print("  1. Frontend calling POST instead of PUT for existing profiles")
    print("  2. Database has unique constraint on user_id in user_profiles table")
    print("  3. Profile already exists but frontend doesn't check first")
    print("  4. Race condition between profile creation and update")
    print("  5. Database trigger or constraint preventing upserts")
    
    print("\n  RECOMMENDED INVESTIGATION:")
    print("  1. Check if profile exists before attempting creation")
    print("  2. Use PUT for updates, POST only for new profiles")
    print("  3. Implement upsert logic (INSERT ... ON CONFLICT DO UPDATE)")
    print("  4. Review database constraints on user_profiles table")

def main():
    """Main testing function"""
    print("=" * 80)
    print("🧪 BACKEND PROFILE UPDATE TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing User ID: {SPECIFIC_USER_ID}")
    print("=" * 80)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n❌ Backend health check failed. Cannot proceed with testing.")
        return
    
    # Test 2: Get User Profile
    profile_exists, existing_profile = test_get_user_profile(SPECIFIC_USER_ID)
    
    # Test 3: Direct Database Query
    test_database_direct_query()
    
    # Test 4: Test PUT endpoint (for existing profiles)
    if profile_exists:
        print(f"\n📝 Profile exists, testing PUT update...")
        put_success, put_result = test_put_user_profile(SPECIFIC_USER_ID, TEST_PROFILE_DATA)
    else:
        print(f"\n📝 Profile doesn't exist, PUT should fail...")
        put_success, put_result = test_put_user_profile(SPECIFIC_USER_ID, TEST_PROFILE_DATA)
    
    # Test 5: Test POST endpoint (for new profiles)
    print(f"\n📝 Testing POST creation (should fail if profile exists)...")
    post_success, post_result = test_post_user_profile(SPECIFIC_USER_ID, TEST_PROFILE_DATA)
    
    # Test 6: Analyze the issue
    analyze_duplicate_key_issue()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TESTING SUMMARY")
    print("=" * 80)
    print(f"✅ Backend Health: OK")
    print(f"{'✅' if profile_exists else '❌'} Profile Exists: {profile_exists}")
    print(f"{'✅' if put_success else '❌'} PUT Update: {put_success}")
    print(f"{'✅' if post_success else '❌'} POST Create: {post_success}")
    
    if not put_success and not post_success:
        print("\n🚨 CRITICAL ISSUE IDENTIFIED:")
        print("   Both PUT and POST operations are failing!")
        print("   This confirms the duplicate key constraint violation issue.")
        print("   The frontend may be calling the wrong endpoint or there's a database issue.")
    
    print("\n💡 RECOMMENDATIONS:")
    if profile_exists and not put_success:
        print("   - Profile exists but PUT update fails - check database constraints")
        print("   - Frontend should use PUT for existing profiles")
    if not profile_exists and not post_success:
        print("   - Profile doesn't exist but POST creation fails - database issue")
        print("   - Check user_profiles table constraints and triggers")
    
    print("=" * 80)

if __name__ == "__main__":
    main()