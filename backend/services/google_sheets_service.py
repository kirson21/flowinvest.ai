"""
Google Sheets Integration Service
Synchronizes data from Supabase to Google Sheets automatically
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
sys.path.append('/app/backend')
from supabase_client import supabase_admin as supabase

class GoogleSheetsService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.balance_sheet_id = "1_q7zuZta8lIdGDmRFhh1rgYYdMUwGLXb7YCIShVB6Ps"
        self.users_sheet_id = "1ZYabLq0ghpI2q1pI5frhZcTGe7rMJwzOL5clV1pV-iE"
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
    def authenticate(self):
        """Authenticate with Google Sheets API using service account credentials"""
        try:
            # First try environment variables
            if all(os.getenv(var) for var in ["GOOGLE_PROJECT_ID", "GOOGLE_PRIVATE_KEY_ID", "GOOGLE_PRIVATE_KEY", "GOOGLE_CLIENT_EMAIL", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_X509_CERT_URL"]):
                print("🔑 Using Google credentials from environment variables")
                credentials_json = {
                    "type": "service_account",
                    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n'),
                    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
                    "universe_domain": "googleapis.com"
                }
            else:
                # Fallback to hardcoded credentials for now (temporary solution)
                print("🔑 Using fallback Google credentials (temporary)")
                credentials_json = {
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
            
            self.credentials = Credentials.from_service_account_info(
                credentials_json, scopes=self.scopes
            )
            
            self.service = build('sheets', 'v4', credentials=self.credentials)
            print("✅ Google Sheets authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets authentication failed: {str(e)}")
            return False
    
    def sync_company_balance(self):
        """Sync company balance data to Google Sheets"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Get company balance data
            balance_data = supabase.table('company_balance').select('*').execute()
            monthly_data = supabase.table('company_balance_monthly').select('*').order('report_month', desc=True).execute()
            
            if not balance_data.data:
                print("⚠️ No company balance data found")
                return False
            
            balance = balance_data.data[0]
            
            # Prepare data for Google Sheets
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
            
            # Clear and update the current balance sheet
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.balance_sheet_id,
                range='Current Balance!A:Z'
            ).execute()
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.balance_sheet_id,
                range='Current Balance!A1',
                valueInputOption='RAW',
                body={'values': [headers, current_data]}
            ).execute()
            
            # Update monthly reports if available
            if monthly_data.data:
                monthly_headers = [
                    'Report Month', 'Total Revenue', 'Subscription Revenue', 
                    'Deposit Revenue', 'Commission Revenue', 'Total Users', 
                    'Active Subscribers', 'New Signups', 'Updated At'
                ]
                
                monthly_rows = [monthly_headers]
                for month in monthly_data.data:
                    monthly_rows.append([
                        month.get('report_month', ''),
                        float(month.get('total_revenue', 0)),
                        float(month.get('subscription_revenue', 0)),
                        float(month.get('deposit_revenue', 0)),
                        float(month.get('commission_revenue', 0)),
                        month.get('total_users', 0),
                        month.get('active_subscribers', 0),
                        month.get('new_signups', 0),
                        month.get('updated_at', '')
                    ])
                
                # Clear and update monthly reports
                self.service.spreadsheets().values().clear(
                    spreadsheetId=self.balance_sheet_id,
                    range='Monthly Reports!A:Z'
                ).execute()
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.balance_sheet_id,
                    range='Monthly Reports!A1',
                    valueInputOption='RAW',
                    body={'values': monthly_rows}
                ).execute()
            
            print(f"✅ Company balance synced to Google Sheets successfully")
            return True
            
        except HttpError as e:
            print(f"❌ Google Sheets API error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error syncing company balance: {str(e)}")
            return False
    
    def sync_users_data(self):
        """Sync users data to Google Sheets"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Get comprehensive users data
            users_query = """
            SELECT 
                u.id as user_id,
                u.email,
                u.created_at as registration_date,
                up.name,
                up.country,
                up.phone,
                up.seller_verification_status,
                s.plan_type,
                s.status as subscription_status,
                s.end_date as subscription_end_date,
                COALESCE(c.total_commissions, 0) as total_commission_earned
            FROM auth.users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            LEFT JOIN subscriptions s ON u.id = s.user_id
            LEFT JOIN (
                SELECT user_id, SUM(amount) as total_commissions
                FROM commissions 
                WHERE status = 'paid'
                GROUP BY user_id
            ) c ON u.id = c.user_id
            ORDER BY u.created_at DESC
            """
            
            # Execute raw SQL query
            result = supabase.rpc('execute_sql', {'sql_query': users_query}).execute()
            
            if not result.data:
                # Fallback to individual table queries if raw SQL doesn't work
                users = supabase.table('auth.users').select('*').execute()
                profiles = supabase.table('user_profiles').select('*').execute()
                subscriptions = supabase.table('subscriptions').select('*').execute()
                
                # Combine data manually
                users_data = []
                for user in users.data:
                    profile = next((p for p in profiles.data if p['user_id'] == user['id']), {})
                    sub = next((s for s in subscriptions.data if s['user_id'] == user['id']), {})
                    
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
            else:
                users_data = result.data
            
            # Prepare headers for Google Sheets
            headers = [
                'User ID', 'Name', 'Email', 'Country', 'Phone', 
                'Registration Date', 'Seller Status', 'Subscription Status',
                'Plan Type', 'Subscription End Date', 'Total Commission Earned'
            ]
            
            # Prepare data rows
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
            
            # Clear and update the users sheet
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.users_sheet_id,
                range='Users Data!A:Z'
            ).execute()
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.users_sheet_id,
                range='Users Data!A1',
                valueInputOption='RAW',
                body={'values': rows}
            ).execute()
            
            print(f"✅ Users data synced to Google Sheets successfully ({len(users_data)} users)")
            return True
            
        except HttpError as e:
            print(f"❌ Google Sheets API error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error syncing users data: {str(e)}")
            return False
    
    def sync_all_data(self):
        """Sync all data to Google Sheets"""
        try:
            print("🔄 Starting Google Sheets sync...")
            
            balance_success = self.sync_company_balance()
            users_success = self.sync_users_data()
            
            if balance_success and users_success:
                print("✅ All data synced to Google Sheets successfully")
                return True
            else:
                print("⚠️ Some data sync operations failed")
                return False
                
        except Exception as e:
            print(f"❌ Error in sync_all_data: {str(e)}")
            return False

# Helper function for SQL execution (if not available as RPC)
def create_sql_executor():
    """Create SQL executor function in Supabase if it doesn't exist"""
    sql_function = """
    CREATE OR REPLACE FUNCTION execute_sql(sql_query TEXT)
    RETURNS TABLE(result JSONB) AS $$
    BEGIN
        RETURN QUERY EXECUTE sql_query;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """
    try:
        supabase.rpc('execute_sql', {'sql_query': sql_function}).execute()
        print("✅ SQL executor function created")
    except Exception as e:
        print(f"⚠️ SQL executor creation failed: {e}")

# Global instance
google_sheets_service = GoogleSheetsService()