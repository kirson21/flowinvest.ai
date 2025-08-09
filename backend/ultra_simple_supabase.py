"""
Ultra-simple Supabase client using only requests
No additional dependencies, no Rust compilation
"""
import requests
import json
import os
from typing import Dict, Any, Optional, List

class UltraSimpleSupabase:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def table(self, name: str):
        return SimpleTable(self, name)

class SimpleTable:
    def __init__(self, client: UltraSimpleSupabase, table_name: str):
        self.client = client
        self.table_name = table_name
        self.base_url = f"{client.url}/rest/v1/{table_name}"
    
    def select(self, columns: str = "*"):
        return SimpleQuery(self, "select", {"select": columns})
    
    def insert(self, data: Dict[str, Any]):
        return SimpleQuery(self, "insert", data)
    
    def update(self, data: Dict[str, Any]):
        return SimpleQuery(self, "update", data)
    
    def delete(self):
        return SimpleQuery(self, "delete", {})

class SimpleQuery:
    def __init__(self, table: SimpleTable, operation: str, data: Any):
        self.table = table
        self.operation = operation
        self.data = data
        self.filters = []
    
    def eq(self, column: str, value: Any):
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def order(self, column: str, desc: bool = False):
        direction = "desc" if desc else "asc"
        self.filters.append(f"order={column}.{direction}")
        return self
    
    def limit(self, count: int):
        self.filters.append(f"limit={count}")
        return self
    
    def single(self):
        self.filters.append("limit=1")
        return self
    
    def execute(self):
        url = self.table.base_url
        if self.filters:
            url += "?" + "&".join(self.filters)
        
        headers = self.table.client.headers
        
        try:
            if self.operation == "select":
                response = requests.get(url, headers=headers, timeout=30)
            elif self.operation == "insert":
                response = requests.post(url, headers=headers, json=self.data, timeout=30)
            elif self.operation == "update":
                response = requests.patch(url, headers=headers, json=self.data, timeout=30)
            elif self.operation == "delete":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            response.raise_for_status()
            
            # Return response in expected format
            data = response.json() if response.content else []
            
            # Handle single record queries
            if "limit=1" in self.filters and data:
                data = data[0] if isinstance(data, list) else data
            
            return SimpleResponse(data, None)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            return SimpleResponse(None, error_msg)
        except Exception as e:
            return SimpleResponse(None, str(e))

class SimpleResponse:
    def __init__(self, data: Any, error: Optional[str]):
        self.data = data
        self.error = error

# Create client instances
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") 
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = UltraSimpleSupabase(SUPABASE_URL, SUPABASE_ANON_KEY)
else:
    supabase = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase_admin = UltraSimpleSupabase(SUPABASE_URL, SUPABASE_SERVICE_KEY)
else:
    supabase_admin = None