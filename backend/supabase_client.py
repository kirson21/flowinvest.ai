import os
import httpx
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional, List

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

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
    
    def order(self, column: str, ascending: bool = True):
        order_dir = "asc" if ascending else "desc"
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
else:
    supabase = None
    print("Warning: Supabase credentials not found")

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase_admin = SupabaseHTTPClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
else:
    supabase_admin = None
    print("Warning: Supabase admin credentials not found")