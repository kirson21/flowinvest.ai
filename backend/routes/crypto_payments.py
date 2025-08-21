"""
Crypto Payments API Routes for Capitalist Integration
Handles deposits, withdrawals, and crypto transaction management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator
from typing import Optional, List
import os
import logging
from datetime import datetime
import uuid

# Import with error handling
try:
    from supabase_client import supabase_admin
except ImportError:
    supabase_admin = None
    logging.warning("Supabase client not available - some features will be limited")

try:
    from services.capitalist_client import CapitalistAPIClient, CurrencyType, validate_crypto_address
except ImportError:
    logging.warning("Capitalist client not available - using mock functionality")
    CapitalistAPIClient = None
    CurrencyType = None
    validate_crypto_address = None

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Capitalist client
def get_capitalist_client():
    """Get configured Capitalist API client"""
    try:
        client = CapitalistAPIClient(
            api_url=os.getenv('CAPITALIST_API_URL', 'https://api.capitalist.net/'),
            username=os.getenv('CAPITALIST_USERNAME'),
            password=os.getenv('CAPITALIST_PASSWORD'),
            cert_path=os.getenv('CAPITALIST_CERT_PATH', '/app/certificates/baad707566.pem'),
            cert_password=os.getenv('CAPITALIST_CERT_PASSWORD')
        )
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Capitalist client: {e}")
        raise HTTPException(status_code=500, detail="Payment service unavailable")

# Pydantic models with v1/v2 compatibility
try:
    from pydantic import Field
    # Try v2 syntax first
    class DepositAddressRequest(BaseModel):
        currency: str = Field(..., description="Currency code")
        network: str = Field(..., description="Network type")
        
        def validate_currency(cls, v):
            if v.upper() not in ['USDT', 'USDC']:
                raise ValueError('Currency must be USDT or USDC')
            return v.upper()
        
        def validate_network(cls, v):
            if v.upper() not in ['ERC20', 'TRC20']:
                raise ValueError('Network must be ERC20 or TRC20')
            return v.upper()

    class WithdrawalRequest(BaseModel):
        recipient_address: str = Field(..., description="Recipient crypto address")
        amount: float = Field(..., gt=0, le=1000000, description="Amount to withdraw")
        currency: str = Field(..., description="Currency code")
        network: str = Field(..., description="Network type")
        memo: Optional[str] = Field(None, description="Optional memo")
        
        def validate_currency(cls, v):
            if v.upper() not in ['USDT', 'USDC']:
                raise ValueError('Currency must be USDT or USDC')
            return v.upper()
        
        def validate_network(cls, v):
            if v.upper() not in ['ERC20', 'TRC20']:
                raise ValueError('Network must be ERC20 or TRC20')
            return v.upper()
        
        def validate_address_format(cls, v, values):
            if len(v) < 20 or len(v) > 64:
                raise ValueError('Invalid address format')
            return v

    class DepositConfirmationRequest(BaseModel):
        crypto_transaction_id: str = Field(..., description="Crypto transaction ID")
        transaction_hash: str = Field(..., description="Blockchain transaction hash")
        confirmations: int = Field(1, ge=1, description="Number of confirmations")

except Exception as e:
    # Fallback to v1 syntax
    class DepositAddressRequest(BaseModel):
        currency: str
        network: str
        
        @validator('currency')
        def validate_currency(cls, v):
            if v.upper() not in ['USDT', 'USDC']:
                raise ValueError('Currency must be USDT or USDC')
            return v.upper()
        
        @validator('network')
        def validate_network(cls, v):
            if v.upper() not in ['ERC20', 'TRC20']:
                raise ValueError('Network must be ERC20 or TRC20')
            return v.upper()

    class WithdrawalRequest(BaseModel):
        recipient_address: str
        amount: float
        currency: str
        network: str
        memo: Optional[str] = None
        
        @validator('currency')
        def validate_currency(cls, v):
            if v.upper() not in ['USDT', 'USDC']:
                raise ValueError('Currency must be USDT or USDC')
            return v.upper()
        
        @validator('network')
        def validate_network(cls, v):
            if v.upper() not in ['ERC20', 'TRC20']:
                raise ValueError('Network must be ERC20 or TRC20')
            return v.upper()
        
        @validator('amount')
        def validate_amount(cls, v):
            if v <= 0:
                raise ValueError('Amount must be greater than 0')
            if v > 1000000:
                raise ValueError('Amount exceeds maximum limit of 1,000,000')
            return round(v, 8)
        
        @validator('recipient_address')
        def validate_address_format(cls, v, values):
            if len(v) < 20 or len(v) > 64:
                raise ValueError('Invalid address format')
            return v

    class DepositConfirmationRequest(BaseModel):
        crypto_transaction_id: str
        transaction_hash: str
        confirmations: int = 1

# =====================================================
# DEPOSIT ENDPOINTS
# =====================================================

@router.post("/crypto/deposit/address")
async def create_deposit_address(
    request: DepositAddressRequest,
    user_id: str
):
    """Generate or retrieve deposit address for user"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        logger.info(f"Creating deposit address for user {user_id}: {request.currency} {request.network}")
        
        # Check for existing active address
        existing_response = supabase_admin.table('deposit_addresses')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('currency', request.currency)\
            .eq('network', request.network)\
            .eq('is_active', True)\
            .execute()
        
        if existing_response.data and len(existing_response.data) > 0:
            existing_address = existing_response.data[0]
            return {
                "success": True,
                "address": existing_address['address'],
                "currency": request.currency,
                "network": request.network,
                "memo": existing_address.get('memo'),
                "is_new": False,
                "message": "Existing deposit address returned"
            }
        
        # Generate new address via Capitalist API
        client = get_capitalist_client()
        currency_type = CurrencyType(f"{request.currency}_{request.network}")
        
        deposit_address = client.create_deposit_address(currency_type, user_id)
        
        if not deposit_address:
            raise HTTPException(status_code=500, detail="Failed to generate deposit address")
        
        # Store in database
        insert_response = supabase_admin.table('deposit_addresses').insert({
            'user_id': user_id,
            'address': deposit_address.address,
            'currency': request.currency,
            'network': request.network,
            'memo': deposit_address.memo,
            'is_active': True
        }).execute()
        
        if not insert_response.data:
            logger.warning(f"Failed to store deposit address in database: {deposit_address.address}")
        
        return {
            "success": True,
            "address": deposit_address.address,
            "currency": request.currency,
            "network": request.network,
            "memo": deposit_address.memo,
            "is_new": True,
            "message": "New deposit address generated",
            "instructions": {
                "step1": f"Send {request.currency} to the address above using {request.network} network",
                "step2": "Your account will be credited automatically after confirmation",
                "step3": "Minimum deposit: $10 USD equivalent",
                "warning": "Only send supported tokens to this address. Sending other tokens may result in permanent loss."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create deposit address error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/crypto/deposit/confirm")
async def confirm_deposit(
    request: DepositConfirmationRequest,
    background_tasks: BackgroundTasks
):
    """Confirm crypto deposit (typically called by webhook or monitoring service)"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        logger.info(f"Confirming deposit: {request.crypto_transaction_id}")
        
        # Use the database function to process deposit
        result = supabase_admin.rpc('process_crypto_deposit', {
            'p_crypto_transaction_id': request.crypto_transaction_id,
            'p_transaction_hash': request.transaction_hash,
            'p_confirmations': request.confirmations
        }).execute()
        
        if result.data:
            return result.data
        else:
            raise HTTPException(status_code=500, detail="Failed to process deposit confirmation")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Confirm deposit error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# =====================================================
# WITHDRAWAL ENDPOINTS
# =====================================================

@router.post("/crypto/withdrawal")
async def submit_withdrawal(
    request: WithdrawalRequest,
    user_id: str,
    background_tasks: BackgroundTasks
):
    """Submit crypto withdrawal request"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        logger.info(f"Processing withdrawal request for user {user_id}: {request.amount} {request.currency}")
        
        # Validate cryptocurrency address
        currency_type = CurrencyType(f"{request.currency}_{request.network}")
        if not validate_crypto_address(request.recipient_address, currency_type):
            raise HTTPException(status_code=400, detail="Invalid recipient address format")
        
        # Check user balance
        balance_response = supabase_admin.table('user_accounts')\
            .select('balance')\
            .eq('user_id', user_id)\
            .execute()
        
        if not balance_response.data:
            raise HTTPException(status_code=400, detail="User account not found")
        
        current_balance = float(balance_response.data[0]['balance']) if balance_response.data[0]['balance'] else 0.0
        
        # Calculate fees (you can adjust these based on your business model)
        withdrawal_fee = max(5.0, request.amount * 0.02)  # Min $5 or 2% of amount
        total_amount_needed = request.amount + withdrawal_fee
        
        if current_balance < total_amount_needed:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Required: ${total_amount_needed:.2f} (amount: ${request.amount:.2f} + fee: ${withdrawal_fee:.2f}), Available: ${current_balance:.2f}"
            )
        
        # Create crypto transaction record
        crypto_tx_id = str(uuid.uuid4())
        crypto_tx_response = supabase_admin.table('crypto_transactions').insert({
            'id': crypto_tx_id,
            'user_id': user_id,
            'transaction_type': 'withdrawal',
            'currency': request.currency,
            'network': request.network,
            'amount': request.amount,
            'recipient_address': request.recipient_address,
            'memo': request.memo,
            'status': 'pending',
            'platform_fee': withdrawal_fee,
            'total_fee': withdrawal_fee,
            'reference': f"withdrawal_{crypto_tx_id[:8]}"
        }).execute()
        
        if not crypto_tx_response.data:
            raise HTTPException(status_code=500, detail="Failed to create withdrawal record")
        
        # Deduct balance immediately (hold the funds)
        new_balance = current_balance - total_amount_needed
        balance_update_response = supabase_admin.table('user_accounts')\
            .update({'balance': new_balance})\
            .eq('user_id', user_id)\
            .execute()
        
        if not balance_update_response.data:
            # Rollback crypto transaction
            supabase_admin.table('crypto_transactions').delete().eq('id', crypto_tx_id).execute()
            raise HTTPException(status_code=500, detail="Failed to update user balance")
        
        # Create balance transaction record
        balance_tx_response = supabase_admin.table('transactions').insert({
            'user_id': user_id,
            'transaction_type': 'withdrawal',
            'amount': total_amount_needed,
            'platform_fee': withdrawal_fee,
            'net_amount': request.amount,
            'status': 'pending',
            'description': f'Crypto withdrawal: {request.amount} USD to {request.currency} ({request.network})'
        }).execute()
        
        balance_tx_id = balance_tx_response.data[0]['id'] if balance_tx_response.data else None
        
        # Link transactions
        if balance_tx_id:
            supabase_admin.table('crypto_transactions')\
                .update({'balance_transaction_id': balance_tx_id})\
                .eq('id', crypto_tx_id)\
                .execute()
        
        # Submit to Capitalist API
        client = get_capitalist_client()
        from services.capitalist_client import WithdrawalRequest as CapitalistWithdrawal
        
        capitalist_withdrawal = CapitalistWithdrawal(
            recipient_address=request.recipient_address,
            amount=request.amount,
            currency=currency_type,
            network=request.network,
            memo=request.memo,
            reference=f"withdrawal_{crypto_tx_id[:8]}"
        )
        
        batch_id = client.submit_withdrawal(capitalist_withdrawal)
        
        if batch_id:
            # Update crypto transaction with batch ID
            supabase_admin.table('crypto_transactions')\
                .update({
                    'capitalist_batch_id': batch_id,
                    'status': 'processing'
                })\
                .eq('id', crypto_tx_id)\
                .execute()
            
            # Update balance transaction
            if balance_tx_id:
                supabase_admin.table('transactions')\
                    .update({'status': 'processing'})\
                    .eq('id', balance_tx_id)\
                    .execute()
            
            # Schedule status monitoring
            background_tasks.add_task(monitor_withdrawal_status, crypto_tx_id, batch_id)
            
            # Create notification
            supabase_admin.table('user_notifications').insert({
                'user_id': user_id,
                'title': 'Withdrawal Request Submitted',
                'message': f'Your withdrawal of ${request.amount:.2f} {request.currency} has been submitted for processing. You will be notified when it\'s complete.',
                'type': 'info',
                'is_read': False
            }).execute()
            
            return {
                "success": True,
                "crypto_transaction_id": crypto_tx_id,
                "batch_id": batch_id,
                "amount": request.amount,
                "fee": withdrawal_fee,
                "total_deducted": total_amount_needed,
                "new_balance": new_balance,
                "status": "processing",
                "estimated_completion": "1-24 hours",
                "message": "Withdrawal request submitted successfully"
            }
        else:
            # Capitalist API failed, rollback everything
            supabase_admin.table('user_accounts')\
                .update({'balance': current_balance})\
                .eq('user_id', user_id)\
                .execute()
            
            supabase_admin.table('crypto_transactions')\
                .update({'status': 'failed', 'error_message': 'Failed to submit to payment processor'})\
                .eq('id', crypto_tx_id)\
                .execute()
            
            if balance_tx_id:
                supabase_admin.table('transactions')\
                    .update({'status': 'failed'})\
                    .eq('id', balance_tx_id)\
                    .execute()
            
            raise HTTPException(status_code=500, detail="Failed to submit withdrawal to payment processor")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit withdrawal error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# =====================================================
# TRANSACTION MANAGEMENT ENDPOINTS
# =====================================================

@router.get("/crypto/transactions")
async def get_crypto_transactions(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    transaction_type: Optional[str] = None
):
    """Get user's crypto transaction history"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        query = supabase_admin.table('crypto_transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .offset(offset)
        
        if transaction_type:
            query = query.eq('transaction_type', transaction_type)
        
        response = query.execute()
        
        return {
            "success": True,
            "transactions": response.data if response.data else [],
            "count": len(response.data) if response.data else 0
        }
        
    except Exception as e:
        logger.error(f"Get crypto transactions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/crypto/supported-currencies")
async def get_supported_currencies():
    """Get list of supported cryptocurrencies and networks"""
    from services.capitalist_client import get_supported_currencies
    
    return {
        "success": True,
        "currencies": get_supported_currencies(),
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
async def get_transaction_status(transaction_id: str, user_id: str):
    """Get crypto transaction status"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        response = supabase_admin.table('crypto_transactions')\
            .select('*')\
            .eq('id', transaction_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        transaction = response.data[0]
        
        # If it's a withdrawal with batch_id, check Capitalist API for latest status
        if (transaction['transaction_type'] == 'withdrawal' and 
            transaction.get('capitalist_batch_id') and 
            transaction['status'] in ['pending', 'processing']):
            
            try:
                client = get_capitalist_client()
                api_status = client.get_transaction_status(transaction['capitalist_batch_id'])
                
                if api_status and api_status.status != transaction['status']:
                    # Update local status
                    new_status = 'confirmed' if api_status.status.lower() in ['completed', 'success'] else api_status.status
                    supabase_admin.table('crypto_transactions')\
                        .update({
                            'status': new_status,
                            'transaction_hash': api_status.transaction_hash,
                            'confirmations': api_status.confirmations
                        })\
                        .eq('id', transaction_id)\
                        .execute()
                    
                    transaction['status'] = new_status
                    transaction['transaction_hash'] = api_status.transaction_hash
                    transaction['confirmations'] = api_status.confirmations
            except Exception as e:
                logger.warning(f"Failed to check API status for transaction {transaction_id}: {e}")
        
        return {
            "success": True,
            "transaction": transaction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get transaction status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# =====================================================
# ADMIN/MONITORING ENDPOINTS
# =====================================================

@router.get("/crypto/company-balance")
async def get_company_balance():
    """Get company balance overview (admin only)"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database not available")
        
        response = supabase_admin.table('company_balance')\
            .select('*')\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Company balance not found")
        
        return {
            "success": True,
            "balance": response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get company balance error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/crypto/health")
async def crypto_health_check():
    """Health check for crypto payment service"""
    try:
        # Test database connection
        db_status = "healthy"
        try:
            supabase_admin.table('crypto_transactions').select('id').limit(1).execute()
        except:
            db_status = "unhealthy"
        
        # Test Capitalist API connection
        api_status = "unknown"
        try:
            client = get_capitalist_client()
            test_result = client.test_connection()
            api_status = "healthy" if test_result['success'] else "unhealthy"
        except:
            api_status = "unhealthy"
        
        overall_status = "healthy" if db_status == "healthy" and api_status == "healthy" else "degraded"
        
        return {
            "status": overall_status,
            "database": db_status,
            "capitalist_api": api_status,
            "supported_currencies": ["USDT", "USDC"],
            "supported_networks": ["ERC20", "TRC20"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# =====================================================
# BACKGROUND TASKS
# =====================================================

async def monitor_withdrawal_status(crypto_transaction_id: str, batch_id: str):
    """Background task to monitor withdrawal status"""
    try:
        logger.info(f"Starting withdrawal monitoring for {crypto_transaction_id}, batch: {batch_id}")
        
        # This would typically run periodically to check status
        # For now, we'll do a one-time check after a delay
        import asyncio
        await asyncio.sleep(60)  # Wait 1 minute before checking
        
        client = get_capitalist_client()
        status = client.get_transaction_status(batch_id)
        
        if status:
            new_status = 'confirmed' if status.status.lower() in ['completed', 'success'] else status.status
            
            # Update crypto transaction
            supabase_admin.table('crypto_transactions')\
                .update({
                    'status': new_status,
                    'transaction_hash': status.transaction_hash,
                    'confirmations': status.confirmations
                })\
                .eq('id', crypto_transaction_id)\
                .execute()
            
            # Update linked balance transaction
            supabase_admin.table('transactions')\
                .update({'status': 'completed' if new_status == 'confirmed' else new_status})\
                .eq('balance_transaction_id', crypto_transaction_id)\
                .execute()
            
            # Get user_id for notification
            tx_response = supabase_admin.table('crypto_transactions')\
                .select('user_id, amount, currency')\
                .eq('id', crypto_transaction_id)\
                .execute()
            
            if tx_response.data:
                tx_data = tx_response.data[0]
                
                # Create completion notification
                notification_title = "Withdrawal Completed" if new_status == 'confirmed' else f"Withdrawal {new_status.title()}"
                notification_message = (
                    f"Your withdrawal of ${tx_data['amount']:.2f} {tx_data['currency']} has been {new_status}."
                    if new_status == 'confirmed' else
                    f"Your withdrawal status has been updated to: {new_status}"
                )
                
                supabase_admin.table('user_notifications').insert({
                    'user_id': tx_data['user_id'],
                    'title': notification_title,
                    'message': notification_message,
                    'type': 'success' if new_status == 'confirmed' else 'warning',
                    'is_read': False
                }).execute()
        
        logger.info(f"Withdrawal monitoring completed for {crypto_transaction_id}")
        
    except Exception as e:
        logger.error(f"Withdrawal monitoring error for {crypto_transaction_id}: {e}")