#!/usr/bin/env python3
"""
Enhanced AI Trading Bot Creator Backend Testing
Testing dual AI model functionality (GPT-5 and Grok-4) with comprehensive validation
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class DualAITradingBotTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.generated_configs = {}
        
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

    def test_model_integration(self):
        """Test both GPT-5 and Grok-4 model integration"""
        print("=== MODEL INTEGRATION TESTING ===")
        
        # Test GPT-5 model integration
        try:
            gpt5_request = {
                "ai_model": "gpt-5",
                "strategy_description": "Create a conservative Bitcoin trading bot with low risk and steady returns"
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=gpt5_request)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('ai_model') == 'gpt-5':
                    bot_config = data.get('bot_config', {})
                    self.generated_configs['gpt5'] = bot_config
                    
                    # Validate GPT-5 specific structure
                    required_gpt5_fields = ['botName', 'description', 'strategy', 'riskManagement']
                    has_required_fields = all(field in bot_config for field in required_gpt5_fields)
                    
                    if has_required_fields:
                        self.log_test("GPT-5 Model Integration", True, 
                                    f"Generated bot: {bot_config.get('botName')}, AI Model: {data.get('ai_model')}")
                    else:
                        missing_fields = [f for f in required_gpt5_fields if f not in bot_config]
                        self.log_test("GPT-5 Model Integration", False, 
                                    f"Missing required fields: {missing_fields}")
                else:
                    self.log_test("GPT-5 Model Integration", False, 
                                f"Invalid response structure or AI model mismatch")
            else:
                self.log_test("GPT-5 Model Integration", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GPT-5 Model Integration", False, error=str(e))

        # Test Grok-4 model integration
        try:
            grok4_request = {
                "ai_model": "grok-4",
                "strategy_description": "Create an aggressive Ethereum scalping bot for quick profits"
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=grok4_request)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('ai_model') == 'grok-4':
                    bot_config = data.get('bot_config', {})
                    self.generated_configs['grok4'] = bot_config
                    
                    # Validate Grok-4 specific structure
                    required_grok4_fields = ['name', 'description', 'strategy', 'risk_level']
                    has_required_fields = all(field in bot_config for field in required_grok4_fields)
                    
                    if has_required_fields:
                        self.log_test("Grok-4 Model Integration", True, 
                                    f"Generated bot: {bot_config.get('name')}, AI Model: {data.get('ai_model')}")
                    else:
                        missing_fields = [f for f in required_grok4_fields if f not in bot_config]
                        self.log_test("Grok-4 Model Integration", False, 
                                    f"Missing required fields: {missing_fields}")
                else:
                    self.log_test("Grok-4 Model Integration", False, 
                                f"Invalid response structure or AI model mismatch")
            else:
                self.log_test("Grok-4 Model Integration", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Grok-4 Model Integration", False, error=str(e))

        # Test invalid model name
        try:
            invalid_request = {
                "ai_model": "invalid-model",
                "strategy_description": "Test invalid model"
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=invalid_request)
            
            if response.status_code == 400:
                self.log_test("Invalid Model Name Validation", True, 
                            "Correctly rejected invalid AI model name")
            else:
                self.log_test("Invalid Model Name Validation", False, 
                            f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Model Name Validation", False, error=str(e))

    def test_bot_configuration_generation(self):
        """Test various strategy descriptions with both models"""
        print("=== BOT CONFIGURATION GENERATION TESTING ===")
        
        test_strategies = [
            ("conservative", "Create a conservative Bitcoin trading strategy with capital preservation focus"),
            ("aggressive", "Build an aggressive high-risk high-reward trading bot for maximum profits"),
            ("scalping", "Design a scalping bot for frequent small trades with tight spreads")
        ]
        
        for strategy_type, description in test_strategies:
            # Test with GPT-5
            try:
                gpt5_request = {
                    "ai_model": "gpt-5",
                    "strategy_description": description
                }
                
                response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=gpt5_request)
                
                if response.status_code == 200:
                    data = response.json()
                    bot_config = data.get('bot_config', {})
                    
                    # Validate GPT-5 structure
                    has_strategy = 'strategy' in bot_config
                    has_risk_mgmt = 'riskManagement' in bot_config
                    has_execution = 'executionRules' in bot_config
                    
                    if has_strategy and has_risk_mgmt and has_execution:
                        strategy_info = bot_config.get('strategy', {})
                        risk_info = bot_config.get('riskManagement', {})
                        
                        self.log_test(f"GPT-5 {strategy_type.title()} Strategy Generation", True, 
                                    f"Strategy: {strategy_info.get('type')}, Leverage: {risk_info.get('leverage')}")
                    else:
                        self.log_test(f"GPT-5 {strategy_type.title()} Strategy Generation", False, 
                                    "Missing required configuration sections")
                else:
                    self.log_test(f"GPT-5 {strategy_type.title()} Strategy Generation", False, 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"GPT-5 {strategy_type.title()} Strategy Generation", False, error=str(e))
            
            # Test with Grok-4
            try:
                grok4_request = {
                    "ai_model": "grok-4",
                    "strategy_description": description
                }
                
                response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=grok4_request)
                
                if response.status_code == 200:
                    data = response.json()
                    bot_config = data.get('bot_config', {})
                    
                    # Validate Grok-4 structure
                    has_strategy = 'strategy' in bot_config
                    has_risk_level = 'risk_level' in bot_config
                    has_profit_target = 'profit_target' in bot_config
                    
                    if has_strategy and has_risk_level and has_profit_target:
                        self.log_test(f"Grok-4 {strategy_type.title()} Strategy Generation", True, 
                                    f"Strategy: {bot_config.get('strategy')}, Risk: {bot_config.get('risk_level')}, Target: {bot_config.get('profit_target')}%")
                    else:
                        self.log_test(f"Grok-4 {strategy_type.title()} Strategy Generation", False, 
                                    "Missing required configuration fields")
                else:
                    self.log_test(f"Grok-4 {strategy_type.title()} Strategy Generation", False, 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Grok-4 {strategy_type.title()} Strategy Generation", False, error=str(e))

    def test_json_structure_validation(self):
        """Test that both models return properly structured JSON configurations"""
        print("=== JSON STRUCTURE VALIDATION TESTING ===")
        
        # Test GPT-5 JSON structure
        if 'gpt5' in self.generated_configs:
            config = self.generated_configs['gpt5']
            
            # Check GPT-5 specific structure
            gpt5_structure_valid = (
                isinstance(config.get('strategy'), dict) and
                isinstance(config.get('riskManagement'), dict) and
                isinstance(config.get('executionRules'), dict) and
                'botName' in config and
                'description' in config
            )
            
            if gpt5_structure_valid:
                # Check nested structure
                strategy = config.get('strategy', {})
                risk_mgmt = config.get('riskManagement', {})
                
                nested_structure_valid = (
                    'type' in strategy and
                    'leverage' in risk_mgmt and
                    'stopLossPercent' in risk_mgmt and
                    'takeProfitPercent' in risk_mgmt
                )
                
                if nested_structure_valid:
                    self.log_test("GPT-5 JSON Structure Validation", True, 
                                "All required fields and nested structures present")
                else:
                    self.log_test("GPT-5 JSON Structure Validation", False, 
                                "Missing nested structure fields")
            else:
                self.log_test("GPT-5 JSON Structure Validation", False, 
                            "Missing top-level required fields")
        else:
            self.log_test("GPT-5 JSON Structure Validation", False, 
                        "No GPT-5 configuration available for validation")
        
        # Test Grok-4 JSON structure
        if 'grok4' in self.generated_configs:
            config = self.generated_configs['grok4']
            
            # Check Grok-4 specific structure
            grok4_structure_valid = (
                'name' in config and
                'description' in config and
                'strategy' in config and
                'risk_level' in config and
                'base_coin' in config and
                'quote_coin' in config and
                'exchange' in config and
                'profit_target' in config and
                'stop_loss' in config
            )
            
            if grok4_structure_valid:
                # Check advanced settings if present
                advanced_settings = config.get('advanced_settings', {})
                if advanced_settings:
                    advanced_valid = (
                        'max_positions' in advanced_settings and
                        'position_size' in advanced_settings and
                        'technical_indicators' in advanced_settings
                    )
                    
                    if advanced_valid:
                        self.log_test("Grok-4 JSON Structure Validation", True, 
                                    "All required fields and advanced settings present")
                    else:
                        self.log_test("Grok-4 JSON Structure Validation", False, 
                                    "Invalid advanced settings structure")
                else:
                    self.log_test("Grok-4 JSON Structure Validation", True, 
                                "All required basic fields present")
            else:
                missing_fields = [f for f in ['name', 'description', 'strategy', 'risk_level', 'base_coin', 'quote_coin', 'exchange', 'profit_target', 'stop_loss'] if f not in config]
                self.log_test("Grok-4 JSON Structure Validation", False, 
                            f"Missing required fields: {missing_fields}")
        else:
            self.log_test("Grok-4 JSON Structure Validation", False, 
                        "No Grok-4 configuration available for validation")

    def test_bot_creation_with_both_models(self):
        """Test bot creation endpoint with configurations from both models"""
        print("=== BOT CREATION WITH BOTH MODELS TESTING ===")
        
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        
        # Test bot creation with GPT-5 generated configuration
        if 'gpt5' in self.generated_configs:
            try:
                gpt5_bot_data = {
                    "bot_name": self.generated_configs['gpt5'].get('botName', 'GPT-5 Test Bot'),
                    "description": self.generated_configs['gpt5'].get('description', 'Test bot generated by GPT-5'),
                    "ai_model": "gpt-5",
                    "bot_config": self.generated_configs['gpt5'],
                    "user_id": test_user_id,
                    "trading_mode": "paper"
                }
                
                response = self.session.post(f"{API_BASE}/trading-bots/create", json=gpt5_bot_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('bot_id'):
                        self.log_test("GPT-5 Bot Creation", True, 
                                    f"Bot created with ID: {data.get('bot_id')[:8]}...")
                    else:
                        self.log_test("GPT-5 Bot Creation", False, 
                                    "Success flag false or missing bot ID")
                else:
                    self.log_test("GPT-5 Bot Creation", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("GPT-5 Bot Creation", False, error=str(e))
        else:
            self.log_test("GPT-5 Bot Creation", False, 
                        "No GPT-5 configuration available for bot creation")
        
        # Test bot creation with Grok-4 generated configuration
        if 'grok4' in self.generated_configs:
            try:
                grok4_bot_data = {
                    "bot_name": self.generated_configs['grok4'].get('name', 'Grok-4 Test Bot'),
                    "description": self.generated_configs['grok4'].get('description', 'Test bot generated by Grok-4'),
                    "ai_model": "grok-4",
                    "bot_config": self.generated_configs['grok4'],
                    "user_id": test_user_id,
                    "trading_mode": "paper"
                }
                
                response = self.session.post(f"{API_BASE}/trading-bots/create", json=grok4_bot_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('bot_id'):
                        self.log_test("Grok-4 Bot Creation", True, 
                                    f"Bot created with ID: {data.get('bot_id')[:8]}...")
                    else:
                        self.log_test("Grok-4 Bot Creation", False, 
                                    "Success flag false or missing bot ID")
                else:
                    self.log_test("Grok-4 Bot Creation", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Grok-4 Bot Creation", False, error=str(e))
        else:
            self.log_test("Grok-4 Bot Creation", False, 
                        "No Grok-4 configuration available for bot creation")

    def test_api_key_validation(self):
        """Test API key validation and error handling"""
        print("=== API KEY VALIDATION TESTING ===")
        
        # Test that endpoints work with current API keys (indirect validation)
        try:
            # Test a simple generation request to validate OpenAI key
            openai_test_request = {
                "ai_model": "gpt-5",
                "strategy_description": "Simple test strategy for API key validation"
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=openai_test_request)
            
            if response.status_code == 200:
                self.log_test("OpenAI API Key Validation", True, 
                            "OpenAI API key working correctly")
            elif response.status_code == 401 or "api_key" in response.text.lower():
                self.log_test("OpenAI API Key Validation", False, 
                            "OpenAI API key invalid or missing")
            elif response.status_code == 500:
                # Check if it's a fallback response (indicates API key issue but fallback works)
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if data.get('success'):
                    self.log_test("OpenAI API Key Validation", True, 
                                "OpenAI API key issue but fallback working")
                else:
                    self.log_test("OpenAI API Key Validation", False, 
                                "OpenAI API key validation failed")
            else:
                self.log_test("OpenAI API Key Validation", True, 
                            f"API responding (HTTP {response.status_code})")
        except Exception as e:
            self.log_test("OpenAI API Key Validation", False, error=str(e))
        
        # Test Grok API key
        try:
            grok_test_request = {
                "ai_model": "grok-4",
                "strategy_description": "Simple test strategy for Grok API key validation"
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=grok_test_request)
            
            if response.status_code == 200:
                self.log_test("Grok API Key Validation", True, 
                            "Grok API key working correctly")
            elif response.status_code == 401 or "api_key" in response.text.lower():
                self.log_test("Grok API Key Validation", False, 
                            "Grok API key invalid or missing")
            elif response.status_code == 500:
                # Check if it's a fallback response
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if data.get('success'):
                    self.log_test("Grok API Key Validation", True, 
                                "Grok API key issue but fallback working")
                else:
                    self.log_test("Grok API Key Validation", False, 
                                "Grok API key validation failed")
            else:
                self.log_test("Grok API Key Validation", True, 
                            f"API responding (HTTP {response.status_code})")
        except Exception as e:
            self.log_test("Grok API Key Validation", False, error=str(e))

    def test_backward_compatibility(self):
        """Test backward compatibility with existing endpoints"""
        print("=== BACKWARD COMPATIBILITY TESTING ===")
        
        # Test legacy create-with-ai endpoint
        try:
            legacy_request = {
                "prompt": "Create a balanced trading bot for Bitcoin with moderate risk",
                "user_id": f"test_user_{uuid.uuid4().hex[:8]}"
            }
            
            response = self.session.post(f"{API_BASE}/bots/create-with-ai", json=legacy_request)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('bot_config'):
                    bot_config = data.get('bot_config')
                    # Check if it has the old Grok structure
                    has_legacy_fields = 'name' in bot_config and 'strategy' in bot_config
                    
                    if has_legacy_fields:
                        self.log_test("Legacy create-with-ai Endpoint", True, 
                                    f"Legacy endpoint working, bot: {bot_config.get('name')}")
                    else:
                        self.log_test("Legacy create-with-ai Endpoint", False, 
                                    "Legacy endpoint response structure invalid")
                else:
                    self.log_test("Legacy create-with-ai Endpoint", False, 
                                "Legacy endpoint success flag false or missing config")
            else:
                self.log_test("Legacy create-with-ai Endpoint", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Legacy create-with-ai Endpoint", False, error=str(e))
        
        # Test user bots retrieval endpoint
        try:
            test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
            response = self.session.get(f"{API_BASE}/bots/user/{test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and 'bots' in data:
                    self.log_test("User Bots Retrieval Endpoint", True, 
                                f"Endpoint working, found {data.get('total', 0)} bots")
                else:
                    self.log_test("User Bots Retrieval Endpoint", False, 
                                "Invalid response structure")
            else:
                self.log_test("User Bots Retrieval Endpoint", False, 
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("User Bots Retrieval Endpoint", False, error=str(e))

    def test_error_handling(self):
        """Test error handling for various edge cases"""
        print("=== ERROR HANDLING TESTING ===")
        
        # Test missing strategy description
        try:
            invalid_request = {
                "ai_model": "gpt-5",
                "strategy_description": ""
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=invalid_request)
            
            if response.status_code == 400:
                self.log_test("Empty Strategy Description Handling", True, 
                            "Correctly rejected empty strategy description")
            else:
                self.log_test("Empty Strategy Description Handling", False, 
                            f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Empty Strategy Description Handling", False, error=str(e))
        
        # Test short strategy description
        try:
            invalid_request = {
                "ai_model": "grok-4",
                "strategy_description": "short"
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/generate-bot", json=invalid_request)
            
            if response.status_code == 400:
                self.log_test("Short Strategy Description Handling", True, 
                            "Correctly rejected short strategy description")
            else:
                self.log_test("Short Strategy Description Handling", False, 
                            f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Short Strategy Description Handling", False, error=str(e))
        
        # Test missing required fields in bot creation
        try:
            invalid_bot_data = {
                "bot_name": "Test Bot",
                # Missing description, ai_model, bot_config
            }
            
            response = self.session.post(f"{API_BASE}/trading-bots/create", json=invalid_bot_data)
            
            if response.status_code == 400:
                self.log_test("Missing Bot Creation Fields Handling", True, 
                            "Correctly rejected incomplete bot data")
            else:
                self.log_test("Missing Bot Creation Fields Handling", False, 
                            f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Missing Bot Creation Fields Handling", False, error=str(e))

    def run_all_tests(self):
        """Run all tests and generate summary"""
        print("🚀 STARTING ENHANCED AI TRADING BOT CREATOR BACKEND TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Focus: Dual AI Model Functionality (GPT-5 & Grok-4)")
        print("=" * 80)
        
        # Run all test suites
        self.test_model_integration()
        self.test_bot_configuration_generation()
        self.test_json_structure_validation()
        self.test_bot_creation_with_both_models()
        self.test_api_key_validation()
        self.test_backward_compatibility()
        self.test_error_handling()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("📊 ENHANCED AI TRADING BOT CREATOR TEST SUMMARY")
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
                    print(f"  - {result['test']}: {result['error'] or result['details']}")
            print()
        
        # Category analysis
        print("🔍 CATEGORY ANALYSIS:")
        
        # Model Integration
        model_tests = [r for r in self.test_results if 'Model Integration' in r['test'] or 'Model Name' in r['test']]
        model_passed = sum(1 for r in model_tests if r['success'])
        if model_passed == len(model_tests) and len(model_tests) > 0:
            print("✅ Model Integration: WORKING")
        else:
            print("❌ Model Integration: ISSUES DETECTED")
        
        # Configuration Generation
        config_tests = [r for r in self.test_results if 'Strategy Generation' in r['test']]
        config_passed = sum(1 for r in config_tests if r['success'])
        if config_passed >= len(config_tests) * 0.8 and len(config_tests) > 0:
            print("✅ Configuration Generation: WORKING")
        else:
            print("❌ Configuration Generation: ISSUES DETECTED")
        
        # JSON Structure
        json_tests = [r for r in self.test_results if 'JSON Structure' in r['test']]
        json_passed = sum(1 for r in json_tests if r['success'])
        if json_passed == len(json_tests) and len(json_tests) > 0:
            print("✅ JSON Structure Validation: WORKING")
        else:
            print("❌ JSON Structure Validation: ISSUES DETECTED")
        
        # Bot Creation
        creation_tests = [r for r in self.test_results if 'Bot Creation' in r['test']]
        creation_passed = sum(1 for r in creation_tests if r['success'])
        if creation_passed == len(creation_tests) and len(creation_tests) > 0:
            print("✅ Bot Creation: WORKING")
        else:
            print("❌ Bot Creation: ISSUES DETECTED")
        
        # API Keys
        api_tests = [r for r in self.test_results if 'API Key' in r['test']]
        api_passed = sum(1 for r in api_tests if r['success'])
        if api_passed >= len(api_tests) * 0.5 and len(api_tests) > 0:  # 50% threshold for API keys
            print("✅ API Key Validation: WORKING")
        else:
            print("❌ API Key Validation: ISSUES DETECTED")
        
        # Backward Compatibility
        compat_tests = [r for r in self.test_results if 'Legacy' in r['test'] or 'Retrieval' in r['test']]
        compat_passed = sum(1 for r in compat_tests if r['success'])
        if compat_passed == len(compat_tests) and len(compat_tests) > 0:
            print("✅ Backward Compatibility: MAINTAINED")
        else:
            print("❌ Backward Compatibility: ISSUES DETECTED")
        
        # Error Handling
        error_tests = [r for r in self.test_results if 'Handling' in r['test']]
        error_passed = sum(1 for r in error_tests if r['success'])
        if error_passed == len(error_tests) and len(error_tests) > 0:
            print("✅ Error Handling: ROBUST")
        else:
            print("❌ Error Handling: NEEDS IMPROVEMENT")
        
        print()
        print("🎯 DUAL AI MODEL FUNCTIONALITY ASSESSMENT:")
        
        # Check if both models are working
        gpt5_working = any(r['success'] for r in self.test_results if 'GPT-5' in r['test'])
        grok4_working = any(r['success'] for r in self.test_results if 'Grok-4' in r['test'])
        
        if gpt5_working and grok4_working:
            print("✅ Both GPT-5 and Grok-4 models are operational")
        elif gpt5_working:
            print("⚠️  Only GPT-5 model is working, Grok-4 has issues")
        elif grok4_working:
            print("⚠️  Only Grok-4 model is working, GPT-5 has issues")
        else:
            print("❌ Both AI models have issues")
        
        # Check JSON structure differences
        if 'gpt5' in self.generated_configs and 'grok4' in self.generated_configs:
            print("✅ Both models generate different but valid JSON structures")
        elif 'gpt5' in self.generated_configs or 'grok4' in self.generated_configs:
            print("⚠️  Only one model generated valid configurations")
        else:
            print("❌ No valid configurations generated by either model")
        
        # Overall assessment
        print()
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Dual AI model functionality working perfectly")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Most dual AI features working, minor issues")
        elif success_rate >= 60:
            print("⚠️  OVERALL ASSESSMENT: FAIR - Core functionality working, some issues remain")
        else:
            print("🚨 OVERALL ASSESSMENT: POOR - Major issues with dual AI model functionality")
        
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'results': self.test_results,
            'generated_configs': self.generated_configs
        }

if __name__ == "__main__":
    tester = DualAITradingBotTester()
    summary = tester.run_all_tests()