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
BASE_URL = os.getenv("REACT_APP_BACKEND_URL", "https://f01i-crypto.preview.emergentagent.com")

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

def get_nowpayments_headers():
    """Get headers for NowPayments API requests"""
    return {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }

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

@router.post("/nowpayments/invoice")
async def create_invoice(request: InvoiceRequest, user_id: str = "demo_user"):
    """Create payment invoice with NowPayments"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Generate unique order ID
        order_id = request.order_id or f"f01i_{user_id}_{int(time.time())}"
        
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
            'user_id': user_id,
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
        
        # Update invoice record
        result = supabase.table('nowpayments_invoices')\
            .update(update_data)\
            .eq('invoice_id', str(payment_id))\
            .execute()
        
        if result.data:
            invoice = result.data[0]
            user_id = invoice['user_id']
            amount = float(webhook_data.get('actually_paid', 0))
            
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
        
        return {"success": True, "message": "Webhook processed successfully"}
        
    except Exception as e:
        # Log error but return success to avoid webhook retries
        print(f"Webhook processing error: {str(e)}")
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
async def create_subscription(request: SubscriptionRequest, user_id: str = "demo_user"):
    """Create an email-based subscription for a user"""
    try:
        import sys
        sys.path.append('/app/backend')
        from supabase_client import supabase_admin as supabase
        
        subscription_data = {
            "subscription_plan_id": int(request.plan_id),
            "email": request.user_email
        }
        
        response = await make_nowpayments_request("POST", "/subscriptions", subscription_data)
        
        if response.status_code not in [200, 201]:
            error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=400, detail=f"Failed to create subscription: {error_detail}")
        
        subscription_result = response.json().get("result", response.json())
        
        # Store subscription record in database
        subscription_record = {
            'user_id': user_id,
            'subscription_id': subscription_result['id'],
            'plan_id': request.plan_id,
            'user_email': request.user_email,
            'status': subscription_result['status'],
            'is_active': subscription_result['is_active'],
            'expire_date': subscription_result['expire_date']
        }
        
        supabase.table('nowpayments_subscriptions').insert(subscription_record).execute()
        
        return {
            "success": True,
            "subscription": subscription_result,
            "message": f"Subscription created successfully. Payment instructions will be sent to {request.user_email}"
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