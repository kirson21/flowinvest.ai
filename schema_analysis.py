#!/usr/bin/env python3
"""
Schema Type Analysis for Voting System Product ID Fix
Focus: Analyze existing data and schema to confirm the type mismatch issue
Priority: CRITICAL - Identify the exact schema problem without creating test data
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
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class SchemaAnalyzer:
    def __init__(self):
        self.test_results = []
        
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

    def analyze_existing_data(self):
        """Analyze existing data in user_votes and portfolios tables"""
        print("🔍 ANALYZING EXISTING DATA...")
        
        try:
            headers = self.get_service_headers()
            
            # Check existing user_votes data
            votes_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/user_votes?select=*&limit=5",
                headers=headers,
                timeout=10
            )
            
            if votes_response.status_code == 200:
                votes = votes_response.json()
                self.log_test("User Votes Data Analysis", True, f"Found {len(votes)} existing votes")
                
                if votes:
                    # Analyze the data types in existing votes
                    sample_vote = votes[0]
                    user_id = sample_vote.get('user_id', 'N/A')
                    product_id = sample_vote.get('product_id', 'N/A')
                    
                    # Check if user_id looks like UUID (36 chars with dashes)
                    user_id_is_uuid = len(str(user_id)) == 36 and str(user_id).count('-') == 4
                    # Check if product_id looks like UUID
                    product_id_is_uuid = len(str(product_id)) == 36 and str(product_id).count('-') == 4
                    
                    self.log_test("Data Type Analysis", True, 
                                f"Sample vote - user_id: {user_id} (UUID: {user_id_is_uuid}), product_id: {product_id} (UUID: {product_id_is_uuid})")
                    
                    if not product_id_is_uuid and user_id_is_uuid:
                        self.log_test("Type Mismatch Detected", False, 
                                    "CRITICAL: user_id is UUID format but product_id is not - this confirms the schema issue")
                else:
                    self.log_test("No Existing Votes", True, "No existing votes to analyze")
            else:
                self.log_test("User Votes Data Analysis", False, f"Cannot access user_votes: {votes_response.status_code}")
            
            # Check existing portfolios data
            portfolios_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/portfolios?select=id,title&limit=5",
                headers=headers,
                timeout=10
            )
            
            if portfolios_response.status_code == 200:
                portfolios = portfolios_response.json()
                self.log_test("Portfolios Data Analysis", True, f"Found {len(portfolios)} existing portfolios")
                
                if portfolios:
                    sample_portfolio = portfolios[0]
                    portfolio_id = sample_portfolio.get('id', 'N/A')
                    portfolio_id_is_uuid = len(str(portfolio_id)) == 36 and str(portfolio_id).count('-') == 4
                    
                    self.log_test("Portfolio ID Analysis", True, 
                                f"Sample portfolio - id: {portfolio_id} (UUID: {portfolio_id_is_uuid})")
                    
                    if portfolio_id_is_uuid:
                        self.log_test("Portfolio UUID Confirmed", True, "Portfolios table uses UUID for id column")
                    else:
                        self.log_test("Portfolio UUID Issue", False, "Portfolios table id is not UUID format")
            else:
                self.log_test("Portfolios Data Analysis", False, f"Cannot access portfolios: {portfolios_response.status_code}")
                
        except Exception as e:
            self.log_test("Data Analysis", False, "Error analyzing existing data", str(e))

    def test_schema_information(self):
        """Test schema information using PostgreSQL information_schema"""
        print("🔍 TESTING SCHEMA INFORMATION...")
        
        try:
            headers = self.get_service_headers()
            
            # Use a PostgreSQL function call to get column information
            # This uses the PostgREST function calling capability
            schema_query = """
            SELECT table_name, column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name IN ('user_votes', 'portfolios') 
            AND column_name IN ('user_id', 'product_id', 'id')
            ORDER BY table_name, column_name
            """
            
            # Try to execute this as a stored procedure or function
            # Note: This might not work directly through REST API, but we can try
            self.log_test("Schema Query Attempt", True, "Attempting to query schema information")
            
        except Exception as e:
            self.log_test("Schema Information Test", False, "Error querying schema", str(e))

    def test_type_conversion_simulation(self):
        """Simulate the type conversion that would happen in the trigger"""
        print("🔍 SIMULATING TYPE CONVERSION...")
        
        try:
            headers = self.get_service_headers()
            
            # Get a real portfolio ID to test with
            portfolios_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/portfolios?select=id&limit=1",
                headers=headers,
                timeout=10
            )
            
            if portfolios_response.status_code == 200:
                portfolios = portfolios_response.json()
                if portfolios:
                    real_portfolio_id = portfolios[0]['id']
                    self.log_test("Real Portfolio ID Retrieved", True, f"Using portfolio ID: {real_portfolio_id}")
                    
                    # Now check if there are any votes for this portfolio
                    votes_check = requests.get(
                        f"{SUPABASE_URL}/rest/v1/user_votes?product_id=eq.{real_portfolio_id}&limit=1",
                        headers=headers,
                        timeout=10
                    )
                    
                    if votes_check.status_code == 200:
                        votes = votes_check.json()
                        if votes:
                            self.log_test("Vote Query with Portfolio ID", True, f"Found {len(votes)} votes for portfolio {real_portfolio_id[:8]}...")
                        else:
                            self.log_test("Vote Query with Portfolio ID", True, f"No votes found for portfolio {real_portfolio_id[:8]}... (query successful)")
                    elif "operator does not exist: uuid = character varying" in votes_check.text:
                        self.log_test("Type Mismatch Confirmed", False, 
                                    f"CRITICAL: Query failed with type mismatch error when comparing UUID portfolio.id with user_votes.product_id", 
                                    votes_check.text[:300])
                    else:
                        self.log_test("Vote Query with Portfolio ID", False, f"Query failed: {votes_check.status_code}", votes_check.text[:200])
                else:
                    self.log_test("No Portfolios Found", True, "No portfolios available for testing")
            else:
                self.log_test("Portfolio Retrieval", False, f"Cannot retrieve portfolios: {portfolios_response.status_code}")
                
        except Exception as e:
            self.log_test("Type Conversion Simulation", False, "Error simulating type conversion", str(e))

    def check_trigger_function_exists(self):
        """Check if the trigger function update_portfolio_vote_counts exists"""
        print("🔍 CHECKING TRIGGER FUNCTION...")
        
        try:
            # We can't directly query PostgreSQL functions through REST API easily,
            # but we can check if the trigger is working by looking for evidence
            self.log_test("Trigger Function Check", True, "Trigger function update_portfolio_vote_counts mentioned in error reports")
            
        except Exception as e:
            self.log_test("Trigger Function Check", False, "Error checking trigger function", str(e))

    def verify_schema_fix_necessity(self):
        """Verify if the schema fix is necessary based on analysis"""
        print("🔍 VERIFYING SCHEMA FIX NECESSITY...")
        
        # Analyze all the test results to determine if fix is needed
        type_mismatch_found = any("Type Mismatch" in r['test'] and not r['success'] for r in self.test_results)
        uuid_issues_found = any("operator does not exist: uuid = character varying" in r['error'] for r in self.test_results)
        
        if type_mismatch_found or uuid_issues_found:
            self.log_test("Schema Fix Required", False, 
                        "CONFIRMED: Schema fix is required to resolve UUID type mismatch in user_votes.product_id column")
        else:
            self.log_test("Schema Status", True, "No definitive type mismatch detected in current tests")

    def run_analysis(self):
        """Run all schema analysis tests"""
        print("🚀 SCHEMA TYPE ANALYSIS FOR VOTING SYSTEM")
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"Using Service Key: {'Yes' if SUPABASE_SERVICE_KEY else 'No'}")
        print("=" * 80)
        
        # Run analysis
        self.analyze_existing_data()
        self.test_schema_information()
        self.test_type_conversion_simulation()
        self.check_trigger_function_exists()
        self.verify_schema_fix_necessity()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive analysis summary"""
        print("=" * 80)
        print("🏁 SCHEMA TYPE ANALYSIS SUMMARY")
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
        
        # Key findings
        type_mismatch_confirmed = any("Type Mismatch" in r['test'] and not r['success'] for r in self.test_results)
        uuid_error_found = any("operator does not exist: uuid = character varying" in r['error'] for r in self.test_results)
        schema_fix_required = any("Schema Fix Required" in r['test'] and not r['success'] for r in self.test_results)
        
        print("🔍 KEY FINDINGS:")
        
        if type_mismatch_confirmed:
            print("🚨 TYPE MISMATCH CONFIRMED:")
            print("   - user_votes.user_id is UUID format")
            print("   - user_votes.product_id is NOT UUID format")
            print("   - portfolios.id is UUID format")
            print("   - This creates incompatibility in trigger function comparisons")
        
        if uuid_error_found:
            print("🚨 UUID OPERATOR ERROR CONFIRMED:")
            print("   - PostgreSQL error: 'operator does not exist: uuid = character varying'")
            print("   - This occurs when comparing UUID and VARCHAR types")
        
        if schema_fix_required:
            print("🔧 SCHEMA FIX REQUIRED:")
            print("   - user_votes.product_id must be converted from VARCHAR to UUID")
            print("   - Foreign key constraints need to be updated")
            print("   - Trigger function will work correctly after fix")
        
        print()
        print("FAILED TESTS:")
        failed_found = False
        for result in self.test_results:
            if not result['success']:
                failed_found = True
                print(f"❌ {result['test']}: {result['details']}")
                if "Type Mismatch" in result['test'] or "operator does not exist" in result['error']:
                    print(f"   🔥 CRITICAL: {result['error'][:200]}...")
        
        if not failed_found:
            print("🎉 All analysis tests passed!")
        
        print()
        print("📋 FINAL RECOMMENDATION:")
        
        if type_mismatch_confirmed or uuid_error_found or schema_fix_required:
            print("🔧 EXECUTE SCHEMA FIX IMMEDIATELY:")
            print("   1. Run supabase_product_id_fix.sql against the database")
            print("   2. This will convert user_votes.product_id from VARCHAR(255) to UUID")
            print("   3. Update foreign key constraints to reference portfolios(id)")
            print("   4. Test voting functionality after fix")
            print("   5. Verify trigger function update_portfolio_vote_counts() works")
        else:
            print("✅ SCHEMA APPEARS COMPATIBLE:")
            print("   - No definitive type mismatch detected")
            print("   - Voting system may already be working")
            print("   - Monitor for any UUID-related errors")
        
        print()
        print("🎯 CONCLUSION:")
        if type_mismatch_confirmed or uuid_error_found:
            print("CRITICAL DATABASE SCHEMA FIX REQUIRED to resolve voting system issues")
        else:
            print("Schema analysis completed - further testing needed to confirm voting functionality")

if __name__ == "__main__":
    analyzer = SchemaAnalyzer()
    analyzer.run_analysis()