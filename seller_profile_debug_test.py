#!/usr/bin/env python3
"""
Seller Profile Data Loading Debug Test
Investigating why user "Kirson" profile shows "No specialties listed yet" and "No social links available"
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
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def test_backend_health():
    """Test basic backend connectivity"""
    print("🔍 Testing Backend Health...")
    
    try:
        endpoints = [
            f"{API_BASE}/",
            f"{API_BASE}/status", 
            f"{API_BASE}/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                print(f"  ✅ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {endpoint}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_supabase_direct_query():
    """Test direct Supabase queries to investigate the profile data"""
    print(f"\n🔍 Testing Direct Supabase Queries...")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("  ❌ Supabase credentials not available")
        return False
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 1. Check what user_profiles exist with display_name containing "Kirson"
        print("\n  📋 1. Searching for profiles with display_name containing 'Kirson'...")
        url = f"{SUPABASE_URL}/rest/v1/user_profiles"
        params = {'display_name': 'ilike.*Kirson*', 'select': '*'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"     Status: {response.status_code}")
        
        if response.status_code == 200:
            profiles = response.json()
            print(f"     Found {len(profiles)} profiles with 'Kirson' in display_name")
            for profile in profiles:
                print(f"       - ID: {profile.get('id')}")
                print(f"         User ID: {profile.get('user_id')}")
                print(f"         Display Name: '{profile.get('display_name')}'")
                print(f"         Specialties: {profile.get('specialties')}")
                print(f"         Social Links: {profile.get('social_links')}")
        else:
            print(f"     ❌ Query failed: {response.text}")
        
        # 2. Look for the specific user profile with user_id
        print(f"\n  📋 2. Looking for specific user profile with user_id: {SPECIFIC_USER_ID}...")
        params = {'user_id': f'eq.{SPECIFIC_USER_ID}', 'select': '*'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"     Status: {response.status_code}")
        
        if response.status_code == 200:
            profiles = response.json()
            print(f"     Found {len(profiles)} profiles for user_id {SPECIFIC_USER_ID}")
            for profile in profiles:
                print(f"       - Profile ID: {profile.get('id')}")
                print(f"         Display Name: '{profile.get('display_name')}'")
                print(f"         Bio: '{profile.get('bio')}'")
                print(f"         Specialties: {profile.get('specialties')}")
                print(f"         Social Links: {profile.get('social_links')}")
                print(f"         Seller Data: {profile.get('seller_data')}")
                print(f"         Experience: '{profile.get('experience')}'")
                print(f"         Avatar URL: '{profile.get('avatar_url')}'")
                
                # Store the profile for further testing
                target_profile = profile
        else:
            print(f"     ❌ Query failed: {response.text}")
            target_profile = None
        
        # 3. Test the ILIKE query that marketplace might be using
        print(f"\n  📋 3. Testing ILIKE query: display_name ILIKE '%Kirson%'...")
        params = {'display_name': 'ilike.%Kirson%', 'select': '*'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"     Status: {response.status_code}")
        
        if response.status_code == 200:
            profiles = response.json()
            print(f"     ILIKE query found {len(profiles)} profiles")
            for profile in profiles:
                print(f"       - Display Name: '{profile.get('display_name')}'")
                print(f"         Has Specialties: {bool(profile.get('specialties'))}")
                print(f"         Has Social Links: {bool(profile.get('social_links'))}")
        else:
            print(f"     ❌ ILIKE query failed: {response.text}")
        
        # 4. Test case-insensitive variations
        print(f"\n  📋 4. Testing case variations...")
        test_cases = ['Kirson', 'kirson', 'KIRSON', 'Kirson Krasniqi']
        
        for test_name in test_cases:
            params = {'display_name': f'ilike.%{test_name}%', 'select': 'display_name,specialties,social_links'}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                profiles = response.json()
                print(f"     '{test_name}': Found {len(profiles)} profiles")
                for profile in profiles:
                    print(f"       - '{profile.get('display_name')}' -> Specialties: {bool(profile.get('specialties'))}, Social: {bool(profile.get('social_links'))}")
            else:
                print(f"     '{test_name}': Query failed")
        
        # 5. Get all profiles to see what's actually in the database
        print(f"\n  📋 5. Getting all user profiles to see what's available...")
        params = {'select': 'user_id,display_name,specialties,social_links', 'limit': '10'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            profiles = response.json()
            print(f"     Total profiles in database (first 10):")
            for profile in profiles:
                print(f"       - '{profile.get('display_name')}' (ID: {profile.get('user_id')[:8]}...)")
                print(f"         Specialties: {profile.get('specialties')}")
                print(f"         Social Links: {profile.get('social_links')}")
        
        return target_profile
        
    except Exception as e:
        print(f"  ❌ Error with direct Supabase queries: {e}")
        return None

def test_marketplace_query_simulation(target_profile):
    """Simulate the marketplace query that might be failing"""
    print(f"\n🔍 Simulating Marketplace Query Logic...")
    
    if not target_profile:
        print("  ❌ No target profile available for simulation")
        return
    
    display_name = target_profile.get('display_name', '')
    specialties = target_profile.get('specialties')
    social_links = target_profile.get('social_links')
    
    print(f"  📋 Target Profile Analysis:")
    print(f"     Display Name: '{display_name}'")
    print(f"     Display Name Length: {len(display_name)}")
    print(f"     Display Name Type: {type(display_name)}")
    print(f"     Contains 'Kirson': {'Kirson' in display_name}")
    print(f"     Contains 'kirson': {'kirson' in display_name.lower()}")
    
    print(f"\n  📋 Specialties Analysis:")
    print(f"     Raw Value: {specialties}")
    print(f"     Type: {type(specialties)}")
    print(f"     Is None: {specialties is None}")
    print(f"     Is Empty List: {specialties == []}")
    print(f"     Boolean Value: {bool(specialties)}")
    
    print(f"\n  📋 Social Links Analysis:")
    print(f"     Raw Value: {social_links}")
    print(f"     Type: {type(social_links)}")
    print(f"     Is None: {social_links is None}")
    print(f"     Is Empty Dict: {social_links == {}}")
    print(f"     Boolean Value: {bool(social_links)}")
    
    # Test what the frontend logic might be doing
    print(f"\n  📋 Frontend Logic Simulation:")
    
    # Check if specialties would show "No specialties listed yet"
    if not specialties or (isinstance(specialties, list) and len(specialties) == 0):
        print(f"     ❌ Specialties would show: 'No specialties listed yet'")
    else:
        print(f"     ✅ Specialties would show: {specialties}")
    
    # Check if social links would show "No social links available"
    if not social_links or (isinstance(social_links, dict) and len(social_links) == 0):
        print(f"     ❌ Social Links would show: 'No social links available'")
    else:
        print(f"     ✅ Social Links would show: {social_links}")

def test_backend_profile_endpoint():
    """Test the backend profile endpoint that marketplace might be using"""
    print(f"\n🔍 Testing Backend Profile Endpoint...")
    
    try:
        # Test the auth endpoint
        url = f"{API_BASE}/auth/user/{SPECIFIC_USER_ID}"
        response = requests.get(url, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Response Structure: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                user_data = data.get('user', {})
                print(f"\n  📋 Backend Profile Data:")
                print(f"     Display Name: '{user_data.get('display_name')}'")
                print(f"     Specialties: {user_data.get('specialties')}")
                print(f"     Social Links: {user_data.get('social_links')}")
                
                return user_data
        else:
            print(f"  ❌ Backend endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Error testing backend endpoint: {e}")
    
    return None

def analyze_root_cause(supabase_profile, backend_profile):
    """Analyze the root cause of the issue"""
    print(f"\n🔍 ROOT CAUSE ANALYSIS")
    print("=" * 50)
    
    if not supabase_profile and not backend_profile:
        print("❌ CRITICAL: No profile data found anywhere!")
        return
    
    if supabase_profile and not backend_profile:
        print("❌ ISSUE: Profile exists in Supabase but backend endpoint fails")
        print("   - Check backend auth endpoint implementation")
        print("   - Verify user authentication/authorization")
        return
    
    if backend_profile and not supabase_profile:
        print("❌ ISSUE: Backend returns data but Supabase direct query fails")
        print("   - Check Supabase query syntax")
        print("   - Verify service key permissions")
        return
    
    # Both profiles exist - compare them
    print("✅ Profile data found in both Supabase and Backend")
    
    # Compare display names
    supabase_name = supabase_profile.get('display_name', '')
    backend_name = backend_profile.get('display_name', '')
    
    print(f"\n📋 Display Name Comparison:")
    print(f"   Supabase: '{supabase_name}'")
    print(f"   Backend:  '{backend_name}'")
    print(f"   Match: {supabase_name == backend_name}")
    
    # Compare specialties
    supabase_specialties = supabase_profile.get('specialties')
    backend_specialties = backend_profile.get('specialties')
    
    print(f"\n📋 Specialties Comparison:")
    print(f"   Supabase: {supabase_specialties} (Type: {type(supabase_specialties)})")
    print(f"   Backend:  {backend_specialties} (Type: {type(backend_specialties)})")
    print(f"   Match: {supabase_specialties == backend_specialties}")
    
    # Compare social links
    supabase_social = supabase_profile.get('social_links')
    backend_social = backend_profile.get('social_links')
    
    print(f"\n📋 Social Links Comparison:")
    print(f"   Supabase: {supabase_social} (Type: {type(supabase_social)})")
    print(f"   Backend:  {backend_social} (Type: {type(backend_social)})")
    print(f"   Match: {supabase_social == backend_social}")
    
    # Identify the issue
    print(f"\n🚨 ISSUE IDENTIFICATION:")
    
    if not supabase_specialties or (isinstance(supabase_specialties, list) and len(supabase_specialties) == 0):
        print("   ❌ SPECIALTIES ISSUE: Database contains empty/null specialties")
        print("      - User needs to update their profile with specialties")
        print("      - Or frontend needs to handle null/empty specialties better")
    
    if not supabase_social or (isinstance(supabase_social, dict) and len(supabase_social) == 0):
        print("   ❌ SOCIAL LINKS ISSUE: Database contains empty/null social links")
        print("      - User needs to update their profile with social links")
        print("      - Or frontend needs to handle null/empty social links better")
    
    # Check if the search would work
    if 'Kirson' in supabase_name or 'kirson' in supabase_name.lower():
        print("   ✅ SEARCH WORKING: Display name contains 'Kirson' - search should work")
    else:
        print("   ❌ SEARCH ISSUE: Display name doesn't contain 'Kirson' - search will fail")
        print(f"      - Marketplace searching for 'Kirson' but name is '{supabase_name}'")

def main():
    """Main testing function"""
    print("=" * 80)
    print("🧪 SELLER PROFILE DATA LOADING DEBUG TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Target User ID: {SPECIFIC_USER_ID}")
    print(f"Investigating: User 'Kirson' profile data loading issue")
    print("=" * 80)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n❌ Backend health check failed. Cannot proceed with testing.")
        return
    
    # Test 2: Direct Supabase Queries
    supabase_profile = test_supabase_direct_query()
    
    # Test 3: Backend Profile Endpoint
    backend_profile = test_backend_profile_endpoint()
    
    # Test 4: Marketplace Query Simulation
    if supabase_profile:
        test_marketplace_query_simulation(supabase_profile)
    
    # Test 5: Root Cause Analysis
    analyze_root_cause(supabase_profile, backend_profile)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 DEBUGGING SUMMARY")
    print("=" * 80)
    
    if supabase_profile:
        display_name = supabase_profile.get('display_name', '')
        specialties = supabase_profile.get('specialties')
        social_links = supabase_profile.get('social_links')
        
        print(f"✅ Profile Found: '{display_name}' (User ID: {SPECIFIC_USER_ID})")
        print(f"📋 Specialties: {specialties}")
        print(f"📋 Social Links: {social_links}")
        
        # Determine why marketplace shows "No specialties" and "No social links"
        if not specialties or (isinstance(specialties, list) and len(specialties) == 0):
            print(f"🚨 SPECIALTIES ISSUE: Database has empty/null specialties -> Shows 'No specialties listed yet'")
        else:
            print(f"✅ Specialties should display correctly")
            
        if not social_links or (isinstance(social_links, dict) and len(social_links) == 0):
            print(f"🚨 SOCIAL LINKS ISSUE: Database has empty/null social links -> Shows 'No social links available'")
        else:
            print(f"✅ Social links should display correctly")
    else:
        print(f"❌ No profile found for user {SPECIFIC_USER_ID}")
    
    print("=" * 80)

if __name__ == "__main__":
    main()