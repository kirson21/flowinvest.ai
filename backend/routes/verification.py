from fastapi import APIRouter, HTTPException, Depends
from supabase_client import supabase, supabase_admin
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/verification/health")
async def verification_health_check():
    """Check verification service health"""
    try:
        if supabase:
            # Test database connection
            response = supabase.table('user_profiles').select('count').limit(1).execute()
            connected = response.status_code == 200
        else:
            connected = False
        
        return {
            "success": True,
            "message": "Verification service is healthy",
            "supabase_connected": connected
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Verification service unhealthy: {str(e)}",
            "supabase_connected": False
        }

@router.post("/verification/status/{user_id}")
async def update_verification_status(user_id: str, status_data: dict):
    """Update user verification status"""
    try:
        if not supabase:
            return {"success": False, "message": "Database not available"}
            
        response = supabase.table('user_profiles').update(status_data).eq('user_id', user_id).execute()
        
        if response.data:
            return {"success": True, "message": "Verification status updated", "user": response.data[0]}
        else:
            return {"success": False, "message": "Failed to update verification status"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to update verification status: {str(e)}"}

@router.get("/verification/status/{user_id}")
async def get_verification_status(user_id: str):
    """Get user verification status"""
    try:
        if not supabase:
            return {"success": False, "message": "Database not available"}
            
        response = supabase.table('user_profiles').select('verification_status, verified_at').eq('user_id', user_id).execute()
        
        if response.data and len(response.data) > 0:
            return {"success": True, "verification": response.data[0]}
        else:
            return {"success": False, "message": "User not found"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to get verification status: {str(e)}"}