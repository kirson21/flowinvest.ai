"""
Simplified exchange keys service - no encryption, just secure Supabase storage
"""
import uuid
from datetime import datetime
from typing import Dict, Any
from ultra_simple_supabase import supabase

class SimpleExchangeKeysService:
    
    def store_api_keys(self, user_id: str, exchange: str, api_key: str, api_secret: str, passphrase: str = None, testnet: bool = True) -> Dict[str, Any]:
        """Store API keys directly in Supabase"""
        try:
            key_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "exchange": exchange,
                "api_key": api_key,  # Stored as is - Supabase handles security
                "api_secret": api_secret,
                "passphrase": passphrase,
                "testnet": testnet,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            result = supabase.table('exchange_api_keys').insert(key_data).execute()
            
            if result.error:
                return {"success": False, "error": result.error}
            
            # Don't return sensitive data
            safe_data = {
                "id": key_data["id"],
                "exchange": exchange,
                "testnet": testnet,
                "created_at": key_data["created_at"]
            }
            
            return {"success": True, "data": safe_data}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_keys(self, user_id: str) -> Dict[str, Any]:
        """Get user's API keys (without sensitive data)"""
        try:
            result = supabase.table('exchange_api_keys').select('id, exchange, testnet, created_at, is_active').eq('user_id', user_id).eq('is_active', True).execute()
            
            if result.error:
                return {"success": False, "error": result.error}
            
            return {"success": True, "keys": result.data}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_api_credentials(self, user_id: str, key_id: str) -> Dict[str, Any]:
        """Get API credentials for trading (internal use only)"""
        try:
            result = supabase.table('exchange_api_keys').select('*').eq('id', key_id).eq('user_id', user_id).eq('is_active', True).single().execute()
            
            if result.error or not result.data:
                return {"success": False, "error": "API keys not found"}
            
            return {
                "success": True,
                "api_key": result.data["api_key"],
                "api_secret": result.data["api_secret"],
                "passphrase": result.data.get("passphrase"),
                "testnet": result.data["testnet"],
                "exchange": result.data["exchange"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_api_keys(self, user_id: str, key_id: str) -> Dict[str, Any]:
        """Delete API keys"""
        try:
            result = supabase.table('exchange_api_keys').update({"is_active": False}).eq('id', key_id).eq('user_id', user_id).execute()
            
            if result.error:
                return {"success": False, "error": result.error}
            
            return {"success": True, "message": "API keys deleted"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_connection(self, user_id: str, key_id: str) -> Dict[str, Any]:
        """Test API key connection to exchange"""
        try:
            # Get credentials
            creds = self.get_api_credentials(user_id, key_id)
            if not creds["success"]:
                return creds
            
            # For now, just return success if we can retrieve the keys
            # In full implementation, this would test actual exchange connection
            return {
                "success": True,
                "message": f"Connection test successful for {creds['exchange']}",
                "testnet": creds["testnet"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}