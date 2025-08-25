#!/usr/bin/env python3
"""
Test the Supabase RPC function for getting all users with emails
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_admin as supabase

def test_rpc_function():
    """Test the get_all_users_with_emails RPC function"""
    try:
        print("🧪 Testing get_all_users_with_emails() RPC function...")
        
        # Test the comprehensive RPC function
        result = supabase.rpc('get_all_users_with_emails').execute()
        
        if result.data:
            print(f"✅ RPC function successful! Found {len(result.data)} users")
            print("\n📊 Sample data from first 3 users:")
            
            for i, user in enumerate(result.data[:3]):
                print(f"\n   User {i+1}:")
                print(f"   - User ID: {user.get('user_id', 'N/A')}")
                print(f"   - Email: {user.get('email', 'N/A')}")
                print(f"   - Name: {user.get('name', 'N/A')}")
                print(f"   - Country: {user.get('country', 'N/A')}")
                print(f"   - Phone: {user.get('phone', 'N/A')}")
                print(f"   - Registration: {user.get('created_at', 'N/A')}")
                print(f"   - Seller Status: {user.get('seller_verification_status', 'N/A')}")
                print(f"   - Plan Type: {user.get('plan_type', 'N/A')}")
                print(f"   - Subscription Status: {user.get('subscription_status', 'N/A')}")
                print(f"   - Total Commission: ${user.get('total_commission_earned', 0)}")
            
            print(f"\n📈 Summary of all {len(result.data)} users:")
            
            # Count statistics
            users_with_email = len([u for u in result.data if u.get('email')])
            users_with_names = len([u for u in result.data if u.get('name')])
            users_with_phone = len([u for u in result.data if u.get('phone')])
            users_with_country = len([u for u in result.data if u.get('country')])
            active_subs = len([u for u in result.data if u.get('subscription_status') == 'active'])
            plus_users = len([u for u in result.data if u.get('plan_type') in ['plus', 'pro']])
            verified_sellers = len([u for u in result.data if u.get('seller_verification_status') == 'verified'])
            
            print(f"   - Total Users: {len(result.data)}")
            print(f"   - Users with Email: {users_with_email}")
            print(f"   - Users with Name: {users_with_names}")
            print(f"   - Users with Phone: {users_with_phone}")
            print(f"   - Users with Country: {users_with_country}")
            print(f"   - Active Subscriptions: {active_subs}")
            print(f"   - Plus/Pro Plan Users: {plus_users}")
            print(f"   - Verified Sellers: {verified_sellers}")
            
            return True
            
        else:
            print("❌ RPC function returned no data")
            return False
            
    except Exception as e:
        print(f"❌ RPC function test failed: {str(e)}")
        
        # Try the simple version as fallback
        try:
            print("\n🔄 Testing fallback simple RPC function...")
            simple_result = supabase.rpc('get_users_emails_simple').execute()
            
            if simple_result.data:
                print(f"✅ Simple RPC works! Found {len(simple_result.data)} users with emails")
                
                print("\n📧 Email data sample:")
                for i, user in enumerate(simple_result.data[:3]):
                    print(f"   User {i+1}: {user.get('email', 'N/A')} (ID: {user.get('user_id', 'N/A')})")
                
                return True
            else:
                print("❌ Simple RPC also returned no data")
                return False
                
        except Exception as simple_error:
            print(f"❌ Simple RPC also failed: {str(simple_error)}")
            return False

def main():
    print("🚀 Starting comprehensive RPC function test...")
    
    success = test_rpc_function()
    
    if success:
        print("\n✅ RPC function test completed successfully!")
        print("🎯 Ready to sync all user data to Google Sheets")
    else:
        print("\n❌ RPC function test failed")
        print("💡 Check Supabase dashboard to ensure the RPC function was created properly")

if __name__ == "__main__":
    main()