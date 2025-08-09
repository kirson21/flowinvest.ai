from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
import uuid
from datetime import datetime

from models.trading_bot import ExchangeKeysRequest
from services.bybit_service import BybitService
from services.encryption_service import EncryptionService
from routes.auth import get_current_user

router = APIRouter(prefix="/api/exchange-keys", tags=["Exchange Keys"])

# Initialize services
bybit_service = BybitService()
encryption_service = EncryptionService()

@router.post("/add")
async def add_exchange_keys(
    keys_request: ExchangeKeysRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add encrypted exchange API keys for user"""
    try:
        from database import supabase
        
        # Test connection first
        test_result = await bybit_service.test_connection(
            keys_request.api_key,
            keys_request.api_secret,
            keys_request.exchange_account_type == "testnet"
        )
        
        if not test_result["success"]:
            raise HTTPException(status_code=400, detail=f"API key validation failed: {test_result['error']}")
        
        # Encrypt the credentials
        encrypted_data = encryption_service.encrypt_api_credentials(
            current_user["id"],
            keys_request.api_key,
            keys_request.api_secret,
            keys_request.passphrase
        )
        
        if not encrypted_data["success"]:
            raise HTTPException(status_code=500, detail=f"Encryption failed: {encrypted_data['error']}")
        
        # Store in database
        key_record = {
            "user_id": current_user["id"],
            "exchange": keys_request.exchange,
            "exchange_account_type": keys_request.exchange_account_type,
            "api_key_encrypted": encrypted_data["api_key_encrypted"],
            "api_secret_encrypted": encrypted_data["api_secret_encrypted"],
            "passphrase_encrypted": encrypted_data["passphrase_encrypted"],
            "encryption_key_id": encrypted_data["encryption_key_id"],
            "salt": encrypted_data["salt"],
            "last_verified_at": datetime.utcnow().isoformat()
        }
        
        # Deactivate existing keys for this exchange type
        supabase.table('user_exchange_keys').update({
            "is_active": False
        }).eq('user_id', current_user["id"]).eq('exchange', keys_request.exchange).eq('exchange_account_type', keys_request.exchange_account_type).execute()
        
        # Insert new keys
        response = supabase.table('user_exchange_keys').insert(key_record).execute()
        
        if response.data:
            return {
                "success": True,
                "message": f"{keys_request.exchange} API keys added successfully",
                "test_result": test_result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store API keys")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to add exchange keys: {str(e)}")

@router.get("/")
async def get_user_exchange_keys(current_user: dict = Depends(get_current_user)):
    """Get user's exchange keys (encrypted data only, not decrypted)"""
    try:
        from database import supabase
        
        response = supabase.table('user_exchange_keys').select(
            'id, exchange, exchange_account_type, is_active, last_verified_at, created_at'
        ).eq('user_id', current_user["id"]).eq('is_active', True).execute()
        
        return {
            "success": True,
            "keys": response.data or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch exchange keys: {str(e)}")

@router.post("/test/{key_id}")
async def test_exchange_keys(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Test existing exchange keys"""
    try:
        from ..database import supabase
        
        # Get encrypted keys
        keys_response = supabase.table('user_exchange_keys').select('*').eq('id', key_id).eq('user_id', current_user["id"]).single().execute()
        
        if not keys_response.data:
            raise HTTPException(status_code=404, detail="Exchange keys not found")
        
        encrypted_keys = keys_response.data
        
        # Decrypt keys
        decrypted = encryption_service.decrypt_api_credentials(current_user["id"], {
            "api_key_encrypted": encrypted_keys["api_key_encrypted"],
            "api_secret_encrypted": encrypted_keys["api_secret_encrypted"],
            "passphrase_encrypted": encrypted_keys.get("passphrase_encrypted"),
            "salt": encrypted_keys["salt"]
        })
        
        if not decrypted["success"]:
            raise HTTPException(status_code=500, detail=f"Decryption failed: {decrypted['error']}")
        
        # Test connection
        test_result = await bybit_service.test_connection(
            decrypted["api_key"],
            decrypted["api_secret"],
            encrypted_keys["exchange_account_type"] == "testnet"
        )
        
        # Update last verified time if successful
        if test_result["success"]:
            supabase.table('user_exchange_keys').update({
                "last_verified_at": datetime.utcnow().isoformat()
            }).eq('id', key_id).execute()
        
        return {
            "success": True,
            "test_result": test_result
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to test exchange keys: {str(e)}")

@router.delete("/{key_id}")
async def delete_exchange_keys(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete exchange keys"""
    try:
        from ..database import supabase
        
        response = supabase.table('user_exchange_keys').delete().eq('id', key_id).eq('user_id', current_user["id"]).execute()
        
        if response.data:
            return {
                "success": True,
                "message": "Exchange keys deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Exchange keys not found")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to delete exchange keys: {str(e)}")

@router.get("/supported-exchanges")
async def get_supported_exchanges():
    """Get list of supported exchanges"""
    return {
        "success": True,
        "exchanges": [
            {
                "id": "bybit",
                "name": "Bybit",
                "logo": "/logos/bybit.png",
                "supports_testnet": True,
                "supports_futures": True,
                "supports_spot": True
            }
        ]
    }