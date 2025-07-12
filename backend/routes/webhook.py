from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import logging
import sys
from pathlib import Path

# Add the backend directory to Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# We'll get the database connection from the main server file
async def get_database():
    from server import db
    return db

async def cleanup_old_entries(db):
    """Keep only the latest 20 feed entries, remove older ones"""
    try:
        # Count total entries
        total_count = await db.feed_entries.count_documents({})
        
        if total_count > 20:
            # Find entries to delete (keep latest 20)
            entries_to_delete = await db.feed_entries.find(
                {},
                {"_id": 1}
            ).sort("created_at", 1).limit(total_count - 20).to_list(total_count - 20)
            
            # Delete old entries
            if entries_to_delete:
                ids_to_delete = [entry["_id"] for entry in entries_to_delete]
                result = await db.feed_entries.delete_many({"_id": {"$in": ids_to_delete}})
                logger.info(f"Cleaned up {result.deleted_count} old feed entries")
                
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Define models for the new OpenAI response format
from pydantic import BaseModel, Field, validator
import uuid

class MessageContent(BaseModel):
    """Content structure from OpenAI API response"""
    title: str = Field(..., description="News headline")
    summary: str = Field(..., description="AI-generated summary")
    sentiment_score: int = Field(..., ge=0, le=100, description="Market sentiment score (0-100)")

class Message(BaseModel):
    """Message structure from OpenAI API response"""
    content: MessageContent

class Choice(BaseModel):
    """Choice structure from OpenAI API response"""
    message: Message

class OpenAIWebhookRequest(BaseModel):
    """OpenAI API response format for webhook"""
    choices: List[Choice]
    source: Optional[str] = Field(default="AI Generated", description="Source of the news")
    timestamp: Optional[str] = Field(default=None, description="ISO datetime string")

    @validator('timestamp', always=True)
    def set_timestamp(cls, v):
        if v is None:
            return datetime.utcnow().isoformat()
        return v

class FeedEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="News headline")
    summary: str = Field(..., description="AI-generated summary")
    sentiment: int = Field(..., ge=0, le=100, description="Market sentiment score (0-100)")
    source: str = Field(..., description="Source of the news")
    timestamp: datetime = Field(..., description="Timestamp of the news")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FeedEntryCreate(BaseModel):
    title: str = Field(..., description="News headline")
    summary: str = Field(..., description="AI-generated summary") 
    sentiment: int = Field(..., ge=0, le=100, description="Market sentiment score (0-100)")
    source: str = Field(..., description="Source of the news")
    timestamp: str = Field(..., description="ISO datetime string")

class FeedEntryResponse(BaseModel):
    id: str
    title: str
    summary: str
    sentiment: int
    source: str
    timestamp: datetime
    created_at: datetime

class TranslatedFeedEntryResponse(BaseModel):
    id: str
    title: str
    summary: str
    sentiment: int
    source: str
    timestamp: datetime
    created_at: datetime
    language: str
    is_translated: bool

