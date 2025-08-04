#!/usr/bin/env python3
"""
Apply database schema fix for user_votes.product_id column type
Fix PostgreSQL UUID vs VARCHAR type mismatch in voting system
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def apply_schema_fix():
    """Apply the schema fix using Supabase RPC call"""
    
    print("🔧 APPLYING SCHEMA FIX FOR user_votes.product_id...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Step 1: Check current schema
    print("📋 Checking current schema...")
    schema_query = """
    SELECT column_name, data_type FROM information_schema.columns 
    WHERE table_name = 'user_votes' AND column_name = 'product_id';
    """
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"sql": schema_query},
            timeout=30
        )
        print(f"Schema check response: {response.status_code}")
        if response.status_code == 200:
            print(f"Current schema: {response.text}")
    except Exception as e:
        print(f"Schema check failed: {e}")
    
    # Step 2: Apply the fix using raw SQL
    print("🔧 Applying schema fix...")
    
    fix_sql = """
    -- Drop foreign key constraint on product_id
    ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_product_id_fkey;
    
    -- Convert product_id from VARCHAR to UUID
    ALTER TABLE user_votes ALTER COLUMN product_id TYPE UUID USING product_id::UUID;
    
    -- Add foreign key constraint back
    ALTER TABLE user_votes ADD CONSTRAINT user_votes_product_id_fkey 
    FOREIGN KEY (product_id) REFERENCES portfolios(id) ON DELETE CASCADE;
    
    -- Force schema reload
    NOTIFY pgrst, 'reload schema';
    """
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"sql": fix_sql},
            timeout=30
        )
        
        print(f"Schema fix response: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Schema fix applied successfully!")
        else:
            print(f"❌ Schema fix failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error applying schema fix: {e}")
    
    # Step 3: Verify the fix
    print("🔍 Verifying schema fix...")
    
    verify_query = """
    SELECT column_name, data_type FROM information_schema.columns 
    WHERE table_name = 'user_votes' AND column_name = 'product_id';
    """
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"sql": verify_query},
            timeout=30
        )
        
        print(f"Verification response: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Verified schema: {response.text}")
        else:
            print(f"❌ Verification failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    apply_schema_fix()