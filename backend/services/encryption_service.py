import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import json
from typing import Dict, Any, Tuple

class EncryptionService:
    def __init__(self):
        # Get master encryption key from environment or generate one
        self.master_key = self._get_or_create_master_key()
        
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        
        # Try to get from environment variable
        master_key_b64 = os.getenv('MASTER_ENCRYPTION_KEY')
        
        if master_key_b64:
            try:
                return base64.urlsafe_b64decode(master_key_b64)
            except Exception:
                print("Warning: Invalid master key in environment, generating new one")
        
        # Generate new master key if not found
        key = Fernet.generate_key()
        print(f"Generated new master encryption key: {base64.urlsafe_b64encode(key).decode()}")
        print("Please save this key in your environment as MASTER_ENCRYPTION_KEY")
        
        return key
    
    def _derive_key_from_user_id(self, user_id: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """Derive encryption key from user ID and salt"""
        
        if salt is None:
            salt = secrets.token_bytes(16)
        
        # Use user ID and master key to derive unique key
        password = f"{user_id}:{base64.urlsafe_b64encode(self.master_key).decode()}".encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key, salt
    
    def encrypt_api_credentials(self, user_id: str, api_key: str, api_secret: str, passphrase: str = None) -> Dict[str, Any]:
        """Encrypt API credentials for secure storage"""
        
        try:
            # Generate user-specific encryption key
            encryption_key, salt = self._derive_key_from_user_id(user_id)
            fernet = Fernet(encryption_key)
            
            # Encrypt credentials
            encrypted_api_key = fernet.encrypt(api_key.encode()).decode()
            encrypted_api_secret = fernet.encrypt(api_secret.encode()).decode()
            encrypted_passphrase = None
            
            if passphrase:
                encrypted_passphrase = fernet.encrypt(passphrase.encode()).decode()
            
            # Create encryption metadata
            encryption_key_id = f"user_{user_id}_{secrets.token_hex(8)}"
            salt_b64 = base64.urlsafe_b64encode(salt).decode()
            
            return {
                "api_key_encrypted": encrypted_api_key,
                "api_secret_encrypted": encrypted_api_secret,
                "passphrase_encrypted": encrypted_passphrase,
                "encryption_key_id": encryption_key_id,
                "salt": salt_b64,
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
            # Get salt from metadata
            salt = base64.urlsafe_b64decode(encrypted_data["salt"])
            
            # Derive the same encryption key
            encryption_key, _ = self._derive_key_from_user_id(user_id, salt)
            fernet = Fernet(encryption_key)
            
            # Decrypt credentials
            api_key = fernet.decrypt(encrypted_data["api_key_encrypted"].encode()).decode()
            api_secret = fernet.decrypt(encrypted_data["api_secret_encrypted"].encode()).decode()
            
            passphrase = None
            if encrypted_data.get("passphrase_encrypted"):
                passphrase = fernet.decrypt(encrypted_data["passphrase_encrypted"].encode()).decode()
            
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
    
    def encrypt_sensitive_data(self, user_id: str, data: Any) -> Dict[str, Any]:
        """Encrypt any sensitive data"""
        
        try:
            # Convert data to JSON string if not already string
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
            
            # Generate user-specific encryption key
            encryption_key, salt = self._derive_key_from_user_id(user_id)
            fernet = Fernet(encryption_key)
            
            # Encrypt data
            encrypted_data = fernet.encrypt(data_str.encode()).decode()
            salt_b64 = base64.urlsafe_b64encode(salt).decode()
            
            return {
                "encrypted_data": encrypted_data,
                "salt": salt_b64,
                "success": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Encryption failed: {str(e)}"
            }
    
    def decrypt_sensitive_data(self, user_id: str, encrypted_data: str, salt: str) -> Dict[str, Any]:
        """Decrypt sensitive data"""
        
        try:
            # Get salt
            salt_bytes = base64.urlsafe_b64decode(salt)
            
            # Derive encryption key
            encryption_key, _ = self._derive_key_from_user_id(user_id, salt_bytes)
            fernet = Fernet(encryption_key)
            
            # Decrypt data
            decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
            
            # Try to parse as JSON
            try:
                parsed_data = json.loads(decrypted_data)
                return {
                    "data": parsed_data,
                    "success": True
                }
            except json.JSONDecodeError:
                return {
                    "data": decrypted_data,
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
            encrypted = self.encrypt_sensitive_data(test_user_id, test_data)
            if not encrypted["success"]:
                return {"success": False, "error": "Encryption test failed"}
            
            # Decrypt
            decrypted = self.decrypt_sensitive_data(
                test_user_id, 
                encrypted["encrypted_data"], 
                encrypted["salt"]
            )
            
            if not decrypted["success"]:
                return {"success": False, "error": "Decryption test failed"}
            
            if decrypted["data"] != test_data:
                return {"success": False, "error": "Encryption/decryption mismatch"}
            
            return {
                "success": True,
                "message": "Encryption service is working correctly",
                "master_key_set": bool(os.getenv('MASTER_ENCRYPTION_KEY'))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Encryption validation failed: {str(e)}"
            }
    
    @staticmethod
    def generate_master_key() -> str:
        """Generate a new master encryption key"""
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode()
    
    def rotate_user_encryption(self, user_id: str, old_encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate encryption for a user (re-encrypt with new salt)"""
        
        try:
            # Decrypt with old key
            decrypted = self.decrypt_api_credentials(user_id, old_encrypted_data)
            if not decrypted["success"]:
                return {"success": False, "error": "Failed to decrypt old data"}
            
            # Re-encrypt with new salt
            new_encrypted = self.encrypt_api_credentials(
                user_id,
                decrypted["api_key"],
                decrypted["api_secret"],
                decrypted.get("passphrase")
            )
            
            return new_encrypted
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Key rotation failed: {str(e)}"
            }