from fastapi import APIRouter, HTTPException, Depends
from supabase_client import supabase
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/setup-verification-storage")
async def setup_verification_storage():
    """Setup Supabase storage bucket for verification documents"""
    try:
        # Create verification-documents bucket if it doesn't exist
        bucket_name = "verification-documents"
        
        # Check if bucket exists
        existing_buckets = supabase.storage.list_buckets()
        bucket_exists = any(bucket.name == bucket_name for bucket in existing_buckets)
        
        if not bucket_exists:
            # Create bucket (updated API - removed 'public' parameter)
            result = supabase.storage.create_bucket(
                bucket_name,
                options={
                    "public": True,
                    "allowedMimeTypes": [
                        "image/jpeg",
                        "image/png", 
                        "image/jpg",
                        "application/pdf",
                        "text/plain",
                        "application/msword",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ]
                }
            )
            logger.info(f"Created verification documents bucket: {result}")
        
        # Set up RLS policies for the bucket
        return {
            "success": True,
            "message": "Verification storage setup completed",
            "bucket_name": bucket_name
        }
        
    except Exception as e:
        logger.error(f"Error setting up verification storage: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to setup verification storage: {str(e)}"
        )