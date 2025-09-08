#!/usr/bin/env python3
"""
Database Schema Verification Test
Check if the custom_urls_schema.sql has been applied to the database
"""

import requests
import json

# Configuration
BACKEND_URL = "https://ai-flow-invest.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_database_schema():
    """Test if database schema has been applied"""
    print("=" * 60)
    print("DATABASE SCHEMA VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Check if reserved_words table exists and has data
    print("1. Testing reserved_words table...")
    try:
        response = requests.get(f"{API_BASE}/urls/reserved-words", timeout=10)
        if response.status_code == 200:
            data = response.json()
            reserved_words = data.get('reserved_words', {})
            total_words = sum(len(words) for words in reserved_words.values())
            print(f"   ✅ Table exists, contains {total_words} words")
            if total_words == 0:
                print("   ⚠️  WARNING: Table is empty - schema may not be fully applied")
        else:
            print(f"   ❌ Table access failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check if validation functions exist
    print("\n2. Testing database validation functions...")
    try:
        payload = {"slug": "test"}
        response = requests.post(
            f"{API_BASE}/urls/validate-slug",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            print("   ✅ Validation functions working")
        else:
            print(f"   ❌ Validation functions failed: HTTP {response.status_code}")
            print(f"      Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check if user_bots has slug column
    print("\n3. Testing user_bots table schema...")
    try:
        response = requests.get(f"{API_BASE}/urls/public/bots/test", timeout=10)
        if response.status_code == 404:
            print("   ✅ user_bots table has slug column (404 = no data, but column exists)")
        elif response.status_code == 500:
            print("   ❌ user_bots table missing slug column (500 = schema error)")
        else:
            print(f"   ? Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check if portfolios has slug column
    print("\n4. Testing portfolios table schema...")
    try:
        response = requests.get(f"{API_BASE}/urls/public/marketplace/test", timeout=10)
        if response.status_code == 404:
            print("   ✅ portfolios table has slug column (404 = no data, but column exists)")
        elif response.status_code == 500:
            print("   ❌ portfolios table missing slug column (500 = schema error)")
        else:
            print(f"   ? Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Check if feed_posts table exists
    print("\n5. Testing feed_posts table...")
    try:
        response = requests.get(f"{API_BASE}/urls/public/feed/test", timeout=10)
        if response.status_code == 404:
            print("   ✅ feed_posts table exists (404 = no data, but table exists)")
        elif response.status_code == 500:
            print("   ❌ feed_posts table does not exist (500 = table missing)")
        else:
            print(f"   ? Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("If you see multiple ❌ errors above, the custom_urls_schema.sql")
    print("has NOT been applied to the Supabase database.")
    print("The schema file exists but needs to be executed manually.")
    print("=" * 60)

if __name__ == "__main__":
    test_database_schema()