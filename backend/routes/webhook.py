from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List
import os
import logging

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

# Define models inline to avoid import issues
from pydantic import BaseModel, Field
import uuid

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

@router.post("/ai_news_webhook", response_model=FeedEntryResponse)
async def receive_news_webhook(
    news_data: FeedEntryCreate, 
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """
    Webhook endpoint to receive investment news updates from n8n
    
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
        
        logger.info(f"Successfully added news entry: {feed_entry.title}")
        
        return FeedEntryResponse(**feed_entry.dict())
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@router.get("/feed_entries", response_model=List[FeedEntryResponse])
async def get_feed_entries(limit: int = 20, db=Depends(get_database)):
    """
    Get the latest feed entries for display in AI Feed
    Returns entries in descending order (latest first)
    """
    try:
        # Fetch latest entries
        entries = await db.feed_entries.find(
            {},
            {"_id": 0}  # Exclude MongoDB _id field
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Convert to response models
        feed_entries = [FeedEntryResponse(**entry) for entry in entries]
        
        logger.info(f"Retrieved {len(feed_entries)} feed entries")
        return feed_entries
        
    except Exception as e:
        logger.error(f"Error retrieving feed entries: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving feed entries: {str(e)}")

@router.delete("/feed_entries", status_code=200)
async def clear_all_feed_entries(db=Depends(get_database)):
    """
    Clear all feed entries (for testing purposes)
    """
    try:
        result = await db.feed_entries.delete_many({})
        logger.info(f"Cleared {result.deleted_count} feed entries")
        return {"message": f"Cleared {result.deleted_count} feed entries"}
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