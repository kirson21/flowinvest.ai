import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self, api_key: str):
        """Initialize translation service with OpenAI API key"""
        self.api_key = api_key
        
    async def translate_to_russian(self, title: str, summary: str) -> Dict[str, str]:
        """
        Translate title and summary from English to Russian using OpenAI
        
        Args:
            title: English title to translate
            summary: English summary to translate
            
        Returns:
            Dict with translated title and summary, or original text if translation fails
        """
        try:
            # Initialize chat session for translation
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"translation_{hash(title + summary)}",
                system_message="""You are a professional financial news translator. Translate the provided English financial news content to fluent, natural Russian while maintaining the professional tone and financial terminology. 

Rules:
1. Translate both title and summary accurately
2. Preserve all numbers, percentages, and financial terms
3. Use appropriate Russian financial terminology
4. Keep the professional and informative tone
5. Respond with ONLY the JSON format as requested"""
            ).with_model("openai", "gpt-4o").with_max_tokens(1000)
            
            # Create translation prompt
            translation_prompt = f"""Please translate this financial news to Russian. Respond with ONLY a JSON object in this exact format:

{{
  "title": "Russian translation of title",
  "summary": "Russian translation of summary"
}}

English content to translate:
Title: {title}
Summary: {summary}"""
            
            # Send translation request
            user_message = UserMessage(text=translation_prompt)
            response = await chat.send_message(user_message)
            
            # Parse the JSON response
            import json
            try:
                # Extract JSON from response
                response_text = response.strip()
                if response_text.startswith('```json'):
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                elif response_text.startswith('```'):
                    response_text = response_text.split('```')[1].split('```')[0].strip()
                
                translation_data = json.loads(response_text)
                
                # Validate the response has required fields
                if 'title' in translation_data and 'summary' in translation_data:
                    logger.info(f"Successfully translated news: {title[:50]}...")
                    return {
                        'title': translation_data['title'],
                        'summary': translation_data['summary']
                    }
                else:
                    raise ValueError("Missing required fields in translation response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse translation response: {e}")
                # Fallback to original text
                return {
                    'title': title,
                    'summary': summary
                }
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original text as fallback
            return {
                'title': title,
                'summary': summary
            }

    async def get_cached_translation(self, db, entry_id: str, language: str) -> Optional[Dict[str, str]]:
        """Get cached translation from database"""
        try:
            translation = await db.translations.find_one({
                "entry_id": entry_id,
                "language": language
            })
            
            if translation:
                return {
                    'title': translation['title'],
                    'summary': translation['summary']
                }
        except Exception as e:
            logger.error(f"Error retrieving cached translation: {e}")
        
        return None

    async def cache_translation(self, db, entry_id: str, language: str, title: str, summary: str):
        """Cache translation in database"""
        try:
            translation_doc = {
                "entry_id": entry_id,
                "language": language,
                "title": title,
                "summary": summary,
                "created_at": datetime.utcnow()
            }
            
            # Upsert the translation
            await db.translations.update_one(
                {"entry_id": entry_id, "language": language},
                {"$set": translation_doc},
                upsert=True
            )
            
            logger.info(f"Cached translation for entry {entry_id} in {language}")
            
        except Exception as e:
            logger.error(f"Error caching translation: {e}")

# Global translation service instance
translation_service = None

def get_translation_service(api_key: str) -> TranslationService:
    """Get or create translation service instance"""
    global translation_service
    if translation_service is None:
        translation_service = TranslationService(api_key)
    return translation_service