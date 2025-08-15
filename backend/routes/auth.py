from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from supabase_client import supabase, supabase_admin
from typing import Optional
import os

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class EmailPasswordSignIn(BaseModel):
    email: EmailStr
    password: str

class EmailPasswordSignUp(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    country: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    session: Optional[dict] = None

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    country: Optional[str] = None
    avatar_url: Optional[str] = None

# Note: Authentication is handled by frontend with Supabase directly
# Backend provides user management and profile endpoints

@router.get("/auth/health")
async def auth_health_check():
    """Check authentication service health"""
    try:
        # Test database connection
        if supabase:
            response = supabase.table('user_profiles').select('count').limit(1).execute()
            connected = response.status_code == 200
        else:
            connected = False
        
        return {
            "success": True,
            "message": "Authentication service is healthy",
            "supabase_connected": connected
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Authentication service unhealthy: {str(e)}",
            "supabase_connected": False
        }

@router.get("/auth/user/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    try:
        if not supabase:
            return {"success": False, "message": "Database not available"}
            
        response = supabase.table('user_profiles').select('*').eq('user_id', user_id).execute()
        
        if response.data and len(response.data) > 0:
            return {"success": True, "user": response.data[0]}
        else:
            return {"success": False, "message": "User not found"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to get user profile: {str(e)}"}

@router.put("/auth/user/{user_id}/profile")
async def update_user_profile(user_id: str, profile_data: dict):
    """Update user profile"""
    try:
        if not supabase:
            return {"success": False, "message": "Database not available"}
            
        response = supabase.table('user_profiles').update(profile_data).eq('user_id', user_id).execute()
        
        if response.data:
            return {"success": True, "message": "Profile updated successfully", "user": response.data[0]}
        else:
            return {"success": False, "message": "Failed to update profile"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to update profile: {str(e)}"}

@router.post("/auth/user/{user_id}/profile")
async def create_user_profile(user_id: str, profile_data: dict):
    """Create user profile"""
    try:
        if not supabase:
            return {"success": False, "message": "Database not available"}
            
        profile_data['user_id'] = user_id
        response = supabase.table('user_profiles').insert(profile_data).execute()
        
        if response.data:
            return {"success": True, "message": "Profile created successfully", "user": response.data[0]}
        else:
            return {"success": False, "message": "Failed to create profile"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to create profile: {str(e)}"}