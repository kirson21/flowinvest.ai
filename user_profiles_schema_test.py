#!/usr/bin/env python3
"""
User Profiles Schema Investigation Test
Investigating the user_profiles table schema to understand what columns exist
and are available for storing user data like specialties and social links.

Focus on user_id: cd0e9717-f85d-4726-81e9-f260394ead58
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Add backend to path for direct database access
sys.path.append('/app/backend')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
TARGET_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"

def test_backend_health():
    """Test basic backend connectivity"""
    print("🔍 Testing Backend Health...")
    
    try:
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

def investigate_user_profile_via_api(user_id):
    """Investigate user profile through API endpoint"""
    print(f"\n🔍 Investigating User Profile via API for {user_id}...")
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}"
        response = requests.get(url, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ User profile found via API")
                user_data = data.get('user', {})
                
                print(f"\n  📊 CURRENT PROFILE STRUCTURE:")
                for key, value in user_data.items():
                    print(f"     {key}: {value} ({type(value).__name__})")
                
                # Check for specific fields we're looking for
                target_fields = ['social_links', 'specialties', 'seller_data', 'experience', 
                               'bio', 'display_name', 'avatar_url', 'seller_verification_status']
                
                print(f"\n  🎯 TARGET FIELDS ANALYSIS:")
                for field in target_fields:
                    if field in user_data:
                        print(f"     ✅ {field}: EXISTS - {user_data[field]}")
                    else:
                        print(f"     ❌ {field}: NOT FOUND")
                
                return True, user_data
            else:
                print(f"  ❌ User not found: {data.get('message')}")
                return False, None
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            print(f"     Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"  ❌ Error investigating user profile via API: {e}")
        return False, None

def investigate_user_profile_direct_db(user_id):
    """Investigate user profile through direct database access"""
    print(f"\n🔍 Investigating User Profile via Direct Database Access for {user_id}...")
    
    try:
        from supabase_client import supabase_admin
        
        if not supabase_admin:
            print("  ❌ Supabase admin client not available")
            return False, None
        
        # Query user_profiles table
        print("  Querying user_profiles table...")
        response = supabase_admin.table('user_profiles').select('*').eq('user_id', user_id).execute()
        
        print(f"  Status Code: {response.status_code}")
        
        if response.data and len(response.data) > 0:
            print(f"  ✅ Found {len(response.data)} profile(s) for user {user_id}")
            
            profile = response.data[0]
            print(f"\n  📊 COMPLETE DATABASE PROFILE STRUCTURE:")
            for key, value in profile.items():
                print(f"     {key}: {value} ({type(value).__name__})")
            
            return True, profile
        else:
            print(f"  ❌ No profiles found for user {user_id}")
            return False, None
        
    except Exception as e:
        print(f"  ❌ Error with direct database access: {e}")
        return False, None

def test_profile_update_with_new_fields(user_id):
    """Test updating profile with fields like specialties and social_links"""
    print(f"\n🔍 Testing Profile Update with New Fields for {user_id}...")
    
    # Test data with fields we want to store
    test_data = {
        "display_name": "Super Admin Test",
        "bio": "Testing profile schema investigation",
        "specialties": ["Trading", "AI", "Blockchain"],
        "social_links": {
            "twitter": "https://twitter.com/test",
            "linkedin": "https://linkedin.com/in/test",
            "github": "https://github.com/test"
        },
        "seller_data": {
            "rating": 4.8,
            "total_sales": 150,
            "verified": True
        },
        "experience": "5+ years in trading and AI development"
    }
    
    try:
        url = f"{API_BASE}/auth/user/{user_id}/profile"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.put(url, json=test_data, headers=headers, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ Profile updated successfully with new fields")
                updated_profile = data.get('user', {})
                
                print(f"\n  📊 UPDATED PROFILE STRUCTURE:")
                for key, value in updated_profile.items():
                    print(f"     {key}: {value}")
                
                return True, updated_profile
            else:
                print(f"  ❌ Update failed: {data.get('message')}")
                return False, data
        else:
            print(f"  ❌ Request failed with status {response.status_code}")
            return False, response.text
            
    except Exception as e:
        print(f"  ❌ Error testing profile update: {e}")
        return False, str(e)

def investigate_related_tables():
    """Investigate if there are separate tables for additional profile data"""
    print(f"\n🔍 Investigating Related Tables for Profile Data...")
    
    try:
        from supabase_client import supabase_admin
        
        if not supabase_admin:
            print("  ❌ Supabase admin client not available")
            return False
        
        # List of potential related tables
        potential_tables = [
            'user_social_links',
            'user_specialties', 
            'seller_profiles',
            'user_seller_data',
            'user_experience',
            'user_skills',
            'user_metadata',
            'profiles_extended'
        ]
        
        print("  🔍 Checking for related tables...")
        
        for table_name in potential_tables:
            try:
                response = supabase_admin.table(table_name).select('*').limit(1).execute()
                if response.status_code == 200:
                    print(f"     ✅ {table_name}: EXISTS")
                    if response.data:
                        print(f"        Sample structure: {list(response.data[0].keys()) if response.data else 'No data'}")
                else:
                    print(f"     ❌ {table_name}: NOT FOUND (Status: {response.status_code})")
            except Exception as e:
                print(f"     ❌ {table_name}: ERROR - {str(e)}")
        
        # Check for user-specific data in existing tables
        print(f"\n  🔍 Checking existing tables for user {TARGET_USER_ID}...")
        
        existing_tables = ['user_profiles', 'seller_verification_applications', 'user_notifications', 'user_accounts']
        
        for table_name in existing_tables:
            try:
                response = supabase_admin.table(table_name).select('*').eq('user_id', TARGET_USER_ID).execute()
                if response.status_code == 200 and response.data:
                    print(f"     ✅ {table_name}: Found {len(response.data)} record(s)")
                    if response.data:
                        print(f"        Structure: {list(response.data[0].keys())}")
                else:
                    print(f"     ❌ {table_name}: No records found")
            except Exception as e:
                print(f"     ❌ {table_name}: ERROR - {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error investigating related tables: {e}")
        return False

def test_json_field_storage():
    """Test if user_profiles supports JSON fields for complex data"""
    print(f"\n🔍 Testing JSON Field Storage Capabilities...")
    
    try:
        from supabase_client import supabase_admin
        
        if not supabase_admin:
            print("  ❌ Supabase admin client not available")
            return False
        
        # Test with JSON data
        json_test_data = {
            "display_name": "JSON Test User",
            "metadata": {
                "specialties": ["AI", "Trading", "Blockchain"],
                "social_links": {
                    "twitter": "https://twitter.com/test",
                    "linkedin": "https://linkedin.com/in/test"
                },
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }
        
        # Try to update with JSON data
        response = supabase_admin.table('user_profiles').update(json_test_data).eq('user_id', TARGET_USER_ID).execute()
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200 and response.data:
            print(f"  ✅ JSON field storage successful")
            updated_profile = response.data[0]
            
            print(f"  📊 JSON FIELD RESULT:")
            for key, value in updated_profile.items():
                if key == 'metadata':
                    print(f"     {key}: {value} (JSON)")
                else:
                    print(f"     {key}: {value}")
            
            return True, updated_profile
        else:
            print(f"  ❌ JSON field storage failed")
            return False, None
            
    except Exception as e:
        print(f"  ❌ Error testing JSON field storage: {e}")
        return False, None

def analyze_schema_findings():
    """Analyze findings and provide recommendations"""
    print(f"\n📊 SCHEMA ANALYSIS & RECOMMENDATIONS")
    print("=" * 60)
    
    print("🎯 INVESTIGATION GOALS:")
    print("   - Understand user_profiles table structure")
    print("   - Find fields for specialties and social links")
    print("   - Test data storage capabilities")
    print("   - Identify best approach for marketplace display")
    
    print("\n💡 RECOMMENDATIONS BASED ON FINDINGS:")
    print("   1. If user_profiles supports JSON fields:")
    print("      - Store specialties and social_links as JSON columns")
    print("      - Use metadata field for complex nested data")
    print("   2. If separate tables exist:")
    print("      - Use dedicated tables for normalized data")
    print("   3. If schema needs extension:")
    print("      - Add new columns to user_profiles table")
    print("      - Consider JSONB for PostgreSQL efficiency")

def main():
    """Main investigation function"""
    print("=" * 80)
    print("🔍 USER PROFILES SCHEMA INVESTIGATION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Target User ID: {TARGET_USER_ID}")
    print("=" * 80)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n❌ Backend health check failed. Cannot proceed with investigation.")
        return
    
    # Test 2: Investigate via API
    api_success, api_profile = investigate_user_profile_via_api(TARGET_USER_ID)
    
    # Test 3: Investigate via Direct Database
    db_success, db_profile = investigate_user_profile_direct_db(TARGET_USER_ID)
    
    # Test 4: Test Profile Update with New Fields
    if api_success or db_success:
        update_success, updated_profile = test_profile_update_with_new_fields(TARGET_USER_ID)
    
    # Test 5: Investigate Related Tables
    investigate_related_tables()
    
    # Test 6: Test JSON Field Storage
    json_result = test_json_field_storage()
    if isinstance(json_result, tuple):
        json_success, json_profile = json_result
    else:
        json_success = json_result
        json_profile = None
    
    # Test 7: Analysis and Recommendations
    analyze_schema_findings()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 INVESTIGATION SUMMARY")
    print("=" * 80)
    print(f"✅ Backend Health: OK")
    print(f"{'✅' if api_success else '❌'} API Profile Access: {api_success}")
    print(f"{'✅' if db_success else '❌'} Direct DB Access: {db_success}")
    print(f"{'✅' if json_success else '❌'} JSON Field Support: {json_success}")
    
    print("\n🔍 KEY FINDINGS:")
    if api_profile:
        print(f"   📋 Current Profile Fields: {list(api_profile.keys())}")
    
    if db_profile:
        print(f"   🗄️  Database Profile Fields: {list(db_profile.keys())}")
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Review the complete field structure above")
    print("   2. Determine best storage approach for specialties/social_links")
    print("   3. Update frontend to use available fields")
    print("   4. Consider schema extensions if needed")
    
    print("=" * 80)

if __name__ == "__main__":
    main()