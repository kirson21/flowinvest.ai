#!/usr/bin/env python3
"""
Sync Real Data to Google Sheets
Sync actual company balance and users data to Google Sheets
"""

import json
import os
import sys
from datetime import datetime

# Add backend path
sys.path.append('/app/backend')

def sync_real_data():
    """Sync real company balance and users data to Google Sheets"""
    
    print("🔄 Syncing Real Data to Google Sheets...")
    
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
        
        balance_sheet_id = "1_q7zuZta8lIdGDmRFhh1rgYYdMUwGLXb7YCIShVB6Ps"
        users_sheet_id = "1ZYabLq0ghpI2q1pI5frhZcTGe7rMJwzOL5clV1pV-iE"
        
        print("✅ Google Sheets service authenticated")
        
        # ========== SYNC COMPANY BALANCE DATA ==========
        print("\n📊 Syncing Company Balance Data...")
        
        try:
            # Get company balance data
            balance_data = supabase.table('company_balance').select('*').execute()
            monthly_data = supabase.table('company_balance_monthly').select('*').order('report_month', desc=True).execute()
            
            print(f"💰 Found {len(balance_data.data)} company balance records")
            print(f"📅 Found {len(monthly_data.data) if monthly_data.data else 0} monthly reports")
            
            if balance_data.data:
                balance = balance_data.data[0]
                
                # Prepare headers and data
                headers = [
                    'Last Updated', 'Company Funds', 'User Funds', 'Total Deposits', 
                    'Total Withdrawals', 'Total Fees Earned', 'Total Subscription Revenue', 'Currency'
                ]
                
                current_data = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    float(balance.get('company_funds', 0)),
                    float(balance.get('user_funds', 0)),
                    float(balance.get('total_deposits', 0)),
                    float(balance.get('total_withdrawals', 0)),
                    float(balance.get('total_fees_earned', 0)),
                    float(balance.get('total_subscription_revenue', 0)),
                    balance.get('currency', 'USD')
                ]
                
                # Clear and update Current Balance sheet
                service.spreadsheets().values().clear(
                    spreadsheetId=balance_sheet_id,
                    range='A:Z'
                ).execute()
                
                service.spreadsheets().values().update(
                    spreadsheetId=balance_sheet_id,
                    range='A1',
                    valueInputOption='RAW',
                    body={'values': [headers, current_data]}
                ).execute()
                
                print("✅ Company balance data synced to Google Sheets")
                print(f"   Company Funds: ${current_data[1]:.2f}")
                print(f"   User Funds: ${current_data[2]:.2f}")
                print(f"   Total Deposits: ${current_data[3]:.2f}")
                print(f"   Total Subscription Revenue: ${current_data[6]:.2f}")
                
        except Exception as e:
            print(f"❌ Company balance sync failed: {e}")
        
        # ========== SYNC USERS DATA ==========
        print("\n👥 Syncing Users Data...")
        
        try:
            # Get users data
            users = supabase.table('auth.users').select('id, email, created_at').execute()
            profiles = supabase.table('user_profiles').select('*').execute()
            subscriptions = supabase.table('subscriptions').select('*').execute()
            
            print(f"👤 Found {len(users.data) if users.data else 0} users")
            print(f"📝 Found {len(profiles.data) if profiles.data else 0} user profiles")
            print(f"💳 Found {len(subscriptions.data) if subscriptions.data else 0} subscriptions")
            
            # Combine data
            users_data = []
            if users.data:
                for user in users.data:
                    profile = next((p for p in profiles.data if p['user_id'] == user['id']), {}) if profiles.data else {}
                    sub = next((s for s in subscriptions.data if s['user_id'] == user['id']), {}) if subscriptions.data else {}
                    
                    users_data.append({
                        'user_id': user['id'],
                        'email': user['email'],
                        'registration_date': user['created_at'],
                        'name': profile.get('name', ''),
                        'country': profile.get('country', ''),
                        'phone': profile.get('phone', ''),
                        'seller_verification_status': profile.get('seller_verification_status', 'not_verified'),
                        'plan_type': sub.get('plan_type', 'free'),
                        'subscription_status': sub.get('status', 'inactive'),
                        'subscription_end_date': sub.get('end_date', ''),
                        'total_commission_earned': 0
                    })
            
            # Prepare headers and data for Google Sheets
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
            
            # Clear and update Users sheet
            service.spreadsheets().values().clear(
                spreadsheetId=users_sheet_id,
                range='A:Z'
            ).execute()
            
            service.spreadsheets().values().update(
                spreadsheetId=users_sheet_id,
                range='A1',
                valueInputOption='RAW',
                body={'values': rows}
            ).execute()
            
            print(f"✅ Users data synced to Google Sheets ({len(users_data)} users)")
            
            # Show summary
            active_subs = len([u for u in users_data if u.get('subscription_status') == 'active'])
            plus_users = len([u for u in users_data if u.get('plan_type') == 'plus'])
            verified_sellers = len([u for u in users_data if u.get('seller_verification_status') == 'verified'])
            
            print(f"   Total Users: {len(users_data)}")
            print(f"   Active Subscriptions: {active_subs}")
            print(f"   Plus Plan Users: {plus_users}")
            print(f"   Verified Sellers: {verified_sellers}")
            
        except Exception as e:
            print(f"❌ Users data sync failed: {e}")
        
        print("\n🎉 Real Data Sync Completed Successfully!")
        print("📊 Check your Google Sheets:")
        print(f"   Balance Sheet: https://docs.google.com/spreadsheets/d/{balance_sheet_id}")
        print(f"   Users Sheet: https://docs.google.com/spreadsheets/d/{users_sheet_id}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing libraries: {e}")
        return False
    except Exception as e:
        print(f"❌ Real data sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = sync_real_data()
    exit(0 if success else 1)