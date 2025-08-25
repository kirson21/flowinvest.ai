#!/usr/bin/env python3
"""
Test Google Sheets sync using manual fallback methods
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_admin as supabase

def test_manual_sync():
    """Test manual data collection for Google Sheets sync"""
    try:
        print("🧪 Testing manual data collection for Google Sheets sync...")
        
        # Get data from individual tables (same as the fallback method)
        print("📊 Getting data from user_profiles...")
        profiles = supabase.table('user_profiles').select('*').execute()
        
        print("📊 Getting data from subscriptions...")
        subscriptions = supabase.table('subscriptions').select('*').execute()
        
        print("📊 Getting data from subscription_email_validation...")
        email_validations = supabase.table('subscription_email_validation').select('user_id, email').execute()
        
        profiles_data = profiles.data if profiles.data else []
        subscriptions_data = subscriptions.data if subscriptions.data else []
        email_validations_data = email_validations.data if email_validations.data else []
        
        print(f"✅ Found {len(profiles_data)} profiles")
        print(f"✅ Found {len(subscriptions_data)} subscriptions")
        print(f"✅ Found {len(email_validations_data)} email validations")
        
        # Collect all unique user IDs
        all_user_ids = set()
        for profile in profiles_data:
            all_user_ids.add(profile.get('user_id'))
        for subscription in subscriptions_data:
            all_user_ids.add(subscription.get('user_id'))
        for email_val in email_validations_data:
            all_user_ids.add(email_val.get('user_id'))
        
        users_data = []
        
        print(f"📊 Processing {len(all_user_ids)} unique users...")
        
        for user_id in all_user_ids:
            if not user_id:
                continue
            
            profile = next((p for p in profiles_data if p.get('user_id') == user_id), {})
            subscription = next((s for s in subscriptions_data if s.get('user_id') == user_id), {})
            email_validation = next((e for e in email_validations_data if e.get('user_id') == user_id), {})
            
            # Get best available email (from email validation table)
            email = email_validation.get('email', '')
            
            user_data = {
                'user_id': user_id,
                'name': profile.get('name', ''),
                'email': email,
                'country': profile.get('country', ''),
                'phone': profile.get('phone', ''),
                'registration_date': profile.get('created_at', '') or subscription.get('created_at', ''),
                'seller_verification_status': profile.get('seller_verification_status', 'not_verified'),
                'plan_type': subscription.get('plan_type', 'free'),
                'subscription_status': subscription.get('status', 'inactive'),
                'subscription_end_date': subscription.get('end_date', ''),
                'total_commission_earned': 0
            }
            
            users_data.append(user_data)
        
        # Sort by registration date (newest first)
        users_data.sort(key=lambda x: x.get('registration_date', ''), reverse=True)
        
        print(f"✅ Successfully collected data for {len(users_data)} users")
        
        # Print detailed summary
        users_with_email = len([u for u in users_data if u.get('email')])
        users_with_names = len([u for u in users_data if u.get('name')])
        users_with_phone = len([u for u in users_data if u.get('phone')])
        users_with_country = len([u for u in users_data if u.get('country')])
        active_subs = len([u for u in users_data if u.get('subscription_status') == 'active'])
        plus_users = len([u for u in users_data if u.get('plan_type') in ['plus', 'pro']])
        verified_sellers = len([u for u in users_data if u.get('seller_verification_status') == 'verified'])
        
        print(f"\n📊 DETAILED SUMMARY OF {len(users_data)} USERS:")
        print(f"   - Users with Email: {users_with_email}")
        print(f"   - Users with Name: {users_with_names}")
        print(f"   - Users with Phone: {users_with_phone}")
        print(f"   - Users with Country: {users_with_country}")
        print(f"   - Active Subscriptions: {active_subs}")
        print(f"   - Plus/Pro Plan Users: {plus_users}")
        print(f"   - Verified Sellers: {verified_sellers}")
        
        print(f"\n👥 Sample user data (first 3 users):")
        for i, user in enumerate(users_data[:3]):
            print(f"\n   User {i+1}:")
            print(f"   - ID: {user.get('user_id', 'N/A')}")
            print(f"   - Name: {user.get('name', 'N/A')}")
            print(f"   - Email: {user.get('email', 'N/A')}")
            print(f"   - Country: {user.get('country', 'N/A')}")
            print(f"   - Phone: {user.get('phone', 'N/A')}")
            print(f"   - Registration: {user.get('registration_date', 'N/A')}")
            print(f"   - Seller Status: {user.get('seller_verification_status', 'N/A')}")
            print(f"   - Plan Type: {user.get('plan_type', 'N/A')}")
            print(f"   - Subscription Status: {user.get('subscription_status', 'N/A')}")
        
        return users_data, True
        
    except Exception as e:
        print(f"❌ Manual data collection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return [], False

def main():
    print("🚀 Starting manual data collection test for Google Sheets sync...")
    
    users_data, success = test_manual_sync()
    
    if success:
        print("\n✅ Manual data collection completed successfully!")
        print(f"🎯 Ready to sync {len(users_data)} users to Google Sheets")
        
        # Show what would be synced to Google Sheets
        print("\n📋 Data ready for Google Sheets:")
        print("   Headers: User ID, Name, Email, Country, Phone, Registration Date, Seller Status, Subscription Status, Plan Type, Subscription End Date, Total Commission Earned")
        print(f"   Rows: {len(users_data)} user records")
        
    else:
        print("\n❌ Manual data collection failed")

if __name__ == "__main__":
    main()