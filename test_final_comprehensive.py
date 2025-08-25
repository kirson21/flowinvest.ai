#!/usr/bin/env python3
"""
Test the simple RPC function that the user successfully created
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_admin as supabase

def test_simple_rpc():
    """Test the simple get_users_emails_simple RPC function"""
    try:
        print("🧪 Testing get_users_emails_simple() RPC function...")
        
        result = supabase.rpc('get_users_emails_simple').execute()
        
        if result.data:
            print(f"✅ Simple RPC works! Found {len(result.data)} users with emails")
            
            print("\n📧 Email data from auth.users:")
            for i, user in enumerate(result.data):
                print(f"   User {i+1}: {user.get('email', 'N/A')} (ID: {str(user.get('user_id', 'N/A'))[:8]}...)")
            
            print(f"\n🎉 SUCCESS! We now have access to all {len(result.data)} user emails!")
            return result.data, True
            
        else:
            print("❌ Simple RPC returned no data")
            return [], False
            
    except Exception as e:
        print(f"❌ Simple RPC function test failed: {str(e)}")
        return [], False

def create_final_comprehensive_data():
    """Create the final comprehensive user data using the working simple RPC"""
    try:
        print("\n🔄 Creating final comprehensive user data...")
        
        # Get emails from the working simple RPC
        emails_data, success = test_simple_rpc()
        
        if not success:
            print("❌ Cannot proceed without email data")
            return []
        
        # Get additional data from other tables
        profiles = supabase.table('user_profiles').select('*').execute()
        subscriptions = supabase.table('subscriptions').select('*').execute()
        
        profiles_data = profiles.data if profiles.data else []
        subscriptions_data = subscriptions.data if subscriptions.data else []
        
        print(f"📊 Combining {len(emails_data)} emails with {len(profiles_data)} profiles and {len(subscriptions_data)} subscriptions")
        
        # Create comprehensive user data
        comprehensive_users = []
        
        for email_user in emails_data:
            user_id = email_user.get('user_id')
            email = email_user.get('email')
            created_at = email_user.get('created_at')
            
            # Find matching profile and subscription
            profile = next((p for p in profiles_data if p.get('user_id') == user_id), {})
            subscription = next((s for s in subscriptions_data if s.get('user_id') == user_id), {})
            
            comprehensive_user = {
                'user_id': user_id,
                'name': profile.get('name', ''),
                'email': email,  # NOW WE HAVE ALL EMAILS!
                'country': profile.get('country', ''),
                'phone': profile.get('phone', ''),
                'registration_date': created_at,
                'seller_verification_status': profile.get('seller_verification_status', 'not_verified'),
                'plan_type': subscription.get('plan_type', 'free'),
                'subscription_status': subscription.get('status', 'inactive'),
                'subscription_end_date': subscription.get('end_date', ''),
                'total_commission_earned': 0
            }
            
            comprehensive_users.append(comprehensive_user)
        
        # Sort by registration date (newest first)
        comprehensive_users.sort(key=lambda x: x.get('registration_date', ''), reverse=True)
        
        print(f"✅ Created comprehensive data for {len(comprehensive_users)} users")
        
        # Summary
        users_with_email = len([u for u in comprehensive_users if u.get('email')])
        users_with_names = len([u for u in comprehensive_users if u.get('name')])
        users_with_phone = len([u for u in comprehensive_users if u.get('phone')])
        users_with_country = len([u for u in comprehensive_users if u.get('country')])
        active_subs = len([u for u in comprehensive_users if u.get('subscription_status') == 'active'])
        plus_users = len([u for u in comprehensive_users if u.get('plan_type') in ['plus', 'pro']])
        verified_sellers = len([u for u in comprehensive_users if u.get('seller_verification_status') == 'verified'])
        
        print(f"\n📊 FINAL COMPREHENSIVE SUMMARY OF {len(comprehensive_users)} USERS:")
        print(f"   - Users with Email: {users_with_email} (should be ALL users now!) ✅")
        print(f"   - Users with Name: {users_with_names}")
        print(f"   - Users with Phone: {users_with_phone}")
        print(f"   - Users with Country: {users_with_country}")
        print(f"   - Active Subscriptions: {active_subs}")
        print(f"   - Plus/Pro Plan Users: {plus_users}")
        print(f"   - Verified Sellers: {verified_sellers}")
        
        print(f"\n👥 Sample final user data (first 3 users):")
        for i, user in enumerate(comprehensive_users[:3]):
            print(f"\n   User {i+1}:")
            print(f"   - ID: {str(user.get('user_id', 'N/A'))[:8]}...")
            print(f"   - Email: {user.get('email', 'N/A')} ← COMPLETE EMAIL DATA! ✅")
            print(f"   - Name: {user.get('name', 'N/A')}")
            print(f"   - Country: {user.get('country', 'N/A')}")
            print(f"   - Registration: {user.get('registration_date', 'N/A')}")
            print(f"   - Plan Type: {user.get('plan_type', 'N/A')}")
            print(f"   - Subscription Status: {user.get('subscription_status', 'N/A')}")
        
        return comprehensive_users
        
    except Exception as e:
        print(f"❌ Final comprehensive data creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("🚀 Testing comprehensive user data with ALL emails from auth.users...")
    
    comprehensive_data = create_final_comprehensive_data()
    
    if comprehensive_data:
        print(f"\n🎉 COMPLETE SUCCESS! Created final comprehensive data for {len(comprehensive_data)} users")
        print("✅ This data includes ALL user emails from auth.users table!")
        print("📊 Ready to sync complete user data to Google Sheets")
        
        return comprehensive_data
    else:
        print("\n❌ Failed to create final comprehensive user data")
        return []

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n🎯 READY FOR GOOGLE SHEETS SYNC: {len(result)} users with complete data!")