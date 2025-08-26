from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from supabase_client import supabase, supabase_admin
from typing import Optional
import os
import sys
import sys

router = APIRouter()
security = HTTPBearer()

# Simplified Pydantic models - avoid EmailStr which can cause typing issues
class EmailPasswordSignIn(BaseModel):
    email: str
    password: str

class EmailPasswordSignUp(BaseModel):
    email: str
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
    """Get user profile by ID - returns empty profile if none exists"""
    try:
        if not supabase:
            return {"success": False, "message": "Database not available"}
            
        response = supabase.table('user_profiles').select('*').eq('user_id', user_id).execute()
        
        if response.data and len(response.data) > 0:
            return {"success": True, "user": response.data[0]}
        else:
            # User has no profile - return a default profile structure
            # This is normal for users who haven't completed seller verification
            default_profile = {
                "user_id": user_id,
                "display_name": None,
                "email": None,
                "bio": None,
                "avatar_url": None,
                "seller_verification_status": "unverified",
                "social_links": {},
                "specialties": [],
                "experience": None,
                "seller_data": {},
                "seller_mode": False,
                "created_at": None,
                "updated_at": None
            }
            return {"success": True, "user": default_profile, "is_default": True}
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return {"success": False, "message": f"Failed to get user profile: {str(e)}"}

@router.put("/auth/user/{user_id}/profile")
async def update_user_profile(user_id: str, profile_data: dict):
    """Update user profile"""
    try:
        if not supabase:
            return {"success": False, "message": "Database not available"}
            
        response = supabase.table('user_profiles').update(profile_data).eq('user_id', user_id).execute()
        
        if response.data:
            # Trigger Google Sheets sync after profile update
            try:
                import httpx
                base_url = os.getenv("REACT_APP_BACKEND_URL", "http://127.0.0.1:8001")
                async with httpx.AsyncClient() as client:
                    await client.post(f"{base_url}/api/google-sheets/auto-sync-webhook")
                print(f"✅ Google Sheets sync triggered after profile update")
            except Exception as sync_error:
                print(f"⚠️ Google Sheets sync trigger failed: {sync_error}")
            
            return {"success": True, "message": "Profile updated successfully", "user": response.data[0]}
        else:
            return {"success": False, "message": "Failed to update profile"}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to update profile: {str(e)}"}

@router.post("/auth/user/{user_id}/profile")
async def create_user_profile(user_id: str, profile_data: dict):
    """Create user profile"""
    try:
        if not supabase_admin:  # Use admin client for reliable access
            return {"success": False, "message": "Database not available"}
        
        # Clean the profile data - remove any fields that don't belong in user_profiles
        allowed_fields = [
            'display_name', 'email', 'bio', 'avatar_url', 
            'seller_verification_status', 'social_links', 'specialties', 
            'experience', 'seller_data', 'seller_mode'
        ]
        
        # Filter out any disallowed fields (like 'email' which comes from auth.users)
        cleaned_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        cleaned_data['user_id'] = user_id
        
        print(f"Creating profile for user {user_id} with data: {cleaned_data}")
        
        # Use admin client to bypass RLS for profile creation
        response = supabase_admin.table('user_profiles').insert(cleaned_data).execute()
        
        if response.data:
            print(f"✅ Profile created successfully for user {user_id}")
            
            # Trigger Google Sheets sync after profile creation
            try:
                import httpx
                base_url = os.getenv("REACT_APP_BACKEND_URL", "http://127.0.0.1:8001")
                async with httpx.AsyncClient() as client:
                    await client.post(f"{base_url}/api/google-sheets/auto-sync-webhook")
                print(f"✅ Google Sheets sync triggered after profile creation")
            except Exception as sync_error:
                print(f"⚠️ Google Sheets sync trigger failed: {sync_error}")
            
            return {"success": True, "message": "Profile created successfully", "user": response.data[0]}
        else:
            print(f"❌ Profile creation returned no data for user {user_id}")
            return {"success": False, "message": "Failed to create profile - no data returned"}
            
    except Exception as e:
        print(f"❌ Profile creation error for user {user_id}: {str(e)}")
        return {"success": False, "message": f"Failed to create profile: {str(e)}"}

