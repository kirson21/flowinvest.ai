import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("Missing required Supabase environment variables")

# Create Supabase clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

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