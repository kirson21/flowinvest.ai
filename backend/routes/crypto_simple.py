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
    """Generate deposit address with unique tracking reference and store in database"""
    try:
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Validate inputs
        if request.currency.upper() not in ['USDT', 'USDC']:
            return {"success": False, "detail": "Unsupported currency"}
        
        if request.network.upper() not in ['ERC20', 'TRC20']:
            return {"success": False, "detail": "Unsupported network"}
        
        if request.currency.upper() == 'USDC' and request.network.upper() != 'ERC20':
            return {"success": False, "detail": "USDC only supports ERC20 network"}
        
        # Get the real Capitalist address
        address = get_real_deposit_address(request.currency.upper(), request.network.upper())
        if not address:
            return {"success": False, "detail": "Address not available for this currency/network"}
        
        # Generate unique deposit reference for this user
        deposit_reference = generate_unique_deposit_reference(user_id, request.currency, request.network)
        
        # Create crypto transaction record in database
        crypto_transaction = {
            'user_id': user_id,
            'transaction_type': 'deposit',
            'currency': request.currency.upper(),
            'network': request.network.upper(),
            'deposit_address': address,
            'reference': deposit_reference,
            'status': 'pending',
            'amount': 0.0  # Amount not known until deposit is made
        }
        
        # Insert into database
        result = supabase.table('crypto_transactions').insert(crypto_transaction).execute()
        
        if not result.data:
            return {"success": False, "detail": "Failed to create transaction record"}
            
        transaction_id = result.data[0]['id']
        
        return {
            "success": True,
            "address": address,
            "currency": request.currency.upper(),
            "network": request.network.upper(),
            "deposit_reference": deposit_reference,
            "transaction_id": transaction_id,
            "memo": None,
            "message": "Deposit address with unique payment reference",
            "instructions": {
                "step1": f"Send {request.currency.upper()} to the address above using {request.network.upper()} network",
                "step2": f"🔥 CRITICAL: Include this reference in transaction description: {deposit_reference}",
                "step3": f"Alternative: Contact support with reference: {deposit_reference}",
                "step4": "Your account will be credited after confirmation (typically 5-30 minutes)",
                "warning": "⚠️ This is a real Capitalist address. Only send the specified cryptocurrency!",
                "tracking": f"Payment Reference: {deposit_reference}",
                "note": "Without the reference, we cannot automatically credit your account!"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "detail": f"Failed to create deposit request: {str(e)}"
        }

@router.post("/crypto/webhook/capitalist")
async def capitalist_webhook(request: dict):
    """Webhook endpoint to receive Capitalist API callbacks for deposit confirmations"""
    try:
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Extract payment data from Capitalist callback
        # Format: Operation code;USDT address;Amount;Payment number from your system;Payment description
        payment_reference = request.get('payment_reference') or request.get('reference')
        amount = float(request.get('amount', 0))
        transaction_hash = request.get('transaction_hash') or request.get('txn_hash')
        status = request.get('status', 'confirmed')
        
        if not payment_reference or amount <= 0:
            return {"success": False, "detail": "Invalid callback data"}
        
        # Find the crypto transaction by reference
        transaction_result = supabase.table('crypto_transactions')\
            .select('*')\
            .eq('reference', payment_reference)\
            .eq('transaction_type', 'deposit')\
            .eq('status', 'pending')\
            .execute()
        
        if not transaction_result.data:
            return {"success": False, "detail": "Transaction not found or already processed"}
        
        crypto_tx = transaction_result.data[0]
        user_id = crypto_tx['user_id']
        transaction_id = crypto_tx['id']
        
        # Update crypto transaction with confirmation details
        supabase.table('crypto_transactions')\
            .update({
                'amount': amount,
                'transaction_hash': transaction_hash,
                'status': 'confirmed',
                'confirmations': 1,
                'updated_at': 'now()'
            })\
            .eq('id', transaction_id)\
            .execute()
        
        # Create balance transaction (credit user account)
        balance_transaction = {
            'user_id': user_id,
            'transaction_type': 'topup',
            'amount': amount,
            'platform_fee': 0.0,  # No fee on deposits
            'net_amount': amount,
            'status': 'completed',
            'description': f"Crypto deposit: ${amount} from {crypto_tx['currency']} ({crypto_tx['network']})"
        }
        
        balance_result = supabase.table('transactions').insert(balance_transaction).execute()
        
        if balance_result.data:
            balance_tx_id = balance_result.data[0]['id']
            
            # Link crypto transaction to balance transaction
            supabase.table('crypto_transactions')\
                .update({'balance_transaction_id': balance_tx_id})\
                .eq('id', transaction_id)\
                .execute()
        
        # Update user balance
        supabase.rpc('update_user_balance', {
            'user_uuid': user_id,
            'amount_change': amount
        }).execute()
        
        # Create success notification
        notification = {
            'user_id': user_id,
            'title': 'Crypto Deposit Confirmed! 🎉',
            'message': f'Your {crypto_tx["currency"]} deposit of ${amount:.2f} has been confirmed and added to your balance.',
            'type': 'success',
            'is_read': False
        }
        
        supabase.table('user_notifications').insert(notification).execute()
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "currency": crypto_tx['currency'],
            "message": "Deposit processed successfully"
        }
        
    except Exception as e:
        return {"success": False, "detail": f"Webhook processing failed: {str(e)}"}