@router.post("/auth/user/{user_id}/profile/oauth")
async def create_oauth_user_profile(user_id: str, oauth_data: dict):
    """Create user profile specifically for OAuth users with enhanced error handling"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"🔍 Creating OAuth profile for user {user_id}")
        print(f"OAuth data received: {oauth_data}")
        
        # First, verify the user exists in auth.users
        try:
            user_check = supabase_admin.rpc('get_users_emails_simple').execute()
            user_exists = False
            if user_check.data:
                user_exists = any(u['user_id'] == user_id for u in user_check.data)
            
            if not user_exists:
                return {"success": False, "message": f"User {user_id} not found in auth.users"}
        
        except Exception as check_error:
            print(f"⚠️ Could not verify user existence: {check_error}")
            # Continue anyway
        
        # Extract and clean OAuth data for profile creation
        profile_data = {
            'user_id': user_id,
            'display_name': (
                oauth_data.get('user_metadata', {}).get('full_name') or 
                oauth_data.get('user_metadata', {}).get('name') or 
                oauth_data.get('email', '').split('@')[0] or 
                'User'
            ),
            'email': oauth_data.get('email', ''),  # Now we can include email!
            'avatar_url': (
                oauth_data.get('user_metadata', {}).get('avatar_url') or 
                oauth_data.get('user_metadata', {}).get('picture')
            ),
            'seller_verification_status': 'unverified',
            'bio': None,
            'social_links': {},
            'specialties': [],
            'seller_data': {},
            'seller_mode': False
        }
        
        print(f"✨ Processed profile data: {profile_data}")
        
        # Check if profile already exists
        existing_check = supabase_admin.table('user_profiles').select('user_id').eq('user_id', user_id).execute()
        if existing_check.data:
            print(f"✅ Profile already exists for user {user_id}")
            return {"success": True, "message": "Profile already exists", "existed": True}
        
        # Create the profile using admin client
        response = supabase_admin.table('user_profiles').insert(profile_data).execute()
        
        if response.data:
            print(f"✅ OAuth profile created successfully for user {user_id}")
            
            # Trigger Google Sheets sync
            try:
                import httpx
                base_url = os.getenv("REACT_APP_BACKEND_URL", "http://127.0.0.1:8001")
                async with httpx.AsyncClient() as client:
                    await client.post(f"{base_url}/api/google-sheets/auto-sync-webhook")
                print(f"✅ Google Sheets sync triggered")
            except Exception as sync_error:
                print(f"⚠️ Google Sheets sync failed: {sync_error}")
            
            return {"success": True, "message": "OAuth profile created successfully", "user": response.data[0]}
        else:
            print(f"❌ OAuth profile creation returned no data")
            return {"success": False, "message": "Profile creation returned no data"}
            
    except Exception as e:
        print(f"❌ OAuth profile creation error for user {user_id}: {str(e)}")
@router.delete("/auth/user/{user_id}/account")
async def delete_user_account(user_id: str):
    """Completely delete user account and all associated data"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"🗑️ Starting complete account deletion for user {user_id}")
        
        # List of all tables that contain user data (in deletion order to avoid foreign key issues)
        tables_to_clean = [
            'user_notifications',      # Delete notifications first
            'transactions',            # Delete transactions
            'user_bots',              # Delete user bots
            'user_votes',             # Delete votes
            'seller_reviews',         # Delete reviews
            'user_purchases',         # Delete purchases
            'portfolios',             # Delete portfolios
            'seller_verification_applications',  # Delete verification applications
            'crypto_transactions',    # Delete crypto transactions
            'nowpayments_invoices',   # Delete payment invoices
            'nowpayments_subscriptions',  # Delete subscriptions
            'nowpayments_withdrawals',    # Delete withdrawal requests
            'subscription_email_validation',  # Delete email validations
            'subscriptions',          # Delete subscription records
            'user_accounts',          # Delete user account (balance)
            'user_profiles',          # Delete user profile
            'commissions'             # Delete commission records
        ]
        
        deletion_summary = {}
        
        # Delete data from each table
        for table in tables_to_clean:
            try:
                print(f"🧹 Deleting from table: {table}")
                
                # Get count before deletion for summary
                count_result = supabase_admin.table(table).select('id').eq('user_id', user_id).execute()
                before_count = len(count_result.data) if count_result.data else 0
                
                if before_count > 0:
                    # Delete all records for this user
                    delete_result = supabase_admin.table(table).delete().eq('user_id', user_id).execute()
                    after_count = len(delete_result.data) if delete_result.data else 0
                    
                    deletion_summary[table] = {
                        "before": before_count,
                        "deleted": after_count,
                        "success": True
                    }
                    print(f"✅ Deleted {after_count} records from {table}")
                else:
                    deletion_summary[table] = {
                        "before": 0,
                        "deleted": 0,
                        "success": True
                    }
                    print(f"ℹ️ No records found in {table}")
                    
            except Exception as table_error:
                print(f"❌ Error deleting from {table}: {table_error}")
                deletion_summary[table] = {
                    "before": "unknown",
                    "deleted": 0,
                    "success": False,
                    "error": str(table_error)
                }
        
        # Finally, delete the user from auth.users (this is the critical part)
        print(f"🔥 Deleting user from auth.users table...")
        try:
            # Delete from auth.users using enhanced admin client
            auth_delete_success = supabase_admin.auth.admin.delete_user(user_id)
            
            if auth_delete_success:
                print(f"✅ User {user_id} deleted from auth.users successfully")
                deletion_summary["auth.users"] = {
                    "success": True,
                    "deleted": 1
                }
            else:
                print(f"❌ User deletion from auth.users failed")
                deletion_summary["auth.users"] = {
                    "success": False,
                    "error": "delete_user method returned False"
                }
                
        except Exception as auth_error:
            print(f"❌ Failed to delete user from auth.users: {auth_error}")
            deletion_summary["auth.users"] = {
                "success": False,
                "error": str(auth_error)
            }
        
        # Delete user from Google Sheets
        print(f"📊 Deleting user from Google Sheets...")
        try:
            # Import Google Sheets service
            sys.path.append('/app/backend/services')
            from google_sheets_service import google_sheets_service
            
            # Try to get user email for better identification
            user_email = None
            if deletion_summary.get("user_profiles", {}).get("success"):
                # Try to get email from the deleted profile data (if we captured it)
                pass  # We'll use user_id for identification
            
            sheets_delete_success = google_sheets_service.delete_user_from_sheets(user_id, user_email)
            
            deletion_summary["google_sheets"] = {
                "success": sheets_delete_success,
                "deleted": 1 if sheets_delete_success else 0
            }
            
            if sheets_delete_success:
                print(f"✅ User deleted from Google Sheets successfully")
            else:
                print(f"⚠️ User deletion from Google Sheets failed (may not have been in sheets)")
                
        except Exception as sheets_error:
            print(f"❌ Google Sheets deletion error: {sheets_error}")
            deletion_summary["google_sheets"] = {
                "success": False,
                "error": str(sheets_error)
            }
        
        # Count total deletions
        total_deleted = sum(
            item["deleted"] for item in deletion_summary.values() 
            if isinstance(item.get("deleted"), int)
        )
        
        # Trigger Google Sheets sync after account deletion
        try:
            import httpx
            base_url = os.getenv("REACT_APP_BACKEND_URL", "http://127.0.0.1:8001")
            async with httpx.AsyncClient() as client:
                await client.post(f"{base_url}/api/google-sheets/auto-sync-webhook")
            print(f"✅ Google Sheets sync triggered after account deletion")
        except Exception as sync_error:
            print(f"⚠️ Google Sheets sync trigger failed: {sync_error}")
        
        print(f"🎉 Account deletion completed! Total records deleted: {total_deleted}")
        
        return {
            "success": True,
            "message": f"Account completely deleted. Total records removed: {total_deleted}",
            "user_id": user_id,
            "deletion_summary": deletion_summary,
            "total_records_deleted": total_deleted,
            "auth_user_deleted": deletion_summary.get("auth.users", {}).get("success", False)
        }
        
    except Exception as e:
        print(f"❌ Account deletion error for user {user_id}: {str(e)}")
        return {
            "success": False, 
            "message": f"Account deletion failed: {str(e)}",
            "user_id": user_id
        }

# ========================================
# BALANCE SYSTEM ENDPOINTS
# ========================================

class TransactionRequest(BaseModel):
    seller_id: str
    product_id: str
    amount: float
    description: Optional[str] = None

