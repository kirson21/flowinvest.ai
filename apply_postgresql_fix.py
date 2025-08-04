#!/usr/bin/env python3
"""
Apply database schema fix using direct PostgreSQL connection
Fix PostgreSQL UUID vs VARCHAR type mismatch in voting system
"""

import psycopg2
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv('/app/backend/.env')

def get_db_connection():
    """Get PostgreSQL connection from Supabase URL"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    # Parse Supabase URL to get database connection info
    # Supabase PostgreSQL connection format: postgresql://postgres:[password]@[host]:5432/postgres
    
    # For Supabase, the connection is typically:
    parsed = urlparse(supabase_url)
    host = parsed.hostname
    
    # The database connection uses a different port and credentials
    db_host = host
    db_port = 5432
    db_name = "postgres"
    db_user = "postgres"
    
    # For this script, we'll need the actual database password
    # This is typically different from the service key
    print(f"Host: {db_host}")
    print("Note: This script requires the actual PostgreSQL password, not the service key")
    print("You would need to get this from your Supabase dashboard under Settings > Database")
    
    return None  # Cannot proceed without actual password

def apply_schema_fix():
    """Apply the schema fix using direct PostgreSQL connection"""
    
    print("🔧 ATTEMPTING SCHEMA FIX WITH POSTGRESQL CONNECTION...")
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Cannot establish database connection")
            print("Alternative approach needed...")
            return False
            
        cursor = conn.cursor()
        
        # Apply the fix
        fix_sql = """
        -- Drop foreign key constraint on product_id
        ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_product_id_fkey;
        
        -- Convert product_id from VARCHAR to UUID
        ALTER TABLE user_votes ALTER COLUMN product_id TYPE UUID USING product_id::UUID;
        
        -- Add foreign key constraint back
        ALTER TABLE user_votes ADD CONSTRAINT user_votes_product_id_fkey 
        FOREIGN KEY (product_id) REFERENCES portfolios(id) ON DELETE CASCADE;
        """
        
        cursor.execute(fix_sql)
        conn.commit()
        
        print("✅ Schema fix applied successfully!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying schema fix: {e}")
        return False

def try_alternative_approach():
    """Try alternative approach using Supabase API with raw SQL"""
    
    print("🔧 TRYING ALTERNATIVE APPROACH...")
    
    # Let's try using the SQL editor endpoint if it exists
    import requests
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Try using the edge functions or database functions
    # This is a workaround approach
    
    print("Alternative approaches:")
    print("1. Manual execution through Supabase Dashboard SQL editor")
    print("2. Create a database function to execute the schema change")
    print("3. Use database migration tools")
    
    return False

if __name__ == "__main__":
    print("🚀 APPLYING SCHEMA FIX FOR VOTING SYSTEM...")
    
    # Try direct connection first
    success = apply_schema_fix()
    
    if not success:
        # Try alternative approach
        try_alternative_approach()
        
        print("\n📋 MANUAL FIX INSTRUCTIONS:")
        print("Since direct database access is limited, please execute this SQL manually:")
        print("1. Go to your Supabase Dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Execute the following SQL:")
        print()
        print("-- Fix user_votes.product_id column type")
        print("ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_product_id_fkey;")
        print("ALTER TABLE user_votes ALTER COLUMN product_id TYPE UUID USING product_id::UUID;")
        print("ALTER TABLE user_votes ADD CONSTRAINT user_votes_product_id_fkey")
        print("FOREIGN KEY (product_id) REFERENCES portfolios(id) ON DELETE CASCADE;")
        print()
        print("4. This will fix the 'operator does not exist: uuid = character varying' error")