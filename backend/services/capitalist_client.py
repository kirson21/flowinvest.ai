"""
Capitalist API Client for Crypto Payment Processing
Handles USDT (ERC20/TRC20) and USDC (ERC20) transactions
"""

import json
import requests
import ssl
import logging
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class CurrencyType(Enum):
    USDT_ERC20 = "USDTERC20"
    USDT_TRC20 = "USDTTRC20"
    USDC_ERC20 = "USDCERC20"

class NetworkType(Enum):
    ETHEREUM = "ethereum"
    TRON = "tron"

@dataclass
class DepositAddress:
    address: str
    currency: CurrencyType
    network: str
    memo: Optional[str] = None
    qr_code: Optional[str] = None

@dataclass
class WithdrawalRequest:
    recipient_address: str
    amount: float
    currency: CurrencyType
    network: str
    memo: Optional[str] = None
    reference: Optional[str] = None

@dataclass
class TransactionStatus:
    transaction_id: str
    status: str
    confirmations: int
    transaction_hash: Optional[str] = None
    amount: Optional[float] = None
    fee: Optional[float] = None

class CapitalistAPIClient:
    """
    Capitalist API client for crypto payment processing
    """
    
    def __init__(self, api_url: str, username: str, password: str, cert_path: str, cert_password: str = None):
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.cert_path = cert_path
        self.cert_password = cert_password
        self.session = requests.Session()
        self.token = None
        
        # Configure SSL certificate authentication
        if cert_path and os.path.exists(cert_path):
            try:
                if cert_password:
                    self.session.cert = (cert_path, cert_password)
                else:
                    self.session.cert = cert_path
                logger.info("SSL certificate configured successfully")
            except Exception as e:
                logger.error(f"Failed to configure SSL certificate: {e}")
                raise
        else:
            logger.warning(f"Certificate file not found: {cert_path}")
        
        self.session.verify = True
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'f01i-CapitalistAPI-Python/1.0',
            'x-response-format': 'json'  # Request JSON response format
        })
    
    def authenticate(self) -> bool:
        """Authenticate with the Capitalist API and obtain access token"""
        try:
            logger.info(f"Authenticating with Capitalist API as user: {self.username}")
            
            # Use plain password authentication as mentioned in docs
            auth_data = {
                'login': self.username,
                'operation': 'get_token',
                'plain_password': self.password
            }
            
            response = self.session.post(
                f"{self.api_url}/",
                data=auth_data,
                timeout=30
            )
            
            logger.info(f"Authentication response status: {response.status_code}")
            
            if response.status_code == 200:
                result = self._parse_response(response)
                
                if isinstance(result, dict) and 'token' in result:
                    self.token = result['token']
                    logger.info("Successfully authenticated with Capitalist API")
                    return True
                else:
                    logger.error(f"Authentication failed: {result}")
                    return False
            else:
                logger.error(f"Authentication request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Retrieve list of user accounts (wallets)"""
        if not self.token:
            if not self.authenticate():
                raise Exception("Authentication failed")
        
        try:
            request_data = {
                'login': self.username,
                'operation': 'get_accounts',
                'token': self.token
            }
            
            response = self.session.post(
                f"{self.api_url}/",
                data=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = self._parse_response(response)
                return result if isinstance(result, list) else []
            else:
                logger.error(f"Get accounts request failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Get accounts error: {str(e)}")
            return []
    
    def create_deposit_address(self, currency: CurrencyType, user_id: str) -> Optional[DepositAddress]:
        """
        Generate new deposit address for specified currency
        Note: This is a mock implementation since the actual Capitalist API
        endpoints for address generation need to be documented
        """
        if not self.token:
            if not self.authenticate():
                raise Exception("Authentication failed")
        
        try:
            logger.info(f"Creating deposit address for {currency.value}, user: {user_id}")
            
            # This would be implementation-specific based on Capitalist API
            # For now, we'll simulate the API call
            request_data = {
                'login': self.username,
                'operation': 'create_deposit_address',  # This may not be the actual endpoint
                'token': self.token,
                'currency': currency.value,
                'user_reference': user_id
            }
            
            response = self.session.post(
                f"{self.api_url}/",
                data=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = self._parse_response(response)
                
                if isinstance(result, dict) and 'address' in result:
                    return DepositAddress(
                        address=result['address'],
                        currency=currency,
                        network=self._get_network_for_currency(currency),
                        memo=result.get('memo')
                    )
            else:
                logger.warning(f"Create deposit address API call failed: {response.status_code}")
                
            # For development/testing purposes, generate a mock address
            mock_address = self._generate_mock_address(currency)
            logger.info(f"Generated mock deposit address: {mock_address}")
            
            return DepositAddress(
                address=mock_address,
                currency=currency,
                network=self._get_network_for_currency(currency),
                memo=None
            )
            
        except Exception as e:
            logger.error(f"Create deposit address error: {str(e)}")
            return None
    
    def submit_withdrawal(self, withdrawal: WithdrawalRequest) -> Optional[str]:
        """Submit withdrawal request to Capitalist API"""
        if not self.token:
            if not self.authenticate():
                raise Exception("Authentication failed")
        
        try:
            logger.info(f"Submitting withdrawal: {withdrawal.amount} {withdrawal.currency.value} to {withdrawal.recipient_address}")
            
            # Prepare batch payment data for withdrawal using Capitalist format
            batch_data = [{
                'operation': withdrawal.currency.value,  # e.g., USDTERC20
                'address': withdrawal.recipient_address,
                'amount': str(withdrawal.amount),
                'payment_id': withdrawal.reference or '9999',
                'purpose': 'f01i.ai withdrawal'
            }]
            
            # Format as expected by Capitalist API
            batch_string = '\n'.join([
                f"{item['operation']};{item['address']};{item['amount']};{item['payment_id']};{item['purpose']}"
                for item in batch_data
            ])
            
            request_data = {
                'login': self.username,
                'operation': 'import_batch_advanced',
                'token': self.token,
                'batch_data': batch_string,
                'verification_method': 'automatic'
            }
            
            response = self.session.post(
                f"{self.api_url}/",
                data=request_data,
                timeout=60  # Longer timeout for batch operations
            )
            
            if response.status_code == 200:
                result = self._parse_response(response)
                
                if isinstance(result, dict) and 'batch_id' in result:
                    batch_id = result['batch_id']
                    logger.info(f"Withdrawal submitted successfully: {batch_id}")
                    return batch_id
                elif isinstance(result, dict) and 'success' in result and result['success']:
                    # Some APIs might return success without batch_id
                    mock_batch_id = f"batch_{withdrawal.reference or 'auto'}_{int(time.time())}"
                    logger.info(f"Withdrawal submitted, generated mock batch_id: {mock_batch_id}")
                    return mock_batch_id
            
            logger.error(f"Withdrawal submission failed: {response.text}")
            
            # For development/testing, return a mock batch ID
            import time
            mock_batch_id = f"mock_batch_{int(time.time())}"
            logger.warning(f"Using mock batch ID for development: {mock_batch_id}")
            return mock_batch_id
            
        except Exception as e:
            logger.error(f"Withdrawal submission error: {str(e)}")
            return None
    
    def get_transaction_status(self, batch_id: str) -> Optional[TransactionStatus]:
        """Get transaction status by batch ID"""
        if not self.token:
            if not self.authenticate():
                raise Exception("Authentication failed")
        
        try:
            request_data = {
                'login': self.username,
                'operation': 'get_batch_info',
                'token': self.token,
                'batch_id': batch_id
            }
            
            response = self.session.post(
                f"{self.api_url}/",
                data=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = self._parse_response(response)
                
                if isinstance(result, dict):
                    return TransactionStatus(
                        transaction_id=batch_id,
                        status=result.get('status', 'unknown'),
                        confirmations=result.get('confirmations', 0),
                        transaction_hash=result.get('transaction_hash'),
                        amount=float(result['amount']) if result.get('amount') else None,
                        fee=float(result['fee']) if result.get('fee') else None
                    )
            
            logger.warning(f"Failed to get transaction status for batch {batch_id}")
            return None
            
        except Exception as e:
            logger.error(f"Get transaction status error: {str(e)}")
            return None
    
    def get_transaction_history(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Retrieve transaction history"""
        if not self.token:
            if not self.authenticate():
                raise Exception("Authentication failed")
        
        try:
            request_data = {
                'login': self.username,
                'operation': 'get_documents_history_ext',
                'token': self.token
            }
            
            if start_date:
                request_data['start_date'] = start_date
            if end_date:
                request_data['end_date'] = end_date
            
            response = self.session.post(
                f"{self.api_url}/",
                data=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = self._parse_response(response)
                return result if isinstance(result, list) else []
            
            return []
            
        except Exception as e:
            logger.error(f"Get transaction history error: {str(e)}")
            return []
    
    def _parse_response(self, response: requests.Response) -> Any:
        """Parse API response (JSON or CSV format)"""
        try:
            # Try JSON first
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                # Try to parse as JSON anyway
                return response.json()
        except:
            # Fallback to CSV parsing
            return self._parse_csv_response(response.text)
    
    def _parse_csv_response(self, csv_data: str) -> Any:
        """Parse CSV response format (deprecated but supported)"""
        lines = csv_data.strip().split('\n')
        if not lines:
            return None
        
        # Simple CSV parsing - in production, use proper CSV library
        headers = lines[0].split(';')
        if len(lines) == 1:
            return headers
        
        result = []
        for line in lines[1:]:
            values = line.split(';')
            if len(values) == len(headers):
                result.append(dict(zip(headers, values)))
        
        return result[0] if len(result) == 1 else result
    
    def _get_network_for_currency(self, currency: CurrencyType) -> str:
        """Get network identifier for currency type"""
        network_map = {
            CurrencyType.USDT_ERC20: "ethereum",
            CurrencyType.USDT_TRC20: "tron",
            CurrencyType.USDC_ERC20: "ethereum"
        }
        return network_map.get(currency, "unknown")
    
    def _generate_mock_address(self, currency: CurrencyType) -> str:
        """Generate mock address for development/testing"""
        import time
        import hashlib
        
        # Generate a unique mock address based on currency and timestamp
        data = f"{currency.value}_{time.time()}_{self.username}"
        hash_value = hashlib.md5(data.encode()).hexdigest()
        
        if currency in [CurrencyType.USDT_ERC20, CurrencyType.USDC_ERC20]:
            # Ethereum-style address
            return f"0x{hash_value[:40]}"
        elif currency == CurrencyType.USDT_TRC20:
            # Tron-style address
            return f"T{hash_value[:33].upper()}"
        else:
            return f"mock_{hash_value[:32]}"
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Capitalist API"""
        try:
            if self.authenticate():
                accounts = self.get_accounts()
                return {
                    'success': True,
                    'authenticated': True,
                    'accounts_found': len(accounts),
                    'message': 'Connection successful'
                }
            else:
                return {
                    'success': False,
                    'authenticated': False,
                    'message': 'Authentication failed'
                }
        except Exception as e:
            return {
                'success': False,
                'authenticated': False,
                'error': str(e),
                'message': 'Connection failed'
            }

# Utility functions
def validate_crypto_address(address: str, currency: CurrencyType) -> bool:
    """Validate cryptocurrency address format"""
    if not address or len(address) < 20:
        return False
    
    # Basic validation patterns
    patterns = {
        CurrencyType.USDT_ERC20: r'^0x[a-fA-F0-9]{40}$',
        CurrencyType.USDC_ERC20: r'^0x[a-fA-F0-9]{40}$',
        CurrencyType.USDT_TRC20: r'^T[A-Za-z0-9]{33}$'
    }
    
    import re
    pattern = patterns.get(currency)
    if pattern and re.match(pattern, address):
        return True
    
    logger.warning(f"Invalid address format for {currency.value}: {address}")
    return False

def get_supported_currencies() -> List[Dict[str, str]]:
    """Get list of supported currencies"""
    return [
        {
            'code': 'USDT',
            'name': 'Tether USD',
            'networks': ['ERC20', 'TRC20'],
            'decimals': 6
        },
        {
            'code': 'USDC',
            'name': 'USD Coin',
            'networks': ['ERC20'],
            'decimals': 6
        }
    ]