class BalanceUpdateRequest(BaseModel):
    amount: float
    transaction_type: str = "topup"  # topup, withdrawal
    description: Optional[str] = None

@router.get("/auth/test-deployment")
async def test_deployment():
    """Test if new deployment is working"""
    return {"message": "New deployment working!", "timestamp": "2025-08-18T13:10:00Z"}

@router.post("/auth/user/{user_id}/sync-balance")
async def sync_balance(user_id: str):
    """Sync balance between frontend and backend systems"""
    print(f"\n=== BALANCE SYNC ENDPOINT HIT ===")
    print(f"Syncing balance for user_id: {user_id}")
    
    try:
        if not supabase_admin:
            print("❌ Database not available")
            return {"success": False, "message": "Database not available"}
        
        # Get current backend balance
        backend_response = supabase_admin.table('user_accounts').select('balance').eq('user_id', user_id).execute()
        backend_balance = 0.0
        if backend_response.data and len(backend_response.data) > 0:
            backend_balance = float(backend_response.data[0]['balance']) if backend_response.data[0]['balance'] else 0.0
        
        print(f"Current backend balance: {backend_balance}")
        
        # Get the balance from the regular supabase client (what frontend was using)
        frontend_response = supabase.table('user_accounts').select('balance').eq('user_id', user_id).execute()
        frontend_balance = 0.0
        if frontend_response.data and len(frontend_response.data) > 0:
            frontend_balance = float(frontend_response.data[0]['balance']) if frontend_response.data[0]['balance'] else 0.0
        
        print(f"Current frontend balance: {frontend_balance}")
        
        # Use the higher balance as the correct one
        correct_balance = max(backend_balance, frontend_balance)
        print(f"Using correct balance: {correct_balance}")
        
        # Update backend balance to match
        if correct_balance != backend_balance:
            print(f"Updating backend balance from {backend_balance} to {correct_balance}")
            supabase_admin.table('user_accounts').upsert({
                'user_id': user_id,
                'balance': correct_balance,
                'currency': 'USD'
            }).execute()
        
        # Create a transaction record for the sync
        try:
            if correct_balance > backend_balance:
                supabase_admin.table('transactions').insert({
                    'user_id': user_id,
                    'transaction_type': 'topup',
                    'amount': correct_balance - backend_balance,
                    'platform_fee': 0.0,
                    'net_amount': correct_balance - backend_balance,
                    'status': 'completed',
                    'description': f'Balance sync: restored ${correct_balance - backend_balance:.2f}'
                }).execute()
        except Exception as tx_error:
            print(f"Failed to create sync transaction record: {tx_error}")
        
        result = {
            "success": True,
            "message": "Balance synced successfully",
            "previous_backend_balance": backend_balance,
            "previous_frontend_balance": frontend_balance,
            "new_balance": correct_balance
        }
        
        print(f"Sync result: {result}")
        print("=== END BALANCE SYNC ENDPOINT ===\n")
        return result
        
    except Exception as e:
        print(f"❌ Exception in sync_balance: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        print("=== END BALANCE SYNC ENDPOINT (ERROR) ===\n")
        return {"success": False, "message": f"Failed to sync balance: {str(e)}"}

class SubscriptionUpgradeRequest(BaseModel):
    plan_type: str
    price: float
    duration_days: Optional[int] = 30

class LimitCheckRequest(BaseModel):
    resource_type: str  # 'ai_bots', 'manual_bots', 'marketplace_products'
    current_count: Optional[int] = 0

@router.get("/auth/user/{user_id}/subscription/limits")
async def get_user_subscription_limits(user_id: str):
    """Get user's subscription limits overview"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Getting subscription limits for user {user_id}")
        
        # Super admin check by UUID
        if user_id == 'cd0e9717-f85d-4726-81e9-f260394ead58':
            return {
                "success": True,
                "subscription": {
                    "plan_type": "super_admin",
                    "limits": None,  # No limits for super admin
                    "is_super_admin": True,
                    "status": "active"
                }
            }
        
        # Get user's subscription
        response = supabase_admin.table('subscriptions')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            # Default to free plan if no subscription found
            return {
                "success": True,
                "subscription": {
                    "plan_type": "free",
                    "limits": {
                        "ai_bots": 1,
                        "manual_bots": 2,
                        "marketplace_products": 1
                    },
                    "is_super_admin": False,
                    "status": "active"
                }
            }
        
        subscription = response.data[0]
        plan_type = subscription.get('plan_type', 'free')
        is_super_admin = plan_type == 'super_admin'
        
        # Get limits based on plan type
        if is_super_admin:
            limits = None  # No limits
        else:
            # Default limits based on plan
            default_limits = {
                "free": {"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1},
                "plus": {"ai_bots": 3, "manual_bots": 5, "marketplace_products": 10},
                "pro": {"ai_bots": -1, "manual_bots": -1, "marketplace_products": -1}
            }
            limits = subscription.get('limits') or default_limits.get(plan_type, default_limits["free"])
        
        return {
            "success": True,
            "subscription": {
                "plan_type": plan_type,
                "limits": limits,
                "is_super_admin": is_super_admin,
                "status": subscription.get('status', 'active'),
                "start_date": subscription.get('start_date'),
                "end_date": subscription.get('end_date')
            }
        }
        
    except Exception as e:
        print(f"Error getting subscription limits: {e}")
        return {"success": False, "message": f"Failed to get subscription limits: {str(e)}"}

@router.post("/auth/user/{user_id}/subscription/check-limit")
async def check_subscription_limit(user_id: str, limit_check: LimitCheckRequest):
    """Check if user can create more resources based on subscription limits"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Checking limit for user {user_id}: {limit_check.resource_type} (current: {limit_check.current_count})")
        
        # Super admin check by UUID
        if user_id == 'cd0e9717-f85d-4726-81e9-f260394ead58':
            return {
                "success": True,
                "can_create": True,
                "limit_reached": False,
                "current_count": limit_check.current_count,
                "limit": -1,  # Unlimited
                "plan_type": "super_admin",
                "is_super_admin": True
            }
        
        # Get user's subscription
        response = supabase_admin.table('subscriptions')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        # Default to free plan if no subscription
        if not response.data or len(response.data) == 0:
            default_limits = {
                "ai_bots": 1,
                "manual_bots": 2,
                "marketplace_products": 1
            }
            limit = default_limits.get(limit_check.resource_type, 1)
            
            # Validate current_count is non-negative
            if limit_check.current_count < 0:
                return {
                    "success": False,
                    "message": "Invalid current_count: must be non-negative",
                    "can_create": False,
                    "limit_reached": True,
                    "current_count": limit_check.current_count,
                    "limit": limit,
                    "plan_type": "free",
                    "is_super_admin": False
                }
            
            return {
                "success": True,
                "can_create": limit_check.current_count < limit,
                "limit_reached": limit_check.current_count >= limit,
                "current_count": limit_check.current_count,
                "limit": limit,
                "plan_type": "free",
                "is_super_admin": False
            }
        
        subscription = response.data[0]
        plan_type = subscription.get('plan_type', 'free')
        
        # Super admin has no limits
        if plan_type == 'super_admin':
            return {
                "success": True,
                "can_create": True,
                "limit_reached": False,
                "current_count": limit_check.current_count,
                "limit": -1,
                "plan_type": plan_type,
                "is_super_admin": True
            }
        
        # Get limits from subscription or use defaults
        limits = subscription.get('limits', {})
        if not limits:
            # Fallback to default limits based on plan
            default_limits = {
                "free": {"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1},
                "plus": {"ai_bots": 3, "manual_bots": 5, "marketplace_products": 10},
                "pro": {"ai_bots": -1, "manual_bots": -1, "marketplace_products": -1}
            }
            limits = default_limits.get(plan_type, default_limits["free"])
        
        limit = limits.get(limit_check.resource_type, 1)
        
        # If limit is -1, it means unlimited
        if limit == -1:
            return {
                "success": True,
                "can_create": True,
                "limit_reached": False,
                "current_count": limit_check.current_count,
                "limit": -1,
                "plan_type": plan_type,
                "is_super_admin": False
            }
        
        # Validate current_count is non-negative
        if limit_check.current_count < 0:
            return {
                "success": False,
                "message": "Invalid current_count: must be non-negative",
                "can_create": False,
                "limit_reached": True,
                "current_count": limit_check.current_count,
                "limit": limit,
                "plan_type": plan_type,
                "is_super_admin": False
            }
        
        # Check if limit is reached
        can_create = limit_check.current_count < limit
        
        return {
            "success": True,
            "can_create": can_create,
            "limit_reached": not can_create,
            "current_count": limit_check.current_count,
            "limit": limit,
            "plan_type": plan_type,
            "is_super_admin": False
        }
        
    except Exception as e:
        print(f"Error checking subscription limit: {e}")
        return {"success": False, "message": f"Failed to check subscription limit: {str(e)}"}

@router.get("/auth/user/{user_id}/subscription")
async def get_user_subscription(user_id: str):
    """Get user's current subscription details"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Getting subscription for user {user_id}")
        
        # Super admin check by UUID
        if user_id == 'cd0e9717-f85d-4726-81e9-f260394ead58':
            # Check if super admin subscription exists, if not create it
            response = supabase_admin.table('subscriptions')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                # Create super admin subscription
                super_admin_sub = {
                    'user_id': user_id,
                    'plan_type': 'super_admin',
                    'status': 'active',
                    'start_date': 'now()',
                    'end_date': None,
                    'renewal': False,
                    'price_paid': 0.0,
                    'currency': 'USD',
                    'limits': None
                }
                
                create_response = supabase_admin.table('subscriptions').insert(super_admin_sub).execute()
                subscription = create_response.data[0] if create_response.data else super_admin_sub
            else:
                subscription = response.data[0]
                # Update to super_admin if not already
                if subscription.get('plan_type') != 'super_admin':
                    supabase_admin.table('subscriptions').update({
                        'plan_type': 'super_admin',
                        'status': 'active',
                        'limits': None
                    }).eq('user_id', user_id).execute()
                    subscription['plan_type'] = 'super_admin'
                    subscription['limits'] = None
            
            return {
                "success": True,
                "subscription": subscription
            }
        
        # Get user's subscription
        response = supabase_admin.table('subscriptions')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            # Create default free subscription
            default_sub = {
                'user_id': user_id,
                'plan_type': 'free',
                'status': 'active',
                'start_date': 'now()',
                'end_date': None,
                'renewal': False,
                'price_paid': 0.0,
                'currency': 'USD',
                'limits': {
                    'ai_bots': 1,
                    'manual_bots': 2,
                    'marketplace_products': 1
                }
            }
            
            create_response = supabase_admin.table('subscriptions').insert(default_sub).execute()
            
            return {
                "success": True,
                "subscription": create_response.data[0] if create_response.data else default_sub
            }
        
        subscription = response.data[0]
        plan_type = subscription.get('plan_type', 'free')
        
        # Ensure limits are set for non-super-admin plans
        if plan_type != 'super_admin' and not subscription.get('limits'):
            default_limits = {
                "free": {"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1},
                "plus": {"ai_bots": 3, "manual_bots": 5, "marketplace_products": 10},
                "pro": {"ai_bots": -1, "manual_bots": -1, "marketplace_products": -1}
            }
            subscription['limits'] = default_limits.get(plan_type, default_limits["free"])
        
        # Check if subscription has expired
        if subscription.get('end_date'):
            from datetime import datetime, timezone
            try:
                end_date = datetime.fromisoformat(subscription['end_date'].replace('Z', '+00:00'))
                if end_date < datetime.now(timezone.utc):
                    # Subscription expired, downgrade to free
                    supabase_admin.table('subscriptions').update({
                        'plan_type': 'free',
                        'status': 'expired',
                        'end_date': None,
                        'limits': {"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1}
                    }).eq('user_id', user_id).execute()
                    
                    subscription['plan_type'] = 'free'
                    subscription['status'] = 'expired'
                    subscription['limits'] = {"ai_bots": 1, "manual_bots": 2, "marketplace_products": 1}
            except Exception as date_error:
                print(f"Error parsing end_date: {date_error}")
        
        return {
            "success": True,
            "subscription": subscription
        }
        
    except Exception as e:
        print(f"Error getting subscription: {e}")
        return {"success": False, "message": f"Failed to get subscription: {str(e)}"}

@router.post("/auth/user/{user_id}/subscription/upgrade")
async def upgrade_user_subscription(user_id: str, upgrade_request: SubscriptionUpgradeRequest):
    """Upgrade user subscription with balance deduction"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Upgrading subscription for user {user_id} to {upgrade_request.plan_type} for ${upgrade_request.price}")
        
        # Use the database function to handle the upgrade
        response = supabase_admin.rpc('upgrade_subscription', {
            'p_user_id': user_id,
            'p_plan_type': upgrade_request.plan_type,
            'p_price': upgrade_request.price
        }).execute()
        
        if response.data:
            result = response.data
            
            # Create success notification if upgrade succeeded
            if result.get('success'):
                try:
                    supabase_admin.table('user_notifications').insert({
                        'user_id': user_id,
                        'title': f'Subscription Upgraded to {upgrade_request.plan_type.title()}',
                        'message': f'Your subscription has been upgraded to {upgrade_request.plan_type.title()} plan for ${upgrade_request.price:.2f}. Enjoy your new features!',
                        'type': 'success',
                        'is_read': False
                    }).execute()
                except Exception as notification_error:
                    print(f"Failed to create upgrade notification: {notification_error}")
            
            return result
        else:
            return {"success": False, "message": "Failed to process subscription upgrade"}
            
    except Exception as e:
        print(f"Error upgrading subscription: {e}")
        return {"success": False, "message": f"Failed to upgrade subscription: {str(e)}"}

