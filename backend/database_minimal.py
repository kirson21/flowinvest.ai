# Alternative database client - no Rust dependencies
import os

# Try to use standard supabase client, fallback to minimal client
try:
    from .supabase_client import supabase, supabase_admin
    print("Using standard Supabase client")
except ImportError:
    try:
        from .minimal_supabase import supabase, supabase_admin
        print("Using minimal Supabase client (no Rust dependencies)")
    except ImportError:
        # Ultimate fallback
        supabase = None
        supabase_admin = None
        print("Warning: No Supabase client available")

__all__ = ['supabase', 'supabase_admin']