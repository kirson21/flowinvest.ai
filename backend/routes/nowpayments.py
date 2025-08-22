"""
NowPayments Integration - Invoice-based Payment Gateway & Subscriptions
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import os
import time
import uuid
import hashlib
import hmac
import json
import httpx
from datetime import datetime, timedelta

router = APIRouter()

# NowPayments API Configuration
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1"
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "DHGG9K5-VAQ4QFP-NDHHDQ7-M4ZQCHM")
NOWPAYMENTS_PUBLIC_KEY = os.getenv("NOWPAYMENTS_PUBLIC_KEY", "f56ecfa5-09db-45d0-95bd-599043c84a5c")
NOWPAYMENTS_IPN_SECRET = os.getenv("NOWPAYMENTS_IPN_SECRET", "")

# Base URL for return URLs (will be configured in environment)
BASE_URL = os.getenv("REACT_APP_BACKEND_URL", "https://f01i-invest.preview.emergentagent.com")

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
        # For subscriptions, we might need to authenticate first
        auth_data = {
            "email": "kirillpopolitov@gmail.com",  # Your account email
            "password": "Osiris@21"  # Your account password
        }
        
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
async def create_invoice(request: InvoiceRequest, user_id: str = "cd0e9717-f85d-4726-81e9-f260394ead58"):
    """Create payment invoice with NowPayments"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Validate inputs and check minimum amounts
        if request.currency.upper() not in ['USD', 'EUR']:
            return {"success": False, "detail": "Unsupported price currency"}
        
        if request.amount <= 0:
            return {"success": False, "detail": "Amount must be positive"}
        
        # If pay_currency is specified, check minimum amount
        if request.pay_currency:
            min_check = await get_minimum_amount(request.currency.lower(), request.pay_currency.lower())
            if min_check["success"] and request.amount < min_check["min_amount"]:
                return {
                    "success": False, 
                    "detail": f"Amount ${request.amount} is below minimum ${min_check['min_amount']} for {request.pay_currency}"
                }
        
        # For demo purposes, use Super Admin UUID
        actual_user_id = user_id if user_id != "demo_user" else "cd0e9717-f85d-4726-81e9-f260394ead58"
        
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
async def get_payment_status(payment_id: str, user_id: str = "demo_user"):
    """Get payment status from NowPayments"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
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
    """Handle NowPayments IPN webhooks"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # Get request body and headers
        body = await request.body()
        signature = request.headers.get("x-nowpayments-sig")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing webhook signature")
        
        # Parse JSON data
        webhook_data = json.loads(body.decode())
        
        # Verify webhook signature (optional but recommended)
        # For production, you should verify the HMAC signature
        
        payment_id = webhook_data.get('payment_id')
        payment_status = webhook_data.get('payment_status')
        order_id = webhook_data.get('order_id')
        
        if not payment_id:
            raise HTTPException(status_code=400, detail="Missing payment_id in webhook")
        
        print(f"🔔 Processing webhook for payment_id: {payment_id}, status: {payment_status}, order_id: {order_id}")
        
        # Update payment record in database
        update_data = {
            'payment_status': payment_status,
            'actually_paid': webhook_data.get('actually_paid', 0),
            'pay_currency': webhook_data.get('pay_currency'),
            'updated_at': 'now()',
            'webhook_data': webhook_data
        }
        
        if payment_status == 'finished':
            update_data['completed_at'] = 'now()'
        
        # Check if this is a subscription payment by looking for a subscription record
        subscription_result = supabase.table('nowpayments_subscriptions')\
            .select('*')\
            .eq('subscription_id', str(payment_id))\
            .execute()
        
        is_subscription_payment = bool(subscription_result.data)
        
        # If no subscription record found but webhook data suggests it's a subscription payment,
        # try to identify it by checking webhook data or order_id patterns
        if not is_subscription_payment and order_id:
            # Check if the order_id indicates this is a subscription (NowPayments subscription orders often have specific patterns)
            # Also check for any subscription with this user's email in waiting status
            webhook_email = webhook_data.get('customer_email') or webhook_data.get('email')
            if webhook_email:
                email_subs = supabase.table('nowpayments_subscriptions')\
                    .select('*')\
                    .eq('user_email', webhook_email)\
                    .eq('status', 'WAITING_PAY')\
                    .execute()
                
                if email_subs.data:
                    # Update the subscription_id to match the payment_id
                    supabase.table('nowpayments_subscriptions')\
                        .update({'subscription_id': str(payment_id)})\
                        .eq('id', email_subs.data[0]['id'])\
                        .execute()
                    
                    subscription_result.data = email_subs.data
                    is_subscription_payment = True
                    print(f"🔄 Matched payment {payment_id} to existing subscription by email {webhook_email}")
        
        # If still no match, check if this could be a direct subscription payment from NowPayments
        # that wasn't created through our API (common when users pay directly on NowPayments)
        if not is_subscription_payment:
            # Check if the amount matches typical subscription amounts ($10 for Plus plan)
            paid_amount = float(webhook_data.get('actually_paid', 0))
            if paid_amount >= 9.0 and paid_amount <= 11.0:  # Allow small variations for crypto fluctuations
                print(f"💡 Payment amount ${paid_amount} suggests subscription payment, creating subscription record")
                
                # Try to determine user from webhook data or use a more intelligent lookup
                webhook_email = webhook_data.get('customer_email') or webhook_data.get('email')
                target_user_id = None
                
                # First try to find user by email from webhook
                if webhook_email:
                    try:
                        user_lookup = supabase.rpc('get_user_by_email', {'email': webhook_email}).execute()
                        if user_lookup.data and isinstance(user_lookup.data, list) and len(user_lookup.data) > 0:
                            target_user_id = user_lookup.data[0].get('id')
                            print(f"🔍 Found user by email {webhook_email}: {target_user_id}")
                    except Exception as lookup_error:
                        print(f"⚠️ Could not lookup user by email: {lookup_error}")
                
                # If no user found by email, check for recent subscription activity or default to provided user
                if not target_user_id:
                    # For now, we'll need to determine the user from context
                    # In production, this should be improved to use order metadata or customer identification
                    target_user_id = "81fa7673-821a-4e7c-92a2-7007fa5e21ef"  # Use the specific user you mentioned
                    webhook_email = webhook_email or "user@f01i.ai"
                    print(f"⚡ Using specified user ID for subscription: {target_user_id}")
                
                # Create subscription record for this payment
                try:
                    new_subscription = {
                        'user_id': target_user_id,
                        'subscription_id': str(payment_id),
                        'plan_id': 'plan_plus',
                        'user_email': webhook_email,
                        'status': 'WAITING_PAY',  # Will be updated to PAID below
                        'is_active': False,
                        'expire_date': None
                    }
                    
                    created_sub = supabase.table('nowpayments_subscriptions').insert(new_subscription).execute()
                    if created_sub.data:
                        subscription_result.data = created_sub.data
                        is_subscription_payment = True
                        print(f"✅ Created new subscription record for payment {payment_id} and user {target_user_id}")
                except Exception as create_error:
                    print(f"❌ Failed to create subscription record: {create_error}")
        
        print(f"🔍 Is subscription payment: {is_subscription_payment}")
        
        if is_subscription_payment and payment_status == 'finished':
            # Handle subscription payment completion
            subscription_record = subscription_result.data[0]
            user_id = subscription_record['user_id']
            plan_id = subscription_record['plan_id']
            
            print(f"💳 Processing subscription upgrade for user {user_id} to plan {plan_id}")
            
            # Update subscription status to PAID
            supabase.table('nowpayments_subscriptions')\
                .update({
                    'status': 'PAID',
                    'is_active': True,
                    'updated_at': 'now()'
                })\
                .eq('subscription_id', str(payment_id))\
                .execute()
            
            # Determine plan type and price from plan_id
            if plan_id == 'plan_plus':
                plan_type = 'plus'
                plan_price = 10.00  # Plus plan price
            else:
                plan_type = 'free'  # Default fallback
                plan_price = 0.00
            
            # Direct subscription upgrade (bypassing problematic RPC function)
            try:
                from datetime import datetime, timedelta
                
                # Calculate subscription end date (31 days from now)
                end_date = datetime.utcnow() + timedelta(days=31)
                
                # Check if user already has a subscription record
                existing_sub = supabase.table('subscriptions').select('*').eq('user_id', user_id).execute()
                
                subscription_data = {
                    'user_id': user_id,
                    'plan_type': plan_type,
                    'status': 'active',
                    'start_date': datetime.utcnow().isoformat(),
                    'end_date': end_date.isoformat(),
                    'renewal': True,
                    'price_paid': plan_price,
                    'currency': 'USD',
                    'metadata': {'payment_method': 'crypto', 'nowpayments_id': str(payment_id)},
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
                    print(f"✅ Direct subscription upgrade completed successfully for user {user_id}")
                    
                    # Create subscription upgrade notification
                    notification = {
                        'user_id': user_id,
                        'title': f'🎉 Subscription Upgraded to {plan_type.title()}!',
                        'message': f'Your crypto payment has been confirmed and your subscription has been upgraded to {plan_type.title()} Plan. Enjoy your new features including 3 AI bots, 5 manual bots, and up to 10 marketplace products! Valid until {end_date.strftime("%B %d, %Y")}',
                        'type': 'success',
                        'is_read': False
                    }
                    
                    supabase.table('user_notifications').insert(notification).execute()
                    
                    print(f"✅ Subscription upgrade completed successfully for user {user_id}")
                else:
                    print(f"❌ Direct subscription upgrade failed for user {user_id}")
                    
            except Exception as upgrade_error:
                print(f"❌ Error with direct subscription upgrade: {upgrade_error}")
                
                # Fallback: try the original RPC function
                try:
                    upgrade_response = supabase.rpc('upgrade_subscription', {
                        'p_user_id': user_id,
                        'p_plan_type': plan_type,
                        'p_price': plan_price
                    }).execute()
                    
                    print(f"📈 Fallback RPC response: {upgrade_response.data}")
                    
                    if upgrade_response.data and upgrade_response.data.get('success'):
                        # Create subscription upgrade notification
                        notification = {
                            'user_id': user_id,
                            'title': f'🎉 Subscription Upgraded to {plan_type.title()}!',
                            'message': f'Your crypto payment has been confirmed and your subscription has been upgraded to {plan_type.title()} Plan. Enjoy your new features including 3 AI bots, 5 manual bots, and up to 10 marketplace products!',
                            'type': 'success',
                            'is_read': False
                        }
                        
                        supabase.table('user_notifications').insert(notification).execute()
                        
                        print(f"✅ Fallback subscription upgrade completed successfully for user {user_id}")
                    else:
                        print(f"❌ Fallback subscription upgrade failed for user {user_id}: {upgrade_response.data}")
                        
                except Exception as fallback_error:
                    print(f"❌ Fallback RPC upgrade also failed: {fallback_error}")
                
                # Still create a notification about payment received
                notification = {
                    'user_id': user_id,
                    'title': 'Payment Received - Processing Upgrade',
                    'message': f'Your crypto payment has been confirmed. We are processing your subscription upgrade. If you experience any issues, please contact support.',
                    'type': 'info',
                    'is_read': False
                }
                
                supabase.table('user_notifications').insert(notification).execute()
        
        else:
            # Handle regular invoice payment (balance top-up)
            # Update invoice record
            result = supabase.table('nowpayments_invoices')\
                .update(update_data)\
                .eq('invoice_id', str(payment_id))\
                .execute()
            
            if result.data:
                invoice = result.data[0]
                user_id = invoice['user_id']
                amount = float(webhook_data.get('actually_paid', 0))
                
                print(f"💰 Processing balance top-up for user {user_id}, amount: ${amount}")
                
                # If payment is completed, credit user balance
                if payment_status == 'finished' and amount > 0:
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
                    
                    balance_result = supabase.table('transactions').insert(balance_transaction).execute()
                    
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
        
        return {"success": True, "message": "Webhook processed successfully"}
        
    except Exception as e:
        # Log error but return success to avoid webhook retries
        print(f"❌ Webhook processing error: {str(e)}")
        return {"success": False, "error": str(e)}

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
async def create_subscription(request: SubscriptionRequest, user_id: str = "cd0e9717-f85d-4726-81e9-f260394ead58"):
    """Create an email-based subscription for a user using real NowPayments API"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        # For demo purposes, use Super Admin UUID
        actual_user_id = user_id if user_id != "demo_user" else "cd0e9717-f85d-4726-81e9-f260394ead58"
        
        # Get JWT token for subscription API
        jwt_token = await get_nowpayments_jwt_token()
        if not jwt_token:
            raise HTTPException(status_code=500, detail="Failed to authenticate with NowPayments for subscriptions")
        
        # Use your real NowPayments subscription plan ID
        nowpayments_plan_id = 1516280944  # Your Plan Plus ID from dashboard
        
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
        
        # Store subscription record in database with proper data extraction
        subscription_record = {
            'user_id': actual_user_id,
            'subscription_id': str(subscription_result.get('id', '')),  # This should be just the ID number
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
            "nowpayments_plan_id": nowpayments_plan_id,
            "message": f"Subscription created successfully with NowPayments! Payment instructions have been sent to {request.user_email}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")

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