#!/usr/bin/env python3
"""
Show Users Data for Google Sheets
Display exactly what will be synced to Google Sheets
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

print('🔄 GOOGLE SHEETS USER DATA SYNC PREVIEW')
print('=' * 80)

# Get all data
email_validations = supabase.table('subscription_email_validation').select('*').execute()
subscriptions = supabase.table('subscriptions').select('*').execute()
profiles = supabase.table('user_profiles').select('*').execute()
accounts = supabase.table('user_accounts').select('*').execute()

print(f'📊 Data Sources:')
print(f'   Email validations: {len(email_validations.data)}')
print(f'   Subscriptions: {len(subscriptions.data)}')
print(f'   User profiles: {len(profiles.data)}')
print(f'   User accounts: {len(accounts.data)}')

# Collect all unique user IDs
all_user_ids = set()

for ev in email_validations.data:
    all_user_ids.add(ev.get('user_id'))

for sub in subscriptions.data:
    all_user_ids.add(sub.get('user_id'))

for profile in profiles.data:
    all_user_ids.add(profile.get('user_id'))

for account in accounts.data:
    all_user_ids.add(account.get('user_id'))

print(f'\\n👥 Total unique users: {len(all_user_ids)}')

# Process each user
print(f'\\n📋 USER DATA FOR GOOGLE SHEETS:')
print('-' * 80)

headers = ['#', 'User ID', 'Name', 'Email', 'Country', 'Phone', 'Plan', 'Status']
print(f"{'#':>3} {'User ID':>10} {'Name':>15} {'Email':>25} {'Country':>10} {'Phone':>15} {'Plan':>8} {'Status':>10}")
print('-' * 110)

for i, user_id in enumerate(sorted(all_user_ids), 1):
    # Find data for this user
    email_validation = next((ev for ev in email_validations.data if ev.get('user_id') == user_id), {})
    profile = next((p for p in profiles.data if p.get('user_id') == user_id), {})
    subscription = next((s for s in subscriptions.data if s.get('user_id') == user_id), {})
    account = next((a for a in accounts.data if a.get('user_id') == user_id), {})
    
    # Get best available email
    email = email_validation.get('email', profile.get('email', ''))
    
    # Get data
    name = profile.get('name', '') or 'No Name'
    country = profile.get('country', '') or 'No Country'
    phone = profile.get('phone', '') or 'No Phone'
    plan_type = subscription.get('plan_type', 'free')
    status = subscription.get('status', 'inactive')
    
    # Truncate for display
    user_display = user_id[:8] + '...' if user_id else 'N/A'
    name_display = (name[:12] + '...') if len(name) > 15 else name
    email_display = (email[:22] + '...') if len(email) > 25 else email
    country_display = (country[:7] + '...') if len(country) > 10 else country
    phone_display = (phone[:12] + '...') if len(phone) > 15 else phone
    
    print(f"{i:>3} {user_display:>10} {name_display:>15} {email_display:>25} {country_display:>10} {phone_display:>15} {plan_type:>8} {status:>10}")

print('-' * 110)

# Summary
users_with_email = len([user_id for user_id in all_user_ids if next((ev for ev in email_validations.data if ev.get('user_id') == user_id), {}).get('email')])
users_with_names = len([user_id for user_id in all_user_ids if next((p for p in profiles.data if p.get('user_id') == user_id), {}).get('name')])
active_subs = len([user_id for user_id in all_user_ids if next((s for s in subscriptions.data if s.get('user_id') == user_id), {}).get('status') == 'active'])

print(f'\\n📊 SUMMARY:')
print(f'   Total Users: {len(all_user_ids)}')
print(f'   ✅ Users with Email: {users_with_email}')
print(f'   ✅ Users with Names: {users_with_names}')
print(f'   ✅ Active Subscriptions: {active_subs}')

# Show the one user with email
if users_with_email > 0:
    user_with_email = next((ev for ev in email_validations.data if ev.get('email')), {})
    print(f'\\n📧 USER WITH EMAIL:')
    print(f'   Email: {user_with_email.get("email")}')
    print(f'   Plan: {user_with_email.get("plan_type")}')
    print(f'   Status: {user_with_email.get("status")}')

print(f'\\n💡 EMAIL ISSUE EXPLANATION:')
print(f'   • Out of {len(all_user_ids)} total users, only {users_with_email} has an email')
print(f'   • This is because user emails are stored in auth.users table (Supabase Auth)')
print(f'   • We can only access emails when users go through payment flow (email_validation table)')
print(f'   • To get all user emails, we need to access the auth.users table directly')

print(f'\\n🚀 WHEN YOU DEPLOY TO RENDER:')
print(f'   • This exact data will sync to your Google Sheets automatically')
print(f'   • Emails will sync whenever users make payments or update profiles')
print(f'   • The sync happens automatically via webhooks')

print('\\n✅ Ready for deployment with your new Google credentials!')