#!/usr/bin/env python3
"""
Simple test to check table existence and structure
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def simple_table_check():
    """Check what tables exist and their basic structure"""
    
    print("🔍 CHECKING TABLE EXISTENCE...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    tables_to_check = ['user_votes', 'seller_reviews', 'portfolios', 'user_profiles']
    
    for table in tables_to_check:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/{table}?limit=1",
                headers=headers,
                timeout=10
            )
            
            print(f"Table '{table}': {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"  Sample columns: {list(data[0].keys())}")
                else:
                    print("  Table exists but is empty")
            else:
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Error checking {table}: {e}")
        
        print()

if __name__ == "__main__":
    simple_table_check()