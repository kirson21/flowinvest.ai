#!/usr/bin/env python3
"""
Backend API Testing for Flow Invest OpenAI Format Webhook System
Tests the new OpenAI format webhook and all related functionality.
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

class OpenAIWebhookTester:
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

    def test_openai_format_webhook(self):
        """Test POST /api/ai_news_webhook with new OpenAI format"""
        print("\n🤖 Testing New OpenAI Format Webhook")
        
        # Sample data in OpenAI format as provided in the request
        openai_sample_data = {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "AI Revolution Transforms Financial Markets",
                            "summary": "Cutting-edge artificial intelligence technologies are revolutionizing financial markets with unprecedented speed and accuracy. Machine learning algorithms now process millions of data points in real-time, enabling traders and investors to make more informed decisions. This technological advancement is democratizing access to sophisticated trading strategies and improving market efficiency across global exchanges.",
                            "sentiment_score": 82
                        }
                    }
                }
            ],
            "source": "FinTech AI Weekly",
            "timestamp": "2025-01-11T10:30:00Z"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/ai_news_webhook",
                json=openai_sample_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Verify response structure
                required_fields = ['id', 'title', 'summary', 'sentiment', 'source', 'timestamp', 'created_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify parameter mapping
                    expected_title = openai_sample_data['choices'][0]['message']['content']['title']
                    expected_summary = openai_sample_data['choices'][0]['message']['content']['summary']
                    expected_sentiment = openai_sample_data['choices'][0]['message']['content']['sentiment_score']
                    expected_source = openai_sample_data['source']
                    
                    mapping_correct = (
                        data['title'] == expected_title and
                        data['summary'] == expected_summary and
                        data['sentiment'] == expected_sentiment and
                        data['source'] == expected_source
                    )
                    
                    if mapping_correct:
                        self.log_test("OpenAI format webhook with parameter mapping", True, 
                                    f"Entry created with ID: {data['id']}, all parameters mapped correctly")
                        return data['id']
                    else:
                        self.log_test("OpenAI format webhook with parameter mapping", False, 
                                    "Parameter mapping incorrect")
                else:
                    self.log_test("OpenAI format webhook", False, f"Missing fields in response: {missing_fields}")
            else:
                self.log_test("OpenAI format webhook", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("OpenAI format webhook", False, f"Exception: {str(e)}")
            
        return None

    def test_parameter_mapping_verification(self):
        """Test detailed parameter mapping verification"""
        print("\n🔍 Testing Parameter Mapping Verification")
        
        # Test data with specific values to verify mapping
        test_data = {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "Parameter Mapping Test Title",
                            "summary": "This is a test summary to verify parameter mapping from OpenAI format to internal format.",
                            "sentiment_score": 67
                        }
                    }
                }
            ],
            "source": "Parameter Test Source",
            "timestamp": "2025-01-11T12:15:30Z"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/ai_news_webhook",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Detailed parameter mapping verification
                mapping_tests = [
                    ("title mapping", data.get('title') == test_data['choices'][0]['message']['content']['title']),
                    ("summary mapping", data.get('summary') == test_data['choices'][0]['message']['content']['summary']),
                    ("sentiment_score to sentiment mapping", data.get('sentiment') == test_data['choices'][0]['message']['content']['sentiment_score']),
                    ("source mapping", data.get('source') == test_data['source']),
                    ("timestamp handling", 'timestamp' in data and data['timestamp'] is not None)
                ]
                
                all_mappings_correct = all(test[1] for test in mapping_tests)
                failed_mappings = [test[0] for test in mapping_tests if not test[1]]
                
                if all_mappings_correct:
                    self.log_test("Parameter mapping verification", True, 
                                "All parameter mappings working correctly")
                else:
                    self.log_test("Parameter mapping verification", False, 
                                f"Failed mappings: {', '.join(failed_mappings)}")
            else:
                self.log_test("Parameter mapping verification", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Parameter mapping verification", False, f"Exception: {str(e)}")

    def test_legacy_webhook_endpoint(self):
        """Test POST /api/ai_news_webhook/legacy for backward compatibility"""
        print("\n🔄 Testing Legacy Webhook Endpoint (Backward Compatibility)")
        
        # Sample data in legacy format
        legacy_sample_data = {
            "title": "Legacy Format Test: Blockchain Innovation Drives Market Growth",
            "summary": "Traditional financial institutions are increasingly adopting blockchain technology to enhance security and efficiency in their operations. This shift represents a significant evolution in how financial services are delivered and managed.",
            "sentiment": 75,
            "source": "Blockchain Finance News",
            "timestamp": "2025-01-11T11:00:00Z"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/ai_news_webhook/legacy",
                json=legacy_sample_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Verify response structure
                required_fields = ['id', 'title', 'summary', 'sentiment', 'source', 'timestamp', 'created_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify data matches input
                    data_matches = (
                        data['title'] == legacy_sample_data['title'] and
                        data['summary'] == legacy_sample_data['summary'] and
                        data['sentiment'] == legacy_sample_data['sentiment'] and
                        data['source'] == legacy_sample_data['source']
                    )
                    
                    if data_matches:
                        self.log_test("Legacy webhook endpoint", True, 
                                    f"Legacy format working, entry created with ID: {data['id']}")
                        return data['id']
                    else:
                        self.log_test("Legacy webhook endpoint", False, "Data mismatch in response")
                else:
                    self.log_test("Legacy webhook endpoint", False, f"Missing fields in response: {missing_fields}")
            else:
                self.log_test("Legacy webhook endpoint", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Legacy webhook endpoint", False, f"Exception: {str(e)}")
            
        return None

    def test_webhook_test_endpoint(self):
        """Test GET /api/webhook/test for format documentation"""
        print("\n📚 Testing Webhook Test Endpoint (Format Documentation)")
        
        try:
            response = self.session.get(f"{API_BASE}/webhook/test")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify documentation structure
                required_fields = ['description', 'example_request', 'n8n_mapping']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify example_request has OpenAI format structure
                    example = data.get('example_request', {})
                    has_openai_structure = (
                        'choices' in example and
                        isinstance(example['choices'], list) and
                        len(example['choices']) > 0 and
                        'message' in example['choices'][0] and
                        'content' in example['choices'][0]['message']
                    )
                    
                    if has_openai_structure:
                        self.log_test("Webhook test endpoint", True, 
                                    "Documentation endpoint working with correct OpenAI format structure")
                    else:
                        self.log_test("Webhook test endpoint", False, 
                                    "Documentation missing proper OpenAI format structure")
                else:
                    self.log_test("Webhook test endpoint", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Webhook test endpoint", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Webhook test endpoint", False, f"Exception: {str(e)}")

    def test_openai_format_error_handling(self):
        """Test error handling with malformed OpenAI format"""
        print("\n🚫 Testing OpenAI Format Error Handling")
        
        # Test various malformed OpenAI format scenarios
        malformed_data_sets = [
            # Missing choices
            {
                "source": "Test Source",
                "timestamp": "2025-01-11T10:30:00Z"
            },
            # Empty choices array
            {
                "choices": [],
                "source": "Test Source",
                "timestamp": "2025-01-11T10:30:00Z"
            },
            # Missing message in choice
            {
                "choices": [
                    {
                        "invalid_field": "test"
                    }
                ],
                "source": "Test Source",
                "timestamp": "2025-01-11T10:30:00Z"
            },
            # Missing content in message
            {
                "choices": [
                    {
                        "message": {
                            "invalid_field": "test"
                        }
                    }
                ],
                "source": "Test Source",
                "timestamp": "2025-01-11T10:30:00Z"
            },
            # Invalid sentiment_score
            {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "Test Title",
                                "summary": "Test summary",
                                "sentiment_score": 150  # Invalid: > 100
                            }
                        }
                    }
                ],
                "source": "Test Source",
                "timestamp": "2025-01-11T10:30:00Z"
            }
        ]
        
        for i, malformed_data in enumerate(malformed_data_sets):
            try:
                response = self.session.post(
                    f"{API_BASE}/ai_news_webhook",
                    json=malformed_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [400, 422, 500]:  # Expected error responses
                    self.log_test(f"OpenAI format error handling {i+1}", True, 
                                f"Properly handled malformed data (HTTP {response.status_code})")
                else:
                    self.log_test(f"OpenAI format error handling {i+1}", False, 
                                f"Unexpected response: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"OpenAI format error handling {i+1}", False, f"Exception: {str(e)}")

    def test_data_storage_and_retrieval(self):
        """Test that entries from new format are stored and retrieved correctly"""
        print("\n💾 Testing Data Storage & Retrieval with OpenAI Format")
        
        # Clear existing data first
        try:
            self.session.delete(f"{API_BASE}/feed_entries")
        except:
            pass
        
        # Add entry using OpenAI format
        openai_data = {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "Storage Test: AI-Powered Investment Analytics",
                            "summary": "Advanced AI analytics are providing unprecedented insights into market trends and investment opportunities, helping both individual and institutional investors optimize their portfolios.",
                            "sentiment_score": 88
                        }
                    }
                }
            ],
            "source": "Investment Analytics Today",
            "timestamp": "2025-01-11T14:45:00Z"
        }
        
        try:
            # Add the entry
            post_response = self.session.post(
                f"{API_BASE}/ai_news_webhook",
                json=openai_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if post_response.status_code == 200:
                entry_data = post_response.json()
                entry_id = entry_data['id']
                
                # Retrieve entries and verify
                get_response = self.session.get(f"{API_BASE}/feed_entries")
                
                if get_response.status_code == 200:
                    entries = get_response.json()
                    
                    # Find our entry
                    our_entry = None
                    for entry in entries:
                        if entry.get('id') == entry_id:
                            our_entry = entry
                            break
                    
                    if our_entry:
                        # Verify data integrity
                        expected_title = openai_data['choices'][0]['message']['content']['title']
                        expected_summary = openai_data['choices'][0]['message']['content']['summary']
                        expected_sentiment = openai_data['choices'][0]['message']['content']['sentiment_score']
                        
                        data_integrity = (
                            our_entry['title'] == expected_title and
                            our_entry['summary'] == expected_summary and
                            our_entry['sentiment'] == expected_sentiment and
                            our_entry['source'] == openai_data['source']
                        )
                        
                        if data_integrity:
                            self.log_test("Data storage and retrieval", True, 
                                        "OpenAI format data stored and retrieved correctly")
                        else:
                            self.log_test("Data storage and retrieval", False, 
                                        "Data integrity check failed")
                    else:
                        self.log_test("Data storage and retrieval", False, 
                                    "Entry not found in retrieval")
                else:
                    self.log_test("Data storage and retrieval", False, 
                                f"Failed to retrieve entries: HTTP {get_response.status_code}")
            else:
                self.log_test("Data storage and retrieval", False, 
                            f"Failed to add entry: HTTP {post_response.status_code}")
                
        except Exception as e:
            self.log_test("Data storage and retrieval", False, f"Exception: {str(e)}")

    def test_translation_with_openai_format(self):
        """Test that translation system works with new format"""
        print("\n🌐 Testing Translation System with OpenAI Format")
        
        # Clear existing data
        try:
            self.session.delete(f"{API_BASE}/feed_entries")
        except:
            pass
        
        # Add entry using OpenAI format
        openai_data = {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "Translation Test: Fintech Innovation Accelerates",
                            "summary": "Financial technology companies are rapidly developing new solutions that enhance user experience and improve financial accessibility for consumers worldwide.",
                            "sentiment_score": 79
                        }
                    }
                }
            ],
            "source": "Fintech Innovation Weekly",
            "timestamp": "2025-01-11T15:30:00Z"
        }
        
        try:
            # Add the entry
            post_response = self.session.post(
                f"{API_BASE}/ai_news_webhook",
                json=openai_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if post_response.status_code == 200:
                # Test English retrieval
                en_response = self.session.get(f"{API_BASE}/feed_entries?language=en")
                
                if en_response.status_code == 200:
                    en_data = en_response.json()
                    if en_data and len(en_data) > 0:
                        en_entry = en_data[0]
                        
                        # Verify English entry structure
                        if (en_entry.get('language') == 'en' and 
                            en_entry.get('is_translated') == False):
                            self.log_test("English retrieval with OpenAI format", True, 
                                        "English entries properly marked as non-translated")
                            
                            # Test Russian translation
                            ru_response = self.session.get(f"{API_BASE}/feed_entries?language=ru")
                            
                            if ru_response.status_code == 200:
                                ru_data = ru_response.json()
                                if ru_data and len(ru_data) > 0:
                                    ru_entry = ru_data[0]
                                    
                                    # Check if translation was attempted or fallback occurred
                                    if ru_entry.get('language') == 'ru' and ru_entry.get('is_translated'):
                                        self.log_test("Russian translation with OpenAI format", True, 
                                                    "Translation system working with OpenAI format")
                                    elif ru_entry.get('language') == 'en' and not ru_entry.get('is_translated'):
                                        self.log_test("Russian translation with OpenAI format", True, 
                                                    "Translation fallback working correctly")
                                    else:
                                        self.log_test("Russian translation with OpenAI format", False, 
                                                    "Unexpected translation result")
                                else:
                                    self.log_test("Russian translation with OpenAI format", False, 
                                                "No Russian data returned")
                            else:
                                self.log_test("Russian translation with OpenAI format", False, 
                                            f"Russian request failed: HTTP {ru_response.status_code}")
                        else:
                            self.log_test("English retrieval with OpenAI format", False, 
                                        "English entry structure incorrect")
                    else:
                        self.log_test("English retrieval with OpenAI format", False, 
                                    "No English data returned")
                else:
                    self.log_test("English retrieval with OpenAI format", False, 
                                f"English request failed: HTTP {en_response.status_code}")
            else:
                self.log_test("Translation test setup", False, 
                            f"Failed to add entry: HTTP {post_response.status_code}")
                
        except Exception as e:
            self.log_test("Translation with OpenAI format", False, f"Exception: {str(e)}")

    def test_feed_retrieval_shows_new_entries(self):
        """Test that feed retrieval shows entries from new format properly"""
        print("\n📋 Testing Feed Retrieval Shows New Entries")
        
        # Clear existing data
        try:
            self.session.delete(f"{API_BASE}/feed_entries")
        except:
            pass
        
        # Add multiple entries using OpenAI format
        test_entries = [
            {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "Feed Test 1: Market Volatility Analysis",
                                "summary": "Recent market analysis shows increased volatility in tech stocks as investors reassess valuations.",
                                "sentiment_score": 45
                            }
                        }
                    }
                ],
                "source": "Market Analysis Pro",
                "timestamp": "2025-01-11T16:00:00Z"
            },
            {
                "choices": [
                    {
                        "message": {
                            "content": {
                                "title": "Feed Test 2: Cryptocurrency Adoption Grows",
                                "summary": "Major corporations continue to adopt cryptocurrency payments, driving mainstream acceptance.",
                                "sentiment_score": 85
                            }
                        }
                    }
                ],
                "source": "Crypto Business News",
                "timestamp": "2025-01-11T16:15:00Z"
            }
        ]
        
        added_count = 0
        for entry in test_entries:
            try:
                response = self.session.post(
                    f"{API_BASE}/ai_news_webhook",
                    json=entry,
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 200:
                    added_count += 1
            except Exception as e:
                print(f"   ⚠️ Failed to add entry: {e}")
        
        # Retrieve and verify
        try:
            response = self.session.get(f"{API_BASE}/feed_entries")
            
            if response.status_code == 200:
                entries = response.json()
                
                if len(entries) >= added_count:
                    # Verify entries have proper structure
                    valid_entries = 0
                    for entry in entries:
                        required_fields = ['id', 'title', 'summary', 'sentiment', 'source', 'timestamp', 'created_at', 'language', 'is_translated']
                        if all(field in entry for field in required_fields):
                            valid_entries += 1
                    
                    if valid_entries >= added_count:
                        self.log_test("Feed retrieval shows new entries", True, 
                                    f"Retrieved {len(entries)} entries, {valid_entries} with proper structure")
                    else:
                        self.log_test("Feed retrieval shows new entries", False, 
                                    f"Only {valid_entries} entries have proper structure")
                else:
                    self.log_test("Feed retrieval shows new entries", False, 
                                f"Expected {added_count} entries, got {len(entries)}")
            else:
                self.log_test("Feed retrieval shows new entries", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Feed retrieval shows new entries", False, f"Exception: {str(e)}")

    def run_openai_tests(self):
        """Run all OpenAI format webhook tests"""
        print("🚀 Starting OpenAI Format Webhook System Tests")
        print("=" * 60)
        
        # Test new OpenAI format webhook
        self.test_openai_format_webhook()
        
        # Test parameter mapping verification
        self.test_parameter_mapping_verification()
        
        # Test legacy endpoint for backward compatibility
        self.test_legacy_webhook_endpoint()
        
        # Test enhanced API features
        self.test_webhook_test_endpoint()
        
        # Test error handling with malformed OpenAI format
        self.test_openai_format_error_handling()
        
        # Test data storage and retrieval
        self.test_data_storage_and_retrieval()
        
        # Test translation system with new format
        self.test_translation_with_openai_format()
        
        # Test feed retrieval shows new entries properly
        self.test_feed_retrieval_shows_new_entries()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 OPENAI FORMAT WEBHOOK TEST SUMMARY")
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
    tester = OpenAIWebhookTester()
    success = tester.run_openai_tests()
    
    if success:
        print("\n🎉 All OpenAI format webhook tests passed!")
        exit(0)
    else:
        print("\n💥 Some tests failed. Check the details above.")
        exit(1)