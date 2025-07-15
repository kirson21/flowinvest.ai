from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import logging
import sys
from pathlib import Path
from pydantic import BaseModel, Field, validator
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for now (replace with Supabase later)
FEED_ENTRIES = []
TRANSLATIONS = {}

def cleanup_old_entries():
    """Keep only the latest 20 feed entries, remove older ones"""
    global FEED_ENTRIES
    try:
        if len(FEED_ENTRIES) > 20:
            # Keep only the latest 20 entries
            FEED_ENTRIES = sorted(FEED_ENTRIES, key=lambda x: x['created_at'], reverse=True)[:20]
            logger.info(f"Cleaned up old entries, keeping {len(FEED_ENTRIES)} entries")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Define models for the new OpenAI response format
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
    background_tasks: BackgroundTasks
):
    """
    Enhanced webhook endpoint to receive investment news updates from n8n with OpenAI format
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
            timestamp = datetime.utcnow()
            logger.warning(f"Could not parse timestamp {news_data.timestamp}, using current time")

        # Create feed entry from OpenAI format
        feed_entry = FeedEntry(
            title=content.title,
            summary=content.summary,
            sentiment=content.sentiment_score,
            source=news_data.source,
            timestamp=timestamp
        )
        
        # Store in memory
        FEED_ENTRIES.append(feed_entry.dict())
        
        # Schedule cleanup of old entries
        background_tasks.add_task(cleanup_old_entries)
        
        logger.info(f"Successfully added news entry from OpenAI format: {feed_entry.title}")
        
        return FeedEntryResponse(**feed_entry.dict())
        
    except Exception as e:
        logger.error(f"Error processing OpenAI webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@router.get("/feed_entries", response_model=List[TranslatedFeedEntryResponse])
async def get_feed_entries(limit: int = 20, language: str = "en"):
    """
    Get the latest feed entries for display in AI Feed
    """
    try:
        # Sort by created_at in descending order and limit
        sorted_entries = sorted(FEED_ENTRIES, key=lambda x: x['created_at'], reverse=True)[:limit]
        
        translated_entries = []
        
        for entry in sorted_entries:
            # For now, just return entries as-is (no translation)
            translated_entry = TranslatedFeedEntryResponse(
                **entry,
                language=language,
                is_translated=False
            )
            translated_entries.append(translated_entry)
        
        logger.info(f"Retrieved {len(translated_entries)} feed entries in {language}")
        return translated_entries
        
    except Exception as e:
        logger.error(f"Error retrieving feed entries: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving feed entries: {str(e)}")

@router.get("/feed_entries/count")
async def get_feed_entries_count():
    """Get the total count of feed entries"""
    try:
        count = len(FEED_ENTRIES)
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting feed entries count: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting count: {str(e)}")

@router.get("/translations/count")
async def get_translations_count():
    """Get the total count of cached translations"""
    try:
        count = len(TRANSLATIONS)
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting translations count: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting translations count: {str(e)}")

@router.delete("/feed_entries", status_code=200)
async def clear_all_feed_entries():
    """Clear all feed entries and translations (for testing purposes)"""
    try:
        global FEED_ENTRIES, TRANSLATIONS
        entries_count = len(FEED_ENTRIES)
        translations_count = len(TRANSLATIONS)
        
        FEED_ENTRIES.clear()
        TRANSLATIONS.clear()
        
        logger.info(f"Cleared {entries_count} feed entries and {translations_count} translations")
        return {
            "message": f"Cleared {entries_count} feed entries and {translations_count} translations"
        }
    except Exception as e:
        logger.error(f"Error clearing feed entries: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing feed entries: {str(e)}")

@router.get("/webhook/test")
async def test_webhook_format():
    """Get example request format for the new webhook"""
    return {
        "description": "Send POST request to /api/ai_news_webhook with this format:",
        "example_request": {
            "choices": [
                {
                    "message": {
                        "content": {
                            "title": "Test News Title",
                            "summary": "This is a test summary",
                            "sentiment_score": 75
                        }
                    }
                }
            ],
            "source": "Test Source",
            "timestamp": "2025-01-11T10:30:00Z"
        }
    }