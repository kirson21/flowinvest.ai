"""
Simple Crypto Payments Routes - Compatible with existing FastAPI setup
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import os
import time
import uuid
import hashlib

router = APIRouter()

# Simple Pydantic models compatible with v1
class DepositAddressRequest(BaseModel):
    currency: str
    network: str

class WithdrawalRequest(BaseModel):
    recipient_address: str
    amount: float
    currency: str
    network: str
    memo: Optional[str] = None

class CryptoTransaction(BaseModel):
    id: str
    transaction_type: str
    currency: str
    network: str
    amount: float
    status: str
    created_at: str

import uuid
import hashlib

# Real Capitalist addresses provided by user
REAL_CAPITALIST_ADDRESSES = {
    'USDT_ERC20': '0xfd5fdd6856ee16e2e908bcea1c015fe7e04cee7b',
    'USDT_TRC20': 'TAAJ2Tb1EW8QaGye61AzsWkueMN649P8fg',
    'USDC_ERC20': '0xd5554bb054e3397cbb26321d4354ac935007d9b6'
}

def get_real_deposit_address(currency: str, network: str) -> Optional[str]:
    """Get real Capitalist deposit address for currency/network combination"""
    key = f"{currency}_{network}"
    return REAL_CAPITALIST_ADDRESSES.get(key)

def generate_unique_deposit_reference(user_id: str, currency: str, network: str) -> str:
    """Generate unique reference for tracking deposits"""
    # Create unique deposit ID using user_id + timestamp + currency
    unique_data = f"{user_id}_{currency}_{network}_{int(time.time())}"
    return hashlib.md5(unique_data.encode()).hexdigest()[:16].upper()

# In-memory storage for pending deposits (in production, use Redis or database)
PENDING_DEPOSITS = {}

@router.get("/crypto/health")
async def crypto_health_check():
    """Health check for crypto payment service"""
    return {
        "status": "healthy",
        "mode": "development",
        "supported_currencies": ["USDT", "USDC"],
        "supported_networks": ["ERC20", "TRC20"],
        "message": "Mock crypto payment service active"
    }

@router.get("/crypto/supported-currencies")
async def get_supported_currencies():
    """Get list of supported cryptocurrencies and networks"""
    return {
        "success": True,
        "currencies": [
            {
                "code": "USDT",
                "name": "Tether USD",
                "networks": ["ERC20", "TRC20"],
                "decimals": 6
            },
            {
                "code": "USDC",
                "name": "USD Coin",
                "networks": ["ERC20"],
                "decimals": 6
            }
        ],
        "networks": {
            "ERC20": {
                "name": "Ethereum Network",
                "confirmation_time": "5-15 minutes",
                "min_confirmations": 12
            },
            "TRC20": {
                "name": "Tron Network", 
                "confirmation_time": "1-3 minutes",
                "min_confirmations": 19
            }
        }
    }

@router.post("/crypto/deposit/address")
async def create_deposit_address(request: DepositAddressRequest, user_id: str = "demo_user"):
    """Generate or retrieve deposit address for user"""
    try:
        # Validate inputs
        if request.currency.upper() not in ['USDT', 'USDC']:
            return {"success": False, "detail": "Unsupported currency"}
        
        if request.network.upper() not in ['ERC20', 'TRC20']:
            return {"success": False, "detail": "Unsupported network"}
        
        if request.currency.upper() == 'USDC' and request.network.upper() != 'ERC20':
            return {"success": False, "detail": "USDC only supports ERC20 network"}
        
        # Get real Capitalist deposit address
        address = get_real_deposit_address(request.currency.upper(), request.network.upper())
        
        if not address:
            return {"success": False, "detail": f"No deposit address available for {request.currency.upper()} on {request.network.upper()} network"}
        
        return {
            "success": True,
            "address": address,
            "currency": request.currency.upper(),
            "network": request.network.upper(),
            "memo": None,
            "is_new": False,
            "message": "Real Capitalist deposit address provided",
            "instructions": {
                "step1": f"Send {request.currency.upper()} to the address above using {request.network.upper()} network",
                "step2": "Your account will be credited automatically after confirmation",
                "step3": "Minimum deposit: $10 USD equivalent",
                "warning": "⚠️ This is a real Capitalist address. Only send the specified cryptocurrency!"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "detail": f"Failed to generate deposit address: {str(e)}"
        }

@router.post("/crypto/withdrawal")
async def submit_withdrawal(request: WithdrawalRequest, user_id: str = "demo_user"):
    """Submit crypto withdrawal request"""
    try:
        # Validate inputs
        if request.currency.upper() not in ['USDT', 'USDC']:
            return {"success": False, "detail": "Unsupported currency"}
        
        if request.network.upper() not in ['ERC20', 'TRC20']:
            return {"success": False, "detail": "Unsupported network"}
        
        if request.amount <= 0 or request.amount > 100000:
            return {"success": False, "detail": "Invalid amount"}
        
        if len(request.recipient_address) < 20:
            return {"success": False, "detail": "Invalid recipient address"}
        
        # Calculate mock fees
        withdrawal_fee = max(5.0, request.amount * 0.02)
        total_needed = request.amount + withdrawal_fee
        
        # Generate mock transaction ID
        transaction_id = str(uuid.uuid4())
        batch_id = f"mock_batch_{int(time.time())}"
        
        return {
            "success": True,
            "crypto_transaction_id": transaction_id,
            "batch_id": batch_id,
            "amount": request.amount,
            "fee": withdrawal_fee,
            "total_deducted": total_needed,
            "status": "processing",
            "estimated_completion": "1-24 hours",
            "message": "Mock withdrawal request submitted (development mode)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "detail": f"Failed to submit withdrawal: {str(e)}"
        }

@router.get("/crypto/transactions")
async def get_crypto_transactions(user_id: str = "demo_user", limit: int = 50):
    """Get user's crypto transaction history"""
    try:
        # Return mock transaction data
        mock_transactions = [
            {
                "id": str(uuid.uuid4()),
                "transaction_type": "deposit",
                "currency": "USDT",
                "network": "ERC20",
                "amount": 100.0,
                "status": "confirmed",
                "transaction_hash": "0x" + "a" * 64,
                "confirmations": 12,
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "transaction_type": "withdrawal", 
                "currency": "USDC",
                "network": "ERC20",
                "amount": 50.0,
                "status": "processing",
                "transaction_hash": None,
                "confirmations": 0,
                "created_at": "2024-01-14T15:45:00Z"
            }
        ]
        
        return {
            "success": True,
            "transactions": mock_transactions[:limit],
            "count": len(mock_transactions),
            "message": "Mock transaction data (development mode)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "transactions": [],
            "detail": f"Failed to fetch transactions: {str(e)}"
        }

