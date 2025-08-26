import os
import httpx
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional, List

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

class SupabaseHTTPClient:
    """Simple Supabase client using httpx (no Rust dependencies)"""
    
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def table(self, table_name: str):
        return SupabaseTable(self, table_name)

class SupabaseTable:
    """Simple table operations"""
    
    def __init__(self, client: SupabaseHTTPClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self.url = f"{client.url}/rest/v1/{table_name}"
    
    def select(self, columns: str = "*"):
        return SupabaseQuery(self, 'select', columns)
    
    def insert(self, data):
        return SupabaseQuery(self, 'insert', data)
    
    def update(self, data):
        return SupabaseQuery(self, 'update', data)
    
    def delete(self):
        return SupabaseQuery(self, 'delete', None)

class SupabaseQuery:
    """Query builder and executor"""
    
    def __init__(self, table: SupabaseTable, operation: str, data):
        self.table = table
        self.operation = operation
        self.data = data
        self.filters = []
    
    def eq(self, column: str, value):
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def neq(self, column: str, value):
        self.filters.append(f"{column}=neq.{value}")
        return self
    
    def gte(self, column: str, value):
        self.filters.append(f"{column}=gte.{value}")
        return self
    
    def lte(self, column: str, value):
        self.filters.append(f"{column}=lte.{value}")
        return self
    
    def like(self, column: str, value):
        self.filters.append(f"{column}=like.{value}")
        return self
    
    def order(self, column: str, desc: bool = False):
        order_dir = "desc" if desc else "asc"
        self.filters.append(f"order={column}.{order_dir}")
        return self
    
    def limit(self, count: int):
        self.filters.append(f"limit={count}")
        return self
    
    def execute(self):
        """Execute the query"""
        try:
            url = self.table.url
            if self.filters:
                url += "?" + "&".join(self.filters)
            
            with httpx.Client() as client:
                if self.operation == 'select':
                    response = client.get(url, headers=self.table.client.headers)
                elif self.operation == 'insert':
                    response = client.post(url, headers=self.table.client.headers, json=self.data)
                elif self.operation == 'update':
                    response = client.patch(url, headers=self.table.client.headers, json=self.data)
                elif self.operation == 'delete':
                    response = client.delete(url, headers=self.table.client.headers)
                else:
                    raise ValueError(f"Unsupported operation: {self.operation}")
                
                # Return response-like object
                result = SupabaseResponse()
                result.status_code = response.status_code
                
                if response.status_code >= 200 and response.status_code < 300:
                    try:
                        result.data = response.json()
                    except:
                        result.data = []
                else:
                    result.data = []
                    print(f"Supabase error: {response.status_code} - {response.text}")
                
                return result
                
        except Exception as e:
            print(f"Supabase request failed: {e}")
            result = SupabaseResponse()
            result.status_code = 500
            result.data = []
            return result

class SupabaseResponse:
    """Response object to mimic supabase library"""
    def __init__(self):
        self.data = []
        self.status_code = 200

# Initialize clients
if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = SupabaseHTTPClient(SUPABASE_URL, SUPABASE_ANON_KEY)
    print(f"✅ Supabase client initialized with URL: {SUPABASE_URL}")
else:
    supabase = None
    print("Warning: Supabase credentials not found")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_ANON_KEY: {'Present' if SUPABASE_ANON_KEY else 'Missing'}")

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase_admin = SupabaseHTTPClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    print(f"✅ Supabase admin client initialized")
else:
    supabase_admin = None
    print("Warning: Supabase admin credentials not found")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'Present' if SUPABASE_SERVICE_ROLE_KEY else 'Missing'}")

# Add RPC support
class SupabaseRPC:
    def __init__(self, client: SupabaseHTTPClient):
        self.client = client
    
    def rpc(self, function_name: str, params: dict = None):
        return SupabaseRPCQuery(self.client, function_name, params)

class SupabaseRPCQuery:
    def __init__(self, client: SupabaseHTTPClient, function_name: str, params: dict = None):
        self.client = client
        self.function_name = function_name
        self.params = params or {}
    
    def execute(self):
        try:
            url = f"{self.client.url}/rest/v1/rpc/{self.function_name}"
            
            with httpx.Client() as client:
                response = client.post(url, headers=self.client.headers, json=self.params)
                
                result = SupabaseResponse()
                result.status_code = response.status_code
                
                if response.status_code >= 200 and response.status_code < 300:
                    try:
                        result.data = response.json()
                    except:
                        result.data = []
                else:
                    result.data = []
                    print(f"Supabase RPC error: {response.status_code} - {response.text}")
                
                return result
                
        except Exception as e:
            print(f"Supabase RPC request failed: {e}")
            result = SupabaseResponse()
            result.status_code = 500
            result.data = []
            return result

# Add Admin Auth functionality
class SupabaseAdminAuth:
    def __init__(self, client: SupabaseHTTPClient):
        self.client = client
    
    def delete_user(self, user_id: str):
        """Delete user from auth.users using admin API"""
        try:
            url = f"{self.client.url}/auth/v1/admin/users/{user_id}"
            
            with httpx.Client() as http_client:
                response = http_client.delete(url, headers=self.client.headers)
                
                if response.status_code in [200, 204]:
                    print(f"✅ User {user_id} deleted from auth.users successfully")
                    return True
                else:
                    print(f"❌ Failed to delete user from auth.users: HTTP {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error deleting user from auth.users: {e}")
            return False

class SupabaseAuth:
    def __init__(self, client: SupabaseHTTPClient):
        self.client = client
        self.admin = SupabaseAdminAuth(client)

# Add auth to admin client
if supabase_admin:
    supabase_admin.auth = SupabaseAuth(supabase_admin)

# Add RPC method to main clients
if supabase:
    supabase.rpc = lambda function_name, params=None: SupabaseRPCQuery(supabase, function_name, params)
if supabase_admin:
    supabase_admin.rpc = lambda function_name, params=None: SupabaseRPCQuery(supabase_admin, function_name, params)