@router.post("/auth/user/{user_id}/subscription/cancel")
async def cancel_user_subscription(user_id: str):
    """Cancel user subscription (keep active until end date, but disable renewal)"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Cancelling subscription for user {user_id}")
        
        # Get current subscription first
        current_response = supabase_admin.table('subscriptions')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if not current_response.data:
            return {"success": False, "message": "No active subscription found"}
        
        subscription = current_response.data[0]
        current_plan = subscription.get('plan_type', 'free')
        end_date = subscription.get('end_date')
        
        # Don't cancel if already free or cancelled
        if current_plan == 'free' or subscription.get('status') == 'cancelled':
            return {"success": False, "message": "No active paid subscription to cancel"}
        
        # Update subscription to cancelled status but keep plan_type until end_date
        response = supabase_admin.table('subscriptions').update({
            'status': 'cancelled',  # Mark as cancelled
            'renewal': False,       # Disable auto-renewal
            'updated_at': 'now()'
        }).eq('user_id', user_id).execute()
        
        # ALSO CANCEL IN NOWPAYMENTS - Get the NowPayments subscription ID
        nowpayments_sub = supabase_admin.table('nowpayments_subscriptions')\
            .select('subscription_id')\
            .eq('user_id', user_id)\
            .eq('is_active', True)\
            .execute()
        
        if nowpayments_sub.data:
            nowpayments_subscription_id = nowpayments_sub.data[0]['subscription_id']
            print(f"🔄 Also cancelling NowPayments subscription: {nowpayments_subscription_id}")
            
            try:
                import httpx
                import json
                import os
                
                # Get JWT token for NowPayments API
                async def get_nowpayments_jwt():
                    auth_data = {
                        "email": os.getenv("NOWPAYMENTS_EMAIL"),
                        "password": os.getenv("NOWPAYMENTS_PASSWORD")
                    }
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "https://api.nowpayments.io/v1/auth",
                            json=auth_data,
                            headers={"x-api-key": os.getenv("NOWPAYMENTS_API_KEY")}
                        )
                        if response.status_code == 200:
                            return response.json().get("token")
                    return None
                
                jwt_token = await get_nowpayments_jwt()
                
                if jwt_token:
                    # Cancel subscription in NowPayments
                    headers = {
                        "x-api-key": os.getenv("NOWPAYMENTS_API_KEY"),
                        "Authorization": f"Bearer {jwt_token}",
                        "Content-Type": "application/json"
                    }
                    
                    async with httpx.AsyncClient() as client:
                        cancel_response = await client.delete(
                            f"https://api.nowpayments.io/v1/subscriptions/{nowpayments_subscription_id}",
                            headers=headers
                        )
                    
                    if cancel_response.status_code in [200, 201]:
                        print(f"✅ Successfully cancelled NowPayments subscription: {nowpayments_subscription_id}")
                        
                        # Also update nowpayments_subscriptions table
                        supabase_admin.table('nowpayments_subscriptions')\
                            .update({
                                'status': 'CANCELLED',
                                'is_active': False,
                                'updated_at': 'now()'
                            })\
                            .eq('subscription_id', nowpayments_subscription_id)\
                            .execute()
                    else:
                        print(f"⚠️ Failed to cancel NowPayments subscription: {nowpayments_subscription_id}, status: {cancel_response.status_code}")
                else:
                    print("⚠️ Failed to get JWT token for NowPayments cancellation")
                    
            except Exception as nowpay_error:
                print(f"❌ Error cancelling NowPayments subscription: {nowpay_error}")
        else:
            print("⚠️ No active NowPayments subscription found to cancel")
        
        # Create notification
        try:
            from datetime import datetime
            end_date_str = "the end of your billing period"
            if end_date:
                try:
                    end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    end_date_str = end_date_obj.strftime('%B %d, %Y')
                except:
                    end_date_str = "the end of your billing period"
            
            supabase_admin.table('user_notifications').insert({
                'user_id': user_id,
                'title': 'Subscription Cancelled',
                'message': f'Your {current_plan.title()} subscription has been cancelled. You will keep your current features until {end_date_str}, after which your plan will automatically downgrade to Free.',
                'type': 'info',
                'is_read': False
            }).execute()
        except Exception as notification_error:
            print(f"Failed to create cancellation notification: {notification_error}")
        
        return {
            "success": True,
            "message": "Subscription cancelled successfully. Your plan will remain active until the end date.",
            "subscription": response.data[0] if response.data else {},
            "end_date": end_date,
            "current_plan": current_plan
        }
        
    except Exception as e:
        print(f"Error cancelling subscription: {e}")
        return {"success": False, "message": f"Failed to cancel subscription: {str(e)}"}

@router.get("/auth/subscription/plans")
async def get_subscription_plans():
    """Get available subscription plans (excludes Super Admin)"""
    return {
        "success": True,
        "plans": [
            {
                "id": "free",
                "name": "Free Plan",
                "price": 0,
                "currency": "USD",
                "billing_period": "month",
                "features": [
                    "Access to AI news feed + push notifications",
                    "Create & manage 1 AI trading bot",
                    "Create & manage 2 manual bots",
                    "Connect to ready-made bots from f01i.ai",
                    "For marketplace sellers: 1 product slot"
                ],
                "limitations": {
                    "ai_bots": 1,
                    "manual_bots": 2,
                    "product_slots": 1
                },
                "description": "Perfect for getting started with AI-powered trading"
            },
            {
                "id": "plus",
                "name": "Plus Plan",
                "price": 10,
                "currency": "USD",
                "billing_period": "month",
                "popular": True,
                "features": [
                    "Access to AI news feed + push notifications",
                    "Telegram notifications + filters",
                    "Create & manage 3 AI trading bots",
                    "Create & manage 5 manual bots",
                    "API access for copytrading integration",
                    "Connect to ready-made bots from f01i.ai",
                    "For marketplace sellers: up to 10 product slots"
                ],
                "limitations": {
                    "ai_bots": 3,
                    "manual_bots": 5,
                    "product_slots": 10,
                    "telegram_notifications": True,
                    "api_access": True
                },
                "description": "Most popular plan for serious traders"
            },
            {
                "id": "pro",
                "name": "Pro Plan",
                "price": 49,
                "currency": "USD",
                "billing_period": "month",
                "coming_soon": True,
                "features": [
                    "All Plus features",
                    "Unlimited AI and manual bots",
                    "Priority support",
                    "Advanced analytics",
                    "White-label options",
                    "Custom integrations"
                ],
                "limitations": {
                    "ai_bots": -1,  # -1 means unlimited
                    "manual_bots": -1,
                    "product_slots": -1,
                    "priority_support": True,
                    "white_label": True
                },
                "description": "Ultimate plan for professional traders"
            }
        ]
    }

@router.get("/auth/user/{user_id}/notifications")
async def get_user_notifications(user_id: str, limit: int = 50, offset: int = 0):
    """Get user notifications"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Getting notifications for user {user_id}, limit: {limit}, offset: {offset}")
        
        response = supabase_admin.table('user_notifications')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        print(f"Notifications response: {response}")
        
        return {
            "success": True,
            "notifications": response.data if response.data else []
        }
        
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return {"success": False, "message": f"Failed to get notifications: {str(e)}"}

