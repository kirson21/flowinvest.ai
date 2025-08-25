#!/usr/bin/env python3
"""
Test User Email Collection
Check what email data we have available in the database
"""

import sys
import os
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
    
    print('🔍 Checking all available user email data...')
    
    # Check subscription_email_validation table
    try:
        email_validations = supabase.table('subscription_email_validation').select('user_id, email, status').execute()
        print(f'📧 Email validations: {len(email_validations.data) if email_validations.data else 0}')
        if email_validations.data:
            for ev in email_validations.data:
                print(f'   User: {ev.get("user_id", "unknown")[:8]}... Email: {ev.get("email", "no_email")} Status: {ev.get("status", "unknown")}')
    except Exception as e:
        print(f'   Error checking email_validations: {e}')
    
    # Check subscriptions metadata for emails
    try:
        subscriptions = supabase.table('subscriptions').select('user_id, metadata, plan_type, status').execute()
        print(f'💳 Subscriptions: {len(subscriptions.data) if subscriptions.data else 0}')
        emails_in_subs = 0
        if subscriptions.data:
            for sub in subscriptions.data:
                metadata = sub.get('metadata', {})
                if isinstance(metadata, dict) and metadata.get('email'):
                    emails_in_subs += 1
                    print(f'   User: {sub.get("user_id", "unknown")[:8]}... Email: {metadata.get("email")} Plan: {sub.get("plan_type", "free")} Status: {sub.get("status", "inactive")}')
            print(f'   📧 Subscriptions with emails: {emails_in_subs}')
    except Exception as e:
        print(f'   Error checking subscriptions: {e}')
    
    # Check user profiles  
    try:
        profiles = supabase.table('user_profiles').select('user_id, name, email, country, phone').execute()
        print(f'👤 User profiles: {len(profiles.data) if profiles.data else 0}')
        emails_in_profiles = 0
        if profiles.data:
            for profile in profiles.data:
                if profile.get('email'):
                    emails_in_profiles += 1
                print(f'   User: {profile.get("user_id", "unknown")[:8]}... Name: {profile.get("name", "no_name")} Email: {profile.get("email", "no_email")} Country: {profile.get("country", "no_country")}')
            print(f'   📧 Profiles with emails: {emails_in_profiles}')
    except Exception as e:
        print(f'   Error checking profiles: {e}')
    
    # Get all unique user IDs
    try:
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
        
        print(f'\\n📊 SUMMARY:')
        print(f'   Total unique users found: {len(all_user_ids)}')
        print(f'   Users with emails (email_validation): {len(email_validations.data) if email_validations.data else 0}')
        print(f'   Users with emails (subscription metadata): {emails_in_subs}')
        print(f'   Users with emails (profiles): {emails_in_profiles}')
        
        # Show all user IDs
        print(f'\\n🆔 All User IDs found:')
        for i, user_id in enumerate(sorted(all_user_ids), 1):
            if user_id:
                print(f'   {i}. {user_id}')
        
    except Exception as e:
        print(f'   Error in summary: {e}')
    
    print('\\n✅ Email data investigation complete')

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()