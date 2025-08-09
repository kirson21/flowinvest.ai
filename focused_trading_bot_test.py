#!/usr/bin/env python3
"""
Focused Backend Testing for AI Trading Bot Constructor Infrastructure
Testing core functionality without authentication dependencies
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append('/app/backend')

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class FocusedTradingBotTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_core_backend_health(self):
        """Test basic backend connectivity and health"""
        print("=== CORE BACKEND HEALTH TESTS ===")
        
        # Test API root endpoint
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root Endpoint", True, f"Status: {data.get('status')}, Environment: {data.get('environment')}")
            else:
                self.log_test("API Root Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("API Root Endpoint", False, error=str(e))

        # Test status endpoint
        try:
            response = self.session.get(f"{API_BASE}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status Endpoint", True, f"Status: {data.get('status')}")
            else:
                self.log_test("Status Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Status Endpoint", False, error=str(e))

        # Test health check endpoint
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                supabase_status = services.get('supabase', 'unknown')
                self.log_test("Health Check Endpoint", True, f"API: {services.get('api')}, Supabase: {supabase_status}")
            else:
                self.log_test("Health Check Endpoint", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Health Check Endpoint", False, error=str(e))

    def test_non_authenticated_endpoints(self):
        """Test endpoints that don't require authentication"""
        print("=== NON-AUTHENTICATED ENDPOINTS TESTS ===")
        
        # Test get supported exchanges (should not require auth)
        try:
            response = self.session.get(f"{API_BASE}/exchange-keys/supported-exchanges")
            if response.status_code == 200:
                data = response.json()
                exchanges = data.get('exchanges', [])
                bybit_found = any(ex.get('id') == 'bybit' for ex in exchanges)
                self.log_test("Get Supported Exchanges", True, f"Found {len(exchanges)} exchanges, Bybit supported: {bybit_found}")
            else:
                self.log_test("Get Supported Exchanges", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Get Supported Exchanges", False, error=str(e))

    def test_openai_service_directly(self):
        """Test OpenAI service directly"""
        print("=== OPENAI SERVICE DIRECT TESTS ===")
        
        try:
            from services.openai_service import OpenAIService
            
            # Test service initialization
            openai_service = OpenAIService()
            self.log_test("OpenAI Service Initialization", True, "Service initialized successfully")
            
            # Test API key configuration
            import os
            openai_key = os.getenv('OPENAI_API_KEY', '')
            if openai_key and openai_key.startswith('sk-'):
                self.log_test("OpenAI API Key Configuration", True, f"API key configured (length: {len(openai_key)})")
            else:
                self.log_test("OpenAI API Key Configuration", False, "OpenAI API key not properly configured")
                
        except Exception as e:
            self.log_test("OpenAI Service Direct Test", False, error=str(e))

    def test_bybit_service_directly(self):
        """Test Bybit service directly"""
        print("=== BYBIT SERVICE DIRECT TESTS ===")
        
        try:
            from services.bybit_service import BybitService
            
            # Test service initialization
            bybit_service = BybitService()
            self.log_test("Bybit Service Initialization", True, "Service initialized successfully")
            
            # Test connection with test credentials
            async def test_connection():
                try:
                    result = await bybit_service.test_connection()
                    return result
                except Exception as e:
                    return {"success": False, "error": str(e)}
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            connection_result = loop.run_until_complete(test_connection())
            loop.close()
            
            if connection_result.get("success"):
                self.log_test("Bybit Testnet Connection", True, f"Connected: {connection_result.get('message', 'Success')}")
            else:
                self.log_test("Bybit Testnet Connection", False, f"Connection failed: {connection_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_test("Bybit Service Direct Test", False, error=str(e))

    def test_encryption_service_directly(self):
        """Test Encryption service directly"""
        print("=== ENCRYPTION SERVICE DIRECT TESTS ===")
        
        try:
            from services.encryption_service import EncryptionService
            
            # Test service initialization
            encryption_service = EncryptionService()
            self.log_test("Encryption Service Initialization", True, "Service initialized successfully")
            
            # Test encryption validation
            validation_result = encryption_service.validate_encryption_setup()
            
            if validation_result.get("success"):
                self.log_test("Encryption Validation", True, f"Validation successful: {validation_result.get('message')}")
            else:
                self.log_test("Encryption Validation", False, f"Validation failed: {validation_result.get('error')}")
                
        except Exception as e:
            self.log_test("Encryption Service Direct Test", False, error=str(e))

    def test_database_connectivity(self):
        """Test database connectivity directly"""
        print("=== DATABASE CONNECTIVITY TESTS ===")
        
        try:
            from database import supabase, supabase_admin
            
            # Test basic connection
            self.log_test("Database Import", True, "Database clients imported successfully")
            
            # Test connection with a simple query
            try:
                # Try to access a table that should exist
                response = supabase.table('user_profiles').select('count').limit(1).execute()
                self.log_test("Supabase Connection Test", True, "Successfully connected to Supabase")
            except Exception as e:
                self.log_test("Supabase Connection Test", False, f"Connection test failed: {str(e)}")
                
        except Exception as e:
            self.log_test("Database Connectivity Test", False, error=str(e))

    def test_authentication_health(self):
        """Test authentication system health"""
        print("=== AUTHENTICATION SYSTEM HEALTH TESTS ===")
        
        # Test auth health endpoint
        try:
            response = self.session.get(f"{API_BASE}/auth/health")
            if response.status_code == 200:
                data = response.json()
                supabase_connected = data.get('supabase_connected', False)
                self.log_test("Auth Health Check", True, f"Supabase connected: {supabase_connected}")
            else:
                self.log_test("Auth Health Check", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Auth Health Check", False, error=str(e))

        # Test admin setup endpoint
        try:
            response = self.session.post(f"{API_BASE}/auth/admin/setup")
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                message = data.get('message', '')
                self.log_test("Super Admin Setup", success, message)
            else:
                self.log_test("Super Admin Setup", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Super Admin Setup", False, error=str(e))

    def test_route_availability(self):
        """Test if trading bot routes are properly registered"""
        print("=== ROUTE AVAILABILITY TESTS ===")
        
        # Test if routes return proper error codes (not 404)
        endpoints_to_test = [
            ("/trading-bots/strategy-templates", "Strategy Templates Endpoint"),
            ("/trading-bots/", "User Bots Endpoint"),
            ("/exchange-keys/", "Exchange Keys Endpoint"),
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                # We expect 401 (unauthorized) or 422 (validation error), not 404 (not found)
                if response.status_code == 404:
                    self.log_test(f"Route Registration - {name}", False, f"Route not found (404)")
                elif response.status_code in [401, 422, 500]:
                    self.log_test(f"Route Registration - {name}", True, f"Route exists (HTTP {response.status_code})")
                else:
                    self.log_test(f"Route Registration - {name}", True, f"Route accessible (HTTP {response.status_code})")
            except Exception as e:
                self.log_test(f"Route Registration - {name}", False, error=str(e))

    def test_environment_configuration(self):
        """Test environment configuration"""
        print("=== ENVIRONMENT CONFIGURATION TESTS ===")
        
        # Test required environment variables
        required_vars = [
            ('OPENAI_API_KEY', 'OpenAI API Key'),
            ('SUPABASE_URL', 'Supabase URL'),
            ('SUPABASE_ANON_KEY', 'Supabase Anon Key'),
            ('SUPABASE_SERVICE_KEY', 'Supabase Service Key'),
        ]
        
        for var_name, display_name in required_vars:
            try:
                value = os.getenv(var_name, '')
                if value:
                    self.log_test(f"Environment - {display_name}", True, f"Configured (length: {len(value)})")
                else:
                    self.log_test(f"Environment - {display_name}", False, "Not configured")
            except Exception as e:
                self.log_test(f"Environment - {display_name}", False, error=str(e))

    def run_all_tests(self):
        """Run all tests and generate summary"""
        print("🚀 STARTING FOCUSED AI TRADING BOT CONSTRUCTOR TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Run all test suites
        self.test_core_backend_health()
        self.test_non_authenticated_endpoints()
        self.test_environment_configuration()
        self.test_authentication_health()
        self.test_route_availability()
        self.test_database_connectivity()
        self.test_openai_service_directly()
        self.test_bybit_service_directly()
        self.test_encryption_service_directly()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("📊 FOCUSED AI TRADING BOT CONSTRUCTOR TEST SUMMARY")
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
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['error']}")
            print()
        
        # Critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        # Check core backend health
        core_tests = [r for r in self.test_results if 'Endpoint' in r['test'] or 'Health' in r['test']]
        core_passed = sum(1 for r in core_tests if r['success'])
        
        if core_passed >= len(core_tests) * 0.8:
            print("✅ Core Backend Health: OPERATIONAL")
        else:
            print("❌ Core Backend Health: ISSUES DETECTED")
        
        # Check environment configuration
        env_tests = [r for r in self.test_results if 'Environment' in r['test']]
        env_passed = sum(1 for r in env_tests if r['success'])
        
        if env_passed == len(env_tests):
            print("✅ Environment Configuration: COMPLETE")
        else:
            print("❌ Environment Configuration: INCOMPLETE")
        
        # Check service integration
        service_tests = [r for r in self.test_results if 'Service' in r['test']]
        service_passed = sum(1 for r in service_tests if r['success'])
        
        if service_passed >= len(service_tests) * 0.8:
            print("✅ Service Integration: OPERATIONAL")
        else:
            print("❌ Service Integration: ISSUES DETECTED")
        
        # Check route registration
        route_tests = [r for r in self.test_results if 'Route' in r['test']]
        route_passed = sum(1 for r in route_tests if r['success'])
        
        if route_passed == len(route_tests):
            print("✅ Route Registration: COMPLETE")
        else:
            print("❌ Route Registration: ISSUES DETECTED")
        
        # Overall assessment
        print()
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Infrastructure ready for full testing")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Minor configuration issues")
        elif success_rate >= 60:
            print("⚠️  OVERALL ASSESSMENT: FAIR - Some infrastructure issues")
        else:
            print("🚨 OVERALL ASSESSMENT: POOR - Major infrastructure problems")
        
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = FocusedTradingBotTester()
    summary = tester.run_all_tests()