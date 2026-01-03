import logging
from typing import Optional, Dict, Any, List
from groq import Groq
from app.config import get_settings
from app.database import supabase

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        settings = get_settings()
        self.client = None
        if settings.groq_api_key:
            try:
                self.client = Groq(api_key=settings.groq_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        self.model = "llama-3.3-70b-versatile"
    
    def check_status(self) -> dict:
        if not self.client:
             return {
                "available": False,
                "error": "API Key not configured"
            }
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return {
                "available": True,
                "model": self.model,
                "quota_ok": True
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    async def generate_response(
        self,
        email_from: str,
        email_subject: str,
        email_body: str,
        tone: str = "professional",
        knowledge_base: Optional[str] = None,
        training_examples: Optional[str] = None,
        include_analytics: bool = True
    ) -> str:
        if not self.client:
            raise Exception("Groq API key not configured")
        
        try:
            # 1. Fetch Context Data
            knowledge_text = self._get_knowledge_context(knowledge_base)
            training_text = self._get_training_context(training_examples)
            analytics_text = self._get_analytics_context(include_analytics)
            
            # 2. Build Prompt
            prompt = self._build_prompt(
                email_from, email_subject, email_body, tone,
                knowledge_text, training_text, analytics_text
            )
            
            # 3. Generate
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI Sales Assistant for a confectionery company."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise Exception(f"Groq API error: {str(e)}")

    def _get_knowledge_context(self, provided_kb: Optional[str]) -> str:
        if provided_kb:
            return provided_kb
            
        if not supabase:
            return ""
            
        try:
            res = supabase.table("knowledge_base").select("title, content").execute()
            if res.data:
                return "\n".join([f"- {k.get('title')}: {k.get('content')}" for k in res.data])
        except Exception as e:
            logger.warning(f"Failed to fetch knowledge: {e}")
            
        return ""

    def _get_training_context(self, provided_examples: Optional[str]) -> str:
        if provided_examples:
            return provided_examples
            
        if not supabase:
            return ""
            
        try:
            res = supabase.table("training_examples").select("question, answer").limit(10).execute()
            if res.data:
                return "\n".join([f"Q: {t.get('question')}\nA: {t.get('answer')}\n" for t in res.data])
        except Exception as e:
            logger.warning(f"Failed to fetch training: {e}")
            
        return ""

    def _get_analytics_context(self, include: bool) -> str:
        if not include:
            return ""
            
        try:
            # Import inside method to avoid circular imports if any
            from app.services.analytics_service import AnalyticsService
            analytics = AnalyticsService()
            
            sales = analytics.get_sales_summary()
            clients = analytics.get_clients_summary()
            monthly = analytics.get_monthly_stats()
            
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
            
        except Exception as e:
            logger.warning(f"Failed to fetch analytics: {e}")
            return ""

    def _build_prompt(self, email_from, email_subject, email_body, tone, knowledge, training, analytics):
        return f"""
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
