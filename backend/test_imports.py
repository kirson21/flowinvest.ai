#!/usr/bin/env python3
"""Test imports to identify cgi module issue"""

print("Testing imports...")

try:
    print("✅ Testing basic imports...")
    import sys
    import os
    import logging
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python executable: {sys.executable}")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")

try:
    print("✅ Testing FastAPI imports...")
    from fastapi import FastAPI, APIRouter
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ FastAPI imports successful")
except Exception as e:
    print(f"❌ FastAPI imports failed: {e}")

try:
    print("✅ Testing dotenv imports...")
    from dotenv import load_dotenv
    from pathlib import Path
    print("✅ Dotenv imports successful")
except Exception as e:
    print(f"❌ Dotenv imports failed: {e}")

try:
    print("✅ Testing supabase client...")
    from supabase_client import supabase, supabase_admin
    print("✅ Supabase client imports successful")
except Exception as e:
    print(f"❌ Supabase client imports failed: {e}")

try:
    print("✅ Testing route imports...")
    from routes import auth
    print("✅ Auth routes import successful")
except Exception as e:
    print(f"❌ Auth routes import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("✅ Testing other route imports...")
    from routes import webhook, verification, ai_bots
    print("✅ Other routes imports successful")
except Exception as e:
    print(f"❌ Other routes imports failed: {e}")
    import traceback
    traceback.print_exc()

print("Import testing complete!")