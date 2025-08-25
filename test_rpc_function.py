#!/usr/bin/env python3
"""
Test RPC Function
Test the RPC function to get user emails from auth.users table
"""

import sys
import os
sys.path.append('/app/backend')

def load_env():
    try:
        with open('/app/backend/.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except Exception as e:
        print(f"Could not load .env: {e}")

load_env()

from supabase_client import supabase_admin as supabase

print('🧪 Testing RPC Functions for User Emails')
print('=' * 60)

# Test 1: Simple RPC function
print('\n🔍 Test 1: get_users_emails_simple()')
try:
    result = supabase.rpc('get_users_emails_simple').execute()
    
    if result.data:
        print(f'✅ SUCCESS! Found {len(result.data)} users with emails')
        print('📧 User Emails:')
        for i, user in enumerate(result.data, 1):
            print(f'   {i}. {user.get("user_id", "unknown")[:8]}... - {user.get("email", "no_email")}')
    else:
        print('⚠️ Function executed but returned no data')
        
except Exception as e:
    print(f'❌ FAILED: {e}')
    print('💡 Make sure you have created the RPC function in Supabase dashboard')

# Test 2: Complex RPC function  
print('\n🔍 Test 2: get_all_users_with_emails()')
try:
    result = supabase.rpc('get_all_users_with_emails').execute()
    
    if result.data:
        print(f'✅ SUCCESS! Found {len(result.data)} users with complete data')
        print('👥 User Data Sample:')
        for i, user in enumerate(result.data[:3], 1):
            print(f'   {i}. ID: {user.get("user_id", "unknown")[:8]}...')
            print(f'      Email: {user.get("email", "no_email")}')
            print(f'      Name: {user.get("name", "no_name") or "No Name"}')
            print(f'      Plan: {user.get("plan_type", "free")}')
            print(f'      Status: {user.get("subscription_status", "inactive")}')
            print()
            
        # Summary stats
        users_with_email = len([u for u in result.data if u.get('email')])
        users_with_names = len([u for u in result.data if u.get('name')])
        active_subs = len([u for u in result.data if u.get('subscription_status') == 'active'])
        
        print(f'📊 SUMMARY:')
        print(f'   Total Users: {len(result.data)}')
        print(f'   With Emails: {users_with_email}')
        print(f'   With Names: {users_with_names}')
        print(f'   Active Subscriptions: {active_subs}')
        
    else:
        print('⚠️ Function executed but returned no data')
        
except Exception as e:
    print(f'❌ FAILED: {e}')
    print('💡 Make sure you have created the RPC function in Supabase dashboard')

print('\n' + '=' * 60)
print('📋 NEXT STEPS:')
print('1. If tests failed: Create the RPC function in Supabase dashboard using the SQL provided')
print('2. If tests passed: The Google Sheets sync will now get ALL user emails!')
print('3. Deploy to Render with your new Google credentials')
print('4. Automated sync will include all user emails from auth.users table')

print('\n✅ RPC function testing complete!')