@router.post("/crypto/deposit/manual-confirm")
async def manual_confirm_deposit(
    deposit_reference: str,
    transaction_hash: str,
    amount: float,
    admin_key: str = "admin123"
):
    """Manually confirm a deposit (for admin/testing use)"""
    try:
        # Simple admin authentication
        if admin_key != "admin123":
            return {"success": False, "detail": "Unauthorized"}
            
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Find the crypto transaction by reference
        transaction_result = supabase.table('crypto_transactions')\
            .select('*')\
            .eq('reference', deposit_reference)\
            .eq('transaction_type', 'deposit')\
            .eq('status', 'pending')\
            .execute()
        
        if not transaction_result.data:
            return {"success": False, "detail": "Transaction not found or already processed"}
        
        crypto_tx = transaction_result.data[0]
        user_id = crypto_tx['user_id']
        transaction_id = crypto_tx['id']
        
        # Update crypto transaction with confirmation details
        supabase.table('crypto_transactions')\
            .update({
                'amount': amount,
                'transaction_hash': transaction_hash,
                'status': 'confirmed',
                'confirmations': 1,
                'updated_at': 'now()'
            })\
            .eq('id', transaction_id)\
            .execute()
        
        # Create balance transaction (credit user account)
        balance_transaction = {
            'user_id': user_id,
            'transaction_type': 'topup',
            'amount': amount,
            'platform_fee': 0.0,
            'net_amount': amount,
            'status': 'completed',
            'description': f"Crypto deposit: ${amount} from {crypto_tx['currency']} ({crypto_tx['network']})"
        }
        
        balance_result = supabase.table('transactions').insert(balance_transaction).execute()
        
        if balance_result.data:
            balance_tx_id = balance_result.data[0]['id']
            
            # Link crypto transaction to balance transaction
            supabase.table('crypto_transactions')\
                .update({'balance_transaction_id': balance_tx_id})\
                .eq('id', transaction_id)\
                .execute()
        
        # Update user balance
        supabase.rpc('update_user_balance', {
            'user_uuid': user_id,
            'amount_change': amount
        }).execute()
        
        # Create success notification
        notification = {
            'user_id': user_id,
            'title': 'Crypto Deposit Confirmed! 🎉',
            'message': f'Your {crypto_tx["currency"]} deposit of ${amount:.2f} has been confirmed and added to your balance.',
            'type': 'success',
            'is_read': False
        }
        
        supabase.table('user_notifications').insert(notification).execute()
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "currency": crypto_tx['currency'],
            "transaction_hash": transaction_hash,
            "message": "Deposit confirmed successfully"
        }
        
    except Exception as e:
        return {"success": False, "detail": f"Manual confirmation failed: {str(e)}"}

