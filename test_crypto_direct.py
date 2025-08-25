#!/usr/bin/env python3
"""
Direct Crypto Payment Testing with Service Role Key
"""

import requests
import json
import time
import uuid
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://dataflow-crypto.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"
ADMIN_KEY = "admin123"

# Direct Supabase access
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

def test_direct_database_access():
    """Test direct database access to crypto_transactions table"""
    print("=== TESTING DIRECT DATABASE ACCESS ===")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # Test table access
    try:
        response = requests.get(f'{SUPABASE_URL}/rest/v1/crypto_transactions?limit=5', headers=headers)
        print(f"✅ crypto_transactions table access: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} existing transactions")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Database access failed: {e}")
    
    # Test direct transaction creation
    try:
        test_transaction = {
            'user_id': TEST_USER_ID,
            'transaction_type': 'deposit',
            'currency': 'USDT',
            'network': 'ERC20',
            'deposit_address': '0xfd5fdd6856ee16e2e908bcea1c015fe7e04cee7b',
            'reference': f'TEST{int(time.time())}',
            'status': 'pending',
            'amount': 0.0
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/crypto_transactions',
            headers=headers,
            json=test_transaction
        )
        
        print(f"✅ Direct transaction creation: Status {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   Created transaction with ID: {data[0]['id']}")
            return data[0]['id']
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Direct transaction creation failed: {e}")
        return None

def test_crypto_endpoints():
    """Test crypto endpoints with backend"""
    print("\n=== TESTING CRYPTO ENDPOINTS ===")
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoTester/1.0'
    })
    
    # Test crypto health
    try:
        response = session.get(f"{BACKEND_URL}/crypto/health")
        print(f"✅ Crypto health: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Mode: {data.get('mode')}, Status: {data.get('status')}")
    except Exception as e:
        print(f"❌ Crypto health failed: {e}")
    
    # Test supported currencies
    try:
        response = session.get(f"{BACKEND_URL}/crypto/supported-currencies")
        print(f"✅ Supported currencies: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            currencies = [c['code'] for c in data.get('currencies', [])]
            print(f"   Currencies: {currencies}")
    except Exception as e:
        print(f"❌ Supported currencies failed: {e}")
    
    # Test deposit address generation
    try:
        payload = {"currency": "USDT", "network": "ERC20"}
        response = session.post(
            f"{BACKEND_URL}/crypto/deposit/address",
            json=payload,
            params={"user_id": TEST_USER_ID}
        )
        
        print(f"✅ Deposit address generation: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   Reference: {data.get('deposit_reference')}")
                print(f"   Address: {data.get('address')}")
                print(f"   Transaction ID: {data.get('transaction_id')}")
                return data.get('deposit_reference'), data.get('transaction_id')
            else:
                print(f"   Error: {data.get('detail')}")
        else:
            print(f"   HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Deposit address generation failed: {e}")
    
    return None, None

def test_manual_confirmation(reference):
    """Test manual confirmation if we have a reference"""
    if not reference:
        print("\n❌ Skipping manual confirmation - no reference available")
        return
    
    print(f"\n=== TESTING MANUAL CONFIRMATION FOR {reference} ===")
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    try:
        response = session.post(
            f"{BACKEND_URL}/crypto/deposit/manual-confirm",
            params={
                "deposit_reference": reference,
                "transaction_hash": f"0x{'a' * 64}",
                "amount": 100.50,
                "admin_key": ADMIN_KEY
            }
        )
        
        print(f"✅ Manual confirmation: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   Confirmed amount: ${data.get('amount')}")
                print(f"   User: {data.get('user_id')}")
            else:
                print(f"   Error: {data.get('detail')}")
        else:
            print(f"   HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Manual confirmation failed: {e}")

def test_transaction_retrieval():
    """Test transaction retrieval endpoints"""
    print(f"\n=== TESTING TRANSACTION RETRIEVAL ===")
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # Test get crypto transactions
    try:
        response = session.get(
            f"{BACKEND_URL}/crypto/transactions",
            params={"user_id": TEST_USER_ID, "limit": 10}
        )
        
        print(f"✅ Get crypto transactions: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                transactions = data.get('transactions', [])
                print(f"   Retrieved {len(transactions)} transactions")
                for tx in transactions[:3]:  # Show first 3
                    print(f"   - {tx.get('currency')} {tx.get('transaction_type')}: {tx.get('status')} (Ref: {tx.get('reference')})")
            else:
                print(f"   Error: {data.get('detail')}")
        else:
            print(f"   HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Get crypto transactions failed: {e}")
    
    # Test get user deposits
    try:
        response = session.get(f"{BACKEND_URL}/crypto/deposits/user/{TEST_USER_ID}")
        
        print(f"✅ Get user deposits: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                deposits = data.get('deposits', [])
                print(f"   Retrieved {len(deposits)} deposits")
            else:
                print(f"   Error: {data.get('detail')}")
        else:
            print(f"   HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Get user deposits failed: {e}")

def main():
    """Main testing function"""
    print("🚀 STARTING DIRECT CRYPTO PAYMENT TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Supabase URL: {SUPABASE_URL}")
    print("=" * 60)
    
    # Test direct database access first
    transaction_id = test_direct_database_access()
    
    # Test crypto endpoints
    reference, api_transaction_id = test_crypto_endpoints()
    
    # Test manual confirmation if we got a reference
    test_manual_confirmation(reference)
    
    # Test transaction retrieval
    test_transaction_retrieval()
    
    print("\n🏁 DIRECT CRYPTO PAYMENT TESTING COMPLETE")

if __name__ == "__main__":
    main()