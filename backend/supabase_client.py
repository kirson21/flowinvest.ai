import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

class SimpleSupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
    
    def table(self, name: str):
        return SimpleTable(self, name)
    
    def auth(self):
        return SimpleAuth(self)

class SimpleTable:
    def __init__(self, client: SimpleSupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self.base_url = f"{client.url}/rest/v1/{table_name}"
        self._filters = []
    
    def select(self, columns: str = "*"):
        self._operation = "select"
        self._select_columns = columns
        return self
    
    def insert(self, data):
        self._operation = "insert"
        self._data = data
        return self
    
    def update(self, data):
        self._operation = "update"  
        self._data = data
        return self
    
    def eq(self, column: str, value):
        self._filters.append(f"{column}=eq.{value}")
        return self
    
    def execute(self):
        try:
            url = self.base_url
            if self._filters:
                url += "?" + "&".join(self._filters)
            
            if hasattr(self, '_operation'):
                if self._operation == "select":
                    response = httpx.get(url, headers=self.client.headers, timeout=30)
                elif self._operation == "insert":
                    response = httpx.post(url, headers=self.client.headers, json=self._data, timeout=30)
                elif self._operation == "update":
                    response = httpx.patch(url, headers=self.client.headers, json=self._data, timeout=30)
                
                if response.status_code in [200, 201]:
                    return SimpleResponse(response.json() if response.content else [], None)
                else:
                    return SimpleResponse(None, f"HTTP {response.status_code}: {response.text}")
            else:
                return SimpleResponse([], None)
        except Exception as e:
            return SimpleResponse(None, str(e))

class SimpleAuth:
    def __init__(self, client):
        self.client = client
    
    def sign_up(self, email: str, password: str):
        try:
            url = f"{self.client.url}/auth/v1/signup"
            data = {"email": email, "password": password}
            response = httpx.post(url, headers=self.client.headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                return SimpleResponse(response.json(), None)
            else:
                return SimpleResponse(None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return SimpleResponse(None, str(e))
    
    def sign_in_with_password(self, email: str, password: str):
        try:
            url = f"{self.client.url}/auth/v1/token?grant_type=password"
            data = {"email": email, "password": password}
            response = httpx.post(url, headers=self.client.headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return SimpleResponse(response.json(), None)
            else:
                return SimpleResponse(None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return SimpleResponse(None, str(e))

class SimpleResponse:
    def __init__(self, data, error):
        self.data = data
        self.error = error

# Create clients using the simple implementation
if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = SimpleSupabaseClient(SUPABASE_URL, SUPABASE_ANON_KEY)
    supabase_admin = SimpleSupabaseClient(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY)
else:
    supabase = None
    supabase_admin = None

# Database connection helper
class SupabaseConnection:
    def __init__(self, use_service_key=False):
        self.client = supabase_admin if use_service_key else supabase
    
    def __enter__(self):
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Supabase client doesn't need explicit closing
        pass

# Helper functions for common operations
async def get_user_by_id(user_id: str):
    """Get user profile from Supabase"""
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

async def create_user_profile(user_id: str, email: str, full_name: str = None):
    """Create user profile in Supabase"""
    try:
        user_data = {
            'id': user_id,
            'email': email,
            'full_name': full_name
        }
        response = supabase.table('users').insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating user profile: {e}")
        return None

async def get_user_bots(user_id: str, include_prebuilt: bool = True):
    """Get user's bots and optionally include prebuilt bots"""
    try:
        query = supabase.table('bots').select('*')
        
        if include_prebuilt:
            query = query.or_(f'user_id.eq.{user_id},is_prebuilt.eq.true')
        else:
            query = query.eq('user_id', user_id)
        
        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error getting user bots: {e}")
        return []

async def get_user_portfolios(user_id: str):
    """Get user's portfolios with assets"""
    try:
        # Get portfolios
        portfolios_response = supabase.table('portfolios').select('*').eq('user_id', user_id).execute()
        portfolios = portfolios_response.data
        
        # Get assets for each portfolio
        for portfolio in portfolios:
            assets_response = supabase.table('portfolio_assets').select('*').eq('portfolio_id', portfolio['id']).execute()
            portfolio['assets'] = assets_response.data
        
        return portfolios
    except Exception as e:
        print(f"Error getting user portfolios: {e}")
        return []

async def get_news_feed(language: str = 'en', limit: int = 20):
    """Get news feed with optional translation"""
    try:
        if language == 'en':
            # Get original English news
            response = supabase.table('news_feed').select('*').order('published_at', desc=True).limit(limit).execute()
            return response.data
        else:
            # Get translated news with proper query syntax
            query = """
                *,
                translations!inner(
                    title_translated,
                    summary_translated
                )
            """
            response = supabase.table('news_feed').select(query).eq('translations.language', language).order('published_at', desc=True).limit(limit).execute()
            
            # Transform data to include translated content
            for item in response.data:
                if item.get('translations'):
                    translation = item['translations'][0]
                    item['title'] = translation['title_translated']
                    item['summary'] = translation['summary_translated']
                    item['is_translated'] = True
                    del item['translations']
            
            return response.data
    except Exception as e:
        print(f"Error getting news feed: {e}")
        return []

async def store_api_key(user_id: str, exchange: str, name: str, api_key: str, api_secret: str, passphrase: str = None):
    """Store encrypted API key for user"""
    try:
        # In production, you would encrypt these values
        # For now, we'll store them as-is (NOT RECOMMENDED for production)
        api_key_data = {
            'user_id': user_id,
            'exchange': exchange,
            'name': name,
            'api_key_encrypted': api_key,  # Should be encrypted
            'api_secret_encrypted': api_secret,  # Should be encrypted
            'passphrase_encrypted': passphrase,  # Should be encrypted
            'is_active': True
        }
        
        response = supabase.table('api_keys').insert(api_key_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error storing API key: {e}")
        return None

# Export the clients and helper functions
__all__ = [
    'supabase',
    'supabase_admin',
    'SupabaseConnection',
    'get_user_by_id',
    'create_user_profile',
    'get_user_bots',
    'get_user_portfolios',
    'get_news_feed',
    'store_api_key'
]