@router.delete("/auth/user/{user_id}/notifications/{notification_id}")
async def delete_notification(user_id: str, notification_id: str):
    """Delete a specific notification"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Deleting notification {notification_id} for user {user_id}")
        
        # Delete the notification
        response = supabase_admin.table('user_notifications').delete().eq('id', notification_id).eq('user_id', user_id).execute()
        
        print(f"Delete response: {response}")
        
        return {
            "success": True,
            "message": "Notification deleted successfully"
        }
        
    except Exception as e:
        print(f"Error deleting notification: {e}")
        return {"success": False, "message": f"Failed to delete notification: {str(e)}"}

@router.delete("/auth/user/{user_id}/notifications")
async def delete_all_notifications(user_id: str):
    """Delete all notifications for a user"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        print(f"Deleting all notifications for user {user_id}")
        
        # Delete all notifications for the user
        response = supabase_admin.table('user_notifications').delete().eq('user_id', user_id).execute()
        
        print(f"Delete all response: {response}")
        
        return {
            "success": True,
            "message": "All notifications deleted successfully"
        }
        
    except Exception as e:
        print(f"Error deleting all notifications: {e}")
        return {"success": False, "message": f"Failed to delete notifications: {str(e)}"}

@router.get("/auth/debug/env")
async def debug_environment():
    """Debug endpoint to check environment variables"""
    import os
    
    env_info = {
        "SUPABASE_URL": bool(os.environ.get("SUPABASE_URL")),
        "SUPABASE_ANON_KEY": bool(os.environ.get("SUPABASE_ANON_KEY")),
        "SUPABASE_SERVICE_KEY": bool(os.environ.get("SUPABASE_SERVICE_KEY")),
        "SUPABASE_SERVICE_ROLE_KEY": bool(os.environ.get("SUPABASE_SERVICE_ROLE_KEY")),
        "supabase_admin_available": bool(supabase_admin),
        "SUPABASE_URL_VALUE": os.environ.get("SUPABASE_URL", "NOT_SET"),
        "service_key_prefix": os.environ.get("SUPABASE_SERVICE_KEY", "NOT_SET")[:20] + "..." if os.environ.get("SUPABASE_SERVICE_KEY") else "NOT_SET",
        "service_role_key_prefix": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "NOT_SET")[:20] + "..." if os.environ.get("SUPABASE_SERVICE_ROLE_KEY") else "NOT_SET"
    }
    
    return {"environment": env_info}

