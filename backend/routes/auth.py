from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from supabase_client import supabase, supabase_admin
from typing import Optional
import os

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