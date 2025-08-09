"""
Fallback encryption service for deployment environments
"""
import os

def get_encryption_service():
    """Get encryption service, fallback to simple version if cryptography not available"""
    try:
        from .services.encryption_service import EncryptionService
        return EncryptionService()
    except ImportError as e:
        print(f"Cryptography package not available ({e}), using simple encryption")
        from .simple_encryption import SimpleEncryptionService  
        return SimpleEncryptionService()

# Create service instance
encryption_service = get_encryption_service()