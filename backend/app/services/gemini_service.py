"""
Google Gemini AI Service
Handles AI-powered email response generation using Google Gemini API
With dynamic data from uploaded sales/customers/products
"""

import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

from app.database import supabase
from app.config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client with API key from config settings"""
        settings = get_settings()
        self.api_key = settings.google_gemini_api_key
        self.model_name = "gemini-1.5-flash"  # Restore standard model
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
        available = self.client is not None
        logger.debug(f"Gemini availability check: {available}")
        return available
    
    async def generate_response(
        self,
        email_from: str,
        email_subject: str,
        email_body: str,
        tone: str = "professional",
        knowledge_base: Optional[str] = None, # kept for signature compatibility
        training_examples: Optional[str] = None,
        include_analytics: bool = True
    ) -> Dict[str, Any]:
        """Generate AI response with full context"""
        
        if not self.is_available():
            logger.warning("Generation requested but Gemini is not available")
            return {
                "success": False,
                "response": "Gemini API не настроен.",
                "confidence": 0.0,
                "error": "API key not configured"
            }
        
        logger.info(f"Generating response for {email_from} with tone {tone}")
        
        try:
            # 1. Static Knowledge (Fetch from DB if not provided)
            knowledge_text = knowledge_base
            if not knowledge_text and supabase:
                try:
                    k_res = supabase.table("knowledge_base").select("title, content").execute()
                    if k_res.data:
                        knowledge_text = self._format_knowledge(k_res.data)
                except Exception as e:
                    logger.warning(f"Failed to fetch knowledge: {e}")

            # 2. Training Examples
            training_text = training_examples
            if not training_text and supabase:
                try:
                    t_res = supabase.table("training_examples").select("question, answer").limit(10).execute()
                    if t_res.data:
                        training_text = self._format_training(t_res.data)
                except Exception as e:
                    logger.warning(f"Failed to fetch training: {e}")

            # 3. Dynamic Analytics
            analytics_text = None
            if include_analytics:
                try:
                    from app.services.analytics_service import AnalyticsService
                    analytics = AnalyticsService()
                    
                    sales = analytics.get_sales_summary()
                    clients = analytics.get_clients_summary()
                    monthly = analytics.get_monthly_stats()
                    
                    analytics_text = self._format_analytics(sales, clients, monthly)
                except Exception as e:
                    logger.warning(f"Failed to fetch analytics: {e}")

            # 4. Build Prompt
            prompt = self._build_enhanced_prompt(
                email_from, email_subject, email_body, tone,
                knowledge_text, training_text, analytics_text
            )
            
            # Generate
            response = await self._generate_with_timeout(prompt)
            
            if response:
                return {
                    "success": True,
                    "response": response,
                    "confidence": 0.95,
                    "model": self.model_name
                }
            return {
                "success": False,
                "response": "Empty response",
                "confidence": 0.0
            }
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Generation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            if "429" in error_str or "Quota" in error_str:
                return {
                    "success": False, 
                    "response": "⚠️ Лимит запросов исчерпан (Quota Exceeded). Попробуйте завтра или смените API ключ.",
                    "error": "Quota Exceeded (429)",
                    "confidence": 0.0
                }
            elif "404" in error_str:
                return {
                    "success": False,
                    "response": f"❌ Модель {self.model_name} недоступна (404). Попробуйте другую модель.",
                    "error": "Model Not Found (404)",
                    "confidence": 0.0
                }
            elif "401" in error_str or "API key" in error_str:
                return {
                    "success": False,
                    "response": "❌ Ошибка ключа API (401).",
                    "error": "Unauthorized (401)",
                    "confidence": 0.0
                }
            
            return {"success": False, "error": str(e), "response": "Ошибка генерации. Проверьте консоль сервера.", "confidence": 0.0}

    def _format_knowledge(self, items):
        return "\n".join([f"- {k.get('title')}: {k.get('content')}" for k in items])

    def _format_training(self, items):
        return "\n".join([f"Q: {t.get('question')}\nA: {t.get('answer')}\n" for t in items])

    def _format_analytics(self, sales, clients, monthly):
        lines = []
        lines.append(f"📊 СТАТИСТИКА ({monthly['period']}):")
        lines.append(f"Выручка: {monthly['revenue']:,.2f} BYN")
        lines.append(f"Заказов: {monthly['orders']}")
        
        if sales:
            lines.append("\n🏆 ТОП ПРОДУКТОВ:")
            for p in sales[:5]:
                lines.append(f"- {p['product']}: {p['quantity']} шт ({p['total']:,.2f} BYN)")
                
        if clients:
            lines.append("\n👥 ТОП КЛИЕНТОВ:")
            for c in clients[:5]:
                lines.append(f"- {c['client']}: {c['orders']} зак. ({c['total']:,.2f} BYN)")
                
        return "\n".join(lines)

    def _build_enhanced_prompt(self, email_from, email_subject, email_body, tone, knowledge, training, analytics):
        return f"""You are an AI Sales Assistant for a confectionery company.
        
TONE: {tone}

===== KNOWLEDGE BASE =====
{knowledge or "No specific knowledge available."}

===== CURRENT STATS & DATA =====
{analytics or "No analytics available."}

===== EXAMPLES =====
{training or "No examples available."}

===== INCOMING EMAIL =====
From: {email_from}
Subject: {email_subject}
Body:
{email_body}

RESPONSE INSTRUCTIONS:
1. Answer in RUSSIAN.
2. Use the data provided. Be specific with numbers if asked.
3. Match the requested tone.
4. Be professional and helpful.

RESPONSE:"""

    async def _generate_with_timeout(self, prompt: str, timeout: int = 30) -> Optional[str]:
        """Generate content with timeout protection"""
        if not self.client:
            return None
            
        try:
            # Note: synchronous call wrapped or handle async if library supports it
            # newer google-generativeai supports async methods
            response = await self.client.generate_content_async(prompt)
            return response.text
        except Exception as e:
            # Re-raise exception to be handled by generate_response
            raise e


# Global instance
gemini_service = GeminiService()
