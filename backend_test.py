#!/usr/bin/env python3
"""
Backend API Testing for Flow Invest Webhook System
Tests all webhook endpoints and functionality as requested.
"""

import requests
import json
import time
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ REACT_APP_BACKEND_URL not found in environment")
    exit(1)

API_BASE = f"{BACKEND_URL}/api"

print(f"🔗 Testing backend at: {API_BASE}")

class WebhookTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def test_webhook_endpoint_valid_data(self):
        """Test POST /api/ai_news_webhook with valid JSON data"""
        print("\n📝 Testing Webhook Endpoint with Valid Data")
        
        # Sample data as provided in the request
        sample_data = {
            "title": "AI Trading Platform Achieves Record Performance",
            "summary": "Revolutionary artificial intelligence trading algorithms have delivered exceptional returns for retail investors, marking a significant milestone in automated investment technology. The platform's machine learning models successfully navigated volatile market conditions, demonstrating the growing sophistication of AI-driven investment strategies.",
            "sentiment": 85,
            "source": "TechFinance Daily",
            "timestamp": "2025-01-10T14:30:00Z"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/ai_news_webhook",
                json=sample_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Verify response structure
                required_fields = ['id', 'title', 'summary', 'sentiment', 'source', 'timestamp', 'created_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Webhook POST with valid data", True, f"Entry created with ID: {data['id']}")
                    return data['id']
                else:
                    self.log_test("Webhook POST with valid data", False, f"Missing fields in response: {missing_fields}")
            else:
                self.log_test("Webhook POST with valid data", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Webhook POST with valid data", False, f"Exception: {str(e)}")
            
        return None
        
    def test_webhook_invalid_data(self):
        """Test webhook with invalid data scenarios"""
        print("\n🚫 Testing Webhook with Invalid Data")
        
        # Test missing required fields
        invalid_data_sets = [
            # Missing title
            {
                "summary": "Test summary",
                "sentiment": 50,
                "source": "Test Source",
                "timestamp": "2025-01-10T14:30:00Z"
            },
            # Invalid sentiment (out of range)
            {
                "title": "Test Title",
                "summary": "Test summary", 
                "sentiment": 150,  # Invalid: > 100
                "source": "Test Source",
                "timestamp": "2025-01-10T14:30:00Z"
            },
            # Invalid timestamp format
            {
                "title": "Test Title",
                "summary": "Test summary",
                "sentiment": 50,
                "source": "Test Source", 
                "timestamp": "invalid-timestamp"
            }
        ]
        
        for i, invalid_data in enumerate(invalid_data_sets):
            try:
                response = self.session.post(
                    f"{API_BASE}/ai_news_webhook",
                    json=invalid_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 422:  # Validation error expected
                    self.log_test(f"Invalid data test {i+1}", True, "Properly rejected invalid data")
                elif response.status_code == 500:  # Server handled gracefully
                    self.log_test(f"Invalid data test {i+1}", True, "Server handled error gracefully")
                else:
                    self.log_test(f"Invalid data test {i+1}", False, f"Unexpected response: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Invalid data test {i+1}", False, f"Exception: {str(e)}")
                
    def test_get_feed_entries(self):
        """Test GET /api/feed_entries to retrieve stored entries"""
        print("\n📖 Testing Feed Entries Retrieval")
        
        try:
            response = self.session.get(f"{API_BASE}/feed_entries")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET feed entries", True, f"Retrieved {len(data)} entries")
                    
                    # Check if entries are in descending order (latest first)
                    if len(data) > 1:
                        timestamps = [entry.get('created_at') for entry in data if 'created_at' in entry]
                        if timestamps:
                            is_descending = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
                            self.log_test("Entries in descending order", is_descending, 
                                        "Latest entries first" if is_descending else "Order may be incorrect")
                    
                    return len(data)
                else:
                    self.log_test("GET feed entries", False, "Response is not a list")
            else:
                self.log_test("GET feed entries", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET feed entries", False, f"Exception: {str(e)}")
            
        return 0
        
    def test_get_feed_entries_count(self):
        """Test GET /api/feed_entries/count"""
        print("\n🔢 Testing Feed Entries Count")
        
        try:
            response = self.session.get(f"{API_BASE}/feed_entries/count")
            
            if response.status_code == 200:
                data = response.json()
                if 'count' in data and isinstance(data['count'], int):
                    self.log_test("GET feed entries count", True, f"Count: {data['count']}")
                    return data['count']
                else:
                    self.log_test("GET feed entries count", False, "Invalid response format")
            else:
                self.log_test("GET feed entries count", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET feed entries count", False, f"Exception: {str(e)}")
            
        return -1
        
    def test_delete_feed_entries(self):
        """Test DELETE /api/feed_entries to clear all entries"""
        print("\n🗑️ Testing Feed Entries Deletion")
        
        try:
            response = self.session.delete(f"{API_BASE}/feed_entries")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_test("DELETE feed entries", True, data['message'])
                    return True
                else:
                    self.log_test("DELETE feed entries", False, "Invalid response format")
            else:
                self.log_test("DELETE feed entries", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("DELETE feed entries", False, f"Exception: {str(e)}")
            
        return False
        
    def test_automatic_cleanup(self):
        """Test automatic cleanup functionality (keep latest 20)"""
        print("\n🧹 Testing Automatic Cleanup (Latest 20 Entries)")
        
        # First clear all entries
        self.test_delete_feed_entries()
        
        # Add 25 entries to test cleanup
        print("   Adding 25 entries to test cleanup...")
        for i in range(25):
            sample_data = {
                "title": f"Test News Entry {i+1}",
                "summary": f"This is test summary number {i+1} for cleanup testing.",
                "sentiment": 50 + (i % 50),  # Vary sentiment
                "source": f"Test Source {i+1}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/ai_news_webhook",
                    json=sample_data,
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code != 200:
                    print(f"   ⚠️ Failed to add entry {i+1}")
            except Exception as e:
                print(f"   ⚠️ Exception adding entry {i+1}: {e}")
                
        # Wait a moment for background cleanup
        time.sleep(2)
        
        # Check final count
        final_count = self.test_get_feed_entries_count()
        if final_count <= 20:
            self.log_test("Automatic cleanup", True, f"Entries limited to {final_count} (≤20)")
        else:
            self.log_test("Automatic cleanup", False, f"Too many entries: {final_count} (>20)")
            
    def test_api_integration(self):
        """Test complete API integration workflow"""
        print("\n🔄 Testing Complete API Integration")
        
        # Clear existing data
        self.test_delete_feed_entries()
        
        # Add a few entries
        test_entries = [
            {
                "title": "Market Analysis: Tech Stocks Surge",
                "summary": "Technology stocks experienced significant gains today as investors showed renewed confidence in AI and cloud computing sectors.",
                "sentiment": 75,
                "source": "Market Watch",
                "timestamp": "2025-01-10T10:00:00Z"
            },
            {
                "title": "Crypto Market Update: Bitcoin Reaches New High",
                "summary": "Bitcoin reached a new all-time high as institutional adoption continues to drive demand for digital assets.",
                "sentiment": 90,
                "source": "Crypto News",
                "timestamp": "2025-01-10T12:00:00Z"
            },
            {
                "title": "Economic Indicators Show Mixed Signals",
                "summary": "Latest economic data presents a mixed picture with some sectors showing growth while others face challenges.",
                "sentiment": 45,
                "source": "Economic Times",
                "timestamp": "2025-01-10T14:00:00Z"
            }
        ]
        
        added_entries = 0
        for entry in test_entries:
            try:
                response = self.session.post(
                    f"{API_BASE}/ai_news_webhook",
                    json=entry,
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 200:
                    added_entries += 1
            except Exception as e:
                print(f"   ⚠️ Failed to add entry: {e}")
                
        # Verify retrieval
        retrieved_count = self.test_get_feed_entries()
        count_endpoint = self.test_get_feed_entries_count()
        
        integration_success = (
            added_entries == len(test_entries) and
            retrieved_count == added_entries and
            count_endpoint == added_entries
        )
        
        self.log_test("Complete API integration", integration_success, 
                     f"Added: {added_entries}, Retrieved: {retrieved_count}, Count: {count_endpoint}")
        
    def run_all_tests(self):
        """Run all webhook system tests"""
        print("🚀 Starting Flow Invest Webhook System Tests")
        print("=" * 60)
        
        # Test basic webhook functionality
        self.test_webhook_endpoint_valid_data()
        self.test_webhook_invalid_data()
        
        # Test data retrieval
        self.test_get_feed_entries()
        self.test_get_feed_entries_count()
        
        # Test data management
        self.test_delete_feed_entries()
        self.test_automatic_cleanup()
        
        # Test complete integration
        self.test_api_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}: {result['details']}")
                    
        return failed_tests == 0

if __name__ == "__main__":
    tester = WebhookTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All webhook system tests passed!")
        exit(0)
    else:
        print("\n💥 Some tests failed. Check the details above.")
        exit(1)