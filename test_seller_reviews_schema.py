#!/usr/bin/env python3
"""
Simple SQL Test for Seller Reviews System - Direct Supabase Schema Check
Similar to voting system diagnosis - check table structure and basic operations
"""

import os
import psycopg2
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def test_seller_reviews_schema():
    """Direct PostgreSQL connection to test seller_reviews table"""
    
    # Get connection details from environment
    supabase_url = os.getenv('SUPABASE_URL', '')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY', '')
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase credentials in environment")
        return
    
    # Extract connection details from Supabase URL
    # Format: https://PROJECT.supabase.co
    project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
    
    try:
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(
            host=f"{project_id}.supabase.co",
            database="postgres",
            user="postgres",
            password=supabase_service_key,
            port="5432"
        )
        
        cursor = conn.cursor()
        print("✅ Connected to Supabase PostgreSQL")
        
        # Test 1: Check if seller_reviews table exists
        print("\n=== TESTING SELLER_REVIEWS TABLE STRUCTURE ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'seller_reviews';
        """)
        
        table_exists = cursor.fetchone()
        if table_exists:
            print("✅ seller_reviews table exists")
        else:
            print("❌ seller_reviews table does NOT exist")
            return
        
        # Test 2: Check table schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'seller_reviews'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 SELLER_REVIEWS TABLE SCHEMA:")
        for column in columns:
            print(f"   {column[0]}: {column[1]} ({'nullable' if column[2] == 'YES' else 'not null'}) {f'default: {column[3]}' if column[3] else ''}")
        
        # Test 3: Check for foreign key constraints
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'seller_reviews';
        """)
        
        fk_constraints = cursor.fetchall()
        print("\n🔗 FOREIGN KEY CONSTRAINTS:")
        if fk_constraints:
            for fk in fk_constraints:
                print(f"   {fk[2]} -> {fk[3]}.{fk[4]} (constraint: {fk[0]})")
        else:
            print("   No foreign key constraints found")
        
        # Test 4: Check for existing data
        cursor.execute("SELECT COUNT(*) FROM seller_reviews;")
        count = cursor.fetchone()[0]
        print(f"\n📊 EXISTING RECORDS: {count} reviews in table")
        
        # Test 5: Try to insert a test review
        print("\n=== TESTING INSERT OPERATION ===")
        test_review_id = str(uuid.uuid4())
        test_seller_id = "cd0e9717-f85d-4726-81e9-f260394ead58"  # Super admin ID
        test_product_id = str(uuid.uuid4())
        
        try:
            cursor.execute("""
                INSERT INTO seller_reviews (id, seller_id, product_id, user_id, rating, comment, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (test_review_id, test_seller_id, test_product_id, test_seller_id, 5, "Test review"))
            
            conn.commit()
            print("✅ INSERT operation successful")
            
            # Clean up test data
            cursor.execute("DELETE FROM seller_reviews WHERE id = %s", (test_review_id,))
            conn.commit()
            print("✅ Test data cleaned up")
            
        except Exception as insert_error:
            conn.rollback()
            print(f"❌ INSERT operation failed: {insert_error}")
            print(f"   Error type: {type(insert_error).__name__}")
            
            # Check specific error details
            if "violates foreign key constraint" in str(insert_error):
                print("   🔍 FOREIGN KEY CONSTRAINT VIOLATION DETECTED")
                print("   This means seller_id, product_id, or user_id references don't exist")
            elif "operator does not exist" in str(insert_error):
                print("   🔍 DATA TYPE MISMATCH DETECTED")
                print("   Similar to voting system - UUID/VARCHAR type issue")
        
        # Test 6: Check referenced tables exist
        print("\n=== CHECKING REFERENCED TABLES ===")
        
        # Check if portfolios table exists (for product_id FK)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'portfolios';
        """)
        if cursor.fetchone():
            print("✅ portfolios table exists (for product_id references)")
        else:
            print("❌ portfolios table missing (needed for product_id FK)")
        
        # Check if auth.users exists (for user_id FK)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'auth' 
            AND table_name = 'users';
        """)
        if cursor.fetchone():
            print("✅ auth.users table exists (for user_id references)")
        else:
            print("❌ auth.users table missing (needed for user_id FK)")
        
        conn.close()
        print("\n🔍 DIAGNOSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_seller_reviews_schema()