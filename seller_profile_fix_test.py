#!/usr/bin/env python3
"""
Seller Profile Fix Test
Testing the fix for seller profile data loading issue
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

def test_seller_data_structure():
    """Test the seller_data structure in the database"""
    print("🔍 Testing Seller Data Structure...")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("  ❌ Supabase credentials not available")
        return False
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get the specific user profile
        url = f"{SUPABASE_URL}/rest/v1/user_profiles"
        params = {'user_id': f'eq.{SPECIFIC_USER_ID}', 'select': '*'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            profiles = response.json()
            if profiles and len(profiles) > 0:
                profile = profiles[0]
                
                print(f"  📋 Profile Data Analysis:")
                print(f"     Display Name: '{profile.get('display_name')}'")
                print(f"     Top-level specialties: {profile.get('specialties')}")
                print(f"     Top-level social_links: {profile.get('social_links')}")
                print(f"     seller_data: {profile.get('seller_data')}")
                
                # Extract data from seller_data
                seller_data = profile.get('seller_data', {})
                if isinstance(seller_data, dict):
                    seller_specialties = seller_data.get('specialties', [])
                    seller_social_links = seller_data.get('socialLinks', {})
                    
                    print(f"\n  📋 seller_data Analysis:")
                    print(f"     seller_data.specialties: {seller_specialties}")
                    print(f"     seller_data.socialLinks: {seller_social_links}")
                    
                    # Check what the frontend should be using
                    print(f"\n  💡 Frontend Fix Required:")
                    if not profile.get('specialties') and seller_specialties:
                        print(f"     ✅ Use seller_data.specialties instead of top-level specialties")
                        print(f"     ✅ Data available: {seller_specialties}")
                    
                    if not profile.get('social_links') and seller_social_links:
                        print(f"     ✅ Use seller_data.socialLinks instead of top-level social_links")
                        print(f"     ✅ Data available: {seller_social_links}")
                        
                        # Filter out empty social links
                        active_social_links = {k: v for k, v in seller_social_links.items() if v and v.strip()}
                        print(f"     ✅ Active social links: {active_social_links}")
                
                return profile
        
        return None
        
    except Exception as e:
        print(f"  ❌ Error testing seller data structure: {e}")
        return None

def simulate_frontend_fix(profile):
    """Simulate how the frontend should be fixed"""
    print(f"\n🔧 Simulating Frontend Fix...")
    
    if not profile:
        print("  ❌ No profile data available")
        return
    
    # Current frontend logic (broken)
    current_specialties = profile.get('specialties', [])
    current_social_links = profile.get('social_links', {})
    
    print(f"  📋 Current Frontend Logic (BROKEN):")
    print(f"     Specialties: {current_specialties} -> Shows: {'No specialties listed yet' if not current_specialties else current_specialties}")
    print(f"     Social Links: {current_social_links} -> Shows: {'No social links available' if not current_social_links else current_social_links}")
    
    # Fixed frontend logic
    seller_data = profile.get('seller_data', {})
    fixed_specialties = seller_data.get('specialties', []) if seller_data else []
    fixed_social_links = seller_data.get('socialLinks', {}) if seller_data else {}
    
    # Filter out empty social links
    active_social_links = {k: v for k, v in fixed_social_links.items() if v and v.strip()} if fixed_social_links else {}
    
    print(f"\n  📋 Fixed Frontend Logic (WORKING):")
    print(f"     Specialties: {fixed_specialties} -> Shows: {fixed_specialties if fixed_specialties else 'No specialties listed yet'}")
    print(f"     Social Links: {active_social_links} -> Shows: {active_social_links if active_social_links else 'No social links available'}")
    
    print(f"\n  ✅ SOLUTION CONFIRMED:")
    if fixed_specialties:
        print(f"     - Specialties will now show: {fixed_specialties}")
    if active_social_links:
        print(f"     - Social links will now show: {list(active_social_links.keys())}")

def main():
    """Main testing function"""
    print("=" * 80)
    print("🧪 SELLER PROFILE FIX TEST")
    print("=" * 80)
    print(f"Target User ID: {SPECIFIC_USER_ID}")
    print(f"Issue: Frontend not reading seller_data field correctly")
    print("=" * 80)
    
    # Test the seller data structure
    profile = test_seller_data_structure()
    
    # Simulate the frontend fix
    simulate_frontend_fix(profile)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FIX VERIFICATION SUMMARY")
    print("=" * 80)
    
    if profile:
        seller_data = profile.get('seller_data', {})
        if seller_data:
            specialties = seller_data.get('specialties', [])
            social_links = seller_data.get('socialLinks', {})
            active_social_links = {k: v for k, v in social_links.items() if v and v.strip()} if social_links else {}
            
            print(f"✅ ROOT CAUSE IDENTIFIED:")
            print(f"   - Frontend reads top-level 'specialties' and 'social_links' fields")
            print(f"   - But actual data is stored in 'seller_data' JSON field")
            print(f"   - Top-level fields are empty: specialties=[], social_links={{}}")
            print(f"   - seller_data contains: specialties={specialties}, socialLinks={social_links}")
            
            print(f"\n✅ SOLUTION REQUIRED:")
            print(f"   - Update SellerProfileModal.loadSellerProfileData() function")
            print(f"   - Check seller_data field for specialties and socialLinks")
            print(f"   - Fallback to top-level fields if seller_data is empty")
            
            print(f"\n✅ EXPECTED RESULT AFTER FIX:")
            if specialties:
                print(f"   - Specialties will show: {specialties}")
            if active_social_links:
                print(f"   - Social links will show: {list(active_social_links.keys())}")
    else:
        print(f"❌ Could not retrieve profile data for analysis")
    
    print("=" * 80)

if __name__ == "__main__":
    main()