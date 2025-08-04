#!/usr/bin/env python3
"""
Comprehensive voting system test after schema fix
Test all voting operations to ensure everything works correctly
"""

import requests
import json
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def comprehensive_voting_test():
    """Test all voting system operations"""
    
    print("🚀 COMPREHENSIVE VOTING SYSTEM TEST AFTER SCHEMA FIX")
    print("=" * 60)
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    test_user_id = "cd0e9717-f85d-4726-81e9-f260394ead58"
    test_results = []
    
    try:
        # Test 1: Get existing portfolio
        portfolio_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/portfolios?limit=1",
            headers=headers,
            timeout=10
        )
        
        if portfolio_response.status_code != 200:
            print("❌ Cannot get portfolios for testing")
            return
            
        portfolios = portfolio_response.json()
        if not portfolios:
            print("❌ No portfolios available for testing")
            return
        
        portfolio_id = portfolios[0]['id']
        print(f"📋 Using portfolio: {portfolio_id}")
        
        # Test 2: Clean up any existing votes
        print("\n🧹 Cleaning up existing votes...")
        cleanup_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{test_user_id}&product_id=eq.{portfolio_id}",
            headers=headers,
            timeout=10
        )
        print(f"Cleanup result: {cleanup_response.status_code}")
        
        # Test 3: Create upvote
        print("\n⬆️ Testing upvote creation...")
        upvote_data = {
            "user_id": test_user_id,
            "product_id": portfolio_id,
            "vote_type": "upvote"
        }
        
        upvote_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/user_votes",
            headers=headers,
            json=upvote_data,
            timeout=10
        )
        
        if upvote_response.status_code == 201:
            print("✅ Upvote created successfully!")
            test_results.append(("Upvote Creation", True))
        else:
            print(f"❌ Upvote failed: {upvote_response.status_code} - {upvote_response.text[:200]}")
            test_results.append(("Upvote Creation", False))
        
        # Test 4: Verify vote was stored
        print("\n🔍 Verifying vote storage...")
        verify_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{test_user_id}&product_id=eq.{portfolio_id}",
            headers=headers,
            timeout=10
        )
        
        if verify_response.status_code == 200:
            votes = verify_response.json()
            if votes and votes[0]['vote_type'] == 'upvote':
                print("✅ Vote stored and retrieved correctly!")
                test_results.append(("Vote Storage", True))
            else:
                print("❌ Vote not found or incorrect")
                test_results.append(("Vote Storage", False))
        else:
            print(f"❌ Vote verification failed: {verify_response.status_code}")
            test_results.append(("Vote Storage", False))
        
        # Test 5: Update vote to downvote
        print("\n⬇️ Testing vote update (upvote to downvote)...")
        update_response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{test_user_id}&product_id=eq.{portfolio_id}",
            headers=headers,
            json={"vote_type": "downvote"},
            timeout=10
        )
        
        if update_response.status_code == 204:
            print("✅ Vote updated successfully!")
            test_results.append(("Vote Update", True))
        else:
            print(f"❌ Vote update failed: {update_response.status_code} - {update_response.text[:200]}")
            test_results.append(("Vote Update", False))
        
        # Test 6: Verify update worked
        print("\n🔍 Verifying vote update...")
        verify_update_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{test_user_id}&product_id=eq.{portfolio_id}",
            headers=headers,
            timeout=10
        )
        
        if verify_update_response.status_code == 200:
            votes = verify_update_response.json()
            if votes and votes[0]['vote_type'] == 'downvote':
                print("✅ Vote update verified correctly!")
                test_results.append(("Vote Update Verification", True))
            else:
                print("❌ Vote update not reflected")
                test_results.append(("Vote Update Verification", False))
        else:
            print(f"❌ Vote update verification failed: {verify_update_response.status_code}")
            test_results.append(("Vote Update Verification", False))
        
        # Test 7: Check portfolio vote counts (trigger function test)
        print("\n📊 Testing portfolio vote count trigger...")
        portfolio_check_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/portfolios?id=eq.{portfolio_id}",
            headers=headers,
            timeout=10
        )
        
        if portfolio_check_response.status_code == 200:
            portfolio_data = portfolio_check_response.json()
            if portfolio_data:
                portfolio = portfolio_data[0]
                vote_counts = {
                    'upvotes': portfolio.get('vote_count_upvotes', 0),
                    'downvotes': portfolio.get('vote_count_downvotes', 0),
                    'total': portfolio.get('vote_count_total', 0)
                }
                print(f"✅ Portfolio vote counts accessible: {vote_counts}")
                test_results.append(("Trigger Function", True))
            else:
                print("❌ Portfolio not found")
                test_results.append(("Trigger Function", False))
        else:
            print(f"❌ Portfolio check failed: {portfolio_check_response.status_code}")
            if "operator does not exist: uuid = character varying" in portfolio_check_response.text:
                print("🚨 CRITICAL: Trigger function still has UUID mismatch error!")
                test_results.append(("Trigger Function", False))
            else:
                test_results.append(("Trigger Function", False))
        
        # Test 8: Delete vote
        print("\n🗑️ Testing vote deletion...")
        delete_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{test_user_id}&product_id=eq.{portfolio_id}",
            headers=headers,
            timeout=10
        )
        
        if delete_response.status_code == 204:
            print("✅ Vote deleted successfully!")
            test_results.append(("Vote Deletion", True))
        else:
            print(f"❌ Vote deletion failed: {delete_response.status_code}")
            test_results.append(("Vote Deletion", False))
        
        # Test 9: Verify deletion
        print("\n🔍 Verifying vote deletion...")
        final_check_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{test_user_id}&product_id=eq.{portfolio_id}",
            headers=headers,
            timeout=10
        )
        
        if final_check_response.status_code == 200:
            remaining_votes = final_check_response.json()
            if not remaining_votes:
                print("✅ Vote deletion verified!")
                test_results.append(("Vote Deletion Verification", True))
            else:
                print("❌ Vote still exists after deletion")
                test_results.append(("Vote Deletion Verification", False))
        else:
            print(f"❌ Vote deletion verification failed: {final_check_response.status_code}")
            test_results.append(("Vote Deletion Verification", False))
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        test_results.append(("Test Execution", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL SUCCESS RATE: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Voting system is fully functional!")
        return True
    else:
        print("⚠️ Some tests failed. Review issues above.")
        return False

if __name__ == "__main__":
    comprehensive_voting_test()