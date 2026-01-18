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

        system_prompt = """You are the Strategic Router for a Sales Analytics System.
        
        CRITICAL: You have access to a LIVE DATABASE with REAL sales data:
        - 22,513 sales records
        - 563 products with real names (FINISH, CALGON, CILLIT BANG, etc.)
        - Real agent names and performance data
        - Complete sales history
        
        ROUTING RULES (STRICT PRIORITY ORDER):
        
        1. INTERNAL_DB (HIGHEST PRIORITY): Use for ANY question about:
           - Sales numbers ("сколько продаж", "какой объем")
           - Products ("топ товар", "какие товары", "продукты")
           - Statistics ("статистика", "аналитика", "данные")
           - Agents ("кто лучший агент", "продавцы")
           - Revenue/money ("выручка", "доход")
           - Time periods ("за месяц", "в январе")
           ALWAYS set sql_needed=true for these queries!
        
        2. EXTERNAL_WEB: ONLY for external market data:
           - Belarus economy news
           - Competitor information
           - Exchange rates
           
        3. HYBRID: When explicitly comparing internal data with external trends
        
        4. CHAT: Only greetings ("привет", "hello")
        
        5. CLARIFY: Only if query is completely ambiguous
        
        CRITICAL RULES:
        - If query mentions numbers, data, statistics → INTERNAL_DB
        - If query asks "сколько", "какой", "топ" → INTERNAL_DB  
        - DO NOT use CHAT for data questions!
        - DO NOT use knowledge base for statistics!
        - ALWAYS prefer INTERNAL_DB over general knowledge!
        
        Analyze the User Query and Context. 
        Return JSON:
        {
            "type": "INTERNAL_DB" | "EXTERNAL_WEB" | "HYBRID" | "CHAT" | "CLARIFY",
            "confidence": 0.0-1.0 (how sure are you),
            "reasoning": "Why you chose this",
            "clarifying_question": "Question to ask user" (if CLARIFY),
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
        
        # CRITICAL: Only use company context if NO SQL data available
        company_context = ""
        if sql_result and sql_result.get("success") and sql_result.get("data"):
            # We have real database data - DON'T use knowledge base!
            company_context = "(Using live database data - knowledge base disabled)"
        else:
            # No SQL data - fallback to knowledge base
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
        
        ОБЯЗАТЕЛЬНОЕ ТРЕБОВАНИЕ: Перед ответом выведи свои рассуждения в тегах <thought>...</thought>.
        В тегах опиши:
        - Что ты понял из вопроса
        - Какие данные у тебя есть
        - Как ты пришёл к выводу
        Затем дай финальный ответ БЕЗ тегов.
        
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
                temperature=0.2  # Lower for factual synthesis (was 0.5)
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
        
        # 1. Classify Intent with confidence tracking
        classification = await self._classify_intent(message, history)
        query_type = classification.get("type", "CHAT")
        confidence = classification.get("confidence", 0.7)
        sources = []
        
        # REASONING TRACE: Log classification decision  
        logger.info(f"[THOUGHT] Query classified as: {query_type} (confidence: {confidence:.2f})")
        logger.info(f"[THOUGHT] Reasoning: {classification.get('reasoning', 'N/A')}")
        
        # CLARIFY: If confidence too low, ask clarifying question instead of guessing
        if query_type == "CLARIFY" or (confidence < 0.8 and query_type not in ["CHAT"]):
            clarifying_question = classification.get("clarifying_question", 
                "Не совсем понял ваш вопрос. Пожалуйста, уточните!")
            
            logger.info(f"[THOUGHT] Low confidence ({confidence:.2f}) - requesting clarification")
            
            self._save_to_history(session_id, "user", message)
            self._save_to_history(session_id, "assistant", clarifying_question)
            
            return {
                "response": clarifying_question,
                "session_id": session_id,
                "sources": [],
                "classification": classification,
                "needs_clarification": True
            }
        
        sql_data = None
        web_data = None
        
        # 2. Execute Tools
        try:
            # Internal DB
            if query_type in ["INTERNAL_DB", "HYBRID"]:
                logger.info(f"[THOUGHT] Executing SQL query for question")
                sql_data = await sql_query_service.query_from_question(message)
                
                if sql_data:
                    logger.info(f"[THOUGHT] SQL: {sql_data.get('sql', 'N/A')[:100]}...")
                    logger.info(f"[THOUGHT] SQL returned {sql_data.get('row_count', 0)} rows")
                    if sql_data.get('summary'):
                        logger.info(f"[THOUGHT] Large dataset summarized: {sql_data['summary']['total_rows']} rows")
                
                sources.append({
                    "type": "internal",
                    "status": "success" if sql_data.get("success") else "error",
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

        # 4. SELF-REFLECTION: Quality Scoring
        quality_score = self._calculate_quality_score(
            query_type=query_type,
            confidence=confidence,
            sql_data=sql_data,
            web_data=web_data,
            response=response_text
        )
        
        logger.info(f"[SELF-REFLECTION] Quality Score: {quality_score}/10")
        
        # Add disclaimer if quality is low
        if quality_score < 5:
            disclaimer = "\n\n⚠️ **Низкая точность ответа**: Недостаточно данных для полноценного анализа. Рекомендую уточнить вопрос или указать конкретный период."
            response_text += disclaimer
            logger.warning(f"[SELF-REFLECTION] Low quality response (score: {quality_score}) - disclaimer added")

        # 5. Update History
        self._save_to_history(session_id, "user", message)
        self._save_to_history(session_id, "assistant", response_text)

        return {
            "response": response_text,
            "session_id": session_id,
            "classification": classification,
            "sources": sources,
            "quality_score": quality_score,
            "debug_sql": sql_data,
            "debug_web": web_data
        }
    
    def _calculate_quality_score(self, query_type: str, confidence: float, 
                                  sql_data: Optional[Dict], web_data: Optional[Dict],
                                  response: str) -> int:
        """
        Self-Reflection: Calculate quality score (1-10) based on:
        1. Data Grounding: Do we have actual data from DB/Web?
        2. Query Clarity: Was classification confident?
        3. Response Quality: Is response substantive?
        
        Returns:
            int: Quality score 1-10
        """
        score = 5  # Start at neutral
        
        # Factor 1: Data Grounding (0-4 points)
        has_db_data = sql_data and sql_data.get("success") and sql_data.get("row_count", 0) > 0
        has_web_data = web_data and web_data.get("success") and len(web_data.get("results", [])) > 0
        
        if has_db_data:
            score += 3  # Strong grounding in internal data
            logger.info(f"[QUALITY] +3 for DB data ({sql_data.get('row_count')} rows)")
        if has_web_data:
            score += 2  # Additional external context
            logger.info(f"[QUALITY] +2 for web data ({len(web_data.get('results', []))} results)")
        
        if not has_db_data and not has_web_data and query_type != "CHAT":
            score -= 3  # No data for a data question
            logger.warning(f"[QUALITY] -3 for no data on {query_type} query")
        
        # Factor 2: Query Clarity (0-3 points)
        if confidence >= 0.9:
            score += 2
            logger.info(f"[QUALITY] +2 for high confidence ({confidence:.2f})")
        elif confidence >= 0.7:
            score += 1
            logger.info(f"[QUALITY] +1 for medium confidence ({confidence:.2f})")
        elif confidence < 0.5:
            score -= 2
            logger.warning(f"[QUALITY] -2 for low confidence ({confidence:.2f})")
        
        # Factor 3: Response Quality (0-3 points)
        response_length = len(response)
        if response_length > 200:
            score += 1  # Substantive response
        if "По данным" in response or "Согласно" in response:
            score += 1  # Cites sources
        if "Извините" in response or "не удалось" in response:
            score -= 1  # Error in response
        
        # Clamp to 1-10
        score = max(1, min(10, score))
        
        return score

# Global Singleton
unified_intelligence_service = UnifiedIntelligenceService()