@router.post("/auth/user/{user_id}/set-balance")
async def set_balance_direct(user_id: str, balance_data: dict):
    """Directly set user balance (admin function)"""
    try:
        amount = float(balance_data.get('amount', 0))
        print(f"Setting balance directly for {user_id} to {amount}")
        
        # Use raw SQL to bypass RLS if needed
        if supabase_admin:
            # First try normal upsert
            response = supabase_admin.table('user_accounts').select('*').eq('user_id', user_id).execute()
            print(f"Current account check: {response.data}")
            
            # Force upsert with admin privileges
            upsert_response = supabase_admin.table('user_accounts').upsert({
                'user_id': user_id,
                'balance': amount,
                'currency': 'USD',
                'updated_at': 'now()'
            }).execute()
            print(f"Upsert response: {upsert_response.data}")
            
            # Verify the update worked
            verify_response = supabase_admin.table('user_accounts').select('*').eq('user_id', user_id).execute()
            print(f"Verification response: {verify_response.data}")
            
            return {
                "success": True,
                "message": f"Balance set to ${amount}",
                "new_balance": amount,
                "verification": verify_response.data
            }
        else:
            return {"success": False, "message": "Admin client not available"}
            
    except Exception as e:
        print(f"Error setting balance: {e}")
        import traceback
        print(traceback.format_exc())
        return {"success": False, "message": f"Failed to set balance: {str(e)}"}

