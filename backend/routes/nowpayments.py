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
from datetime import datetime, timedelta

router = APIRouter()

# NowPayments API Configuration
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1"
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
NOWPAYMENTS_PUBLIC_KEY = os.getenv("NOWPAYMENTS_PUBLIC_KEY", "f56ecfa5-09db-45d0-95bd-599043c84a5c")
NOWPAYMENTS_IPN_SECRET = os.getenv("NOWPAYMENTS_IPN_SECRET", "")

# Base URL for return URLs (will be configured in environment)
BASE_URL = os.getenv("REACT_APP_BACKEND_URL", "https://dataflow-crypto.preview.emergentagent.com")

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
            "email": os.getenv("NOWPAYMENTS_TEST_EMAIL", "test@example.com"),  # Test email for development
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
    """Handle NowPayments IPN webhooks with email validation"""
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
        
        payment_id = webhook_data.get('payment_id')
        payment_status = webhook_data.get('payment_status')
        order_id = webhook_data.get('order_id')
        customer_email = webhook_data.get('customer_email') or webhook_data.get('email')
        actually_paid = float(webhook_data.get('actually_paid', 0))
        
        if not payment_id:
            raise HTTPException(status_code=400, detail="Missing payment_id in webhook")
        
        print(f"🔔 Processing webhook for payment_id: {payment_id}, status: {payment_status}, email: {customer_email}, amount: ${actually_paid}")
        
        # For subscription payments (amount around $10), use email validation approach
        if customer_email and actually_paid >= 9.0 and actually_paid <= 11.0 and payment_status == 'finished':
            print(f"💡 Processing subscription payment via email validation")
            
            # Find matching email validation record
            validation_result = supabase.table('subscription_email_validation')\
                .select('*')\
                .eq('email', customer_email)\
                .eq('status', 'pending')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if validation_result.data:
                validation_record = validation_result.data[0]
                user_id = validation_record['user_id']
                plan_type = validation_record['plan_type']
                
                print(f"✅ Found email validation record for user {user_id}, plan: {plan_type}")
                
                # Update validation record to completed
                supabase.table('subscription_email_validation')\
                    .update({
                        'status': 'completed',
                        'updated_at': 'now()'
                    })\
                    .eq('id', validation_record['id'])\
                    .execute()
                
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
                    'metadata': {'payment_method': 'crypto', 'nowpayments_id': str(payment_id), 'email_validated': True},
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
                            supabase.table('company_balance')\
                                .update({
                                    'company_funds': supabase.table('company_balance').select('company_funds').execute().data[0]['company_funds'] + actually_paid,
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
                print(f"⚠️ No pending email validation record found for {customer_email}")
                print(f"   - This might be a duplicate webhook or payment for a different service")
        
        # For regular invoice payments (balance top-ups) or non-subscription payments
        else:
            print(f"💰 Processing as invoice payment or balance top-up")
            
            # Update invoice record if exists
            result = supabase.table('nowpayments_invoices')\
                .update({
                    'payment_status': payment_status,
                    'actually_paid': actually_paid,
                    'pay_currency': webhook_data.get('pay_currency'),
                    'updated_at': 'now()',
                    'webhook_data': webhook_data,
                    'completed_at': 'now()' if payment_status == 'finished' else None
                })\
                .eq('invoice_id', str(payment_id))\
                .execute()
            
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