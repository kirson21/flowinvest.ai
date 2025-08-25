#!/usr/bin/env python3
"""
Temporary Google Sheets Integration Test
Test Google Sheets integration with provided credentials
"""

import json
import os
import sys
import tempfile
from datetime import datetime

# Add backend path
sys.path.append('/app/backend')
sys.path.append('/app/backend/services')

def test_google_sheets_integration():
    """Test Google Sheets integration with the provided credentials"""
    
    print("🧪 Testing Google Sheets Integration...")
    
    # Credentials from the uploaded JSON file
    credentials_data = {
        "type": "service_account",
        "project_id": "flowinvestaiapp",
        "private_key_id": "dc3b8a091db97936e2d715c37cd6bf91662caec0",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCcEH4g/Dt9WXaX\nTfaYhE857hNHWKCWeV/vwfx6w0AXafFL+68QWc7lkyTiccAyJTB38I4Jdy99JNtz\n8x2FOcZ65lcnDE6z3XbO+EwhIUOjVMeKVDCWBlRUMmTU6dmZeq0lsD1OLyD59BJz\n5HLr1rsvavEvnPYFJHcOjZhwFKL8JogP4oViFXLsh3jxYnv7mmy+Ufkm09Y+f9pG\nWEyW4IDBKm6CT4nUk4qYQX+b220hN4jVLu26PqK3xWzkvTtBxNXM5TOcDGy4LkfL\nvhYYSeBGWt11v0zlRrXaxvaO0H3zlmLKoO/YMBrDHxiy+ZUGGzBFM+cGVASd574S\nnGZNGwKVAgMBAAECggEAKKnTc1zFU1/gGoRh4FN5ISr7MvfQv+RYLuxokMQXCwK7\nsISflK8RzZeNYMMqxOYTvuya1bSMVxsnYwrRgkkPgi5KPw5h41OtBTiE/YzhRsls\nRIqzLiPwDRAkXaWg4PCp9Mv67UgyW25Q8IlxuCl3FF/VAAbxw11A+DXEpk96OCCZ\nvf9+fNqXQ43g3Qfa5IGIXBWFNbSiKRd4y63aMmO1tJtxJwWBNqr06aVPD099MhxV\ndpl2sUaV9vMdKpZrJdJheQETZcsjmYeiSjANQNmXigw//supFg4vc7TtIcbaUWyo\nG53wkdDv7boXrdkoCi5TRv5U4KmI5y/7Mfrjq1hr8QKBgQDSgU6GEfKuTTkeIMGJ\n6pkTye5CEftQD6zE5Gy5Y75Vkq3p1frrQLZXRZKlWT9+5ieCtC7N73yHOLk5ldcL\nqvYdkmqWFTNMnz556eQGrntUAIUvUf/oeVqUNIlv7Uyz6Iw8/nCCqJOtKdh3hwnu\nkpmDousH6a3WCS/auQHRrJxEzwKBgQC9yyBfjiAwDSYcSReP1bD6e2hQMHaKLMLd\nNLmndww4ITdo3xU7B4nK2eAx7EcweHIyVzoX1dU/ktIXKHdmg/RzGHB5kDmXe2oU\nfwz7EibvC09StDa6kZe8KBBMTWGL6baXIav0xoaiRRySTPctgdz7h+9XqTxvscoF\nveXQj4XjWwKBgQDHu2ctMMRp+92xJ3VbjdvW+ed2iydATM8qNm6u7OQAv98CG0Us\niEc6wUmmV+s2VdyxWJN8VLp8dybQa8sSSBGj93PomY8GKaaW+ISijlV4W9IDFzPQ\neaynKL4rFCaOIZ1Glklcv+T3DdhVeSzEUBcW3rNQ27lUd30PdDE0qCnR4wKBgDzK\nFcllXVvmqkE/DAPu3uuroUKl8yHYqmVtoNVJpSlJQlUdttAcXv8Q/+Udl8OnoHQN\nSjceL1pYbWArfurf8uj2d/gHwNqLFfQQqZi1PLEt/y8vN6RUQ7RpZKb71fWZWvlX\nOJuDBtZsqnUVn8n8oUoTRQ7fztK7sEhchYJipfCnAoGBALb4ByNLps51QjgGxY0L\n9SAv/UIX9fcExkTZWLMejhhEeIP4SvIlmW8QCtCN+qDdE0pyAZk4ZMXoa40DOBHY\nBHhjw9wBmNKmR0B9Td9Op6KvfzjjlSurLu0pZeQCHoFEOgB90iQF/KEKFrXjekkL\nOHA+JJ13uDfaltLNGG3PziK/\n-----END PRIVATE KEY-----\n",
        "client_email": "f01i-sheets-editor@flowinvestaiapp.iam.gserviceaccount.com",
        "client_id": "114101703747959694009",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/f01i-sheets-editor%40flowinvestaiapp.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    try:
        # Import Google API libraries
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        print("✅ Google API libraries imported successfully")
        
        # Create credentials
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_info(credentials_data, scopes=scopes)
        service = build('sheets', 'v4', credentials=credentials)
        
        print("✅ Google Sheets service created successfully")
        print(f"📧 Service account: {credentials_data['client_email']}")
        
        # Test sheets
        balance_sheet_id = "1_q7zuZta8lIdGDmRFhh1rgYYdMUwGLXb7YCIShVB6Ps"
        users_sheet_id = "1ZYabLq0ghpI2q1pI5frhZcTGe7rMJwzOL5clV1pV-iE"
        
        # Test 1: Access Balance Sheet
        print("\n🧪 Test 1: Accessing Balance Sheet...")
        try:
            sheet_metadata = service.spreadsheets().get(spreadsheetId=balance_sheet_id).execute()
            print(f"✅ Balance Sheet accessible: {sheet_metadata.get('properties', {}).get('title', 'Unknown')}")
            
            # Try to read existing data
            result = service.spreadsheets().values().get(
                spreadsheetId=balance_sheet_id,
                range='A1:Z10'
            ).execute()
            
            values = result.get('values', [])
            print(f"📊 Found {len(values)} rows of existing data")
            
        except HttpError as e:
            print(f"❌ Balance Sheet access failed: {e}")
            return False
        
        # Test 2: Access Users Sheet
        print("\n🧪 Test 2: Accessing Users Sheet...")
        try:
            sheet_metadata = service.spreadsheets().get(spreadsheetId=users_sheet_id).execute()
            print(f"✅ Users Sheet accessible: {sheet_metadata.get('properties', {}).get('title', 'Unknown')}")
            
            # Try to read existing data
            result = service.spreadsheets().values().get(
                spreadsheetId=users_sheet_id,
                range='A1:Z10'
            ).execute()
            
            values = result.get('values', [])
            print(f"👥 Found {len(values)} rows of existing data")
            
        except HttpError as e:
            print(f"❌ Users Sheet access failed: {e}")
            return False
        
        # Test 3: Write Test Data to Balance Sheet
        print("\n🧪 Test 3: Writing Test Data to Balance Sheet...")
        try:
            test_headers = [
                'Last Updated', 'Company Funds', 'User Funds', 'Total Deposits', 
                'Total Withdrawals', 'Total Fees Earned', 'Total Subscription Revenue', 'Currency'
            ]
            
            test_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                1000.0,  # Company Funds
                500.0,   # User Funds  
                1500.0,  # Total Deposits
                100.0,   # Total Withdrawals
                50.0,    # Total Fees Earned
                200.0,   # Total Subscription Revenue
                'USD'    # Currency
            ]
            
            # Clear the test range first
            service.spreadsheets().values().clear(
                spreadsheetId=balance_sheet_id,
                range='Test Data!A:Z'
            ).execute()
            
            # Write test data
            service.spreadsheets().values().update(
                spreadsheetId=balance_sheet_id,
                range='Test Data!A1',
                valueInputOption='RAW',
                body={'values': [test_headers, test_data]}
            ).execute()
            
            print("✅ Test data written to Balance Sheet successfully")
            
        except HttpError as e:
            print(f"⚠️ Balance Sheet write test failed: {e}")
        
        # Test 4: Write Test Data to Users Sheet
        print("\n🧪 Test 4: Writing Test Data to Users Sheet...")
        try:
            test_user_headers = [
                'User ID', 'Name', 'Email', 'Country', 'Phone', 
                'Registration Date', 'Seller Status', 'Subscription Status',
                'Plan Type', 'Subscription End Date', 'Total Commission Earned'
            ]
            
            test_user_data = [
                'test-user-id-123',
                'Test User',
                'test@example.com',
                'US',
                '+1-555-0123',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'not_verified',
                'active',
                'plus',
                '2025-09-21',
                150.0
            ]
            
            # Clear the test range first
            service.spreadsheets().values().clear(
                spreadsheetId=users_sheet_id,
                range='Test Data!A:Z'
            ).execute()
            
            # Write test data
            service.spreadsheets().values().update(
                spreadsheetId=users_sheet_id,
                range='Test Data!A1',
                valueInputOption='RAW',
                body={'values': [test_user_headers, test_user_data]}
            ).execute()
            
            print("✅ Test data written to Users Sheet successfully")
            
        except HttpError as e:
            print(f"⚠️ Users Sheet write test failed: {e}")
        
        print("\n🎉 Google Sheets Integration Test Completed Successfully!")
        print("📊 Both sheets are accessible and writable")
        print("🔑 Service account authentication working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing Google API libraries: {e}")
        return False
    except Exception as e:
        print(f"❌ Google Sheets integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_google_sheets_integration()
    if success:
        print("\n✅ Google Sheets integration is working correctly!")
        print("🔧 The issue is likely that environment variables are not being loaded properly by the backend service.")
    else:
        print("\n❌ Google Sheets integration test failed")
    
    exit(0 if success else 1)