@router.get("/crypto/fees")
async def get_withdrawal_fees():
    """Get current withdrawal fees"""
    return {
        "success": True,
        "fees": {
            "withdrawal": {
                "minimum_fee": 5.0,
                "percentage_fee": 0.02,
                "description": "Minimum $5 or 2% of withdrawal amount, whichever is higher"
            },
            "deposit": {
                "fee": 0.0,
                "description": "Deposits are free (network fees paid by user)"
            }
        },
        "limits": {
            "min_withdrawal": 10.0,
            "max_withdrawal": 100000.0,
            "min_deposit": 1.0,
            "daily_withdrawal_limit": 50000.0
        }
    }

@router.get("/crypto/status/{transaction_id}")
async def get_transaction_status(transaction_id: str, user_id: str = "demo_user"):
    """Get crypto transaction status"""
    try:
        # Return mock status
        mock_transaction = {
            "id": transaction_id,
            "transaction_type": "withdrawal",
            "currency": "USDT",
            "network": "ERC20",
            "amount": 100.0,
            "status": "processing",
            "transaction_hash": None,
            "confirmations": 0,
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        return {
            "success": True,
            "transaction": mock_transaction
        }
        
    except Exception as e:
        return {
            "success": False,
            "detail": f"Failed to get transaction status: {str(e)}"
        }