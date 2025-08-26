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
        """Authenticate with Google Sheets API using service account credentials from environment variables ONLY"""
        try:
            # Load service account credentials from environment variables ONLY
            print("🔑 Loading Google credentials from environment variables...")
            
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
            
            # Validate ALL required environment variables
            required_vars = [
                "GOOGLE_PROJECT_ID", "GOOGLE_PRIVATE_KEY_ID", "GOOGLE_PRIVATE_KEY", 
                "GOOGLE_CLIENT_EMAIL", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_X509_CERT_URL"
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}. Please add these to your Render environment variables.")
            
            print(f"✅ All required environment variables found")
            print(f"📧 Service account: {credentials_json['client_email']}")
            
            self.credentials = Credentials.from_service_account_info(
                credentials_json, scopes=self.scopes
            )
            
            self.service = build('sheets', 'v4', credentials=self.credentials)
            print("✅ Google Sheets authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets authentication failed: {str(e)}")
            print("💡 Make sure to add all Google service account credentials to Render environment variables")
            print("📋 Required variables: GOOGLE_PROJECT_ID, GOOGLE_PRIVATE_KEY_ID, GOOGLE_PRIVATE_KEY, GOOGLE_CLIENT_EMAIL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_X509_CERT_URL")
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
        """Sync users data to Google Sheets with emails from auth.users via RPC function"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            print("📊 Collecting user data using RPC function...")
            
            # Try to use the RPC function to get complete user data with emails
            users_data = []
            
            try:
                print("🔍 Using working get_users_emails_simple() RPC function...")
                emails_result = supabase.rpc('get_users_emails_simple').execute()
                
                if emails_result.data:
                    print(f"✅ Simple RPC successful! Found {len(emails_result.data)} users with emails")
                    
                    # Get additional data manually
                    profiles = supabase.table('user_profiles').select('*').execute()
                    subscriptions = supabase.table('subscriptions').select('*').execute()
                    
                    profiles_data = profiles.data if profiles.data else []
                    subscriptions_data = subscriptions.data if subscriptions.data else []
                    
                    print(f"📊 Combining {len(emails_result.data)} emails with {len(profiles_data)} profiles and {len(subscriptions_data)} subscriptions")
                    
                    for email_user in emails_result.data:
                        user_id = email_user.get('user_id', '')
                        
                        # Find matching profile and subscription
                        profile = next((p for p in profiles_data if p.get('user_id') == user_id), {})
                        subscription = next((s for s in subscriptions_data if s.get('user_id') == user_id), {})
                        
                        users_data.append({
                            'user_id': user_id,
                            'name': profile.get('name', ''),
                            'email': email_user.get('email', ''),  # Email from auth.users!
                            'country': profile.get('country', ''),
                            'phone': profile.get('phone', ''),
                            'registration_date': email_user.get('created_at', ''),
                            'seller_verification_status': profile.get('seller_verification_status', 'not_verified'),
                            'plan_type': subscription.get('plan_type', 'free'),
                            'subscription_status': subscription.get('status', 'inactive'),
                            'subscription_end_date': subscription.get('end_date', ''),
                            'total_commission_earned': 0
                        })
                else:
                    print("⚠️ Simple RPC returned no data, falling back to manual method")
                    raise Exception("No data from simple RPC")
                    
            except Exception as rpc_error:
                print(f"⚠️ Complex RPC failed: {rpc_error}")
                print("🔄 Trying simple RPC function get_users_emails_simple()...")
                
                try:
                    # Fallback to simple RPC + manual joins
                    emails_result = supabase.rpc('get_users_emails_simple').execute()
                    
                    if emails_result.data:
                        print(f"✅ Simple RPC successful! Found {len(emails_result.data)} users with emails")
                        
                        # Get additional data manually
                        profiles = supabase.table('user_profiles').select('*').execute()
                        subscriptions = supabase.table('subscriptions').select('*').execute()
                        
                        profiles_data = profiles.data if profiles.data else []
                        subscriptions_data = subscriptions.data if subscriptions.data else []
                        
                        for user in emails_result.data:
                            user_id = user.get('user_id', '')
                            
                            # Find matching profile and subscription
                            profile = next((p for p in profiles_data if p.get('user_id') == user_id), {})
                            subscription = next((s for s in subscriptions_data if s.get('user_id') == user_id), {})
                            
                            users_data.append({
                                'user_id': user_id,
                                'name': profile.get('name', ''),
                                'email': user.get('email', ''),
                                'country': profile.get('country', ''),
                                'phone': profile.get('phone', ''),
                                'registration_date': user.get('created_at', ''),
                                'seller_verification_status': profile.get('seller_verification_status', 'not_verified'),
                                'plan_type': subscription.get('plan_type', 'free'),
                                'subscription_status': subscription.get('status', 'inactive'),
                                'subscription_end_date': subscription.get('end_date', ''),
                                'total_commission_earned': 0
                            })
                    else:
                        print("❌ Simple RPC also returned no data")
                        raise Exception("No data from simple RPC")
                        
                except Exception as simple_rpc_error:
                    print(f"❌ Simple RPC also failed: {simple_rpc_error}")
                    print("🔄 Falling back to manual data collection...")
                    
                    # Final fallback: use the original manual method
                    users_data = self._fallback_manual_sync()
            
            if not users_data:
                print("❌ No user data collected from any method")
                return False
            
            # Sort by registration date (newest first)
            users_data.sort(key=lambda x: x.get('registration_date', ''), reverse=True)
            
            # Prepare headers for Google Sheets
            headers = [
                'User ID', 'Name', 'Email', 'Country', 
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
                range='A:Z'
            ).execute()
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.users_sheet_id,
                range='A1',
                valueInputOption='RAW',
                body={'values': rows}
            ).execute()
            
            print(f"✅ Users data synced to Google Sheets successfully ({len(users_data)} users)")
            
            # Print detailed summary
            users_with_email = len([u for u in users_data if u.get('email')])
            users_with_names = len([u for u in users_data if u.get('name')])
            users_with_phone = len([u for u in users_data if u.get('phone')])
            users_with_country = len([u for u in users_data if u.get('country')])
            active_subs = len([u for u in users_data if u.get('subscription_status') == 'active'])
            plus_users = len([u for u in users_data if u.get('plan_type') == 'plus'])
            verified_sellers = len([u for u in users_data if u.get('seller_verification_status') == 'verified'])
            
            print(f"   📊 DETAILED SUMMARY:")
            print(f"   Total Users: {len(users_data)}")
            print(f"   Users with Email: {users_with_email}")
            print(f"   Users with Name: {users_with_names}")
            print(f"   Users with Phone: {users_with_phone}")
            print(f"   Users with Country: {users_with_country}")
            print(f"   Active Subscriptions: {active_subs}")
            print(f"   Plus Plan Users: {plus_users}")
            print(f"   Verified Sellers: {verified_sellers}")
            
            return True
            
        except HttpError as e:
            print(f"❌ Google Sheets API error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error syncing users data: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _fallback_manual_sync(self):
        """Fallback method for manual data collection when RPC functions fail"""
        print("📊 Using fallback manual data collection...")
        
        try:
            # Get data from individual tables
            profiles = supabase.table('user_profiles').select('*').execute()
            subscriptions = supabase.table('subscriptions').select('*').execute()
            email_validations = supabase.table('subscription_email_validation').select('user_id, email').execute()
            
            profiles_data = profiles.data if profiles.data else []
            subscriptions_data = subscriptions.data if subscriptions.data else []
            email_validations_data = email_validations.data if email_validations.data else []
            
            # Collect all unique user IDs
            all_user_ids = set()
            for profile in profiles_data:
                all_user_ids.add(profile.get('user_id'))
            for subscription in subscriptions_data:
                all_user_ids.add(subscription.get('user_id'))
            for email_val in email_validations_data:
                all_user_ids.add(email_val.get('user_id'))
            
            users_data = []
            
            for user_id in all_user_ids:
                if not user_id:
                    continue
                
                profile = next((p for p in profiles_data if p.get('user_id') == user_id), {})
                subscription = next((s for s in subscriptions_data if s.get('user_id') == user_id), {})
                email_validation = next((e for e in email_validations_data if e.get('user_id') == user_id), {})
                
                # Get best available email (from email validation table)
                email = email_validation.get('email', '')
                
                users_data.append({
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
                })
            
            print(f"✅ Fallback method collected {len(users_data)} users")
            return users_data
            
        except Exception as e:
            print(f"❌ Fallback method also failed: {e}")
            return []
    
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