@router.post("/ai_news_webhook", response_model=FeedEntryResponse)
async def receive_news_webhook(
    news_data: OpenAIWebhookRequest, 
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """
    Enhanced webhook endpoint to receive investment news updates from n8n with OpenAI format
    
    Expected JSON format:
    {
        "choices": [
            {
                "message": {
                    "content": {
                        "title": "News headline",
                        "summary": "AI-generated summary",
                        "sentiment_score": 75
                    }
                }
            }
        ],
        "source": "Source name (optional)",
        "timestamp": "ISO datetime string (optional)"
    }
    """
    try:
        # Extract data from OpenAI response format
        if not news_data.choices or len(news_data.choices) == 0:
            raise HTTPException(status_code=400, detail="No choices found in request")
        
        choice = news_data.choices[0]
        content = choice.message.content
        
        # Parse the timestamp
        try:
            timestamp = datetime.fromisoformat(news_data.timestamp.replace('Z', '+00:00'))
        except ValueError:
            # Fallback to current time if timestamp parsing fails
            timestamp = datetime.utcnow()
            logger.warning(f"Could not parse timestamp {news_data.timestamp}, using current time")

        # Create feed entry from OpenAI format
        feed_entry = FeedEntry(
            title=content.title,
            summary=content.summary,
            sentiment=content.sentiment_score,  # Map sentiment_score to sentiment
            source=news_data.source,
            timestamp=timestamp
        )
        
        # Insert into database
        result = await db.feed_entries.insert_one(feed_entry.dict())
        
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert feed entry")
        
        # Schedule cleanup of old entries in background
        background_tasks.add_task(cleanup_old_entries, db)
        
        logger.info(f"Successfully added news entry from OpenAI format: {feed_entry.title}")
        
        return FeedEntryResponse(**feed_entry.dict())
        
    except Exception as e:
        logger.error(f"Error processing OpenAI webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@router.post("/ai_news_webhook/legacy", response_model=FeedEntryResponse)
async def receive_news_webhook_legacy(
    news_data: FeedEntryCreate, 
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """
    Legacy webhook endpoint for backward compatibility
    
    Expected JSON format:
    {
        "title": "string",
        "summary": "string", 
        "sentiment": number (0-100),
        "source": "string",
        "timestamp": "ISO datetime string"
    }
    """
    try:
        # Parse the timestamp
        try:
            timestamp = datetime.fromisoformat(news_data.timestamp.replace('Z', '+00:00'))
        except ValueError:
            # Fallback to current time if timestamp parsing fails
            timestamp = datetime.utcnow()
            logger.warning(f"Could not parse timestamp {news_data.timestamp}, using current time")

        # Create feed entry
        feed_entry = FeedEntry(
            title=news_data.title,
            summary=news_data.summary,
            sentiment=news_data.sentiment,
            source=news_data.source,
            timestamp=timestamp
        )
        
        # Insert into database
        result = await db.feed_entries.insert_one(feed_entry.dict())
        
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert feed entry")
        
        # Schedule cleanup of old entries in background
        background_tasks.add_task(cleanup_old_entries, db)
        
        logger.info(f"Successfully added news entry via legacy endpoint: {feed_entry.title}")
        
        return FeedEntryResponse(**feed_entry.dict())
        
    except Exception as e:
        logger.error(f"Error processing legacy webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@router.get("/feed_entries", response_model=List[TranslatedFeedEntryResponse])
async def get_feed_entries(
    limit: int = 20, 
    language: str = "en",
    db=Depends(get_database)
):
    """
    Get the latest feed entries for display in AI Feed
    Returns entries in descending order (latest first)
    Supports automatic translation to Russian
    """
    try:
        # Fetch latest entries
        entries = await db.feed_entries.find(
            {},
            {"_id": 0}  # Exclude MongoDB _id field
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        translated_entries = []
        
        for entry in entries:
            # If language is Russian, attempt to get/create translation
            if language == "ru":
                translated_entry = await get_translated_entry(db, entry)
                translated_entries.append(translated_entry)
            else:
                # Return original English entry
                translated_entry = TranslatedFeedEntryResponse(
                    **entry,
                    language="en",
                    is_translated=False
                )
                translated_entries.append(translated_entry)
        
        logger.info(f"Retrieved {len(translated_entries)} feed entries in {language}")
        return translated_entries
        
    except Exception as e:
        logger.error(f"Error retrieving feed entries: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving feed entries: {str(e)}")

async def get_translated_entry(db, entry: dict) -> TranslatedFeedEntryResponse:
    """Get or create translated version of a feed entry"""
    try:
        # Import translation service
        from services.translation import get_translation_service
        
        entry_id = entry['id']
        
        # Check for cached translation
        cached = await db.translations.find_one({
            "entry_id": entry_id,
            "language": "ru"
        })
        
        if cached:
            # Return cached translation
            return TranslatedFeedEntryResponse(
                id=entry['id'],
                title=cached['title'],
                summary=cached['summary'],
                sentiment=entry['sentiment'],
                source=entry['source'],
                timestamp=entry['timestamp'],
                created_at=entry['created_at'],
                language="ru",
                is_translated=True
            )
        
        # Get API key and create translation
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key not found, returning original text")
            return TranslatedFeedEntryResponse(
                **entry,
                language="en",
                is_translated=False
            )
        
        # Translate the content
        translation_service = get_translation_service(api_key)
        translation = await translation_service.translate_to_russian(
            entry['title'], 
            entry['summary']
        )
        
        # Cache the translation
        try:
            translation_doc = {
                "entry_id": entry_id,
                "language": "ru",
                "title": translation['title'],
                "summary": translation['summary'],
                "created_at": datetime.utcnow()
            }
            
            await db.translations.update_one(
                {"entry_id": entry_id, "language": "ru"},
                {"$set": translation_doc},
                upsert=True
            )
        except Exception as cache_error:
            logger.error(f"Failed to cache translation: {cache_error}")
        
        # Return translated entry
        return TranslatedFeedEntryResponse(
            id=entry['id'],
            title=translation['title'],
            summary=translation['summary'],
            sentiment=entry['sentiment'],
            source=entry['source'],
            timestamp=entry['timestamp'],
            created_at=entry['created_at'],
            language="ru",
            is_translated=True
        )
        
    except Exception as e:
        logger.error(f"Translation failed for entry {entry['id']}: {e}")
        # Return original entry as fallback
        return TranslatedFeedEntryResponse(
            **entry,
            language="en", 
            is_translated=False
        )

@router.delete("/feed_entries", status_code=200)
async def clear_all_feed_entries(db=Depends(get_database)):
    """
    Clear all feed entries and translations (for testing purposes)
    """
    try:
        # Clear feed entries
        entries_result = await db.feed_entries.delete_many({})
        
        # Clear translations
        translations_result = await db.translations.delete_many({})
        
        logger.info(f"Cleared {entries_result.deleted_count} feed entries and {translations_result.deleted_count} translations")
        return {
            "message": f"Cleared {entries_result.deleted_count} feed entries and {translations_result.deleted_count} translations"
        }
    except Exception as e:
        logger.error(f"Error clearing feed entries: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing feed entries: {str(e)}")

@router.get("/feed_entries/count")
async def get_feed_entries_count(db=Depends(get_database)):
    """
    Get the total count of feed entries
    """
    try:
        count = await db.feed_entries.count_documents({})
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting feed entries count: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting count: {str(e)}")

@router.get("/translations/count")
async def get_translations_count(db=Depends(get_database)):
    """
    Get the total count of cached translations
    """
    try:
        count = await db.translations.count_documents({})
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting translations count: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting translations count: {str(e)}")

@router.get("/webhook/test")
async def test_webhook_format():
    """
    Get example request format for the new webhook
    """
    return {
        "description": "Send POST request to /api/ai_news_webhook with this format:",
        "example_request": {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "{{ $json.choices[0].message.content.title }}",
                            "summary": "{{ $json.choices[0].message.content.summary }}",
                            "sentiment_score": "{{ $json.choices[0].message.content.sentiment_score }}"
                        }
                    }
                }
            ],
            "source": "Your News Source",
            "timestamp": "2025-01-11T10:30:00Z"
        },
        "n8n_mapping": {
            "title": "{{ $json.choices[0].message.content.title }}",
            "summary": "{{ $json.choices[0].message.content.summary }}",
            "sentiment_score": "{{ $json.choices[0].message.content.sentiment_score }}"
        }
    }