@router.get("/crypto/deposits/pending")
async def get_pending_deposits(admin_key: str = "admin123"):
    """Get all pending deposits (for admin monitoring) from database"""
    try:
        if admin_key != "admin123":
            return {"success": False, "detail": "Unauthorized"}
            
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Get pending deposits from database
        pending_result = supabase.table('crypto_transactions')\
            .select('*')\
            .eq('transaction_type', 'deposit')\
            .eq('status', 'pending')\
            .order('created_at', desc=True)\
            .execute()
        
        pending = []
        for deposit in pending_result.data:
            # Calculate age in minutes
            from datetime import datetime
            created_at = datetime.fromisoformat(deposit['created_at'].replace('Z', '+00:00'))
            age_minutes = (datetime.now().timestamp() - created_at.timestamp()) / 60
            
            pending.append({
                "id": deposit['id'],
                "reference": deposit['reference'],
                "user_id": deposit['user_id'],
                "currency": deposit['currency'],
                "network": deposit['network'],
                "address": deposit['deposit_address'],
                "created_at": deposit['created_at'],
                "age_minutes": age_minutes
            })
                
        return {
            "success": True,
            "pending_deposits": pending,
            "count": len(pending)
        }
        
    except Exception as e:
        return {"success": False, "detail": f"Failed to get pending deposits: {str(e)}"}

