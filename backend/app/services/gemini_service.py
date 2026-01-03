"""
Google Gemini AI Service
Handles AI-powered email response generation using Google Gemini API
"""

import os
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client with API key from environment"""
        self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"  # Fast and cost-effective
        self.client = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini AI initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.client = None
        else:
            logger.warning("GOOGLE_GEMINI_API_KEY not found in environment")
    
    def is_available(self) -> bool:
        """Check if Gemini client is initialized"""
        return self.client is not None
    
    async def generate_response(
        self,
        email_from: str,
        email_subject: str,
        email_body: str,
        tone: str = "professional",
        knowledge_base: Optional[str] = None,
        training_examples: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered email response using Gemini
        
        Args:
            email_from: Sender email address
            email_subject: Email subject
            email_body: Email body text
            tone: Response tone (professional, friendly, formal, etc.)
            knowledge_base: Context from knowledge base
            training_examples: Similar examples from training data
            
        Returns:
            Dict with success status, response text, and confidence score
        """
        
        if not self.is_available():
            return {
                "success": False,
                "response": "Gemini API не настроен. Добавьте API ключ в настройках.",
                "confidence": 0.0,
                "error": "API key not configured"
            }
        
        try:
            # Build prompt with context
            prompt = self._build_prompt(
                email_from=email_from,
                email_subject=email_subject,
                email_body=email_body,
                tone=tone,
                knowledge_base=knowledge_base,
                training_examples=training_examples
            )
            
            # Generate response with timeout
            response = await self._generate_with_timeout(prompt, timeout=30)
            
            if response:
                return {
                    "success": True,
                    "response": response,
                    "confidence": 0.95,  # Gemini doesn't provide confidence, using fixed high value
                    "model": self.model_name
                }
            else:
                return {
                    "success": False,
                    "response": "Не удалось сгенерировать ответ",
                    "confidence": 0.0,
                    "error": "Empty response from Gemini"
                }
                
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return {
                "success": False,
                "response": f"Ошибка генерации: {str(e)}",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _build_prompt(
        self,
        email_from: str,
        email_subject: str,
        email_body: str,
        tone: str,
        knowledge_base: Optional[str] = None,
        training_examples: Optional[str] = None
    ) -> str:
        """Build comprehensive prompt with context"""
        
        tone_instructions = {
            "professional": "профессиональным и деловым",
            "friendly": "дружелюбным и неформальным",
            "formal": "официальным и строгим",
            "brief": "кратким и по делу",
            "detailed": "подробным и исчерпывающим",
            "creative": "креативным и оригинальным"
        }
        
        tone_desc = tone_instructions.get(tone, "профессиональным")
        
        prompt = f"""Ты — AI ассистент компании по продаже кондитерских изделий.

ТВОЯ ЗАДАЧА: Сгенерировать {tone_desc} ответ на письмо клиента.

"""
        
        # Add knowledge base if available
        if knowledge_base:
            prompt += f"""ИНФОРМАЦИЯ О КОМПАНИИ И ПРОДУКТАХ:
{knowledge_base}

"""
        
        # Add training examples if available
        if training_examples:
            prompt += f"""ПРИМЕРЫ ПОХОЖИХ ОТВЕТОВ:
{training_examples}

"""
        
        # Add email details
        prompt += f"""НОВОЕ ПИСЬМО ОТ КЛИЕНТА:
От: {email_from}
Тема: {email_subject}
Текст:
{email_body}

ТРЕБОВАНИЯ К ОТВЕТУ:
1. Отвечай на русском языке
2. Используй информацию из базы знаний (если есть)
3. Следуй стилю примеров ответов (если есть)
4. Будь вежливым и профессиональным
5. Отвечай конкретно на вопросы клиента
6. Не придумывай информацию, которой нет в базе знаний
7. Тон ответа: {tone_desc}

СГЕНЕРИРУЙ ОТВЕТ:"""
        
        return prompt
    
    async def _generate_with_timeout(self, prompt: str, timeout: int = 30) -> Optional[str]:
        """Generate response with timeout protection"""
        import asyncio
        
        try:
            # Gemini SDK doesn't have native async, run in executor
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, self._sync_generate, prompt),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.error(f"Gemini generation timeout after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None
    
    def _sync_generate(self, prompt: str) -> str:
        """Synchronous generation call"""
        response = self.client.generate_content(prompt)
        return response.text if response and response.text else ""


# Global instance
gemini_service = GeminiService()