@router.get("/auth/user/{user_id}/balance")
async def get_user_balance(user_id: str):
    """Get user's current account balance"""
    print(f"\n=== GET BALANCE ENDPOINT HIT ===")
    print(f"Requested user_id: {user_id}")
    
    try:
        if not supabase_admin:
            print("❌ Database not available")
            return {"success": False, "message": "Database not available"}
            
        print("✅ Database client available")
        print(f"Querying user_accounts table for user_id: {user_id}")
        
        response = supabase_admin.table('user_accounts').select('balance, currency').eq('user_id', user_id).execute()
        
        print(f"Database response: {response}")
        print(f"Response data: {response.data}")
        print(f"Response count: {response.count if hasattr(response, 'count') else 'N/A'}")
        
        if response.data and len(response.data) > 0:
            balance_value = response.data[0]['balance']
            currency_value = response.data[0].get('currency', 'USD')
            print(f"Found balance record: balance={balance_value}, currency={currency_value}")
            
            result = {
                "success": True, 
                "balance": float(balance_value) if balance_value else 0.0,
                "currency": currency_value
            }
            print(f"Returning result: {result}")
            print("=== END GET BALANCE ENDPOINT ===\n")
            return result
        else:
            print("No balance record found, creating new account with zero balance")
            # Create account with zero balance if doesn't exist
            insert_response = supabase_admin.table('user_accounts').insert({
                'user_id': user_id,
                'balance': 0.0,
                'currency': 'USD'
            }).execute()
            print(f"Insert response: {insert_response}")
            
            result = {"success": True, "balance": 0.0, "currency": "USD"}
            print(f"Returning new account result: {result}")
            print("=== END GET BALANCE ENDPOINT ===\n")
            return result
            
    except Exception as e:
        print(f"❌ Exception in get_balance: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        print("=== END GET BALANCE ENDPOINT (ERROR) ===\n")
        return {"success": False, "message": f"Failed to get balance: {str(e)}"}

@router.post("/auth/user/{user_id}/process-transaction")
async def process_transaction(user_id: str, transaction: TransactionRequest):
    """Process marketplace purchase with balance validation"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        # Call the database function to process the purchase
        # Since we don't have rpc support, we'll implement the logic here
        
        # First check buyer's balance
        balance_response = supabase_admin.table('user_accounts').select('balance').eq('user_id', user_id).execute()
        
        if not balance_response.data or len(balance_response.data) == 0:
            # Create account with zero balance if doesn't exist
            supabase_admin.table('user_accounts').insert({
                'user_id': user_id,
                'balance': 0.0,
                'currency': 'USD'
            }).execute()
            current_balance = 0.0
        else:
            current_balance = float(balance_response.data[0]['balance']) if balance_response.data[0]['balance'] else 0.0
        
        # Check if buyer has sufficient funds
        if current_balance < transaction.amount:
            return {
                'success': False,
                'error': 'insufficient_funds',
                'message': 'Insufficient balance to complete purchase',
                'current_balance': current_balance,
                'required_amount': transaction.amount
            }
        
        # Calculate fees (10% platform fee)
        platform_fee = transaction.amount * 0.10
        seller_amount = transaction.amount * 0.90
        
        try:
            # 1. Deduct amount from buyer's balance
            new_buyer_balance = current_balance - transaction.amount
            supabase_admin.table('user_accounts').update({
                'balance': new_buyer_balance,
                'updated_at': 'now()'
            }).eq('user_id', user_id).execute()
            
            # 2. Add seller amount to seller's balance (create account if doesn't exist)
            seller_balance_response = supabase_admin.table('user_accounts').select('balance').eq('user_id', transaction.seller_id).execute()
            
            if not seller_balance_response.data or len(seller_balance_response.data) == 0:
                # Create seller account
                supabase_admin.table('user_accounts').insert({
                    'user_id': transaction.seller_id,
                    'balance': seller_amount,
                    'currency': 'USD'
                }).execute()
            else:
                current_seller_balance = float(seller_balance_response.data[0]['balance']) if seller_balance_response.data[0]['balance'] else 0.0
                new_seller_balance = current_seller_balance + seller_amount
                supabase_admin.table('user_accounts').update({
                    'balance': new_seller_balance,
                    'updated_at': 'now()'
                }).eq('user_id', transaction.seller_id).execute()
            
            # 3. Create transaction record for the purchase
            transaction_record = supabase_admin.table('transactions').insert({
                'user_id': user_id,
                'seller_id': transaction.seller_id,
                'product_id': transaction.product_id,
                'transaction_type': 'purchase',
                'amount': transaction.amount,
                'platform_fee': platform_fee,
                'net_amount': seller_amount,
                'status': 'completed',
                'description': transaction.description or f"Purchase of product {transaction.product_id}"
            }).execute()
            
            transaction_id = transaction_record.data[0]['id'] if transaction_record.data else None
            
            result = {
                'success': True,
                'transaction_id': transaction_id,
                'amount_charged': transaction.amount,
                'platform_fee': platform_fee,
                'seller_received': seller_amount,
                'buyer_new_balance': new_buyer_balance
            }
            
        except Exception as e:
            # Return error if transaction fails
            return {
                'success': False,
                'error': 'transaction_failed',
                'message': f'Failed to process purchase: {str(e)}'
            }
            
            # Create notification for buyer
            if result.get('success'):
                try:
                    supabase.table('user_notifications').insert({
                        'user_id': user_id,
                        'title': 'Purchase Successful',
                        'message': f'You have successfully purchased a product for ${transaction.amount:.2f}. Your new balance is ${result.get("buyer_new_balance", 0):.2f}.',
                        'type': 'success',
                        'is_read': False
                    }).execute()
                    
                    # Create notification for seller
                    supabase.table('user_notifications').insert({
                        'user_id': transaction.seller_id,
                        'title': 'Sale Completed',
                        'message': f'Your product was purchased for ${transaction.amount:.2f}. You received ${result.get("seller_received", 0):.2f} (after 10% platform fee).',
                        'type': 'success',
                        'is_read': False
                    }).execute()
                except Exception as notification_error:
                    print(f"Failed to create notifications: {notification_error}")
            
            return result
            
    except Exception as e:
        return {"success": False, "message": f"Failed to process transaction: {str(e)}"}

@router.post("/auth/user/{user_id}/update-balance")
async def update_balance(user_id: str, balance_update: BalanceUpdateRequest):
    """Update user balance (topup/withdrawal)"""
    print(f"\n=== UPDATE BALANCE ENDPOINT HIT ===")
    print(f"Received request for user_id: {user_id}")
    print(f"Request data: {balance_update}")
    print(f"Amount: {balance_update.amount}")
    print(f"Transaction type: {balance_update.transaction_type}")
    print(f"Description: {balance_update.description}")
    
    try:
        if not supabase_admin:
            print("❌ Database not available")
            return {"success": False, "message": "Database not available"}
        
        print("✅ Database client available")
        
        # Validate amount
        if balance_update.amount <= 0:
            print(f"❌ Invalid amount: {balance_update.amount}")
            return {"success": False, "message": "Amount must be greater than zero"}
        
        print(f"✅ Amount validation passed: {balance_update.amount}")
        
        # For topup, add amount; for withdrawal, subtract amount
        amount_change = balance_update.amount if balance_update.transaction_type == "topup" else -balance_update.amount
        print(f"Amount change calculated: {amount_change}")
        
        # Get current balance first
        print(f"Fetching current balance for user: {user_id}")
        current_response = supabase_admin.table('user_accounts').select('balance').eq('user_id', user_id).execute()
        print(f"Current balance query response: {current_response}")
        
        if not current_response.data or len(current_response.data) == 0:
            print("No existing account found, creating new account")
            current_balance = 0.0
            # Create account with zero balance if doesn't exist
            supabase_admin.table('user_accounts').insert({
                'user_id': user_id,
                'balance': 0.0,
                'currency': 'USD'
            }).execute()
            print("✅ New account created")
        else:
            current_balance = float(current_response.data[0]['balance']) if current_response.data[0]['balance'] else 0.0
            print(f"Current balance found: {current_balance}")
        
        # Check for sufficient funds on withdrawal
        if balance_update.transaction_type == "withdrawal" and current_balance < balance_update.amount:
            print(f"❌ Insufficient funds: {current_balance} < {balance_update.amount}")
            return {
                "success": False, 
                "message": "Insufficient funds for withdrawal",
                "current_balance": current_balance,
                "requested_amount": balance_update.amount
            }
        
        new_balance = current_balance + amount_change
        print(f"New balance calculated: {new_balance}")
        
        # Update balance
        print("Updating balance in database...")
        update_response = supabase_admin.table('user_accounts').update({
            'balance': new_balance,
            'currency': 'USD'
        }).eq('user_id', user_id).execute()
        print(f"Balance update response: {update_response}")
        
        if not update_response.data:
            print("Update failed, trying insert (upsert behavior)...")
            # If update failed, try insert (upsert behavior)
            insert_response = supabase_admin.table('user_accounts').insert({
                'user_id': user_id,
                'balance': new_balance,
                'currency': 'USD'
            }).execute()
            print(f"Insert response: {insert_response}")
        
        # Create transaction record (skip if table doesn't exist)
        try:
            print("Creating transaction record...")
            tx_response = supabase_admin.table('transactions').insert({
                'user_id': user_id,
                'transaction_type': balance_update.transaction_type,
                'amount': balance_update.amount,
                'platform_fee': 0.0,
                'net_amount': balance_update.amount,
                'status': 'completed',
                'description': balance_update.description or f"{balance_update.transaction_type.title()} of ${balance_update.amount:.2f}"
            }).execute()
            print(f"Transaction record created: {tx_response}")
        except Exception as tx_error:
            print(f"Failed to create transaction record (table may not exist): {tx_error}")
        
        # Create notification (skip if table doesn't exist)
        try:
            print("Creating notification...")
            notification_message = (
                f"Your account has been topped up with ${balance_update.amount:.2f}. New balance: ${new_balance:.2f}" 
                if balance_update.transaction_type == "topup" 
                else f"You have withdrawn ${balance_update.amount:.2f}. New balance: ${new_balance:.2f}"
            )
            
            notification_response = supabase_admin.table('user_notifications').insert({
                'user_id': user_id,
                'title': f"{balance_update.transaction_type.title()} Successful",
                'message': notification_message,
                'type': 'success',
                'is_read': False
            }).execute()
            print(f"Notification created: {notification_response}")
        except Exception as notification_error:
            print(f"Failed to create notification (table may not exist): {notification_error}")
        
        print(f"✅ Balance updated: {user_id} - {balance_update.transaction_type} ${balance_update.amount} - New balance: ${new_balance}")
        
        result = {
            "success": True, 
            "message": f"{balance_update.transaction_type.title()} successful",
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "amount_changed": amount_change
        }
        print(f"Returning success result: {result}")
        print("=== END UPDATE BALANCE ENDPOINT ===\n")
        return result
        
    except Exception as e:
        print(f"❌ Exception in update_balance: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        print("=== END UPDATE BALANCE ENDPOINT (ERROR) ===\n")
        return {"success": False, "message": f"Failed to update balance: {str(e)}"}

@router.get("/auth/user/{user_id}/transactions")
async def get_user_transactions(user_id: str, limit: int = 50, offset: int = 0):
    """Get user's transaction history"""
    try:
        if not supabase_admin:
            return {"success": False, "message": "Database not available"}
        
        # Check if transactions table exists, return empty list if not
        try:
            response = supabase_admin.table('transactions')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', False)\
                .limit(limit)\
                .execute()
            
            # Also get transactions where user is the seller
            seller_response = supabase_admin.table('transactions')\
                .select('*')\
                .eq('seller_id', user_id)\
                .order('created_at', False)\
                .limit(limit)\
                .execute()
            
            # Combine and sort results
            all_transactions = []
            if response.data:
                all_transactions.extend(response.data)
            if seller_response.data:
                all_transactions.extend(seller_response.data)
            
            # Remove duplicates and sort by created_at
            seen_ids = set()
            unique_transactions = []
            for tx in all_transactions:
                if tx['id'] not in seen_ids:
                    seen_ids.add(tx['id'])
                    unique_transactions.append(tx)
            
            # Sort by created_at descending
            unique_transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Apply limit
            limited_transactions = unique_transactions[:limit]
            
            return {"success": True, "transactions": limited_transactions}
            
        except Exception as table_error:
            print(f"Transactions table not available: {table_error}")
            return {"success": True, "transactions": []}
            
    except Exception as e:
        return {"success": False, "message": f"Failed to get transactions: {str(e)}"}

# =====================================================
# Subscription Limits Management Endpoints
# =====================================================

