#!/usr/bin/env python3
"""
Test direct access to auth.users table for emails
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_admin as supabase

def test_auth_users_access():
    """Test direct access to auth.users table"""
    try:
        print("🧪 Testing direct access to auth.users table...")
        
        # Try to access auth.users directly
        result = supabase.table('auth.users').select('id, email, created_at').execute()
        
        if result.data:
            print(f"✅ Successfully accessed auth.users! Found {len(result.data)} users")
            
            print("\n📧 Email data from auth.users:")
            for i, user in enumerate(result.data):
                print(f"   User {i+1}: {user.get('email', 'N/A')} (ID: {user.get('id', 'N/A')[:8]}...)")
            
            return result.data, True
        else:
            print("❌ No data found in auth.users")
            return [], False
            
    except Exception as e:
        print(f"❌ Direct auth.users access failed: {str(e)}")
        return [], False

def create_comprehensive_user_data():
    """Create comprehensive user data by manually joining tables"""
    try:
        print("\n🔄 Creating comprehensive user data by manual joins...")
        
        # Get auth.users data
        auth_users, auth_success = test_auth_users_access()
        
        if not auth_success:
            print("❌ Cannot proceed without auth.users data")
            return []
        
        # Get other data
        profiles = supabase.table('user_profiles').select('*').execute()
        subscriptions = supabase.table('subscriptions').select('*').execute()
        
        profiles_data = profiles.data if profiles.data else []
        subscriptions_data = subscriptions.data if subscriptions.data else []
        
        print(f"📊 Found {len(profiles_data)} profiles and {len(subscriptions_data)} subscriptions")
        
        # Manual join
        comprehensive_users = []
        
        for auth_user in auth_users:
            user_id = auth_user.get('id')
            email = auth_user.get('email')
            created_at = auth_user.get('created_at')
            
            # Find matching profile and subscription
            profile = next((p for p in profiles_data if p.get('user_id') == user_id), {})
            subscription = next((s for s in subscriptions_data if s.get('user_id') == user_id), {})
            
            comprehensive_user = {
                'user_id': user_id,
                'email': email,  # This is the key - emails from auth.users!
                'created_at': created_at,
                'name': profile.get('name', ''),
                'country': profile.get('country', ''),
                'phone': profile.get('phone', ''),
                'seller_verification_status': profile.get('seller_verification_status', 'not_verified'),
                'plan_type': subscription.get('plan_type', 'free'),
                'subscription_status': subscription.get('status', 'inactive'),
                'subscription_end_date': subscription.get('end_date', ''),
                'total_commission_earned': 0
            }
            
            comprehensive_users.append(comprehensive_user)
        
        # Sort by created_at (newest first)
        comprehensive_users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        print(f"✅ Created comprehensive data for {len(comprehensive_users)} users")
        
        # Summary
        users_with_email = len([u for u in comprehensive_users if u.get('email')])
        users_with_names = len([u for u in comprehensive_users if u.get('name')])
        
        print(f"\n📊 COMPREHENSIVE SUMMARY OF {len(comprehensive_users)} USERS:")
        print(f"   - Users with Email: {users_with_email} (should be ALL users now!)")
        print(f"   - Users with Name: {users_with_names}")
        
        print(f"\n👥 Sample comprehensive user data (first 3 users):")
        for i, user in enumerate(comprehensive_users[:3]):
            print(f"\n   User {i+1}:")
            print(f"   - ID: {user.get('user_id', 'N/A')[:8]}...")
            print(f"   - Email: {user.get('email', 'N/A')} ← FROM AUTH.USERS!")
            print(f"   - Name: {user.get('name', 'N/A')}")
            print(f"   - Registration: {user.get('created_at', 'N/A')}")
            print(f"   - Plan Type: {user.get('plan_type', 'N/A')}")
            print(f"   - Subscription Status: {user.get('subscription_status', 'N/A')}")
        
        return comprehensive_users
        
    except Exception as e:
        print(f"❌ Comprehensive data creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("🚀 Testing comprehensive user data collection with auth.users emails...")
    
    comprehensive_data = create_comprehensive_user_data()
    
    if comprehensive_data:
        print(f"\n✅ SUCCESS! Created comprehensive data for {len(comprehensive_data)} users")
        print("🎯 This data includes ALL user emails from auth.users table!")
        print("🎉 Ready to sync complete user data to Google Sheets")
        
        # Show the difference
        emails_count = len([u for u in comprehensive_data if u.get('email')])
        print(f"\n📧 Email coverage: {emails_count}/{len(comprehensive_data)} users have emails")
        
        return True
    else:
        print("\n❌ Failed to create comprehensive user data")
        return False

if __name__ == "__main__":
    main()