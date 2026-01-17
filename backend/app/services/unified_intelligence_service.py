"""
Unified Intelligence Service
The "Brain" of the system that orchestrates:
1. Intent Classification (Internal DB vs External Web vs Hybrid)
2. Smart Routing
3. Response Synthesis
4. Context Management
"""

from typing import Dict, List, Optional, Any, Union
import logging
import json
import uuid
from datetime import datetime
from openai import OpenAI
from app.config import settings
from app.services.sql_query_service import sql_query_service
from app.services.web_search_service import web_search_service
from app.services.company_knowledge_service import company_knowledge_service

logger = logging.getLogger(__name__)

# In-memory history for MVP (SessionID -> List[Message])
# TODO: Move to Redis or Postgres/Supabase for production
conversation_history: Dict[str, List[Dict]] = {}
MAX_HISTORY_LENGTH = 10

class UnifiedIntelligenceService:
    """
    Central service for handling intelligent user queries.
    Routes between SQL (Internal) and Web Search (External).
    """

    def __init__(self):
        # Prefer Groq for speed/formatting, fall back to OpenAI
        self.api_key = settings.groq_api_key or settings.openai_api_key
        self.base_url = "https://api.groq.com/openai/v1" if settings.groq_api_key else None
        self.model = "llama-3.3-70b-versatile" if settings.groq_api_key else settings.openai_model
        
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except Exception as e:
                logger.error(f"Failed to initialize Intelligence Client: {e}")

    def _get_history(self, session_id: str) -> List[Dict]:
        """Get flattened conversation history for prompt"""
        return conversation_history.get(session_id, [])

    def _save_to_history(self, session_id: str, role: str, content: str):
        """Save message to in-memory history"""
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add timestamp/metadata if specific structure needed
        conversation_history[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Truncate
        if len(conversation_history[session_id]) > MAX_HISTORY_LENGTH:
            conversation_history[session_id] = conversation_history[session_id][-MAX_HISTORY_LENGTH:]

    async def _classify_intent(self, query: str, history: List[Dict]) -> Dict[str, Any]:
        """
        Determine if query needs:
        - INTERNAL_DB (SQL)
        - EXTERNAL_WEB (Search)
        - HYBRID (Both)
        - CHAT (Just simple conversation)
        """
        if not self.client:
            return {"type": "CHAT", "reasoning": "No LLM configured"}

        system_prompt = """You are the Strategic Router for a Belarus-based Sales Analytics System.
        
        Context: You work for a confectionery company in Belarus with deep knowledge of:
        - Belarus geography (6 oblasts: Минская, Брестская, Гродненская, Гомельская, Могилевская, Витебская)
        - Regional logistics and distribution networks
        - Belarus tax system (20% VAT) and retail market specifics
        
        Capabilities:
        1. INTERNAL_DB: Access to 'sales', 'customers', 'products', 'agents' tables. Use this for specific sales data, revenue, quantities, employee performance, regional sales in Belarus.
        2. EXTERNAL_WEB: Access to internet search (Tavily). Use this for Belarus market news, inflation rates, competitor info, BYN exchange rates, regional economic conditions.
        3. HYBRID: Needs BOTH internal data AND external context (e.g., "compare our Brest sales vs regional economic trends").
        4. CHAT: Greeting, clarification, or questions not needing data.

        ALWAYS prioritize INTERNAL_DB first. Only use EXTERNAL_WEB if database cannot answer the question.
        
        Analyze the User Query and Context. 
        Return JSON:
        {
            "type": "INTERNAL_DB" | "EXTERNAL_WEB" | "HYBRID" | "CHAT",
            "reasoning": "Why you chose this",
            "search_queries": ["query1"] (if WEB or HYBRID),
            "sql_needed": true/false
        }
        """

        # Format history string
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"History:\n{history_str}\n\nCurrent Query: {query}"}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {"type": "CHAT", "reasoning": "Error in classification"}

    async def _synthesize_response(
        self, 
        query: str, 
        intent: Dict, 
        sql_result: Optional[Dict] = None, 
        web_result: Optional[Dict] = None,
        history: List[Dict] = []
    ) -> str:
        """Combine all data sources into a final natural language answer"""
        
        # Check if AI client is available
        if not self.client:
            return "Извините, AI-сервис недоступен. Пожалуйста, настройте GROQ_API_KEY или OPENAI_API_KEY в конфигурации системы."
        
        # Load company knowledge context
        try:
            company_context = company_knowledge_service.get_context_for_ai()
        except Exception as e:
            logger.warning(f"Failed to load company context: {e}")
            company_context = "(Контекст компании временно недоступен)"
        
        system_prompt = f"""Ты — стратегический AI-аналитик и Директор по развитию кондитерской компании в Беларуси.
        
        Твоя роль:
        - Искать возможности для роста и предупреждать о рисках
        - Эксперт по рынку Беларуси: знаешь географию (области, райцентры), логистические цепочки, налоговое законодательство РБ и специфику ритейла
        - ВСЕГДА сначала смотришь в исторические данные продаж (БД). Если данных не хватает — идёшь в интернет (Web Search)
        - НИКОГДА не выдумываешь факты. Если данных недостаточно, честно говоришь об этом
        
        {company_context}
        
        Правила ответа:
        1. Отвечай на русском языке.
        2. Цитируй источники (например, "По данным нашей базы..." или "Согласно новостям...").
        3. Если внутренние данные противоречат внешним, укажи на это.
        4. Будь кратким, но обстоятельным.
        5. Давай стратегические рекомендации, а не просто цифры.
        6. Учитывай региональную специфику Беларуси в своих советах.
        
        Источники данных:
        """
        
        data_context = ""
        if sql_result and sql_result.get("success"):
            data_context += f"\n[ВНУТРЕННЯЯ БАЗА ДАННЫХ]:\nЗапрос: {sql_result.get('sql')}\nРезультаты: {str(sql_result.get('data'))}\nПояснение: {sql_result.get('explanation')}\n"
        
        if web_result and web_result.get("success"):
            data_context += f"\n[ВНЕШНИЙ ВЕБ-ПОИСК]:\nСводка: {web_result.get('summary')}\nДетали: {str(web_result.get('results'))}\n"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {query}\n\nData Context:\n{data_context}"}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI synthesis error: {e}")
            # Return data summary instead of crashing
            if sql_result or web_result:
                return f"Извините, возникла ошибка при генерации ответа, но вот доступные данные:\n{data_context}"
            return f"Извините, не удалось обработать запрос: {str(e)}"

    async def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Main entry point.
        1. Classify
        2. Execute Tools
        3. Synthesize
        4. Save History
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            
        history = self._get_history(session_id)
        
        # 1. Classify Intent
        classification = await self._classify_intent(message, history)
        query_type = classification.get("type", "CHAT")
        sources = []
        
        sql_data = None
        web_data = None
        
        # 2. Execute Tools
        try:
            # Internal DB
            if query_type in ["INTERNAL_DB", "HYBRID"]:
                # Pass the classification context to SQL service if needed, or just the raw query
                # Maybe improve prompt to be more specific based on classification?
                # For now, just pass the user query + relevant history context? 
                # Actually SQLQueryService takes just a natural language string.
                # Let's verify if we need to refine the question.
                
                sql_data = await sql_query_service.query_from_question(message)
                sources.append({
                    "type": "internal",
                    "status": "success" if sql_data["success"] else "error",
                    "details": sql_data.get("sql") or sql_data.get("error")
                })

            # External Web
            if query_type in ["EXTERNAL_WEB", "HYBRID"]:
                search_queries = classification.get("search_queries", [message])
                # Execute primary search query
                q = search_queries[0] if search_queries else message
                
                # Use news search if it seems like news, otherwise general
                # For simplicity, let's look at keywords or default to general/market
                if "news" in message.lower() or "новости" in message.lower():
                    web_data = await web_search_service.search_news(q)
                else:
                    web_data = await web_search_service.search(q, search_depth="advanced")
                    
                sources.append({
                    "type": "external",
                    "status": "success" if web_data["success"] else "error",
                    "details": [r['url'] for r in web_data.get('results', [])]
                })

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            # Continue to synthesis even if tools fail (to explain error)

        # 3. Synthesize
        if query_type == "CHAT":
            # Simple chat approach without data context handling overhead
            response_text = await self._synthesize_response(message, classification, None, None, history)
        else:
            response_text = await self._synthesize_response(message, classification, sql_data, web_data, history)

        # 4. Update History
        self._save_to_history(session_id, "user", message)
        self._save_to_history(session_id, "assistant", response_text)

        return {
            "response": response_text,
            "session_id": session_id,
            "classification": classification,
            "sources": sources,
            "debug_sql": sql_data,
            "debug_web": web_data
        }

# Global Singleton
unified_intelligence_service = UnifiedIntelligenceService()
