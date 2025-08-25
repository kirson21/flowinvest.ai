#!/usr/bin/env python3
"""
Fixed User Data Sync to Google Sheets
Properly sync user profiles and subscriptions data to Google Sheets
"""

import json
import os
import sys
from datetime import datetime

# Add backend path
sys.path.append('/app/backend')

def sync_users_data_fixed():
    """Sync user profiles and subscriptions data to Google Sheets (fixed version)"""
    
    print("👥 Syncing Users Data to Google Sheets (Fixed Version)...")
    
    # Credentials from the uploaded JSON file
    credentials_data = {
        "type": "service_account",
        "project_id": "flowinvestaiapp",
        "private_key_id": "dc3b8a091db97936e2d715c37cd6bf91662caec0",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCcEH4g/Dt9WXaX
TfaYhE857hNHWKCWeV/vwfx6w0AXafFL+68QWc7lkyTiccAyJTB38I4Jdy99JNtz
8x2FOcZ65lcnDE6z3XbO+EwhIUOjVMeKVDCWBlRUMmTU6dmZeq0lsD1OLyD59BJz
5HLr1rsvavEvnPYFJHcOjZhwFKL8JogP4oViFXLsh3jxYnv7mmy+Ufkm09Y+f9pG
WEyW4IDBKm6CT4nUk4qYQX+b220hN4jVLu26PqK3xWzkvTtBxNXM5TOcDGy4LkfL
vhYYSeBGWt11v0zlRrXaxvaO0H3zlmLKoO/YMBrDHxiy+ZUGGzBFM+cGVASd574S
nGZNGwKVAgMBAAECggEAKKnTc1zFU1/gGoRh4FN5ISr7MvfQv+RYLuxokMQXCwK7
sISflK8RzZeNYMMqxOYTvuya1bSMVxsnYwrRgkkPgi5KPw5h41OtBTiE/YzhRsls
RIqzLiPwDRAkXaWg4PCp9Mv67UgyW25Q8IlxuCl3FF/VAAbxw11A+DXEpk96OCCZ
vf9+fNqXQ43g3Qfa5IGIXBWFNbSiKRd4y63aMmO1tJtxJwWBNqr06aVPD099MhxV
dpl2sUaV9vMdKpZrJdJheQETZcsjmYeiSjANQNmXigw//supFg4vc7TtIcbaUWyo
G53wkdDv7boXrdkoCi5TRv5U4KmI5y/7Mfrjq1hr8QKBgQDSgU6GEfKuTTkeIMGJ
6pkTye5CEftQD6zE5Gy5Y75Vkq3p1frrQLZXRZKlWT9+5ieCtC7N73yHOLk5ldcL
qvYdkmqWFTNMnz556eQGrntUAIUvUf/oeVqUNIlv7Uyz6Iw8/nCCqJOtKdh3hwnu
kpmDousH6a3WCS/auQHRrJxEzwKBgQC9yyBfjiAwDSYcSReP1bD6e2hQMHaKLMLd
NLmndww4ITdo3xU7B4nK2eAx7EcweHIyVzoX1dU/ktIXKHdmg/RzGHB5kDmXe2oU
fwz7EibvC09StDa6kZe8KBBMTWGL6baXIav0xoaiRRySTPctgdz7h+9XqTxvscoF
veXQj4XjWwKBgQDHu2ctMMRp+92xJ3VbjdvW+ed2iydATM8qNm6u7OQAv98CG0Us
iEc6wUmmV+s2VdyxWJN8VLp8dybQa8sSSBGj93PomY8GKaaW+ISijlV4W9IDFzPQ
eaynKL4rFCaOIZ1Glklcv+T3DdhVeSzEUBcW3rNQ27lUd30PdDE0qCnR4wKBgDzK
FcllXVvmqkE/DAPu3uuroUKl8yHYqmVtoNVJpSlJQlUdttAcXv8Q/+Udl8OnoHQN
SjceL1pYbWArfurf8uj2d/gHwNqLFfQQqZi1PLEt/y8vN6RUQ7RpZKb71fWZWvlX
OJuDBtZsqnUVn8n8oUoTRQ7fztK7sEhchYJipfCnAoGBALb4ByNLps51QjgGxY0L
9SAv/UIX9fcExkTZWLMejhhEeIP4SvIlmW8QCtCN+qDdE0pyAZk4ZMXoa40DOBHY
BHhjw9wBmNKmR0B9Td9Op6KvfzjjlSurLu0pZeQCHoFEOgB90iQF/KEKFrXjekkL
OHA+JJ13uDfaltLNGG3PziK/
-----END PRIVATE KEY-----""",
        "client_email": "f01i-sheets-editor@flowinvestaiapp.iam.gserviceaccount.com",
        "client_id": "114101703747959694009",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/f01i-sheets-editor%40flowinvestaiapp.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    try:
        # Import libraries
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from supabase_client import supabase_admin as supabase
        
        print("✅ Libraries imported successfully")
        
        # Create credentials and service
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_info(credentials_data, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        
        users_sheet_id = "1ZYabLq0ghpI2q1pI5frhZcTGe7rMJwzOL5clV1pV-iE"
        
        print("✅ Google Sheets service authenticated")
        
        # ========== GET USER DATA FROM DATABASE ==========
        print("\n📊 Retrieving user data from database...")
        
        # Get all user profiles (this will be our main source of users)
        profiles_result = supabase.table('user_profiles').select('*').execute()
        profiles = profiles_result.data if profiles_result.data else []
        
        # Get all subscriptions
        subscriptions_result = supabase.table('subscriptions').select('*').execute()
        subscriptions = subscriptions_result.data if subscriptions_result.data else []
        
        # Get user accounts for balance/transaction info if available
        try:
            accounts_result = supabase.table('user_accounts').select('*').execute()
            accounts = accounts_result.data if accounts_result.data else []
        except:
            accounts = []
        
        # Get commissions if available
        try:
            commissions_result = supabase.table('commissions').select('user_id, amount, status').execute()
            commissions = commissions_result.data if commissions_result.data else []
        except:
            commissions = []
        
        print(f"📝 Found {len(profiles)} user profiles")
        print(f"💳 Found {len(subscriptions)} subscriptions")
        print(f"💰 Found {len(accounts)} user accounts")
        print(f"💵 Found {len(commissions)} commission records")
        
        # ========== PROCESS AND COMBINE DATA ==========
        users_data = []
        
        for profile in profiles:
            user_id = profile.get('user_id', '')
            
            # Find matching subscription
            user_subscription = next((s for s in subscriptions if s['user_id'] == user_id), {})
            
            # Find matching account
            user_account = next((a for a in accounts if a['user_id'] == user_id), {})
            
            # Calculate total commissions for this user
            user_commissions = [c for c in commissions if c.get('user_id') == user_id and c.get('status') == 'paid']
            total_commission = sum(float(c.get('amount', 0)) for c in user_commissions)
            
            # Create user data record
            user_data = {
                'user_id': user_id,
                'name': profile.get('name', ''),
                'email': profile.get('email', ''),  # Try to get email from profile
                'country': profile.get('country', ''),
                'phone': profile.get('phone', ''),
                'registration_date': profile.get('created_at', ''),
                'seller_verification_status': profile.get('seller_verification_status', 'not_verified'),
                'plan_type': user_subscription.get('plan_type', 'free'),
                'subscription_status': user_subscription.get('status', 'inactive'),
                'subscription_end_date': user_subscription.get('end_date', ''),
                'total_commission_earned': total_commission
            }
            
            users_data.append(user_data)
        
        # ========== PREPARE DATA FOR GOOGLE SHEETS ==========
        headers = [
            'User ID', 'Name', 'Email', 'Country', 'Phone', 
            'Registration Date', 'Seller Status', 'Subscription Status',
            'Plan Type', 'Subscription End Date', 'Total Commission Earned'
        ]
        
        rows = [headers]
        for user in users_data:
            rows.append([
                user.get('user_id', ''),
                user.get('name', ''),
                user.get('email', ''),
                user.get('country', ''),
                user.get('phone', ''),
                user.get('registration_date', ''),
                user.get('seller_verification_status', ''),
                user.get('subscription_status', ''),
                user.get('plan_type', ''),
                user.get('subscription_end_date', ''),
                float(user.get('total_commission_earned', 0))
            ])
        
        # ========== SYNC TO GOOGLE SHEETS ==========
        print(f"\n📤 Syncing {len(users_data)} users to Google Sheets...")
        
        # Clear existing data
        service.spreadsheets().values().clear(
            spreadsheetId=users_sheet_id,
            range='A:Z'
        ).execute()
        
        # Write new data
        service.spreadsheets().values().update(
            spreadsheetId=users_sheet_id,
            range='A1',
            valueInputOption='RAW',
            body={'values': rows}
        ).execute()
        
        print(f"✅ Users data synced successfully! ({len(users_data)} users)")
        
        # ========== SHOW SUMMARY ==========
        active_subs = len([u for u in users_data if u.get('subscription_status') == 'active'])
        plus_users = len([u for u in users_data if u.get('plan_type') == 'plus'])
        verified_sellers = len([u for u in users_data if u.get('seller_verification_status') == 'verified'])
        total_commissions = sum(u.get('total_commission_earned', 0) for u in users_data)
        
        print(f"\n📊 USER DATA SUMMARY:")
        print(f"   Total Users: {len(users_data)}")
        print(f"   Active Subscriptions: {active_subs}")
        print(f"   Plus Plan Users: {plus_users}")
        print(f"   Verified Sellers: {verified_sellers}")
        print(f"   Total Commissions Earned: ${total_commissions:.2f}")
        
        # Show a few sample users
        print(f"\n👤 SAMPLE USERS:")
        for i, user in enumerate(users_data[:3]):
            print(f"   {i+1}. {user.get('name', 'No Name')} - {user.get('plan_type', 'free')} plan - {user.get('subscription_status', 'inactive')}")
        
        print(f"\n🔗 Check your updated Users Sheet:")
        print(f"   https://docs.google.com/spreadsheets/d/{users_sheet_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Users data sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = sync_users_data_fixed()
    exit(0 if success else 1)