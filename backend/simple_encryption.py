"""
Simple encryption service using base64 encoding
For deployment environments that can't compile cryptography package
"""
import base64
import json
import os
import secrets
import hashlib
from typing import Dict, Any

class SimpleEncryptionService:
    def __init__(self):
        # Use a simple key derivation
        self.master_key = self._get_or_create_master_key()
    
    def _get_or_create_master_key(self) -> str:
        """Get or create master encryption key"""
        master_key = os.getenv('MASTER_ENCRYPTION_KEY')
        if not master_key:
            # Generate a simple key
            master_key = base64.b64encode(secrets.token_bytes(32)).decode()
            print(f"Generated simple master key: {master_key}")
            print("Please save this key in your environment as MASTER_ENCRYPTION_KEY")
        return master_key
    
    def _simple_encrypt(self, data: str, key: str) -> str:
        """Simple XOR-based encryption (not cryptographically secure, but works for deployment)"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        data_bytes = data.encode()
        
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted).decode()
    
    def _simple_decrypt(self, encrypted_data: str, key: str) -> str:
        """Simple XOR-based decryption"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return decrypted.decode()
    
    def encrypt_api_credentials(self, user_id: str, api_key: str, api_secret: str, passphrase: str = None) -> Dict[str, Any]:
        """Encrypt API credentials for secure storage"""
        try:
            # Create user-specific key
            user_key = f"{user_id}:{self.master_key}"
            salt = secrets.token_hex(16)
            
            # Encrypt credentials
            encrypted_api_key = self._simple_encrypt(api_key, user_key + salt)
            encrypted_api_secret = self._simple_encrypt(api_secret, user_key + salt)
            encrypted_passphrase = None
            
            if passphrase:
                encrypted_passphrase = self._simple_encrypt(passphrase, user_key + salt)
            
            return {
                "api_key_encrypted": encrypted_api_key,
                "api_secret_encrypted": encrypted_api_secret,
                "passphrase_encrypted": encrypted_passphrase,
                "encryption_key_id": f"simple_{user_id}_{secrets.token_hex(4)}",
                "salt": salt,
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Encryption failed: {str(e)}"
            }
    
    def decrypt_api_credentials(self, user_id: str, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt API credentials for use"""
        try:
            # Get salt and reconstruct key
            salt = encrypted_data["salt"]
            user_key = f"{user_id}:{self.master_key}"
            
            # Decrypt credentials
            api_key = self._simple_decrypt(encrypted_data["api_key_encrypted"], user_key + salt)
            api_secret = self._simple_decrypt(encrypted_data["api_secret_encrypted"], user_key + salt)
            
            passphrase = None
            if encrypted_data.get("passphrase_encrypted"):
                passphrase = self._simple_decrypt(encrypted_data["passphrase_encrypted"], user_key + salt)
            
            return {
                "api_key": api_key,
                "api_secret": api_secret,
                "passphrase": passphrase,
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Decryption failed: {str(e)}"
            }
    
    def validate_encryption_setup(self) -> Dict[str, Any]:
        """Validate that encryption is properly set up"""
        try:
            # Test encryption/decryption cycle
            test_user_id = "test_user_123"
            test_data = "test_api_key_12345"
            
            # Encrypt
            encrypted = self.encrypt_api_credentials(test_user_id, test_data, "test_secret")
            if not encrypted["success"]:
                return {"success": False, "error": "Encryption test failed"}
            
            # Decrypt
            decrypted = self.decrypt_api_credentials(test_user_id, encrypted)
            
            if not decrypted["success"]:
                return {"success": False, "error": "Decryption test failed"}
            
            if decrypted["api_key"] != test_data:
                return {"success": False, "error": "Encryption/decryption mismatch"}
            
            return {
                "success": True,
                "message": "Simple encryption service is working correctly",
                "master_key_set": bool(os.getenv('MASTER_ENCRYPTION_KEY'))
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Encryption validation failed: {str(e)}"
            }