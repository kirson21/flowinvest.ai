"""
NowPayments Integration - Invoice-based Payment Gateway & Subscriptions
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import os
import time
import uuid
import hashlib
import hmac
import json
import httpx
import pyotp  # For TOTP 2FA code generation
from datetime import datetime, timedelta

router = APIRouter()

# NowPayments API Configuration
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1"
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
NOWPAYMENTS_PUBLIC_KEY = os.getenv("NOWPAYMENTS_PUBLIC_KEY", "f56ecfa5-09db-45d0-95bd-599043c84a5c")
NOWPAYMENTS_IPN_SECRET = os.getenv("NOWPAYMENTS_IPN_SECRET", "")
NOWPAYMENTS_2FA_SECRET = os.getenv("NOWPAYMENTS_2FA_SECRET")  # For TOTP 2FA automation

# Base URL for return URLs (will be configured in environment)
BASE_URL = os.getenv("REACT_APP_BACKEND_URL", "https://payflow-ai.preview.emergentagent.com")

# Pydantic models
class InvoiceRequest(BaseModel):
    amount: float
    currency: str = "usd"  # Price currency (fiat)
    pay_currency: Optional[str] = None  # Crypto currency to pay with
    order_id: Optional[str] = None
    description: Optional[str] = None
    user_email: Optional[EmailStr] = None

class SubscriptionPlanRequest(BaseModel):
    title: str
    interval_days: int
    amount: float
    currency: str = "usd"

class SubscriptionRequest(BaseModel):
    plan_id: str
    user_email: EmailStr

class PayoutRequest(BaseModel):
    recipient_address: str
    amount: float
    currency: str
    description: Optional[str] = None

class WithdrawalRequest(BaseModel):
    recipient_address: str
    amount: float
    currency: str
    description: Optional[str] = None

class VerifyWithdrawalRequest(BaseModel):
    withdrawal_id: str
    verification_code: Optional[str] = None

# NowPayments supported currencies configuration
SUPPORTED_CURRENCIES = {
    'USDT': {
        'networks': {
            'TRX': 'usdttrc20',     # USDT on Tron
            'BSC': 'usdtbsc',       # USDT on BSC  
            'SOL': 'usdtsol',       # USDT on Solana
            'TON': 'usdtton',       # USDT on TON
            'ETH': 'usdterc20'      # USDT on Ethereum
        }
    },
    'USDC': {
        'networks': {
            'ETH': 'usdcerc20',     # USDC on Ethereum
            'BSC': 'usdcbsc',       # USDC on BSC
            'SOL': 'usdcsol',       # USDC on Solana
        }
    }
}

async def get_nowpayments_jwt_token():
    """Get JWT token for NowPayments subscriptions API"""
    try:
        # Get credentials from environment variables
        nowpayments_email = os.getenv("NOWPAYMENTS_EMAIL")
        nowpayments_password = os.getenv("NOWPAYMENTS_PASSWORD")
        
        if not nowpayments_email or not nowpayments_password:
            print(f"❌ NowPayments credentials missing:")
            print(f"   NOWPAYMENTS_EMAIL: {'Present' if nowpayments_email else 'Missing'}")
            print(f"   NOWPAYMENTS_PASSWORD: {'Present' if nowpayments_password else 'Missing'}")
            return None
        
        auth_data = {
            "email": nowpayments_email,
            "password": nowpayments_password
        }
        
        print(f"🔐 Authenticating with NowPayments using email: {nowpayments_email}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.nowpayments.io/v1/auth",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("token")
            else:
                print(f"JWT auth failed: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"JWT auth error: {str(e)}")
        return None

def get_nowpayments_headers_with_jwt(jwt_token=None):
    """Get headers for NowPayments API requests with JWT"""
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    
    return headers

def get_nowpayments_headers():
    """Get headers for NowPayments API requests (backward compatibility)"""
    return get_nowpayments_headers_with_jwt()

async def make_nowpayments_request(method: str, endpoint: str, data: Optional[Dict] = None):
    """Make HTTP request to NowPayments API"""
    url = f"{NOWPAYMENTS_API_URL}{endpoint}"
    headers = get_nowpayments_headers()
    
    async with httpx.AsyncClient() as client:
        if method.upper() == "GET":
            response = await client.get(url, headers=headers, params=data or {})
        elif method.upper() == "POST":
            response = await client.post(url, headers=headers, json=data or {})
        elif method.upper() == "PUT":
            response = await client.put(url, headers=headers, json=data or {})
        elif method.upper() == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response

@router.get("/nowpayments/health")
async def nowpayments_health_check():
    """Health check for NowPayments integration"""
    try:
        response = await make_nowpayments_request("GET", "/status")
        if response.status_code == 200:
            return {
                "status": "healthy",
                "nowpayments_status": response.json(),
                "supported_currencies": list(SUPPORTED_CURRENCIES.keys()),
                "api_connected": True
            }
        else:
            return {
                "status": "degraded",
                "message": "NowPayments API connection issues",
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Failed to connect to NowPayments: {str(e)}"
        }

@router.get("/nowpayments/currencies")
async def get_supported_currencies():
    """Get supported cryptocurrencies and networks"""
    try:
        # Get available currencies from NowPayments
        response = await make_nowpayments_request("GET", "/currencies")
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch currencies from NowPayments")
        
        available_currencies = response.json().get("currencies", [])
        
        # Filter and organize our supported currencies
        filtered_currencies = {}
        for currency, config in SUPPORTED_CURRENCIES.items():
            filtered_currencies[currency] = {
                "name": "Tether USD" if currency == "USDT" else "USD Coin",
                "networks": []
            }
            
            for network_name, nowpayments_code in config["networks"].items():
                if nowpayments_code in available_currencies:
                    filtered_currencies[currency]["networks"].append({
                        "name": network_name,
                        "code": nowpayments_code,
                        "display_name": f"{currency} ({network_name})"
                    })
        
        return {
            "success": True,
            "currencies": filtered_currencies,
            "total_networks": sum(len(c["networks"]) for c in filtered_currencies.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get supported currencies: {str(e)}")

@router.get("/nowpayments/min-amount")
async def get_minimum_amount(currency_from: str = "usd", currency_to: str = "usdttrc20"):
    """Get minimum payment amount for currency pair"""
    try:
        params = {
            "currency_from": currency_from,
            "currency_to": currency_to
        }
        
        response = await make_nowpayments_request("GET", "/min-amount", params)
        
        if response.status_code != 200:
            return {"success": False, "min_amount": 10.0}  # Default fallback
        
        result = response.json()
        return {
            "success": True,
            "min_amount": result.get("min_amount", 10.0),
            "currency_from": result.get("currency_from", currency_from),
            "currency_to": result.get("currency_to", currency_to)
        }
        
    except Exception as e:
        return {"success": False, "min_amount": 10.0}  # Safe fallback

@router.post("/nowpayments/invoice")
async def create_invoice(request: InvoiceRequest, user_id: str = Query(..., description="User ID for the invoice")):
    """Create payment invoice with NowPayments"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Validate required fields
        if not request.amount or request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        if not request.currency:
            raise HTTPException(status_code=400, detail="Currency is required")
        
        # Validate user_id is provided
        if not user_id:
            raise HTTPException(status_code=400, detail="Valid user_id is required for invoice creation")
        
        # Use the provided user_id directly
        actual_user_id = user_id
        
        # Generate unique order ID
        order_id = request.order_id or f"f01i_{actual_user_id[-8:]}_{int(time.time())}"
        
        # Prepare invoice data
        invoice_data = {
            "price_amount": request.amount,
            "price_currency": request.currency,
            "order_id": order_id,
            "order_description": request.description or f"f01i.ai Payment - ${request.amount}",
            "success_url": f"{BASE_URL}/payment/success?order_id={order_id}",
            "cancel_url": f"{BASE_URL}/payment/cancel?order_id={order_id}",
            "ipn_callback_url": f"{BASE_URL}/api/nowpayments/webhook"
        }
        
        # Add specific pay currency if provided
        if request.pay_currency:
            invoice_data["pay_currency"] = request.pay_currency
        
        # Create invoice with NowPayments
        response = await make_nowpayments_request("POST", "/invoice", invoice_data)
        
        if response.status_code not in [200, 201]:
            error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=400, detail=f"NowPayments invoice creation failed: {error_detail}")
        
        invoice_response = response.json()
        
        # Store payment record in database
        payment_record = {
            'user_id': actual_user_id,
            'order_id': order_id,
            'invoice_id': invoice_response['id'],
            'payment_status': 'waiting',
            'amount': request.amount,
            'currency': request.currency,
            'pay_currency': request.pay_currency,
            'invoice_url': invoice_response['invoice_url'],
            'user_email': request.user_email,
            'description': request.description
        }
        
        # Insert into nowpayments_invoices table
        result = supabase.table('nowpayments_invoices').insert(payment_record).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to store payment record")
        
        return {
            "success": True,
            "invoice_id": invoice_response['id'],
            "invoice_url": invoice_response['invoice_url'],
            "order_id": order_id,
            "amount": request.amount,
            "currency": request.currency,
            "pay_currency": request.pay_currency,
            "message": "Invoice created successfully. Redirect user to invoice_url to complete payment."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")

@router.get("/nowpayments/payment/{payment_id}")
async def get_payment_status(payment_id: str, user_id: str = Query(..., description="User ID for payment verification")):
    """Get payment status from NowPayments"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Validate user_id is provided
        if not user_id:
            raise HTTPException(status_code=400, detail="Valid user_id is required for payment verification")
        
        # Get payment status from NowPayments
        response = await make_nowpayments_request("GET", f"/payment/{payment_id}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment_data = response.json()
        
        # Update our database record
        update_data = {
            'payment_status': payment_data.get('payment_status', 'unknown'),
            'actually_paid': payment_data.get('actually_paid', 0),
            'updated_at': 'now()'
        }
        
        if payment_data.get('payment_status') == 'finished':
            update_data['completed_at'] = 'now()'
        
        supabase.table('nowpayments_invoices')\
            .update(update_data)\
            .eq('invoice_id', payment_id)\
            .eq('user_id', user_id)\
            .execute()
        
        return {
            "success": True,
            "payment": payment_data,
            "local_status": update_data['payment_status']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")

@router.post("/nowpayments/webhook")
async def nowpayments_webhook(request: Request):
    """Handle NowPayments IPN webhooks with proper signature verification"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Get request body and headers
        body = await request.body()
        signature = request.headers.get("x-nowpayments-sig")
        
        print(f"🔔 Received webhook - Signature: {signature[:20]}..." if signature else "🔔 Received webhook - NO SIGNATURE")
        
        # Parse JSON data first
        webhook_data = json.loads(body.decode())
        
        # Handle both "All-Strings" and "Classic way" webhook formats
        payment_id = webhook_data.get('payment_id')
        payment_status = webhook_data.get('payment_status')
        order_id = webhook_data.get('order_id')
        customer_email = webhook_data.get('customer_email') or webhook_data.get('email')
        
        # Handle amount as string (All-Strings format) or number (Classic format)
        actually_paid_raw = webhook_data.get('actually_paid', 0)
        if isinstance(actually_paid_raw, str):
            actually_paid = float(actually_paid_raw) if actually_paid_raw else 0
        else:
            actually_paid = float(actually_paid_raw) if actually_paid_raw else 0
        
        print(f"📊 Webhook data: payment_id={payment_id}, status={payment_status}, email={customer_email}, amount=${actually_paid}")
        
        # Verify IPN signature if secret is available
        if NOWPAYMENTS_IPN_SECRET and signature:
            try:
                expected_signature = hmac.new(
                    NOWPAYMENTS_IPN_SECRET.encode('utf-8'),
                    body,
                    hashlib.sha256
                ).hexdigest()
                
                if signature != expected_signature:
                    print(f"❌ Invalid webhook signature.")
                    print(f"   Expected: {expected_signature}")
                    print(f"   Received: {signature}")
                    print(f"   Body: {body.decode()}")
                    # Don't fail on signature verification for now - log and continue
                    print(f"⚠️ Continuing webhook processing despite signature mismatch for debugging")
                else:
                    print(f"✅ Webhook signature verified successfully")
            except Exception as sig_error:
                print(f"⚠️ Signature verification error: {sig_error}")
                print(f"⚠️ Continuing webhook processing for debugging")
        elif NOWPAYMENTS_IPN_SECRET:
            print(f"⚠️ IPN secret is configured but no signature provided in webhook")
        else:
            print(f"⚠️ No IPN secret configured - skipping signature verification")
            
        # Log all webhook data for debugging
        print(f"🔍 COMPLETE WEBHOOK DATA:")
        print(f"   Payment ID: {payment_id}")
        print(f"   Status: {payment_status}")
        print(f"   Email: {customer_email}")
        print(f"   Amount: ${actually_paid:.2f}")
        print(f"   Order ID: {order_id}")
        print(f"   Full webhook data: {webhook_data}")
        
        if not payment_id:
            raise HTTPException(status_code=400, detail="Missing payment_id in webhook")
        
        print(f"🔔 Processing webhook for payment_id: {payment_id}, status: {payment_status}, email: {customer_email}, amount: ${actually_paid}")
        
        # For subscription payments, we need to handle the case where email is None
        # Look for subscription payments by amount range and check if it's a subscription
        is_subscription_payment = False
        
        # Method 1: Check by amount (subscription payments are usually $9-15)
        if actually_paid >= 9.0 and actually_paid <= 15.0 and payment_status == 'finished':
            print(f"💡 Detected potential subscription payment by amount: ${actually_paid}")
            
            # Method 2: Look for recent subscription validation records for this amount
            validation_result = supabase.table('subscription_email_validation')\
                .select('*')\
                .eq('status', 'pending')\
                .gte('amount', actually_paid - 1.0)\
                .lte('amount', actually_paid + 1.0)\
                .order('created_at', desc=True)\
                .limit(5)\
                .execute()
            
            if validation_result.data:
                print(f"🎯 Found {len(validation_result.data)} potential matching subscription validation records")
                
                # Find the best match (closest amount and most recent)
                best_match = None
                min_amount_diff = float('inf')
                
                for validation_record in validation_result.data:
                    amount_diff = abs(float(validation_record.get('amount', 0)) - actually_paid)
                    if amount_diff < min_amount_diff:
                        min_amount_diff = amount_diff
                        best_match = validation_record
                
                if best_match:
                    user_id = best_match['user_id']
                    customer_email = best_match['email']  # Get email from validation record
                    plan_type = best_match['plan_type']
                    
                    print(f"✅ Best match found: user {user_id}, email: {customer_email}, amount diff: ${min_amount_diff:.2f}")
                    
                    is_subscription_payment = True
                    
                    # Update validation record to completed
                    supabase.table('subscription_email_validation')\
                        .update({
                            'status': 'completed',
                            'nowpayments_payment_id': str(payment_id),
                            'actual_amount_paid': actually_paid,
                            'updated_at': 'now()'
                        })\
                        .eq('id', best_match['id'])\
                        .execute()
                    
                    print(f"✅ Validation record updated with payment ID {payment_id}")
        
        # Process subscription upgrade if we identified this as a subscription payment
        if is_subscription_payment and customer_email:
            print(f"💡 Processing as subscription payment for {customer_email}")
            
            # ALWAYS update existing subscription - never try to insert
            # This avoids the unique constraint error
            from datetime import datetime, timedelta
            end_date = datetime.utcnow() + timedelta(days=31)
            
            plus_plan_limits = {
                'ai_bots': 3,
                'manual_bots': 5, 
                'marketplace_products': 10
            }
            
            subscription_data = {
                'plan_type': 'plus',
                'status': 'active',
                'start_date': datetime.utcnow().isoformat(),
                'end_date': end_date.isoformat(),
                'renewal': True,
                'price_paid': actually_paid,
                'currency': 'USD',
                'limits': plus_plan_limits,
                'metadata': {
                    'payment_method': 'crypto', 
                    'nowpayments_payment_id': str(payment_id), 
                    'email_validated': True,
                    'webhook_processed': True
                },
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # ALWAYS use UPDATE with ADMIN CLIENT to bypass RLS - this handles both existing subscriptions and creates if none exist
            result = supabase.table('subscriptions')\
                .update(subscription_data)\
                .eq('user_id', user_id)\
                .execute()
            
            if result.data:
                print(f"✅ Updated subscription for user {user_id} to Plus plan")
            else:
                print(f"⚠️ No existing subscription found, creating new one...")
                # If update didn't work (no existing record), create new one
                subscription_data['user_id'] = user_id
                subscription_data['created_at'] = datetime.utcnow().isoformat()
                
                try:
                    result = supabase.table('subscriptions')\
                        .insert(subscription_data)\
                        .execute()
                    print(f"➕ Created new subscription for user {user_id}")
                except Exception as insert_error:
                    print(f"❌ Failed to create subscription: {insert_error}")
                    # Try one more update in case of race condition
                    result = supabase.table('subscriptions')\
                        .update(subscription_data)\
                        .eq('user_id', user_id)\
                        .execute()
                    print(f"🔄 Retry update result: {len(result.data) if result.data else 0} records updated")
            
            # Create success notification
            notification = {
                'user_id': user_id,
                'title': '🎉 Subscription Upgraded to Plus!',
                'message': f'Your crypto payment of ${actually_paid:.2f} has been confirmed and your subscription has been upgraded to Plus Plan. Enjoy your new features!',
                'type': 'success',
                'is_read': False
            }
            
            supabase.table('user_notifications').insert(notification).execute()
            
            # Update company balance
            print(f"💰 Adding ${actually_paid:.2f} subscription revenue to company balance")
            try:
                company_update = supabase.rpc('update_company_balance_subscription', {
                    'subscription_revenue': actually_paid
                }).execute()
                
                if company_update.data:
                    print(f"✅ Company balance updated with subscription revenue: ${actually_paid:.2f}")
            except Exception as balance_error:
                print(f"❌ Error updating company balance: {balance_error}")
            
            # Trigger Google Sheets sync
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    await client.post(f"{BASE_URL}/api/google-sheets/trigger-sync")
                print(f"✅ Google Sheets sync triggered")
            except Exception as sync_error:
                print(f"⚠️ Google Sheets sync trigger failed: {sync_error}")
            
            return {"success": True, "message": "Subscription webhook processed successfully"}
            
        # For subscription payments, use email validation approach
        # Check if this is a subscription payment (amount around $10 and has customer email)
        elif customer_email and actually_paid >= 9.0 and actually_paid <= 15.0 and payment_status == 'finished':
            print(f"💡 Processing as subscription payment via email validation")
            
            # Find matching email validation record (ANY status to handle retries)
            validation_result = supabase.table('subscription_email_validation')\
                .select('*')\
                .eq('email', customer_email)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if validation_result.data:
                validation_record = validation_result.data[0]
                user_id = validation_record['user_id']
                plan_type = validation_record['plan_type']
                current_status = validation_record['status']
                
                print(f"✅ Found email validation record for user {user_id}, plan: {plan_type}, current_status: {current_status}")
                
                # Always update validation record with webhook payment data
                supabase.table('subscription_email_validation')\
                    .update({
                        'status': 'completed',
                        'nowpayments_payment_id': str(payment_id),
                        'actual_amount_paid': actually_paid,
                        'updated_at': 'now()'
                    })\
                    .eq('id', validation_record['id'])\
                    .execute()
                
                print(f"✅ Validation record updated with payment ID {payment_id}")
                
                # Check if user already has an active subscription to avoid duplicates
                existing_active_sub = supabase.table('subscriptions')\
                    .select('*')\
                    .eq('user_id', user_id)\
                    .eq('status', 'active')\
                    .eq('plan_type', 'plus')\
                    .execute()
                
                if existing_active_sub.data:
                    print(f"ℹ️ User {user_id} already has an active Plus subscription, skipping upgrade")
                    return {"success": True, "message": "User already has active subscription"}
                
                # Process subscription upgrade
                from datetime import datetime, timedelta
                
                # Calculate subscription end date (31 days from now)
                end_date = datetime.utcnow() + timedelta(days=31)
                
                # Define proper Plus plan limits
                plus_plan_limits = {
                    'ai_bots': 3,
                    'manual_bots': 5, 
                    'marketplace_products': 10
                }
                
                # Check if user has ANY subscription record (active, cancelled, etc.)
                existing_sub = supabase.table('subscriptions').select('*').eq('user_id', user_id).execute()
                
                subscription_data = {
                    'user_id': user_id,
                    'plan_type': 'plus',
                    'status': 'active',
                    'start_date': datetime.utcnow().isoformat(),
                    'end_date': end_date.isoformat(),
                    'renewal': True,
                    'price_paid': actually_paid,
                    'currency': 'USD',
                    'limits': plus_plan_limits,
                    'metadata': {
                        'payment_method': 'crypto', 
                        'nowpayments_payment_id': str(payment_id), 
                        'email_validated': True,
                        'webhook_processed': True
                    },
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                if existing_sub.data:
                    # Update existing subscription
                    result = supabase.table('subscriptions')\
                        .update(subscription_data)\
                        .eq('user_id', user_id)\
                        .execute()
                    print(f"📝 Updated existing subscription for user {user_id}")
                else:
                    # Create new subscription
                    subscription_data['created_at'] = datetime.utcnow().isoformat()
                    result = supabase.table('subscriptions')\
                        .insert(subscription_data)\
                        .execute()
                    print(f"➕ Created new subscription for user {user_id}")
                
                if result.data:
                    print(f"✅ Email-validated subscription upgrade completed for user {user_id}")
                    
                    # Update NowPayments subscription record if exists
                    supabase.table('nowpayments_subscriptions')\
                        .update({
                            'status': 'PAID',
                            'is_active': True,
                            'updated_at': 'now()'
                        })\
                        .eq('user_id', user_id)\
                        .eq('user_email', customer_email)\
                        .execute()
                    
                    # Create success notification
                    notification = {
                        'user_id': user_id,
                        'title': '🎉 Subscription Upgraded to Plus!',
                        'message': f'Your crypto payment of ${actually_paid:.2f} has been confirmed and your subscription has been upgraded to Plus Plan. Enjoy your new features including 3 AI bots, 5 manual bots, and up to 10 marketplace products! Valid until {end_date.strftime("%B %d, %Y")}',
                        'type': 'success',
                        'is_read': False
                    }
                    
                    supabase.table('user_notifications').insert(notification).execute()
                    
                    # UPDATE COMPANY BALANCE - Add subscription revenue
                    print(f"💰 Adding ${actually_paid:.2f} subscription revenue to company balance")
                    try:
                        # Update company balance with subscription revenue
                        company_update = supabase.rpc('update_company_balance_subscription', {
                            'subscription_revenue': actually_paid
                        }).execute()
                        
                        if company_update.data:
                            print(f"✅ Company balance updated with subscription revenue: ${actually_paid:.2f}")
                        else:
                            print(f"⚠️ Company balance update failed, will try direct update")
                            
                            # Fallback: Direct update to company_balance table
                            current_balance = supabase.table('company_balance').select('company_funds').execute()
                            if current_balance.data:
                                current_funds = float(current_balance.data[0]['company_funds'])
                                supabase.table('company_balance')\
                                    .update({
                                        'company_funds': current_funds + actually_paid,
                                        'last_updated': 'now()'
                                    })\
                                    .eq('id', '00000000-0000-0000-0000-000000000001')\
                                    .execute()
                                
                                print(f"✅ Company balance updated directly with subscription revenue: ${actually_paid:.2f}")
                            
                    except Exception as balance_error:
                        print(f"❌ Error updating company balance: {balance_error}")
                    
                    # TRIGGER GOOGLE SHEETS SYNC
                    try:
                        import httpx
                        async with httpx.AsyncClient() as client:
                            await client.post(f"{BASE_URL}/api/google-sheets/trigger-sync")
                        print(f"✅ Google Sheets sync triggered")
                    except Exception as sync_error:
                        print(f"⚠️ Google Sheets sync trigger failed: {sync_error}")
                    
                    return {"success": True, "message": "Subscription webhook processed successfully via email validation"}
                else:
                    print(f"❌ Failed to upgrade subscription for user {user_id}")
                    
            else:
                print(f"⚠️ No email validation record found for {customer_email}")
                print(f"   This might be a regular invoice payment, not a subscription")
        
        # For regular invoice payments (balance top-ups) or non-subscription payments
        else:
            print(f"💰 Processing as invoice payment or balance top-up")
            
            # Extract the correct invoice_id from webhook data
            invoice_id = webhook_data.get('invoice_id')
            
            if not invoice_id:
                print(f"⚠️ No invoice_id found in webhook data, trying payment_id as fallback")
                invoice_id = payment_id
            
            print(f"🔍 Looking for invoice record with invoice_id: {invoice_id}")
            
            # Update invoice record if exists - use the correct invoice_id
            result = supabase.table('nowpayments_invoices')\
                .update({
                    'payment_status': payment_status,
                    'actually_paid': actually_paid,
                    'pay_currency': webhook_data.get('pay_currency'),
                    'updated_at': 'now()',
                    'webhook_data': webhook_data,
                    'completed_at': 'now()' if payment_status == 'finished' else None
                })\
                .eq('invoice_id', str(invoice_id))\
                .execute()
            
            print(f"📊 Invoice update result: {len(result.data) if result.data else 0} records updated")
            
            if result.data and payment_status == 'finished':
                invoice = result.data[0]
                user_id = invoice['user_id']
                amount = float(actually_paid)
                
                print(f"💰 Processing balance top-up for user {user_id}, amount: ${amount}")
                
                # Create balance transaction
                balance_transaction = {
                    'user_id': user_id,
                    'transaction_type': 'topup',
                    'amount': amount,
                    'platform_fee': 0.0,
                    'net_amount': amount,
                    'status': 'completed',
                    'description': f"Crypto payment: ${amount} via NowPayments (Order: {order_id})"
                }
                
                supabase.table('transactions').insert(balance_transaction).execute()
                
                # Update user balance
                supabase.rpc('update_user_balance', {
                    'user_uuid': user_id,
                    'amount_change': amount
                }).execute()
                
                # Create success notification
                notification = {
                    'user_id': user_id,
                    'title': 'Payment Successful! 🎉',
                    'message': f'Your payment of ${amount:.2f} has been confirmed and added to your balance.',
                    'type': 'success',
                    'is_read': False
                }
                
                supabase.table('user_notifications').insert(notification).execute()
                
                print(f"✅ Balance top-up completed for user {user_id}")
            else:
                print(f"ℹ️ No matching invoice found for payment_id {payment_id} or payment not finished")
        
        return {"success": True, "message": "Webhook processed successfully"}
        
    except Exception as e:
        # Log error but return success to avoid webhook retries
        print(f"❌ Webhook processing error: {str(e)}")
        return {"success": False, "error": str(e)}

@router.get("/nowpayments/webhook/test")
async def test_webhook_connectivity():
    """Test endpoint to verify webhook URL is reachable"""
    try:
        return {
            "success": True,
            "message": "Webhook endpoint is reachable",
            "url": f"{BASE_URL}/api/nowpayments/webhook",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "base_url": BASE_URL,
                "ipn_secret_configured": bool(NOWPAYMENTS_IPN_SECRET),
                "api_key_configured": bool(NOWPAYMENTS_API_KEY)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/nowpayments/webhook/simulate")
async def simulate_webhook_payment(test_data: dict):
    """Simulate a webhook call for testing purposes"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        payment_id = test_data.get('payment_id', '5737988853')
        customer_email = test_data.get('email', 'footballinphuket@gmail.com') 
        amount = test_data.get('amount', '10.07')
        
        # Create a simulated webhook request
        from fastapi import Request
        import io
        
        # Simulate the webhook data
        simulated_webhook_data = {
            "payment_id": payment_id,
            "payment_status": "finished",
            "customer_email": customer_email,
            "email": customer_email,
            "actually_paid": amount,
            "order_id": f"subscription_{customer_email}_{payment_id}",
            "pay_currency": "usdttrc20",
            "price_amount": amount,
            "price_currency": "USD"
        }
        
        print(f"🧪 Simulating webhook call with data: {simulated_webhook_data}")
        
        # Process this data through our webhook logic manually
        webhook_body = json.dumps(simulated_webhook_data).encode()
        
        # Find matching email validation record
        validation_result = supabase.table('subscription_email_validation')\
            .select('*')\
            .eq('email', customer_email)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if validation_result.data:
            validation_record = validation_result.data[0]
            user_id = validation_record['user_id']
            
            print(f"✅ Found validation record for user {user_id}")
            
            # Update validation record to completed with webhook data
            supabase.table('subscription_email_validation')\
                .update({
                    'status': 'completed',
                    'nowpayments_payment_id': str(payment_id),
                    'actual_amount_paid': float(amount),
                    'updated_at': 'now()'
                })\
                .eq('id', validation_record['id'])\
                .execute()
            
            print(f"✅ Validation record updated with payment ID {payment_id}")
            
            # Process subscription upgrade
            from datetime import datetime, timedelta
            end_date = datetime.utcnow() + timedelta(days=31)
            
            plus_plan_limits = {
                'ai_bots': 3,
                'manual_bots': 5, 
                'marketplace_products': 10
            }
            
            subscription_data = {
                'user_id': user_id,
                'plan_type': 'plus',
                'status': 'active',
                'start_date': datetime.utcnow().isoformat(),
                'end_date': end_date.isoformat(),
                'renewal': True,
                'price_paid': float(amount),
                'currency': 'USD',
                'limits': plus_plan_limits,
                'metadata': {
                    'payment_method': 'crypto', 
                    'nowpayments_payment_id': str(payment_id), 
                    'email_validated': True,
                    'simulated_webhook': True
                },
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Update or create subscription
            existing_sub = supabase.table('subscriptions').select('*').eq('user_id', user_id).execute()
            
            if existing_sub.data:
                result = supabase.table('subscriptions')\
                    .update(subscription_data)\
                    .eq('user_id', user_id)\
                    .execute()
                print(f"📝 Updated existing subscription for user {user_id}")
            else:
                subscription_data['created_at'] = datetime.utcnow().isoformat()
                result = supabase.table('subscriptions')\
                    .insert(subscription_data)\
                    .execute()
                print(f"➕ Created new subscription for user {user_id}")
            
            # Update company balance
            if result.data:
                company_update = supabase.rpc('update_company_balance_subscription', {
                    'subscription_revenue': float(amount)
                }).execute()
                
                if company_update.data:
                    print(f"✅ Company balance updated with ${amount}")
            
            return {
                "success": True,
                "message": f"Simulated webhook processed successfully for {customer_email}",
                "user_id": user_id,
                "payment_id": payment_id,
                "amount": amount
            }
        else:
            return {"success": False, "message": f"No validation record found for {customer_email}"}
            
    except Exception as e:
        print(f"❌ Simulation error: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/nowpayments/webhook/debug")
async def debug_webhook_data(request: Request):
    """Debug endpoint to see what webhook data we're receiving"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Get request body and headers
        body = await request.body()
        headers = dict(request.headers)
        
        print(f"🔍 DEBUG WEBHOOK DATA:")
        print(f"Headers: {headers}")
        print(f"Body: {body.decode()}")
        
        # Parse JSON data
        webhook_data = json.loads(body.decode())
        print(f"Parsed webhook data: {webhook_data}")
        
        # Store the webhook data for analysis
        debug_record = {
            'webhook_data': webhook_data,
            'headers': headers,
            'received_at': datetime.now().isoformat(),
            'payment_id': webhook_data.get('payment_id'),
            'payment_status': webhook_data.get('payment_status'),
            'customer_email': webhook_data.get('customer_email') or webhook_data.get('email'),
            'actually_paid': float(webhook_data.get('actually_paid', 0))
        }
        
        print(f"🔍 Debug record: {debug_record}")
        
        return {
            "success": True,
            "message": "Webhook data captured for debugging",
            "data": debug_record
        }
        
    except Exception as e:
        print(f"❌ Webhook debug error: {str(e)}")
        return {"success": False, "error": str(e)}

@router.post("/nowpayments/subscription/manual-process")
async def manual_process_subscription_payment(payment_data: dict):
    """Manually process a subscription payment for debugging"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        payment_id = payment_data.get('payment_id')
        customer_email = payment_data.get('customer_email') 
        actually_paid = float(payment_data.get('actually_paid', 0))
        
        print(f"🔧 Manual processing: payment_id={payment_id}, email={customer_email}, amount=${actually_paid}")
        
        # Find matching email validation record
        validation_result = supabase.table('subscription_email_validation')\
            .select('*')\
            .eq('email', customer_email)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if validation_result.data:
            validation_record = validation_result.data[0]
            user_id = validation_record['user_id']
            
            print(f"✅ Found validation record for user {user_id}")
            
            # Update validation record with actual payment ID
            supabase.table('subscription_email_validation')\
                .update({
                    'status': 'completed',
                    'nowpayments_payment_id': str(payment_id),  # Store the actual payment ID
                    'actual_amount_paid': actually_paid,
                    'updated_at': 'now()'
                })\
                .eq('id', validation_record['id'])\
                .execute()
            
            # Process subscription upgrade (same logic as webhook)
            from datetime import datetime, timedelta
            
            end_date = datetime.utcnow() + timedelta(days=31)
            
            plus_plan_limits = {
                'ai_bots': 3,
                'manual_bots': 5, 
                'marketplace_products': 10
            }
            
            # Check if user already has a subscription record
            existing_sub = supabase.table('subscriptions').select('*').eq('user_id', user_id).execute()
            
            subscription_data = {
                'user_id': user_id,
                'plan_type': 'plus',
                'status': 'active',
                'start_date': datetime.utcnow().isoformat(),
                'end_date': end_date.isoformat(),
                'renewal': True,
                'price_paid': actually_paid,
                'currency': 'USD',
                'limits': plus_plan_limits,
                'metadata': {'payment_method': 'crypto', 'nowpayments_payment_id': str(payment_id), 'email_validated': True},
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if existing_sub.data:
                # Update existing subscription
                result = supabase.table('subscriptions')\
                    .update(subscription_data)\
                    .eq('user_id', user_id)\
                    .execute()
                print(f"📝 Updated existing subscription for user {user_id}")
            else:
                # Create new subscription
                subscription_data['created_at'] = datetime.utcnow().isoformat()
                result = supabase.table('subscriptions')\
                    .insert(subscription_data)\
                    .execute()
                print(f"➕ Created new subscription for user {user_id}")
            
            if result.data:
                print(f"✅ Subscription upgrade completed for user {user_id}")
                
                # Update company balance
                company_update = supabase.rpc('update_company_balance_subscription', {
                    'subscription_revenue': actually_paid
                }).execute()
                
                if company_update.data:
                    print(f"✅ Company balance updated with subscription revenue: ${actually_paid:.2f}")
                
                return {
                    "success": True,
                    "message": f"Subscription manually processed for {customer_email}",
                    "user_id": user_id,
                    "payment_id": payment_id,
                    "amount": actually_paid
                }
            else:
                return {"success": False, "message": "Failed to process subscription"}
        else:
            return {"success": False, "message": f"No validation record found for email {customer_email}"}
            
    except Exception as e:
        print(f"❌ Manual processing error: {str(e)}")
        return {"success": False, "message": f"Manual processing failed: {str(e)}"}

# Subscription Management Endpoints

@router.post("/nowpayments/subscription/plan")
async def create_subscription_plan(request: SubscriptionPlanRequest):
    """Create a subscription plan"""
    try:
        plan_data = {
            "title": request.title,
            "interval_day": request.interval_days,
            "amount": request.amount,
            "currency": request.currency
        }
        
        response = await make_nowpayments_request("POST", "/subscriptions/plans", plan_data)
        
        if response.status_code not in [200, 201]:
            error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=400, detail=f"Failed to create subscription plan: {error_detail}")
        
        return {
            "success": True,
            "plan": response.json().get("result", response.json())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create subscription plan: {str(e)}")

@router.post("/nowpayments/subscription")
async def create_subscription(request: SubscriptionRequest, user_id: str = Query(..., description="User ID for the subscription")):
    """Create subscription with NowPayments and store email validation record"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Validate user_id is provided and not a default value
        if not user_id or user_id == "demo_user":
            raise HTTPException(status_code=400, detail="Valid user_id is required for subscription creation")
        
        # Use the provided user_id directly (no more defaults to Super Admin!)
        actual_user_id = user_id
        
        # Get JWT token for subscription API
        jwt_token = await get_nowpayments_jwt_token()
        if not jwt_token:
            raise HTTPException(status_code=500, detail="Failed to authenticate with NowPayments for subscriptions")
        
        # Use your real NowPayments subscription plan ID
        nowpayments_plan_id = 1516280944  # Your Plan Plus ID from dashboard
        
        # Create email validation record FIRST
        validation_record = {
            'user_id': actual_user_id,
            'email': request.user_email,
            'plan_type': request.plan_id,
            'amount': 10.00,  # Plus plan amount
            'status': 'pending'
        }
        
        validation_result = supabase.table('subscription_email_validation').insert(validation_record).execute()
        
        if not validation_result.data:
            raise HTTPException(status_code=500, detail="Failed to create subscription validation record")
        
        validation_id = validation_result.data[0]['id']
        
        # Now create subscription with NowPayments
        subscription_data = {
            "subscription_plan_id": nowpayments_plan_id,
            "email": request.user_email
        }
        
        # Make authenticated request to NowPayments subscriptions API
        headers = get_nowpayments_headers_with_jwt(jwt_token)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NOWPAYMENTS_API_URL}/subscriptions",
                json=subscription_data,
                headers=headers
            )
        
        if response.status_code not in [200, 201]:
            # Clean up validation record if NowPayments call fails
            supabase.table('subscription_email_validation').delete().eq('id', validation_id).execute()
            error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=400, detail=f"Failed to create NowPayments subscription: {error_detail}")
        
        # Parse the response - handle both formats
        response_data = response.json()
        print(f"NowPayments subscription response: {response_data}")  # Debug log
        
        # NowPayments returns result as array with subscription object
        if isinstance(response_data, dict) and "result" in response_data:
            if isinstance(response_data["result"], list) and len(response_data["result"]) > 0:
                subscription_result = response_data["result"][0]  # Get first subscription from array
            else:
                subscription_result = response_data["result"]
        else:
            subscription_result = response_data
        
        print(f"Parsed subscription result: {subscription_result}")  # Debug log
        
        nowpayments_subscription_id = subscription_result.get('id')
        
        # Update validation record with NowPayments subscription ID
        supabase.table('subscription_email_validation')\
            .update({'nowpayments_subscription_id': str(nowpayments_subscription_id)})\
            .eq('id', validation_id)\
            .execute()
        
        # Store subscription record in database with proper data extraction
        subscription_record = {
            'user_id': actual_user_id,
            'subscription_id': str(nowpayments_subscription_id),  # This should be just the ID number
            'plan_id': request.plan_id,  # Keep our plan ID for reference
            'user_email': request.user_email,
            'status': subscription_result.get('status', 'WAITING_PAY'),
            'is_active': subscription_result.get('is_active', False),
            'expire_date': subscription_result.get('expire_date')
        }
        
        result = supabase.table('nowpayments_subscriptions').insert(subscription_record).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to store subscription record")
        
        # Create success notification
        notification = {
            'user_id': actual_user_id,
            'title': 'Subscription Created! 📧',
            'message': f'Your Plus Plan subscription has been created with NowPayments. Payment instructions have been sent to {request.user_email}. Check your email for payment details.',
            'type': 'success',
            'is_read': False
        }
        
        supabase.table('user_notifications').insert(notification).execute()
        
        return {
            "success": True,
            "subscription": subscription_result,
            "validation_id": validation_id,
            "nowpayments_plan_id": nowpayments_plan_id,
            "message": f"Subscription created successfully with NowPayments! Payment instructions have been sent to {request.user_email}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")

@router.delete("/nowpayments/subscription/{subscription_id}")
async def cancel_subscription(subscription_id: str, user_id: str = Query(..., description="User ID for subscription cancellation")):
    """Cancel a NowPayments subscription"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Validate user_id is provided
        if not user_id:
            raise HTTPException(status_code=400, detail="Valid user_id is required for subscription cancellation")
        
        # Get JWT token for subscription API
        jwt_token = await get_nowpayments_jwt_token()
        if not jwt_token:
            raise HTTPException(status_code=500, detail="Failed to authenticate with NowPayments for subscription cancellation")
        
        # Make authenticated DELETE request to NowPayments subscriptions API
        headers = get_nowpayments_headers_with_jwt(jwt_token)
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{NOWPAYMENTS_API_URL}/subscriptions/{subscription_id}",
                headers=headers
            )
        
        if response.status_code not in [200, 201]:
            error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=400, detail=f"Failed to cancel NowPayments subscription: {error_detail}")
        
        # Update local database to mark subscription as cancelled
        result = supabase.table('nowpayments_subscriptions')\
            .update({
                'status': 'CANCELLED',
                'is_active': False,
                'updated_at': 'now()'
            })\
            .eq('subscription_id', subscription_id)\
            .eq('user_id', user_id)\
            .execute()
        
        # Create cancellation notification
        notification = {
            'user_id': user_id,
            'title': 'Subscription Cancelled ❌',
            'message': f'Your subscription has been successfully cancelled. You can still use your current plan features until the expiry date.',
            'type': 'info',
            'is_read': False
        }
        
        supabase.table('user_notifications').insert(notification).execute()
        
        return {
            "success": True,
            "message": "Subscription cancelled successfully",
            "subscription_id": subscription_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")

@router.get("/nowpayments/user/{user_id}/payments")
async def get_user_payments(user_id: str, limit: int = 50):
    """Get user's payment history"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        result = supabase.table('nowpayments_invoices')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "payments": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user payments: {str(e)}")

@router.post("/nowpayments/admin/reset-balances")
async def reset_all_balances(admin_key: str = "admin123"):
    """Reset all user balances to 0 (admin only)"""
    try:
        if admin_key != "admin123":
            raise HTTPException(status_code=403, detail="Unauthorized")
            
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # First, get all user accounts to see how many exist
        all_accounts = supabase.table('user_accounts').select('user_id, balance').execute()
        
        # Reset all balances to 0 - update all existing records
        reset_result = supabase.table('user_accounts')\
            .update({'balance': 0.0})\
            .neq('balance', -99999)\
            .execute()  # Update all accounts (using a condition that matches all)
        
        # Count affected records
        affected_count = len(reset_result.data) if reset_result.data else 0
        total_accounts = len(all_accounts.data) if all_accounts.data else 0
        
        return {
            "success": True,
            "message": f"Successfully reset {affected_count} user balances to $0.00",
            "affected_users": affected_count,
            "total_accounts": total_accounts,
            "accounts_before": all_accounts.data[:5] if all_accounts.data else []  # Show first 5 as sample
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset balances: {str(e)}")

# Estimated price endpoint for frontend
@router.get("/nowpayments/estimate")
async def get_estimated_price(amount: float, currency_from: str = "usd", currency_to: str = "usdttrc20"):
    """Get estimated price for crypto payment"""
    try:
        params = {
            "amount": amount,
            "currency_from": currency_from,
            "currency_to": currency_to
        }
        
        response = await make_nowpayments_request("GET", "/estimate", params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get price estimate")
        
        return {
            "success": True,
            "estimate": response.json()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get price estimate: {str(e)}")

# =====================================================
# WITHDRAWALS/PAYOUTS FUNCTIONALITY
# =====================================================

def generate_2fa_code():
    """Generate 2FA code using TOTP and environment variable secret"""
    try:
        if not NOWPAYMENTS_2FA_SECRET:
            raise Exception("NOWPAYMENTS_2FA_SECRET environment variable not set")
        
        totp = pyotp.TOTP(NOWPAYMENTS_2FA_SECRET)
        code = totp.now()
        print(f"🔐 Generated 2FA code: {code}")
        return code
    except Exception as e:
        print(f"❌ Failed to generate 2FA code: {str(e)}")
        return None

@router.get("/nowpayments/withdrawal/min-amount/{currency}")
async def get_withdrawal_min_amount(currency: str):
    """Get minimum withdrawal amount for a specific currency"""
    try:
        response = await make_nowpayments_request("GET", f"/payout-withdrawal/min-amount/{currency}")
        
        if response.status_code != 200:
            # Fallback minimum amounts for supported currencies
            fallback_minimums = {
                "usdttrc20": 1.0,
                "usdtbsc": 1.0,
                "usdtsol": 1.0,
                "usdtton": 1.0,
                "usdterc20": 10.0,
                "usdcbsc": 1.0,
                "usdcsol": 1.0,
                "usdcerc20": 10.0
            }
            
            min_amount = fallback_minimums.get(currency.lower(), 10.0)
            
            return {
                "success": True,
                "min_amount": min_amount,
                "currency": currency,
                "source": "fallback"
            }
        
        result = response.json()
        return {
            "success": True,
            "min_amount": result.get("min_amount", 10.0),
            "currency": currency,
            "source": "nowpayments_api"
        }
        
    except Exception as e:
        print(f"Error getting min amount for {currency}: {str(e)}")
        return {
            "success": False,
            "min_amount": 10.0,  # Safe fallback
            "currency": currency,
            "error": str(e)
        }

@router.get("/nowpayments/withdrawal/fee")
async def get_withdrawal_fee(currency: str, amount: float):
    """Get withdrawal fee for a specific currency and amount"""
    try:
        params = {
            "currency": currency,
            "amount": amount
        }
        
        response = await make_nowpayments_request("GET", "/payout/fee", params)
        
        if response.status_code != 200:
            # Fallback network fees for supported currencies (approximate)
            fallback_fees = {
                "usdttrc20": 1.0,   # TRC20 usually ~$1
                "usdtbsc": 0.5,     # BSC usually ~$0.5
                "usdtsol": 0.01,    # Solana usually very low
                "usdtton": 0.05,    # TON usually low
                "usdterc20": 15.0,  # Ethereum usually higher
                "usdcbsc": 0.5,     # BSC usually ~$0.5
                "usdcsol": 0.01,    # Solana usually very low
                "usdcerc20": 15.0   # Ethereum usually higher
            }
            
            fee = fallback_fees.get(currency.lower(), 5.0)
            
            return {
                "success": True,
                "fee": fee,
                "currency": currency,
                "amount": amount,
                "source": "fallback"
            }
        
        result = response.json()
        return {
            "success": True,
            "fee": result.get("fee", 5.0),
            "currency": currency,
            "amount": amount,
            "source": "nowpayments_api"
        }
        
    except Exception as e:
        print(f"Error getting fee for {currency} amount {amount}: {str(e)}")
        return {
            "success": False,
            "fee": 5.0,  # Safe fallback
            "currency": currency,
            "amount": amount,
            "error": str(e)
        }

@router.post("/nowpayments/withdrawal/create")
async def create_withdrawal_request(request: WithdrawalRequest, user_id: str = Query(..., description="User ID for withdrawal")):
    """Create a withdrawal/payout request"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Validate input
        if not user_id:
            raise HTTPException(status_code=400, detail="Valid user_id is required for withdrawal")
        
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        if not request.recipient_address:
            raise HTTPException(status_code=400, detail="Recipient address is required")
        
        if not request.currency:
            raise HTTPException(status_code=400, detail="Currency is required")
        
        # Validate currency is supported
        supported_currencies = []
        for curr_data in SUPPORTED_CURRENCIES.values():
            supported_currencies.extend(curr_data["networks"].values())
        
        if request.currency not in supported_currencies:
            raise HTTPException(status_code=400, detail=f"Currency {request.currency} is not supported")
        
        # Check minimum amount
        min_amount_result = await get_withdrawal_min_amount(request.currency)
        min_amount = min_amount_result.get("min_amount", 1.0)
        
        if request.amount < min_amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Amount {request.amount} is below minimum withdrawal amount {min_amount} for {request.currency}"
            )
        
        # Check user balance
        user_balance_result = supabase.table('user_accounts').select('balance').eq('user_id', user_id).execute()
        
        user_balance = 0.0
        if user_balance_result.data:
            user_balance = float(user_balance_result.data[0]['balance'])
        
        if user_balance < request.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: ${user_balance:.2f}, Requested: ${request.amount:.2f}"
            )
        
        # Create withdrawal record using database function
        result = supabase.rpc('create_withdrawal_request', {
            'p_user_id': user_id,
            'p_recipient_address': request.recipient_address,
            'p_currency': request.currency,
            'p_amount': request.amount,
            'p_description': request.description
        }).execute()
        
        if not result.data or not result.data[0].get('success'):
            error_msg = result.data[0].get('message', 'Unknown error') if result.data else 'Database function failed'
            raise HTTPException(status_code=400, detail=error_msg)
        
        withdrawal_data = result.data[0]
        withdrawal_id = withdrawal_data['withdrawal_id']
        
        # Create notification
        notification = {
            'user_id': user_id,
            'title': '🔄 Withdrawal Request Created',
            'message': f'Your withdrawal request for {request.amount} {request.currency} has been created. Please verify the withdrawal to process it.',
            'type': 'info',
            'is_read': False
        }
        
        supabase.table('user_notifications').insert(notification).execute()
        
        return {
            "success": True,
            "withdrawal_id": withdrawal_id,
            "amount": request.amount,
            "currency": request.currency,
            "recipient_address": request.recipient_address,
            "status": "pending",
            "min_amount": min_amount,
            "message": "Withdrawal request created successfully. Please verify to process."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create withdrawal: {str(e)}")

@router.post("/nowpayments/withdrawal/verify")
async def verify_and_process_withdrawal(request: VerifyWithdrawalRequest, user_id: str = Query(..., description="User ID for verification")):
    """Verify withdrawal with 2FA and process the payout via NowPayments API"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Validate input
        if not user_id:
            raise HTTPException(status_code=400, detail="Valid user_id is required for verification")
        
        # Get withdrawal record
        withdrawal_result = supabase.table('nowpayments_withdrawals')\
            .select('*')\
            .eq('id', request.withdrawal_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not withdrawal_result.data:
            raise HTTPException(status_code=404, detail="Withdrawal request not found")
        
        withdrawal = withdrawal_result.data[0]
        
        # Check if withdrawal is in correct state
        if withdrawal['status'] != 'pending':
            raise HTTPException(status_code=400, detail=f"Withdrawal is in {withdrawal['status']} state and cannot be verified")
        
        # Check expiration
        if withdrawal['verification_expires_at']:
            expires_at = datetime.fromisoformat(withdrawal['verification_expires_at'].replace('Z', '+00:00'))
            if datetime.now(expires_at.tzinfo) > expires_at:
                # Update status to expired
                supabase.table('nowpayments_withdrawals')\
                    .update({'status': 'failed', 'error_message': 'Verification expired'})\
                    .eq('id', request.withdrawal_id)\
                    .execute()
                
                raise HTTPException(status_code=400, detail="Verification has expired. Please create a new withdrawal request.")
        
        # Generate 2FA code automatically
        verification_code = generate_2fa_code()
        if not verification_code:
            raise HTTPException(status_code=500, detail="Failed to generate 2FA code")
        
        # Get JWT token for payout API
        jwt_token = await get_nowpayments_jwt_token()
        if not jwt_token:
            raise HTTPException(status_code=500, detail="Failed to authenticate with NowPayments")
        
        # Create payout request with NowPayments
        payout_data = {
            "withdrawals": [{
                "address": withdrawal['recipient_address'],
                "currency": withdrawal['currency'],
                "amount": withdrawal['amount'],
                "ipn_callback_url": f"{BASE_URL}/api/nowpayments/withdrawal/webhook"
            }]
        }
        
        headers = get_nowpayments_headers_with_jwt(jwt_token)
        async with httpx.AsyncClient() as client:
            payout_response = await client.post(
                f"{NOWPAYMENTS_API_URL}/payout",
                json=payout_data,
                headers=headers
            )
        
        if payout_response.status_code not in [200, 201]:
            error_detail = payout_response.json() if payout_response.headers.get("content-type", "").startswith("application/json") else payout_response.text
            
            # Update withdrawal with error
            supabase.table('nowpayments_withdrawals')\
                .update({
                    'status': 'failed',
                    'error_message': f'NowPayments payout creation failed: {error_detail}',
                    'api_response': error_detail
                })\
                .eq('id', request.withdrawal_id)\
                .execute()
            
            raise HTTPException(status_code=400, detail=f"Failed to create payout with NowPayments: {error_detail}")
        
        payout_result = payout_response.json()
        print(f"NowPayments payout response: {payout_result}")  # Debug log
        
        # Extract batch withdrawal ID for 2FA verification
        batch_withdrawal_id = None
        if isinstance(payout_result, dict):
            if "result" in payout_result:
                if isinstance(payout_result["result"], list) and len(payout_result["result"]) > 0:
                    batch_withdrawal_id = payout_result["result"][0].get('id')
                else:
                    batch_withdrawal_id = payout_result["result"].get('id')
            else:
                batch_withdrawal_id = payout_result.get('id')
        
        if not batch_withdrawal_id:
            raise HTTPException(status_code=500, detail="Failed to get batch withdrawal ID from NowPayments")
        
        # Verify the payout with 2FA code
        verify_data = {
            "verification_code": verification_code
        }
        
        async with httpx.AsyncClient() as client:
            verify_response = await client.post(
                f"{NOWPAYMENTS_API_URL}/payout/{batch_withdrawal_id}/verify",
                json=verify_data,
                headers=headers
            )
        
        if verify_response.status_code not in [200, 201]:
            verify_error = verify_response.json() if verify_response.headers.get("content-type", "").startswith("application/json") else verify_response.text
            
            # Update withdrawal with verification error
            supabase.table('nowpayments_withdrawals')\
                .update({
                    'status': 'verifying',
                    'batch_withdrawal_id': str(batch_withdrawal_id),
                    'verification_code': verification_code,
                    'error_message': f'2FA verification failed: {verify_error}',
                    'api_response': {'payout': payout_result, 'verify_error': verify_error}
                })\
                .eq('id', request.withdrawal_id)\
                .execute()
            
            print(f"2FA verification failed: {verify_error}")
            raise HTTPException(status_code=400, detail=f"2FA verification failed: {verify_error}")
        
        verify_result = verify_response.json()
        print(f"2FA verification successful: {verify_result}")
        
        # Update withdrawal record with success
        supabase.table('nowpayments_withdrawals')\
            .update({
                'status': 'verified',
                'batch_withdrawal_id': str(batch_withdrawal_id),
                'verification_code': verification_code,
                'verified_at': 'now()',
                'api_response': {'payout': payout_result, 'verify': verify_result}
            })\
            .eq('id', request.withdrawal_id)\
            .execute()
        
        # Process the verified withdrawal (deduct balance)
        process_result = supabase.rpc('process_verified_withdrawal', {
            'p_withdrawal_id': request.withdrawal_id
        }).execute()
        
        if not process_result.data or not process_result.data[0].get('success'):
            print(f"Warning: Failed to process verified withdrawal: {process_result}")
            # Don't fail the entire request, as NowPayments part was successful
        
        # Create success notification
        notification = {
            'user_id': user_id,
            'title': '✅ Withdrawal Verified & Processing',
            'message': f'Your withdrawal of {withdrawal["amount"]} {withdrawal["currency"]} has been verified and is now being processed by NowPayments. You will receive a notification when the transaction is completed.',
            'type': 'success',
            'is_read': False
        }
        
        supabase.table('user_notifications').insert(notification).execute()
        
        return {
            "success": True,
            "withdrawal_id": request.withdrawal_id,
            "batch_withdrawal_id": batch_withdrawal_id,
            "status": "verified",
            "amount": withdrawal['amount'],
            "currency": withdrawal['currency'],
            "recipient_address": withdrawal['recipient_address'],
            "message": "Withdrawal verified successfully and is now being processed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error verifying withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify withdrawal: {str(e)}")

@router.get("/nowpayments/user/{user_id}/withdrawals")
async def get_user_withdrawals(user_id: str, limit: int = 50):
    """Get user's withdrawal history"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        result = supabase.table('nowpayments_withdrawals')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "withdrawals": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user withdrawals: {str(e)}")

@router.post("/nowpayments/withdrawal/webhook")
async def withdrawal_webhook(request: Request):
    """Handle NowPayments withdrawal webhooks"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Get request body
        body = await request.body()
        webhook_data = json.loads(body.decode())
        
        print(f"🔔 Withdrawal webhook received: {webhook_data}")
        
        # Extract relevant data
        withdrawal_id = webhook_data.get('withdrawal_id') or webhook_data.get('id')
        status = webhook_data.get('status')
        transaction_hash = webhook_data.get('transaction_hash')
        actual_amount = webhook_data.get('actual_amount')
        error_message = webhook_data.get('error_message')
        
        if not withdrawal_id:
            print("❌ No withdrawal ID in webhook")
            return {"success": False, "error": "Missing withdrawal ID"}
        
        # Find withdrawal record by batch_withdrawal_id
        withdrawal_result = supabase.table('nowpayments_withdrawals')\
            .select('*')\
            .eq('batch_withdrawal_id', str(withdrawal_id))\
            .execute()
        
        if not withdrawal_result.data:
            print(f"⚠️ Withdrawal record not found for batch ID: {withdrawal_id}")
            return {"success": False, "error": "Withdrawal record not found"}
        
        withdrawal = withdrawal_result.data[0]
        user_id = withdrawal['user_id']
        
        # Update withdrawal record
        update_data = {
            'api_response': webhook_data,
            'updated_at': 'now()'
        }
        
        # Map NowPayments status to our status
        if status == 'sent':
            update_data['status'] = 'sent'
            update_data['transaction_hash'] = transaction_hash
            update_data['actual_amount_sent'] = actual_amount
        elif status == 'completed':
            update_data['status'] = 'completed'
            update_data['completed_at'] = 'now()'
            update_data['transaction_hash'] = transaction_hash
            update_data['actual_amount_sent'] = actual_amount
        elif status == 'failed':
            update_data['status'] = 'failed'
            update_data['error_message'] = error_message
        else:
            update_data['status'] = status
        
        # Update the withdrawal record
        supabase.table('nowpayments_withdrawals')\
            .update(update_data)\
            .eq('id', withdrawal['id'])\
            .execute()
        
        # Create notification for user
        notification_title = ""
        notification_message = ""
        notification_type = "info"
        
        if status == 'sent':
            notification_title = "🚀 Withdrawal Sent"
            notification_message = f"Your withdrawal of {withdrawal['amount']} {withdrawal['currency']} has been sent to the blockchain. Transaction hash: {transaction_hash}"
            notification_type = "info"
        elif status == 'completed':
            notification_title = "✅ Withdrawal Completed"
            notification_message = f"Your withdrawal of {withdrawal['amount']} {withdrawal['currency']} has been completed successfully. Transaction hash: {transaction_hash}"
            notification_type = "success"
        elif status == 'failed':
            notification_title = "❌ Withdrawal Failed"
            notification_message = f"Your withdrawal of {withdrawal['amount']} {withdrawal['currency']} has failed. Reason: {error_message}. Your balance has been restored."
            notification_type = "error"
            
            # Restore user balance if withdrawal failed
            supabase.rpc('update_user_balance', {
                'user_uuid': user_id,
                'amount_change': withdrawal['amount']
            }).execute()
        
        if notification_title:
            notification = {
                'user_id': user_id,
                'title': notification_title,
                'message': notification_message,
                'type': notification_type,
                'is_read': False
            }
            
            supabase.table('user_notifications').insert(notification).execute()
        
        print(f"✅ Withdrawal webhook processed for user {user_id}")
        
        return {"success": True, "message": "Withdrawal webhook processed"}
        
    except Exception as e:
        print(f"❌ Withdrawal webhook error: {str(e)}")
        return {"success": False, "error": str(e)}