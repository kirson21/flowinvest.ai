from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from supabase_client import supabase, supabase_admin
import re
from datetime import datetime
import uuid

router = APIRouter()

# Pydantic models
class SlugValidationRequest(BaseModel):
    slug: str
    exclude_user_id: Optional[str] = None

class SlugValidationResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    suggestions: Optional[List[str]] = None

class PublicUserProfile(BaseModel):
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    social_links: Optional[Dict[str, Any]]
    specialties: Optional[List[str]]
    seller_mode: bool
    created_at: str

class PublicBotDetails(BaseModel):
    name: str
    description: str
    strategy: str
    slug: str
    is_prebuilt: bool
    created_at: str
    performance_metrics: Optional[Dict[str, Any]] = None

class PublicPortfolioDetails(BaseModel):
    title: str
    description: str
    price: float
    category: Optional[str]
    slug: str
    rating: float
    votes_count: int
    created_at: str
    seller_info: Dict[str, Any]

class FeedPostDetails(BaseModel):
    title: str
    summary: Optional[str]
    content: Optional[str]
    sentiment: Optional[str]
    source: Optional[str]
    language: str
    slug: str
    created_at: str
    published_at: Optional[str]

# Utility functions
def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text"""
    if not text or not text.strip():
        return ""
    
    # Remove special characters, convert to lowercase
    slug = re.sub(r'[^a-zA-Z0-9\s\-_]', '', text.strip())
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Replace multiple consecutive hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-').lower()
    
    return slug

def generate_slug_suggestions(base_slug: str, count: int = 3) -> List[str]:
    """Generate alternative slug suggestions"""
    suggestions = []
    for i in range(1, count + 1):
        suggestions.append(f"{base_slug}-{i}")
        suggestions.append(f"{base_slug}{i}")
    
    # Add some creative variations
    import random
    suffixes = ['pro', 'plus', 'v2', 'new', 'alt']
    suggestions.extend([f"{base_slug}-{suffix}" for suffix in random.sample(suffixes, min(2, len(suffixes)))])
    
    return suggestions[:count]

# Validation endpoints
@router.post("/validate-slug", response_model=SlugValidationResponse)
async def validate_slug(request: SlugValidationRequest):
    """Validate if a slug/display_name is available and properly formatted"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Call the database validation function
        result = supabase_admin.rpc(
            'validate_url_slug', 
            {
                'slug_to_check': request.slug,
                'exclude_user_id': request.exclude_user_id
            }
        ).execute()
        
        if result.data:
            validation_result = result.data
            if validation_result.get('valid'):
                return SlugValidationResponse(valid=True)
            else:
                # Generate suggestions if slug is invalid due to being taken
                error_message = validation_result.get('error', 'Invalid slug')
                suggestions = []
                
                if 'already taken' in error_message.lower():
                    base_slug = generate_slug(request.slug)
                    suggestions = generate_slug_suggestions(base_slug)
                
                return SlugValidationResponse(
                    valid=False,
                    error=error_message,
                    suggestions=suggestions
                )
        else:
            raise HTTPException(status_code=500, detail="Validation function failed")
            
    except Exception as e:
        print(f"Error validating slug: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.get("/reserved-words")
async def get_reserved_words():
    """Get list of reserved words for client-side validation"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        result = supabase.table('reserved_words').select('word, category').execute()
        
        words = {}
        for item in result.data or []:
            category = item.get('category', 'system')
            if category not in words:
                words[category] = []
            words[category].append(item.get('word'))
        
        return {"reserved_words": words}
        
    except Exception as e:
        print(f"Error fetching reserved words: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching reserved words: {str(e)}")

# Public URL endpoints
@router.get("/public/user/{display_name}", response_model=PublicUserProfile)
async def get_public_user_profile(display_name: str):
    """Get public user profile by display name"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Fetch user profile by display_name
        result = supabase.table('user_profiles')\
            .select('display_name, bio, avatar_url, social_links, specialties, seller_mode, created_at')\
            .eq('display_name', display_name)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = result.data[0]
        
        return PublicUserProfile(
            display_name=profile['display_name'],
            bio=profile.get('bio'),
            avatar_url=profile.get('avatar_url'),
            social_links=profile.get('social_links', {}),
            specialties=profile.get('specialties', []),
            seller_mode=profile.get('seller_mode', False),
            created_at=profile['created_at']
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching public user profile: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user profile")

@router.get("/public/bots/{slug}", response_model=PublicBotDetails)
async def get_public_bot(slug: str):
    """Get public bot details by slug (only prebuilt bots)"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Fetch bot by slug, only if it's prebuilt and public
        result = supabase.table('user_bots')\
            .select('name, description, strategy, slug, is_prebuilt, created_at, daily_pnl, weekly_pnl, monthly_pnl, win_rate, total_trades, successful_trades')\
            .eq('slug', slug)\
            .eq('is_prebuilt', True)\
            .eq('is_public', True)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Bot not found or not publicly available")
        
        bot = result.data[0]
        
        # Prepare performance metrics
        performance_metrics = {
            'daily_pnl': bot.get('daily_pnl', 0.0),
            'weekly_pnl': bot.get('weekly_pnl', 0.0),
            'monthly_pnl': bot.get('monthly_pnl', 0.0),
            'win_rate': bot.get('win_rate', 0.0),
            'total_trades': bot.get('total_trades', 0),
            'successful_trades': bot.get('successful_trades', 0)
        }
        
        return PublicBotDetails(
            name=bot['name'],
            description=bot.get('description', ''),
            strategy=bot.get('strategy', ''),
            slug=bot['slug'],
            is_prebuilt=bot['is_prebuilt'],
            created_at=bot['created_at'],
            performance_metrics=performance_metrics
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching public bot: {e}")
        raise HTTPException(status_code=500, detail="Error fetching bot details")

@router.get("/public/marketplace/{slug}", response_model=PublicPortfolioDetails)
async def get_public_marketplace_product(slug: str):
    """Get public marketplace product by slug"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Fetch portfolio/product by slug, only if public
        result = supabase.table('portfolios')\
            .select('''
                title, description, price, category, slug, rating, votes_count, created_at, seller_id,
                user_profiles!portfolios_seller_id_fkey(display_name, avatar_url, seller_mode)
            ''')\
            .eq('slug', slug)\
            .eq('is_public', True)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Product not found or not publicly available")
        
        product = result.data[0]
        
        # Prepare seller info
        seller_profile = product.get('user_profiles', {})
        seller_info = {
            'display_name': seller_profile.get('display_name', 'Anonymous'),
            'avatar_url': seller_profile.get('avatar_url'),
            'is_verified_seller': seller_profile.get('seller_mode', False)
        }
        
        return PublicPortfolioDetails(
            title=product['title'],
            description=product.get('description', ''),
            price=product.get('price', 0.0),
            category=product.get('category'),
            slug=product['slug'],
            rating=product.get('rating', 0.0),
            votes_count=product.get('votes_count', 0),
            created_at=product['created_at'],
            seller_info=seller_info
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching public marketplace product: {e}")
        raise HTTPException(status_code=500, detail="Error fetching product details")

@router.get("/public/feed/{slug}", response_model=FeedPostDetails)
async def get_public_feed_post(slug: str):
    """Get public feed post by slug"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Fetch feed post by slug, only if public
        result = supabase.table('feed_posts')\
            .select('title, summary, content, sentiment, source, language, slug, created_at, published_at')\
            .eq('slug', slug)\
            .eq('is_public', True)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Feed post not found or not publicly available")
        
        post = result.data[0]
        
        return FeedPostDetails(
            title=post['title'],
            summary=post.get('summary'),
            content=post.get('content'),
            sentiment=post.get('sentiment'),
            source=post.get('source'),
            language=post.get('language', 'en'),
            slug=post['slug'],
            created_at=post['created_at'],
            published_at=post.get('published_at')
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error fetching public feed post: {e}")
        raise HTTPException(status_code=500, detail="Error fetching feed post")

# Slug management endpoints for authenticated users
@router.post("/generate-slug")
async def generate_slug_endpoint(text: str = Query(..., description="Text to convert to slug")):
    """Generate a URL-friendly slug from any text"""
    try:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        slug = generate_slug(text)
        
        if not slug:
            raise HTTPException(status_code=400, detail="Unable to generate valid slug from provided text")
        
        return {
            "original_text": text,
            "generated_slug": slug,
            "suggestions": generate_slug_suggestions(slug)
        }
        
    except Exception as e:
        print(f"Error generating slug: {e}")
        raise HTTPException(status_code=500, detail="Error generating slug")

@router.post("/update-bot-slug/{bot_id}")
async def update_bot_slug(bot_id: str, new_slug: str = Query(...)):
    """Update a bot's slug (authenticated endpoint)"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate slug first
        validation_request = SlugValidationRequest(slug=new_slug)
        validation_result = await validate_slug(validation_request)
        
        if not validation_result.valid:
            raise HTTPException(status_code=400, detail=validation_result.error)
        
        # Update the bot slug
        result = supabase_admin.table('user_bots')\
            .update({'slug': new_slug})\
            .eq('id', bot_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        return {"success": True, "new_slug": new_slug, "bot_id": bot_id}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error updating bot slug: {e}")
        raise HTTPException(status_code=500, detail="Error updating bot slug")

@router.post("/update-portfolio-slug/{portfolio_id}")
async def update_portfolio_slug(portfolio_id: str, new_slug: str = Query(...)):
    """Update a portfolio/product's slug (authenticated endpoint)"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Validate slug first
        validation_request = SlugValidationRequest(slug=new_slug)
        validation_result = await validate_slug(validation_request)
        
        if not validation_result.valid:
            raise HTTPException(status_code=400, detail=validation_result.error)
        
        # Update the portfolio slug
        result = supabase_admin.table('portfolios')\
            .update({'slug': new_slug})\
            .eq('id', portfolio_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return {"success": True, "new_slug": new_slug, "portfolio_id": portfolio_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating portfolio slug: {e}")
        raise HTTPException(status_code=500, detail="Error updating portfolio slug")

# Admin endpoints for feed post management
@router.post("/admin/feed-posts/create")
async def create_feed_post(
    title: str = Query(...),
    summary: Optional[str] = Query(None),
    content: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    language: str = Query('en'),
    external_id: Optional[str] = Query(None)
):
    """Create a new feed post with auto-generated slug (admin only)"""
    try:
        if not supabase_admin:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Generate slug from title
        slug = generate_slug(title)
        if not slug:
            raise HTTPException(status_code=400, detail="Unable to generate slug from title")
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while True:
            existing = supabase_admin.table('feed_posts')\
                .select('id')\
                .eq('slug', slug)\
                .execute()
            
            if not existing.data:
                break
            
            slug = f"{base_slug}-{counter}"
            counter += 1
            
            if counter > 100:  # Prevent infinite loop
                slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
                break
        
        # Create the feed post
        post_data = {
            'title': title,
            'summary': summary,
            'content': content,
            'sentiment': sentiment,
            'source': source,
            'language': language,
            'external_id': external_id,
            'slug': slug,
            'is_public': True,
            'published_at': datetime.utcnow().isoformat()
        }
        
        result = supabase_admin.table('feed_posts')\
            .insert(post_data)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create feed post")
        
        created_post = result.data[0]
        
        return {
            "success": True,
            "post": created_post,
            "public_url": f"/feed/{slug}"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error creating feed post: {e}")
        raise HTTPException(status_code=500, detail="Error creating feed post")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for custom URLs service"""
    try:
        # Test database connectivity
        db_status = "connected" if supabase else "disconnected"
        admin_db_status = "connected" if supabase_admin else "disconnected"
        
        return {
            "status": "healthy",
            "database": db_status,
            "admin_database": admin_db_status,
            "features": [
                "slug_validation",
                "public_urls",
                "reserved_words",
                "user_profiles",
                "bot_pages",
                "marketplace_products",
                "feed_posts"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")