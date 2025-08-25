#!/usr/bin/env python3
"""
Create Mock Users Sheet Data
Show what the Google Sheets sync will look like with all available user data
"""

import sys
import os
from datetime import datetime
sys.path.append('/app/backend')

# Set environment variables from .env file
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

try:
    from supabase_client import supabase_admin as supabase
    
    print('📊 Creating Mock Users Sheet with All Available Data...')
    
    # Get all data sources
    email_validations = supabase.table('subscription_email_validation').select('user_id, email, status').execute()
    subscriptions = supabase.table('subscriptions').select('*').execute()
    profiles = supabase.table('user_profiles').select('*').execute()
    
    try:
        accounts = supabase.table('user_accounts').select('*').execute()
    except:
        accounts = type('obj', (object,), {'data': []})()
    
    try:
        commissions = supabase.table('commissions').select('user_id, amount, status').execute()
    except:
        commissions = type('obj', (object,), {'data': []})()
        
    print(f"📊 Data loaded:")
    print(f"   Email validations: {len(email_validations.data) if email_validations.data else 0}")
    print(f"   Subscriptions: {len(subscriptions.data) if subscriptions.data else 0}")
    print(f"   Profiles: {len(profiles.data) if profiles.data else 0}")
    print(f"   Accounts: {len(accounts.data) if accounts.data else 0}")
    print(f"   Commissions: {len(commissions.data) if commissions.data else 0}")
    
    # Get all unique user IDs
    all_user_ids = set()
    
    if email_validations.data:
        for ev in email_validations.data:
            all_user_ids.add(ev.get('user_id'))
    
    if subscriptions.data:
        for sub in subscriptions.data:
            all_user_ids.add(sub.get('user_id'))
    
    if profiles.data:
        for profile in profiles.data:
            all_user_ids.add(profile.get('user_id'))
    
    # Process each user
    users_data = []
    
    for user_id in sorted(all_user_ids):
        if not user_id:
            continue
        
        # Find matching data
        email_validation = next((e for e in email_validations.data if e.get('user_id') == user_id), {}) if email_validations.data else {}
        user_profile = next((p for p in profiles.data if p.get('user_id') == user_id), {}) if profiles.data else {}
        user_subscription = next((s for s in subscriptions.data if s.get('user_id') == user_id), {}) if subscriptions.data else {}
        user_account = next((a for a in accounts.data if a.get('user_id') == user_id), {}) if accounts.data else {}
        
        # Calculate commissions
        user_commissions = []
        if commissions.data:
            user_commissions = [c for c in commissions.data if c.get('user_id') == user_id and c.get('status') == 'paid']
        total_commission = sum(float(c.get('amount', 0)) for c in user_commissions)
        
        # Get best available email
        email = (email_validation.get('email', '') or 
                user_profile.get('email', '') or 
                user_subscription.get('metadata', {}).get('email', '') if isinstance(user_subscription.get('metadata'), dict) else '')
        
        # Get best available registration date
        registration_date = (email_validation.get('created_at', '') or
                            user_profile.get('created_at', '') or 
                            user_subscription.get('created_at', ''))
        
        user_data = {
            'user_id': user_id,
            'name': user_profile.get('name', ''),
            'email': email,
            'country': user_profile.get('country', ''),
            'phone': user_profile.get('phone', ''),
            'registration_date': registration_date,
            'seller_verification_status': user_profile.get('seller_verification_status', 'not_verified'),
            'plan_type': user_subscription.get('plan_type', 'free'),
            'subscription_status': user_subscription.get('status', 'inactive'),
            'subscription_end_date': user_subscription.get('end_date', ''),
            'total_commission_earned': total_commission
        }
        
        users_data.append(user_data)
    
    # Create the sheet format
    headers = [
        'User ID', 'Name', 'Email', 'Country', 'Phone', 
        'Registration Date', 'Seller Status', 'Subscription Status',
        'Plan Type', 'Subscription End Date', 'Total Commission Earned'
    ]
    
    print(f'\\n📋 USERS SHEET DATA PREVIEW:')
    print('=' * 120)
    
    # Print headers
    header_line = '|'.join(f'{h:15}' for h in headers)
    print(header_line)
    print('-' * len(header_line))
    
    # Print data rows
    for i, user in enumerate(users_data, 1):
        row = [
            user.get('user_id', '')[:12] + '...',
            user.get('name', '') or 'No Name',
            user.get('email', '') or 'No Email',
            user.get('country', '') or 'No Country',
            user.get('phone', '') or 'No Phone',
            user.get('registration_date', '')[:10],
            user.get('seller_verification_status', ''),
            user.get('subscription_status', ''),
            user.get('plan_type', ''),
            user.get('subscription_end_date', '')[:10],
            f'${float(user.get("total_commission_earned", 0)):.2f}'
        ]
        
        row_line = '|'.join(f'{str(cell):15}' for cell in row)
        print(f'{i:2d}. {row_line}')
    
    print('=' * 120)
    
    # Summary
    users_with_email = len([u for u in users_data if u.get('email')])
    users_with_names = len([u for u in users_data if u.get('name')])
    active_subs = len([u for u in users_data if u.get('subscription_status') == 'active'])
    plus_users = len([u for u in users_data if u.get('plan_type') == 'plus'])
    
    print(f'\\n📊 SUMMARY STATS:')
    print(f'   Total Users: {len(users_data)}')
    print(f'   Users with Email: {users_with_email}')
    print(f'   Users with Names: {users_with_names}')
    print(f'   Active Subscriptions: {active_subs}')
    print(f'   Plus Plan Users: {plus_users}')
    
    # Email sources breakdown
    print(f'\\n📧 EMAIL SOURCES:')
    email_from_validation = len([u for u in users_data if u.get('email') and any(ev.get('user_id') == u.get('user_id') and ev.get('email') == u.get('email') for ev in email_validations.data) if email_validations.data])
    print(f'   From email_validation table: {email_from_validation}')
    print(f'   From user_profiles table: 0 (no emails in profiles)')
    print(f'   From subscription metadata: 0 (no emails in metadata)')
    
    print(f'\\n🔍 THE MISSING EMAIL ISSUE:')
    print(f'   The reason we only have 1 email out of {len(users_data)} users is that:')
    print(f'   1. User emails are stored in the auth.users table (Supabase Auth)')
    print(f'   2. We cannot access auth.users directly via normal Supabase client')
    print(f'   3. Only 1 user has been through the subscription payment flow (email_validation table)')
    print(f'   4. User profiles don\'t have email column (emails come from auth.users)')
    
    print(f'\\n💡 SOLUTIONS:')
    print(f'   1. ✅ Current: Using subscription_email_validation table (1 email found)')
    print(f'   2. 🔄 Option: Add RPC function in Supabase to access auth.users')
    print(f'   3. 🔄 Option: Trigger profile updates to copy emails from auth.users to user_profiles')
    print(f'   4. 🔄 Option: Use Supabase webhooks to sync auth.users emails automatically')
    
    print(f'\\n✅ This data will be synced to your Google Sheets when you deploy with the environment variables!')

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()