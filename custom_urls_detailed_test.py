#!/usr/bin/env python3
"""
Detailed Custom URLs Database Schema Testing
Tests specific database schema elements to identify what's missing
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://foliapp-slugs.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_database_columns():
    """Test if specific columns exist in tables"""
    print("🔍 Testing Database Schema Columns...")
    
    # Test user_bots table for slug column
    try:
        response = requests.get(f"{API_BASE}/urls/public/bots/nonexistent-bot-slug", timeout=10)
        print(f"user_bots table test: HTTP {response.status_code}")
        if response.status_code == 500:
            print(f"   Error details: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test portfolios table for slug column
    try:
        response = requests.get(f"{API_BASE}/urls/public/marketplace/nonexistent-portfolio-slug", timeout=10)
        print(f"portfolios table test: HTTP {response.status_code}")
        if response.status_code == 500:
            print(f"   Error details: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test feed_posts table existence
    try:
        response = requests.get(f"{API_BASE}/urls/public/feed/nonexistent-feed-slug", timeout=10)
        print(f"feed_posts table test: HTTP {response.status_code}")
        if response.status_code == 500:
            print(f"   Error details: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test user_profiles table for display_name uniqueness
    try:
        response = requests.get(f"{API_BASE}/urls/public/user/nonexistent-user", timeout=10)
        print(f"user_profiles table test: HTTP {response.status_code}")
        if response.status_code == 500:
            print(f"   Error details: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

def test_database_functions():
    """Test database functions directly"""
    print("\n🔧 Testing Database Functions...")
    
    # Test validate_url_slug function
    test_cases = [
        {"slug": "test-function", "description": "Basic function test"},
        {"slug": "admin", "description": "Reserved word test"},
        {"slug": "valid-slug-123", "description": "Valid complex slug"},
    ]
    
    for case in test_cases:
        try:
            payload = {"slug": case["slug"]}
            response = requests.post(
                f"{API_BASE}/urls/validate-slug",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {case['description']}: valid={data.get('valid')}, error={data.get('error', 'None')}")
            else:
                print(f"❌ {case['description']}: HTTP {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {case['description']}: Error - {e}")

def test_reserved_words_data():
    """Test reserved words data in detail"""
    print("\n📝 Testing Reserved Words Data...")
    
    try:
        response = requests.get(f"{API_BASE}/urls/reserved-words", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            reserved_words = data.get('reserved_words', {})
            
            print(f"✅ Reserved words endpoint working")
            print(f"   Categories found: {list(reserved_words.keys())}")
            
            for category, words in reserved_words.items():
                print(f"   {category}: {len(words)} words - {words[:5]}{'...' if len(words) > 5 else ''}")
                
        else:
            print(f"❌ Reserved words endpoint failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Reserved words test error: {e}")

def test_slug_generation_edge_cases():
    """Test slug generation with edge cases"""
    print("\n🔧 Testing Slug Generation Edge Cases...")
    
    edge_cases = [
        {"text": "", "description": "Empty string"},
        {"text": "   ", "description": "Only spaces"},
        {"text": "!@#$%^&*()", "description": "Only special characters"},
        {"text": "123", "description": "Only numbers"},
        {"text": "a", "description": "Single character"},
        {"text": "Test Bot With Very Long Name That Exceeds Normal Limits", "description": "Very long text"},
    ]
    
    for case in edge_cases:
        try:
            response = requests.post(
                f"{API_BASE}/urls/generate-slug",
                params={"text": case["text"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                slug = data.get('generated_slug', '')
                print(f"✅ {case['description']}: '{case['text']}' -> '{slug}'")
            elif response.status_code == 400:
                print(f"⚠️  {case['description']}: Expected validation error - {response.text[:100]}")
            else:
                print(f"❌ {case['description']}: HTTP {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {case['description']}: Error - {e}")

def check_existing_data():
    """Check if there's any existing data with slugs"""
    print("\n📊 Checking for Existing Data with Slugs...")
    
    # This is indirect - we can't query the database directly, but we can check
    # if the validation functions work with realistic data
    
    realistic_slugs = [
        "trading-bot-1",
        "high-yield-portfolio", 
        "crypto-strategy",
        "ai-trading-system",
        "market-analysis-bot"
    ]
    
    for slug in realistic_slugs:
        try:
            payload = {"slug": slug}
            response = requests.post(
                f"{API_BASE}/urls/validate-slug",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                is_valid = data.get('valid')
                error = data.get('error', '')
                
                if not is_valid and 'already taken' in error.lower():
                    print(f"📊 Found existing data: '{slug}' is already taken")
                elif is_valid:
                    print(f"✅ Available slug: '{slug}'")
                else:
                    print(f"⚠️  Slug issue: '{slug}' - {error}")
            else:
                print(f"❌ Validation failed for '{slug}': HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking '{slug}': {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("DETAILED CUSTOM URLS DATABASE SCHEMA TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    test_database_columns()
    test_database_functions()
    test_reserved_words_data()
    test_slug_generation_edge_cases()
    check_existing_data()
    
    print("\n" + "=" * 80)
    print("DETAILED TESTING COMPLETE")
    print("=" * 80)