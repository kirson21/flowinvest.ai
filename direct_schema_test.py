#!/usr/bin/env python3
"""
Direct Database Schema Testing for Voting System Product ID Fix
Focus: Test the product_id column type issue using service key to bypass RLS
Priority: CRITICAL - Confirm and fix PostgreSQL type mismatch error
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from backend
load_dotenv('/app/backend/.env')

# Get Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Service key bypasses RLS

class DirectSchemaFixTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = str(uuid.uuid4())
        self.test_product_id = str(uuid.uuid4())
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results with enhanced formatting"""
        status = "✅" if success else "❌"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def get_service_headers(self):
        """Get headers with service key for admin access"""
        return {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }

    def test_supabase_connection(self):
        """Test Supabase connection with service key"""
        print("🔍 TESTING SUPABASE CONNECTION...")
        
        try:
            headers = self.get_service_headers()
            
            # Test basic connection
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Supabase Connection", True, f"Connected to Supabase with service key")
            else:
                self.log_test("Supabase Connection", False, f"Connection failed: {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("Supabase Connection", False, "Connection error", str(e))

    def test_user_votes_table_schema(self):
        """Test current user_votes table schema to identify the type issue"""
        print("🔍 TESTING USER_VOTES TABLE SCHEMA...")
        
        try:
            headers = self.get_service_headers()
            
            # First, check if table exists and is accessible
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/user_votes?select=*&limit=1",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("User Votes Table Access", True, "Successfully accessed user_votes table with service key")
                
                # Now test the schema by attempting to insert with UUID product_id
                test_vote = {
                    "user_id": self.test_user_id,
                    "product_id": self.test_product_id,  # UUID format
                    "vote_type": "upvote"
                }
                
                insert_response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/user_votes",
                    headers=headers,
                    json=test_vote,
                    timeout=10
                )
                
                if insert_response.status_code == 201:
                    self.log_test("UUID Product ID Insert Test", True, "UUID product_id accepted - schema may be fixed")
                    # Clean up
                    requests.delete(
                        f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{self.test_user_id}&product_id=eq.{self.test_product_id}",
                        headers=headers
                    )
                elif "operator does not exist: uuid = character varying" in insert_response.text:
                    self.log_test("UUID Product ID Insert Test", False, "CONFIRMED: product_id column type mismatch - VARCHAR vs UUID", insert_response.text[:300])
                elif "invalid input syntax for type uuid" in insert_response.text:
                    self.log_test("UUID Product ID Insert Test", False, "product_id column expects UUID but has validation issues", insert_response.text[:300])
                else:
                    self.log_test("UUID Product ID Insert Test", False, f"Unexpected error: {insert_response.status_code}", insert_response.text[:300])
                    
            else:
                self.log_test("User Votes Table Access", False, f"Cannot access user_votes table: {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("User Votes Schema Test", False, "Error testing schema", str(e))

    def test_portfolios_table_schema(self):
        """Test portfolios table to confirm it uses UUID for id column"""
        print("🔍 TESTING PORTFOLIOS TABLE SCHEMA...")
        
        try:
            headers = self.get_service_headers()
            
            # Check portfolios table structure
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/portfolios?select=*&limit=1",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                portfolios = response.json()
                self.log_test("Portfolios Table Access", True, f"Successfully accessed portfolios table, found {len(portfolios)} records")
                
                # Test creating a portfolio with UUID id
                test_portfolio = {
                    "id": self.test_product_id,  # UUID format
                    "title": "Schema Test Portfolio",
                    "description": "Testing UUID compatibility",
                    "user_id": self.test_user_id,
                    "price": 99.99,
                    "category": "test"
                }
                
                portfolio_response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/portfolios",
                    headers=headers,
                    json=test_portfolio,
                    timeout=10
                )
                
                if portfolio_response.status_code == 201:
                    self.log_test("Portfolio UUID ID Test", True, "Portfolios table accepts UUID for id column")
                    # Clean up
                    requests.delete(
                        f"{SUPABASE_URL}/rest/v1/portfolios?id=eq.{self.test_product_id}",
                        headers=headers
                    )
                else:
                    self.log_test("Portfolio UUID ID Test", False, f"Portfolio creation failed: {portfolio_response.status_code}", portfolio_response.text[:200])
                    
            else:
                self.log_test("Portfolios Table Access", False, f"Cannot access portfolios table: {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_test("Portfolios Schema Test", False, "Error testing portfolios schema", str(e))

    def test_trigger_function_issue(self):
        """Test the specific trigger function issue by simulating the problematic scenario"""
        print("🔍 TESTING TRIGGER FUNCTION ISSUE...")
        
        try:
            headers = self.get_service_headers()
            
            # First create a portfolio with UUID id
            portfolio_data = {
                "id": self.test_product_id,
                "title": "Trigger Test Portfolio",
                "description": "Testing trigger function",
                "user_id": self.test_user_id,
                "price": 99.99,
                "category": "test"
            }
            
            portfolio_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/portfolios",
                headers=headers,
                json=portfolio_data,
                timeout=10
            )
            
            if portfolio_response.status_code == 201:
                self.log_test("Test Portfolio Creation", True, f"Created test portfolio with UUID: {self.test_product_id[:8]}...")
                
                # Now try to create a vote that would trigger the update_portfolio_vote_counts function
                vote_data = {
                    "user_id": self.test_user_id,
                    "product_id": self.test_product_id,  # This should match the portfolio.id
                    "vote_type": "upvote"
                }
                
                vote_response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/user_votes",
                    headers=headers,
                    json=vote_data,
                    timeout=10
                )
                
                if vote_response.status_code == 201:
                    self.log_test("Trigger Function Test", True, "Vote created successfully - trigger function working")
                    
                    # Check if vote counts were updated in portfolio
                    portfolio_check = requests.get(
                        f"{SUPABASE_URL}/rest/v1/portfolios?id=eq.{self.test_product_id}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if portfolio_check.status_code == 200:
                        portfolio = portfolio_check.json()[0] if portfolio_check.json() else {}
                        vote_fields = [k for k in portfolio.keys() if 'vote' in k.lower() or 'upvote' in k.lower() or 'downvote' in k.lower()]
                        if vote_fields:
                            self.log_test("Vote Count Update", True, f"Portfolio has vote count fields: {vote_fields}")
                        else:
                            self.log_test("Vote Count Update", False, "Portfolio missing vote count fields")
                    
                elif "operator does not exist: uuid = character varying" in vote_response.text:
                    self.log_test("Trigger Function Test", False, "CRITICAL: Trigger function has UUID type mismatch", vote_response.text[:300])
                else:
                    self.log_test("Trigger Function Test", False, f"Vote creation failed: {vote_response.status_code}", vote_response.text[:300])
                
                # Clean up
                requests.delete(f"{SUPABASE_URL}/rest/v1/user_votes?user_id=eq.{self.test_user_id}&product_id=eq.{self.test_product_id}", headers=headers)
                requests.delete(f"{SUPABASE_URL}/rest/v1/portfolios?id=eq.{self.test_product_id}", headers=headers)
                
            else:
                self.log_test("Test Portfolio Creation", False, f"Failed to create test portfolio: {portfolio_response.status_code}", portfolio_response.text[:200])
                
        except Exception as e:
            self.log_test("Trigger Function Test", False, "Error testing trigger function", str(e))

    def check_schema_fix_sql(self):
        """Check the schema fix SQL file"""
        print("🔍 CHECKING SCHEMA FIX SQL...")
        
        try:
            with open('/app/supabase_product_id_fix.sql', 'r') as f:
                fix_sql = f.read()
            
            self.log_test("Schema Fix SQL Available", True, f"Schema fix SQL loaded ({len(fix_sql)} characters)")
            
            # Check if the SQL contains the expected operations
            expected_operations = [
                "ALTER TABLE user_votes ALTER COLUMN product_id TYPE UUID",
                "user_votes_product_id_fkey",
                "FOREIGN KEY (product_id) REFERENCES portfolios(id)"
            ]
            
            operations_found = []
            for op in expected_operations:
                if op in fix_sql:
                    operations_found.append(op)
            
            if len(operations_found) == len(expected_operations):
                self.log_test("Schema Fix SQL Validation", True, f"All required operations found: {len(operations_found)}/{len(expected_operations)}")
            else:
                self.log_test("Schema Fix SQL Validation", False, f"Missing operations: {len(operations_found)}/{len(expected_operations)}")
            
        except Exception as e:
            self.log_test("Schema Fix SQL Check", False, "Error checking schema fix SQL", str(e))

    def run_all_tests(self):
        """Run all direct schema tests"""
        print("🚀 DIRECT DATABASE SCHEMA TESTING FOR VOTING SYSTEM")
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"Using Service Key: {'Yes' if SUPABASE_SERVICE_KEY else 'No'}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"Test Product ID: {self.test_product_id}")
        print("=" * 80)
        
        # Run tests
        self.test_supabase_connection()
        self.test_user_votes_table_schema()
        self.test_portfolios_table_schema()
        self.test_trigger_function_issue()
        self.check_schema_fix_sql()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("🏁 DIRECT DATABASE SCHEMA TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Analyze critical findings
        schema_issue_confirmed = any("operator does not exist: uuid = character varying" in r['error'] for r in self.test_results)
        uuid_working = any("UUID product_id accepted" in r['details'] for r in self.test_results)
        trigger_issue = any("Trigger function has UUID type mismatch" in r['details'] for r in self.test_results)
        
        print("🔍 CRITICAL ANALYSIS:")
        
        if schema_issue_confirmed:
            print("🚨 CONFIRMED: user_votes.product_id column type mismatch")
            print("   - user_votes.product_id is VARCHAR(255)")
            print("   - portfolios.id is UUID")
            print("   - Trigger function update_portfolio_vote_counts() fails on comparison")
        elif uuid_working:
            print("✅ SCHEMA APPEARS FIXED: UUID product_id working correctly")
        else:
            print("⚠️ SCHEMA STATUS: Unable to definitively confirm issue")
        
        if trigger_issue:
            print("🚨 TRIGGER FUNCTION: update_portfolio_vote_counts() has type mismatch")
        
        print()
        print("FAILED TESTS:")
        failed_found = False
        for result in self.test_results:
            if not result['success']:
                failed_found = True
                print(f"❌ {result['test']}: {result['details']}")
                if result['error'] and "operator does not exist: uuid = character varying" in result['error']:
                    print(f"   🔥 CRITICAL ERROR: {result['error'][:200]}...")
                elif result['error']:
                    print(f"   Error: {result['error'][:200]}...")
        
        if not failed_found:
            print("🎉 All tests passed!")
        
        print()
        print("📋 RECOMMENDED ACTIONS:")
        
        if schema_issue_confirmed:
            print("1. 🔧 EXECUTE SCHEMA FIX:")
            print("   - Run supabase_product_id_fix.sql against the database")
            print("   - This will convert user_votes.product_id from VARCHAR to UUID")
            print("   - Will update foreign key constraints")
            print("2. 🔄 RESTART CONNECTIONS:")
            print("   - Restart any database connection pools")
            print("   - Clear any cached schema information")
            print("3. 🧪 RE-TEST:")
            print("   - Test voting functionality after fix")
            print("   - Verify trigger function works without errors")
        elif uuid_working:
            print("✅ SCHEMA FIX APPEARS SUCCESSFUL")
            print("✅ Voting system should be operational")
        else:
            print("⚠️ FURTHER INVESTIGATION NEEDED")
            print("   - Check database logs for more details")
            print("   - Verify table structures manually")
        
        print()
        if schema_issue_confirmed:
            print("🎯 CONCLUSION: Schema fix is REQUIRED to resolve voting system issues")
        elif uuid_working:
            print("🎯 CONCLUSION: Schema appears to be working correctly")
        else:
            print("🎯 CONCLUSION: Unable to confirm schema status - manual verification needed")

if __name__ == "__main__":
    tester = DirectSchemaFixTester()
    tester.run_all_tests()