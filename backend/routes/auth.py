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

# Authentication dependency
async def get_current_user(credentials: HTTPBearer = Depends(security)):
    """Extract and verify user from JWT token"""
    try:
        token = credentials.credentials
        
        # Verify token with Supabase
        response = supabase.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return response.user
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/auth/signup", response_model=AuthResponse)
async def sign_up(request: EmailPasswordSignUp):
    """Register a new user with email and password"""
    try:
        # Sign up user with Supabase
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name,
                    "country": request.country
                }
            }
        })
        
        if response.user:
            return AuthResponse(
                success=True,
                message="User created successfully. Please check your email for verification.",
                user={
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": request.full_name,
                    "country": request.country
                },
                session={
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        elif "password" in error_message.lower():
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        else:
            raise HTTPException(status_code=400, detail=f"Sign up failed: {error_message}")

@router.post("/auth/signin", response_model=AuthResponse)
async def sign_in(request: EmailPasswordSignIn):
    """Sign in user with email and password"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user and response.session:
            # Get user profile from users table
            user_profile = supabase.table('users').select('*').eq('id', response.user.id).execute()
            
            user_data = {
                "id": response.user.id,
                "email": response.user.email
            }
            
            # Add profile data if available
            if user_profile.data:
                profile = user_profile.data[0]
                user_data.update({
                    "full_name": profile.get("full_name"),
                    "country": profile.get("country"),
                    "avatar_url": profile.get("avatar_url")
                })
            
            return AuthResponse(
                success=True,
                message="Sign in successful",
                user=user_data,
                session={
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        error_message = str(e)
        if "invalid" in error_message.lower() or "credentials" in error_message.lower():
            raise HTTPException(status_code=401, detail="Invalid email or password")
        else:
            raise HTTPException(status_code=400, detail=f"Sign in failed: {error_message}")

@router.post("/auth/signout")
async def sign_out(current_user: dict = Depends(get_current_user)):
    """Sign out current user"""
    try:
        response = supabase.auth.sign_out()
        return {"success": True, "message": "Signed out successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sign out failed: {str(e)}")

@router.get("/auth/user")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user profile"""
    try:
        # Get user profile from users table
        user_profile = supabase.table('users').select('*').eq('id', current_user.id).execute()
        
        user_data = {
            "id": current_user.id,
            "email": current_user.email
        }
        
        # Add profile data if available
        if user_profile.data:
            profile = user_profile.data[0]
            user_data.update({
                "full_name": profile.get("full_name"),
                "country": profile.get("country"),
                "avatar_url": profile.get("avatar_url"),
                "created_at": profile.get("created_at"),
                "updated_at": profile.get("updated_at")
            })
        
        return {"success": True, "user": user_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@router.put("/auth/user/profile")
async def update_user_profile(
    profile_update: UserProfile,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        # Update user profile in users table
        update_data = {
            "full_name": profile_update.full_name,
            "country": profile_update.country
        }
        
        response = supabase.table('users').update(update_data).eq('id', current_user.id).execute()
        
        if response.data:
            return {"success": True, "message": "Profile updated successfully", "user": response.data[0]}
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.get("/auth/google")
async def google_auth(request: Request):
    """Initiate Google OAuth flow"""
    try:
        # Get the origin URL for redirect
        origin = str(request.base_url).rstrip('/')
        redirect_url = f"{origin}/auth/callback"
        
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        return {"success": True, "auth_url": response.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google auth initiation failed: {str(e)}")

@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        response = supabase.auth.refresh_session(refresh_token)
        
        if response.session:
            return {
                "success": True,
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")

# Admin endpoints (for your account setup)
@router.post("/auth/admin/setup")
async def setup_admin_account():
    """Set up admin account - for initial setup only"""
    try:
        admin_email = "kirillpopolitov@gmail.com"
        
        # Check if admin already exists
        existing_user = supabase.table('users').select('*').eq('email', admin_email).execute()
        
        if existing_user.data:
            # Update existing user to admin
            response = supabase_admin.table('users').update({
                "role": "admin"
            }).eq('email', admin_email).execute()
            
            return {
                "success": True, 
                "message": f"Admin role granted to {admin_email}",
                "user": response.data[0] if response.data else None
            }
        else:
            return {
                "success": False,
                "message": f"User {admin_email} not found. Please sign up first."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Admin setup failed: {str(e)}")

# Health check endpoint
@router.get("/auth/health")
async def auth_health_check():
    """Check authentication service health"""
    try:
        # Test Supabase connection
        response = supabase.table('users').select('count').execute()
        
        return {
            "success": True,
            "message": "Authentication service is healthy",
            "supabase_connected": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Authentication service unhealthy: {str(e)}",
            "supabase_connected": False
        }