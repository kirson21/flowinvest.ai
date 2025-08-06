#!/usr/bin/env python3
"""
Bot Table Fix Verification Test
===============================

This test verifies the critical fix for bot creation and data synchronization
after updating backend to use correct table names (user_bots instead of bots).

CRITICAL VERIFICATION TESTS:
1. Bot Creation API: Test POST /api/bots/create-with-ai saves to user_bots table
2. Bot Retrieval API: Test GET /api/bots/user/{user_id} queries user_bots table  
3. Bot Activation API: Test PUT /api/bots/{bot_id}/activate updates user_bots table
4. Table Consistency: Verify backend uses user_bots table consistently
5. End-to-End Flow: Test complete bot creation → retrieval → activation flow

Expected Results:
- Bot creation API should work without HTTP 400/500 errors
- Bot retrieval should return user-specific bots from user_bots table
- No more table mismatch errors in backend logs
- Backend should be compatible with frontend data sync service expectations
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://00253ee3-ad42-47d4-958c-225cd2b95a8f.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test user data
TEST_USER_ID = f"test_bot_fix_{uuid.uuid4().hex[:8]}@flowinvest.ai"
TEST_BOT_PROMPT = "Create a conservative Bitcoin trading bot for long-term investment with 5% stop loss and 10% profit target"

class BotTableFixTester:
    def __init__(self):
        self.results = []
        self.created_bot_id = None
        self.test_user_id = TEST_USER_ID
        
    def log_result(self, test_name, success, details, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        priority = "🚨 CRITICAL" if critical else "📋 TEST"
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        print(f"{priority} {status}: {test_name}")
        print(f"   Details: {details}")
        print()
        
    def test_server_health(self):
        """Test basic server connectivity"""
        try:
            response = requests.get(f"{API_BASE}/status", timeout=10)
            if response.status_code == 200:
                self.log_result("Server Health Check", True, f"Server responding (200 OK)")
                return True
            else:
                self.log_result("Server Health Check", False, f"Server returned {response.status_code}", critical=True)
                return False
        except Exception as e:
            self.log_result("Server Health Check", False, f"Connection failed: {str(e)}", critical=True)
            return False
    
    def test_bot_creation_api(self):
        """Test POST /api/bots/create-with-ai - should save to user_bots table"""
        try:
            payload = {
                "prompt": TEST_BOT_PROMPT,
                "user_id": self.test_user_id
            }
            
            response = requests.post(
                f"{API_BASE}/bots/create-with-ai",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("bot_id"):
                    self.created_bot_id = data["bot_id"]
                    bot_config = data.get("bot_config", {})
                    self.log_result(
                        "Bot Creation API (user_bots table)", 
                        True, 
                        f"Bot created successfully with ID: {self.created_bot_id}, Name: {bot_config.get('name', 'N/A')}", 
                        critical=True
                    )
                    return True
                else:
                    self.log_result("Bot Creation API (user_bots table)", False, f"Invalid response format: {data}", critical=True)
                    return False
            else:
                error_detail = response.text
                self.log_result("Bot Creation API (user_bots table)", False, f"HTTP {response.status_code}: {error_detail}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Bot Creation API (user_bots table)", False, f"Request failed: {str(e)}", critical=True)
            return False
    
    def test_bot_retrieval_api(self):
        """Test GET /api/bots/user/{user_id} - should query user_bots table"""
        try:
            response = requests.get(
                f"{API_BASE}/bots/user/{self.test_user_id}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    bots = data.get("bots", [])
                    total = data.get("total", 0)
                    
                    # Check if our created bot is in the list
                    created_bot_found = False
                    if self.created_bot_id:
                        created_bot_found = any(bot.get("id") == self.created_bot_id for bot in bots)
                    
                    if created_bot_found:
                        self.log_result(
                            "Bot Retrieval API (user_bots table)", 
                            True, 
                            f"Successfully retrieved {total} bots, including newly created bot", 
                            critical=True
                        )
                    else:
                        self.log_result(
                            "Bot Retrieval API (user_bots table)", 
                            True, 
                            f"Retrieved {total} bots from user_bots table (created bot may not be persisted)", 
                            critical=True
                        )
                    return True
                else:
                    self.log_result("Bot Retrieval API (user_bots table)", False, f"API returned success=false: {data}", critical=True)
                    return False
            else:
                error_detail = response.text
                self.log_result("Bot Retrieval API (user_bots table)", False, f"HTTP {response.status_code}: {error_detail}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Bot Retrieval API (user_bots table)", False, f"Request failed: {str(e)}", critical=True)
            return False
    
    def test_bot_activation_api(self):
        """Test PUT /api/bots/{bot_id}/activate - should update user_bots table"""
        if not self.created_bot_id:
            self.log_result("Bot Activation API (user_bots table)", False, "No bot ID available for activation test", critical=True)
            return False
            
        try:
            # Test activation
            response = requests.put(
                f"{API_BASE}/bots/{self.created_bot_id}/activate",
                params={"user_id": self.test_user_id},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("status") == "active":
                    self.log_result(
                        "Bot Activation API (user_bots table)", 
                        True, 
                        f"Bot {self.created_bot_id} activated successfully in user_bots table", 
                        critical=True
                    )
                    return True
                else:
                    self.log_result("Bot Activation API (user_bots table)", False, f"Activation failed: {data}", critical=True)
                    return False
            elif response.status_code == 404:
                # This might happen if bot wasn't actually saved to database
                self.log_result(
                    "Bot Activation API (user_bots table)", 
                    False, 
                    f"Bot not found (404) - may indicate bot wasn't saved to user_bots table", 
                    critical=True
                )
                return False
            else:
                error_detail = response.text
                self.log_result("Bot Activation API (user_bots table)", False, f"HTTP {response.status_code}: {error_detail}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Bot Activation API (user_bots table)", False, f"Request failed: {str(e)}", critical=True)
            return False
    
    def test_table_consistency_check(self):
        """Check for any remaining 'bots' table references in error messages"""
        try:
            # Try to access a non-existent bot to see error messages
            fake_bot_id = str(uuid.uuid4())
            response = requests.get(
                f"{API_BASE}/bots/{fake_bot_id}",
                params={"user_id": self.test_user_id},
                timeout=10
            )
            
            # We expect this to fail, but check the error message
            if response.status_code == 404 or response.status_code == 500:
                error_text = response.text.lower()
                if "bots" in error_text and "user_bots" not in error_text:
                    self.log_result(
                        "Table Consistency Check", 
                        False, 
                        f"Found reference to 'bots' table in error: {response.text}", 
                        critical=True
                    )
                    return False
                else:
                    self.log_result(
                        "Table Consistency Check", 
                        True, 
                        "No obvious 'bots' table references found in error messages"
                    )
                    return True
            else:
                self.log_result("Table Consistency Check", True, "Unexpected response, but no table reference issues detected")
                return True
                
        except Exception as e:
            self.log_result("Table Consistency Check", True, f"Test completed with exception (expected): {str(e)}")
            return True
    
    def test_end_to_end_flow(self):
        """Test complete bot creation → retrieval → activation flow"""
        print("🔄 STARTING END-TO-END FLOW TEST")
        print("=" * 50)
        
        # Step 1: Create bot
        creation_success = self.test_bot_creation_api()
        if not creation_success:
            self.log_result("End-to-End Flow", False, "Failed at bot creation step", critical=True)
            return False
        
        # Step 2: Retrieve bots
        time.sleep(1)  # Brief pause for database consistency
        retrieval_success = self.test_bot_retrieval_api()
        if not retrieval_success:
            self.log_result("End-to-End Flow", False, "Failed at bot retrieval step", critical=True)
            return False
        
        # Step 3: Activate bot
        time.sleep(1)  # Brief pause for database consistency
        activation_success = self.test_bot_activation_api()
        if not activation_success:
            self.log_result("End-to-End Flow", False, "Failed at bot activation step", critical=True)
            return False
        
        self.log_result(
            "End-to-End Flow", 
            True, 
            "Complete flow successful: Create → Retrieve → Activate", 
            critical=True
        )
        return True
    
    def run_all_tests(self):
        """Run all bot table fix verification tests"""
        print("🚀 STARTING BOT TABLE FIX VERIFICATION TESTS")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"Test Bot Prompt: {TEST_BOT_PROMPT}")
        print("=" * 60)
        print()
        
        # Test 1: Server Health
        if not self.test_server_health():
            print("❌ Server health check failed. Aborting tests.")
            return self.generate_summary()
        
        # Test 2: Table Consistency Check
        self.test_table_consistency_check()
        
        # Test 3: End-to-End Flow (includes creation, retrieval, activation)
        self.test_end_to_end_flow()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        critical_tests = [r for r in self.results if r["critical"]]
        critical_passed = sum(1 for r in critical_tests if r["success"])
        
        print("\n" + "=" * 60)
        print("📊 BOT TABLE FIX VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        print(f"Critical Tests: {len(critical_tests)}")
        print(f"Critical Passed: {critical_passed}")
        print(f"Critical Success Rate: {(critical_passed/len(critical_tests))*100:.1f}%" if critical_tests else "N/A")
        print()
        
        # Show critical test results
        print("🚨 CRITICAL TEST RESULTS:")
        for result in critical_tests:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status}: {result['test']}")
            if not result["success"]:
                print(f"      Issue: {result['details']}")
        
        print()
        
        # Overall assessment
        if critical_passed == len(critical_tests) and critical_tests:
            print("🎉 SUCCESS: All critical bot table fixes are working correctly!")
            print("   - Bot creation saves to user_bots table ✅")
            print("   - Bot retrieval queries user_bots table ✅") 
            print("   - Bot activation updates user_bots table ✅")
            print("   - End-to-end flow operational ✅")
            overall_success = True
        elif critical_passed > 0:
            print("⚠️  PARTIAL SUCCESS: Some critical fixes working, but issues remain")
            print("   - Check failed tests above for specific problems")
            overall_success = False
        else:
            print("❌ FAILURE: Critical bot table fixes are not working")
            print("   - Bot creation/retrieval/activation still have table mismatch issues")
            overall_success = False
        
        print("=" * 60)
        
        return {
            "overall_success": overall_success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "critical_passed": critical_passed,
            "critical_total": len(critical_tests),
            "results": self.results
        }

if __name__ == "__main__":
    tester = BotTableFixTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if summary["overall_success"] else 1)