@router.get("/crypto/deposits/user/{user_id}")
async def get_user_deposits(user_id: str):
    """Get user's deposit history and pending deposits from database"""
    try:
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Get user's crypto transactions (deposits only)
        deposits_result = supabase.table('crypto_transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('transaction_type', 'deposit')\
            .order('created_at', desc=True)\
            .execute()
        
        deposits = []
        for deposit in deposits_result.data:
            deposits.append({
                "id": deposit['id'],
                "reference": deposit['reference'],
                "currency": deposit['currency'],
                "network": deposit['network'],
                "address": deposit['deposit_address'],
                "amount": deposit['amount'],
                "status": deposit['status'],
                "transaction_hash": deposit['transaction_hash'],
                "confirmations": deposit['confirmations'],
                "created_at": deposit['created_at'],
                "updated_at": deposit['updated_at']
            })
                
        return {
            "success": True,
            "deposits": deposits,
            "count": len(deposits)
        }
        
    except Exception as e:
        return {"success": False, "detail": f"Failed to get user deposits: {str(e)}"}
@router.post("/crypto/withdrawal")
async def submit_withdrawal(request: WithdrawalRequest, user_id: str = "demo_user"):
    """Submit crypto withdrawal request with database integration"""
    try:
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Validate inputs
        if request.currency.upper() not in ['USDT', 'USDC']:
            return {"success": False, "detail": "Unsupported currency"}
        
        if request.network.upper() not in ['ERC20', 'TRC20']:
            return {"success": False, "detail": "Unsupported network"}
        
        if request.amount <= 0 or request.amount > 100000:
            return {"success": False, "detail": "Invalid amount"}
        
        if len(request.recipient_address) < 20:
            return {"success": False, "detail": "Invalid recipient address"}
        
        # Check user balance
        balance_result = supabase.table('user_accounts')\
            .select('balance')\
            .eq('user_id', user_id)\
            .execute()
        
        if not balance_result.data or balance_result.data[0]['balance'] < request.amount:
            return {"success": False, "detail": "Insufficient balance"}
        
        # Calculate withdrawal fees
        withdrawal_fee = max(5.0, request.amount * 0.02)
        total_needed = request.amount + withdrawal_fee
        
        if balance_result.data[0]['balance'] < total_needed:
            return {"success": False, "detail": f"Insufficient balance. Need ${total_needed:.2f} (including ${withdrawal_fee:.2f} fee)"}
        
        # Generate unique batch ID for tracking
        batch_id = f"batch_{int(time.time())}_{user_id[-8:]}"
        
        # Create crypto withdrawal transaction
        crypto_transaction = {
            'user_id': user_id,
            'transaction_type': 'withdrawal',
            'currency': request.currency.upper(),
            'network': request.network.upper(),
            'amount': request.amount,
            'recipient_address': request.recipient_address,
            'memo': request.memo,
            'capitalist_batch_id': batch_id,
            'status': 'processing',
            'network_fee': 0.0,  # Will be updated by Capitalist
            'platform_fee': withdrawal_fee,
            'total_fee': withdrawal_fee
        }
        
        crypto_result = supabase.table('crypto_transactions').insert(crypto_transaction).execute()
        
        if not crypto_result.data:
            return {"success": False, "detail": "Failed to create withdrawal request"}
            
        transaction_id = crypto_result.data[0]['id']
        
        # Create balance transaction (debit user account)
        balance_transaction = {
            'user_id': user_id,
            'transaction_type': 'withdrawal',
            'amount': -total_needed,  # Negative for withdrawal
            'platform_fee': withdrawal_fee,
            'net_amount': -request.amount,
            'status': 'completed',
            'description': f"Crypto withdrawal: ${request.amount} {request.currency} to {request.recipient_address[:10]}...{request.recipient_address[-10:]}"
        }
        
        balance_result = supabase.table('transactions').insert(balance_transaction).execute()
        
        if balance_result.data:
            balance_tx_id = balance_result.data[0]['id']
            
            # Link crypto transaction to balance transaction
            supabase.table('crypto_transactions')\
                .update({'balance_transaction_id': balance_tx_id})\
                .eq('id', transaction_id)\
                .execute()
        
        # Update user balance
        supabase.rpc('update_user_balance', {
            'user_uuid': user_id,
            'amount_change': -total_needed
        }).execute()
        
        # Create notification for withdrawal initiation
        notification = {
            'user_id': user_id,
            'title': 'Withdrawal Request Submitted 📤',
            'message': f'Your withdrawal of ${request.amount:.2f} {request.currency} has been submitted for processing. Estimated completion: 1-24 hours.',
            'type': 'info',
            'is_read': False
        }
        
        supabase.table('user_notifications').insert(notification).execute()
        
        return {
            "success": True,
            "crypto_transaction_id": transaction_id,
            "batch_id": batch_id,
            "amount": request.amount,
            "fee": withdrawal_fee,
            "total_deducted": total_needed,
            "status": "processing",
            "estimated_completion": "1-24 hours",
            "message": "Withdrawal request submitted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "detail": f"Failed to submit withdrawal: {str(e)}"
        }

@router.get("/crypto/transactions")
async def get_crypto_transactions(user_id: str = "demo_user", limit: int = 50):
    """Get user's crypto transaction history from database"""
    try:
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Get user's crypto transactions
        transactions_result = supabase.table('crypto_transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        transactions = []
        for tx in transactions_result.data:
            transactions.append({
                "id": tx['id'],
                "transaction_type": tx['transaction_type'],
                "currency": tx['currency'],
                "network": tx['network'],
                "amount": tx['amount'] or 0.0,
                "status": tx['status'],
                "transaction_hash": tx['transaction_hash'],
                "confirmations": tx['confirmations'] or 0,
                "created_at": tx['created_at'],
                "reference": tx['reference'],
                "deposit_address": tx['deposit_address'],
                "recipient_address": tx['recipient_address'],
                "platform_fee": tx['platform_fee'] or 0.0,
                "total_fee": tx['total_fee'] or 0.0
            })
        
        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions),
            "message": "Real transaction data from database"
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
    """Get crypto transaction status from database"""
    try:
        # Import Supabase client
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase
        
        # Get transaction from database
        transaction_result = supabase.table('crypto_transactions')\
            .select('*')\
            .eq('id', transaction_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not transaction_result.data:
            return {"success": False, "detail": "Transaction not found"}
        
        tx = transaction_result.data[0]
        
        return {
            "success": True,
            "transaction": {
                "id": tx['id'],
                "transaction_type": tx['transaction_type'],
                "currency": tx['currency'],
                "network": tx['network'],
                "amount": tx['amount'] or 0.0,
                "status": tx['status'],
                "transaction_hash": tx['transaction_hash'],
                "confirmations": tx['confirmations'] or 0,
                "created_at": tx['created_at'],
                "updated_at": tx['updated_at'],
                "reference": tx['reference'],
                "deposit_address": tx['deposit_address'],
                "recipient_address": tx['recipient_address']
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "detail": f"Failed to get transaction status: {str(e)}"
        }