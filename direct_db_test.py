#!/usr/bin/env python3
"""
Direct Database Query Test for Custom URLs
Tests direct database queries to identify missing columns/tables
"""

import requests
import json

# Configuration
BACKEND_URL = "https://url-wizard.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_direct_database_access():
    """Test direct database access to identify issues"""
    print("🔍 Testing Direct Database Access...")
    
    # Test user_profiles table
    try:
        response = requests.get(f"{API_BASE}/urls/public/user/test-user-that-does-not-exist", timeout=10)
        print(f"user_profiles query: HTTP {response.status_code}")
        if response.status_code == 404:
            print("   ✅ user_profiles table accessible (404 = table exists, no data found)")
        elif response.status_code == 500:
            print(f"   ❌ user_profiles table issue: {response.text}")
    except Exception as e:
        print(f"   ❌ user_profiles error: {e}")
    
    # Test user_bots table with slug column
    try:
        response = requests.get(f"{API_BASE}/urls/public/bots/test-bot-that-does-not-exist", timeout=10)
        print(f"user_bots query: HTTP {response.status_code}")
        if response.status_code == 404:
            print("   ✅ user_bots table with slug column accessible")
        elif response.status_code == 500:
            print(f"   ❌ user_bots table/slug column issue: {response.text}")
    except Exception as e:
        print(f"   ❌ user_bots error: {e}")
    
    # Test portfolios table with slug column
    try:
        response = requests.get(f"{API_BASE}/urls/public/marketplace/test-portfolio-that-does-not-exist", timeout=10)
        print(f"portfolios query: HTTP {response.status_code}")
        if response.status_code == 404:
            print("   ✅ portfolios table with slug column accessible")
        elif response.status_code == 500:
            print(f"   ❌ portfolios table/slug column issue: {response.text}")
    except Exception as e:
        print(f"   ❌ portfolios error: {e}")
    
    # Test feed_posts table
    try:
        response = requests.get(f"{API_BASE}/urls/public/feed/test-feed-that-does-not-exist", timeout=10)
        print(f"feed_posts query: HTTP {response.status_code}")
        if response.status_code == 404:
            print("   ✅ feed_posts table accessible")
        elif response.status_code == 500:
            print(f"   ❌ feed_posts table issue: {response.text}")
    except Exception as e:
        print(f"   ❌ feed_posts error: {e}")

if __name__ == "__main__":
    test_direct_database_access()