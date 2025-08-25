#!/usr/bin/env python3
"""
NowPayments Webhook Processing Verification Test
Verify that webhook processing correctly handles both subscription and invoice payments
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://dataflow-crypto.preview.emergentagent.com/api"
TEST_USER_ID = "cd0e9717-f85d-4726-81e9-f260394ead58"
TEST_EMAIL = "kirillpopolitov@gmail.com"

def test_webhook_subscription_processing():
    """Test webhook processing for subscription payments"""
    print("🔔 Testing Subscription Payment Webhook Processing")
    
    # Create a subscription first
    subscription_data = {
        "plan_id": "plan_plus",
        "user_email": TEST_EMAIL
    }
    
    response = requests.post(
        f"{BACKEND_URL}/nowpayments/subscription",
        json=subscription_data,
        params={"user_id": TEST_USER_ID},
        timeout=20
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create subscription: {response.text}")
        return False
    
    data = response.json()
    subscription = data.get('subscription', {})
    subscription_id = subscription.get('id')
    
    if not subscription_id:
        print("❌ No subscription ID returned")
        return False
    
    print(f"✅ Created subscription: {subscription_id}")
    
    # Simulate subscription payment webhook
    webhook_data = {
        "payment_id": str(subscription_id),
        "payment_status": "finished",
        "order_id": f"subscription_{subscription_id}",
        "actually_paid": 10.0,
        "pay_currency": "usdttrc20",
        "customer_email": TEST_EMAIL
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-nowpayments-sig": "test_signature"
    }
    
    webhook_response = requests.post(
        f"{BACKEND_URL}/nowpayments/webhook",
        json=webhook_data,
        headers=headers,
        timeout=15
    )
    
    if webhook_response.status_code == 200:
        webhook_result = webhook_response.json()
        success = webhook_result.get('success', False)
        print(f"✅ Subscription webhook processed: {success}")
        return success
    else:
        print(f"❌ Webhook processing failed: {webhook_response.text}")
        return False

def test_webhook_invoice_processing():
    """Test webhook processing for invoice payments"""
    print("💰 Testing Invoice Payment Webhook Processing")
    
    # Create an invoice first
    invoice_data = {
        "amount": 50.0,
        "currency": "usd",
        "pay_currency": "usdttrc20",
        "description": "Test invoice for webhook",
        "user_email": TEST_EMAIL
    }
    
    response = requests.post(
        f"{BACKEND_URL}/nowpayments/invoice",
        json=invoice_data,
        params={"user_id": TEST_USER_ID},
        timeout=15
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create invoice: {response.text}")
        return False
    
    data = response.json()
    invoice_id = data.get('invoice_id')
    order_id = data.get('order_id')
    
    if not invoice_id:
        print("❌ No invoice ID returned")
        return False
    
    print(f"✅ Created invoice: {invoice_id}")
    
    # Simulate invoice payment webhook
    webhook_data = {
        "payment_id": str(invoice_id),
        "payment_status": "finished",
        "order_id": order_id,
        "actually_paid": 50.0,
        "pay_currency": "usdttrc20",
        "customer_email": TEST_EMAIL
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-nowpayments-sig": "test_signature"
    }
    
    webhook_response = requests.post(
        f"{BACKEND_URL}/nowpayments/webhook",
        json=webhook_data,
        headers=headers,
        timeout=15
    )
    
    if webhook_response.status_code == 200:
        webhook_result = webhook_response.json()
        success = webhook_result.get('success', False)
        print(f"✅ Invoice webhook processed: {success}")
        return success
    else:
        print(f"❌ Webhook processing failed: {webhook_response.text}")
        return False

def main():
    """Main test execution"""
    print("=" * 80)
    print("🔔 NOWPAYMENTS WEBHOOK PROCESSING VERIFICATION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Test Email: {TEST_EMAIL}")
    print("=" * 80)
    print()
    
    # Test subscription webhook processing
    subscription_success = test_webhook_subscription_processing()
    print()
    
    # Test invoice webhook processing  
    invoice_success = test_webhook_invoice_processing()
    print()
    
    # Summary
    print("=" * 80)
    print("📊 WEBHOOK VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Subscription Webhook: {'✅ PASS' if subscription_success else '❌ FAIL'}")
    print(f"Invoice Webhook: {'✅ PASS' if invoice_success else '❌ FAIL'}")
    
    if subscription_success and invoice_success:
        print("✅ All webhook processing tests passed!")
        return 0
    else:
        print("❌ Some webhook processing tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())