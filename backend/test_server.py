#!/usr/bin/env python3
"""Test server startup to diagnose issues"""

print("=== TESTING SERVER STARTUP ===")

try:
    print("1. Testing CGI compatibility...")
    import cgi_compat
    print("✅ CGI compatibility loaded")
except Exception as e:
    print(f"❌ CGI compatibility failed: {e}")

try:
    print("2. Testing server imports...")
    import server
    print("✅ Server module imported successfully")
except Exception as e:
    print(f"❌ Server import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("3. Testing FastAPI app...")
    from server import app
    print("✅ FastAPI app created successfully")
    print(f"   App title: {app.title}")
    print(f"   App version: {app.version}")
except Exception as e:
    print(f"❌ FastAPI app failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("4. Testing route loading...")
    from server import api_router
    print(f"✅ API router loaded with {len(api_router.routes)} routes")
    for route in api_router.routes[:5]:  # Show first 5 routes
        print(f"   {route.methods} {route.path}")
    if len(api_router.routes) > 5:
        print(f"   ... and {len(api_router.routes) - 5} more routes")
except Exception as e:
    print(f"❌ Route loading failed: {e}")
    import traceback
    traceback.print_exc()

print("=== SERVER STARTUP TEST COMPLETE ===")