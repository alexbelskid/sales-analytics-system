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
        # Use Groq for speed/formatting
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"
        
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
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎯 CRITICAL: FULL DATABASE ACCESS (STEP 3 FIX)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        You have access to a LIVE DATABASE with COMPLETE REAL data:
        ✅ 22,513 sales records (FULL ACCESS via SQL)
        ✅ 563 products with real names (ALL available)
        ✅ All agent names and complete performance data
        ✅ Complete sales history (no limits on queries)
        
        KEY CAPABILITY: You can retrieve ALL data through SQL queries!
        - "Покажи все товары" → SQL returns ALL 563 products (no limit)
        - "Полный список агентов" → SQL returns ALL agents
        - "Все продажи за год" → SQL returns ALL matching sales
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📋 ROUTING RULES (STRICT PRIORITY ORDER):
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        1. INTERNAL_DB (HIGHEST PRIORITY - 90% of queries):
           Use for ANY question about internal business data:
           
           📊 Sales & Revenue:
              - "сколько продаж", "какой объем", "выручка", "доход"
              - "продажи за период", "динамика продаж"
           
           📦 Products:
              - "топ товар", "какие товары", "все продукты"
              - "товары категории X", "список товаров"
              - REMEMBER: User can ask for ALL products!
           
           👥 Agents & Performance:
              - "кто лучший агент", "все продавцы", "агенты региона"
              - "план выполнения", "статистика агентов"
           
           📈 Statistics & Analytics:
              - "статистика", "аналитика", "данные", "показатели"
              - "средний чек", "общая сумма", "количество"
           
           📅 Time-based queries:
              - "за месяц", "в январе", "за год", "последние 30 дней"
           
           🎯 List queries (IMPORTANT!):
              - "все", "полный список", "покажи все", "complete list"
              - "список всех X" → INTERNAL_DB, sql_needed=true
           
           ⚠️  ALWAYS set sql_needed=true for these queries!
        
        2. EXTERNAL_WEB (LOW PRIORITY - <5% of queries):
           ONLY for external market data NOT in our database:
           - Belarus economy news (макроэкономика)
           - Competitor information (конкуренты)
           - Exchange rates (курсы валют)
           - Industry trends (тренды отрасли)
           
        3. HYBRID (RARE - <3% of queries):
           Only when explicitly comparing internal vs external:
           - "Как наши продажи на фоне рынка Беларуси?"
           - "Сравни наш рост с индустрией"
           
        4. CHAT (MINIMAL - <2% of queries):
           Only for greetings and small talk:
           - "привет", "hello", "как дела"
           - NO data questions here!
           
        5. CLARIFY (RARE):
           Only if query is completely ambiguous
           - NOT for data questions (assume INTERNAL_DB)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🚨 CRITICAL DECISION RULES:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        ✅ IF query mentions ANY of these → INTERNAL_DB:
           - numbers, data, statistics, analytics
           - "сколько", "какой", "топ", "список", "все"
           - products, agents, sales, customers
           - dates, periods, trends
        
        ❌ DO NOT use CHAT for data questions!
        ❌ DO NOT use knowledge base for statistics!
        ❌ ALWAYS prefer INTERNAL_DB over general knowledge!
        
        💡 REMEMBER: You have FULL database access - never say "I only see partial data"
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        Analyze the User Query and Context. 
        Return JSON:
        {
            "type": "INTERNAL_DB" | "EXTERNAL_WEB" | "HYBRID" | "CHAT" | "CLARIFY",
            "confidence": 0.0-1.0 (how sure are you),
            "reasoning": "Why you chose this route (mention full DB access if INTERNAL_DB)",
            "clarifying_question": "Question to ask user" (if CLARIFY),
            "search_queries": ["query1"] (if WEB or HYBRID),
            "sql_needed": true/false (true for INTERNAL_DB with data queries)
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
            return "Извините, AI-сервис недоступен. Пожалуйста, настройте GROQ_API_KEY в конфигурации системы."
        
        # HYBRID APPROACH: Use BOTH SQL data AND knowledge base context
        # SQL gives us FACTS (numbers, names, dates)
        # Knowledge base gives us CONTEXT (business rules, market insights)
        # Agent analytics gives us REAL AGENT DATA (performance, sales, rankings)
        
        company_context = ""
        agent_context = ""  # NEW: Real agent data context
        sql_facts = ""
        
        # Always try to load company knowledge for context
        try:
            company_context = company_knowledge_service.get_context_for_ai()
        except Exception as e:
            logger.warning(f"Failed to load company context: {e}")
            company_context = "(Контекст компании временно недоступен)"
        
        # NEW: Load agent analytics context from REAL DATABASE
        try:
            from app.services.ai_context_service import ai_context
            agent_context = ai_context.get_context_for_ai(
                include_agents=True,  # Agent analytics
                include_general=False,  # Already have from company_knowledge
                include_imports=True  # Show data sources
            )
            if agent_context:
                logger.info(f"[CONTEXT] Loaded agent analytics context: {len(agent_context)} chars")
        except Exception as e:
            logger.warning(f"Failed to load agent context: {e}")
            agent_context = ""
        
        # STEP 1 FIX: Load COMPLETE data catalog for AI
        catalog_context = ""
        try:
            from app.services.enhanced_data_context_service import enhanced_data_context
            data_catalog = await enhanced_data_context.get_data_catalog()
            
            catalog_context = f"""
📊 ПОЛНЫЙ КАТАЛОГ ДАННЫХ В БАЗЕ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ДОСТУП К ДАННЫМ: ПОЛНЫЙ (через SQL запросы)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 ОБЪЕМ ДАННЫХ:
  • Всего продаж в БД: {data_catalog.total_sales:,} записей
  • Всего клиентов: {data_catalog.total_customers:,} записей
  • Всего товаров: {data_catalog.total_products:,} записей
  • Всего агентов: {data_catalog.total_agents:,} записей

📅 ВРЕМЕННОЙ ПЕРИОД:
  • Начало данных: {data_catalog.date_range_start or 'Не указано'}
  • Конец данных: {data_catalog.date_range_end or 'Не указано'}
  • Последний импорт: {data_catalog.last_import_date or 'Не указано'}

📦 КАТЕГОРИИ ТОВАРОВ ({len(data_catalog.categories)}):
  {', '.join(data_catalog.categories[:15])}
  {"..." if len(data_catalog.categories) > 15 else ""}

🌍 РЕГИОНЫ ({len(data_catalog.regions)}):
  {', '.join(data_catalog.regions)}

📁 ИСТОЧНИКИ ДАННЫХ:
  {', '.join(data_catalog.data_sources[:5]) if data_catalog.data_sources else 'Нет данных об импорте'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  КРИТИЧЕСКИ ВАЖНО:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ты имеешь доступ к ПОЛНОЙ базе данных через SQL запросы!

Для запросов типа:
  • "покажи ВСЕ товары" → SQL БЕЗ LIMIT
  • "полный список клиентов" → SQL БЕЗ LIMIT
  • "топ 10 товаров" → SQL с LIMIT 10
  • "средняя выручка" → SQL с агрегацией (COUNT/SUM/AVG)

НЕ говори "я вижу только часть данных" - у тебя ПОЛНЫЙ доступ!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            logger.info(f"[CONTEXT] Loaded data catalog: {data_catalog.total_sales} sales, {data_catalog.total_products} products")
        except Exception as e:
            logger.warning(f"Failed to load data catalog: {e}")
            catalog_context = ""
        
        # Extract SQL facts if available
        if sql_result and sql_result.get("success") and sql_result.get("data"):
            data = sql_result.get("data", [])
            if isinstance(data, list) and len(data) > 0:
                sql_facts = f"DATABASE FACTS (PRIORITY): {len(data)} records retrieved\n"
                sql_facts += f"Sample data: {str(data[:3])}\n"
            elif isinstance(data, dict):
                sql_facts = f"DATABASE FACTS (PRIORITY): {data}\n"
        
        # Combine ALL sources (SQL facts, Data Catalog, Agent data, Business context)
        context_parts = []
        if sql_facts:
            context_parts.append(sql_facts)
        if catalog_context:  # STEP 1 FIX: Add complete data catalog first!
            context_parts.append(catalog_context)
        if agent_context:
            context_parts.append(f"AGENT ANALYTICS (REAL DATA FROM DB):\n{agent_context}")
        if company_context:
            context_parts.append(f"BUSINESS CONTEXT:\n{company_context}")
        
        combined_context = "\n\n".join(context_parts) if context_parts else "No data available"
        
        system_prompt = f"""Ты — AI-аналитик для системы аналитики продаж.
        
        ЗАДАЧА: Дай точный, основанный на ФАКТАХ ответ.
        
        ИСТОЧНИКИ ДАННЫХ (в порядке приоритета):
        1. DATABASE FACTS - РЕАЛЬНЫЕ данные из базы (ВСЕГДА используй в первую очередь!)
        2. DATA CATALOG - ПОЛНАЯ информация о доступных данных
        3. BUSINESS CONTEXT - Контекст компании для понимания
        4. External Web - Рыночные данные (если есть)
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎯 КРИТИЧЕСКИЕ ПРАВИЛА ДОСТУПА К ДАННЫМ:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        ✅ У ТЕБЯ ЕСТЬ ПОЛНЫЙ ДОСТУП КО ВСЕЙ БАЗЕ ДАННЫХ!
        
        Через SQL ты можешь получить:
          • ВСЕ {combined_context.count('товаров')} товары (без ограничений!)
          • ВСЕ продажи (десятки тысяч записей)
          • ВСЕ данные по агентам, клиентам, категориям
        
        НИКОГДА не говори: "я вижу только часть данных"
        НИКОГДА не говори: "нужно больше информации для полного анализа"
        
        ❌ ЕСЛИ DATABASE FACTS ПУСТЫЕ:
          → Это значит SQL запрос не вернул данных
          → Скажи: "По вашему запросу данных не найдено в базе"
        
        ✅ ЕСЛИ ЕСТЬ DATABASE FACTS:
          → Базируй ответ ТОЛЬКО на них
          → Приводи точные цифры, имена, даты
          → НЕ придумывай данные!
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        ФОРМАТ ОТВЕТА:
        1. Прямой ответ с цифрами из DATABASE FACTS
        2. Краткое объяснение/контекст из BUSINESS CONTEXT
        3. Инсайты и рекомендации (если применимо)
        
        Доступные данные:
        {combined_context}
        
        ОБЯЗАТЕЛЬНОЕ ТРЕБОВАНИЕ: Перед ответом выведи свои рассуждения в тегах <thought>...</thought>.
        В тегах опиши:
        - Что ты понял из вопроса
        - Какие данные у тебя есть (из DATABASE FACTS и DATA CATALOG)
        - Как ты пришёл к выводу
        - Достаточно ли данных для ответа (ПОМНИ: у тебя ПОЛНЫЙ доступ через SQL!)
        Затем дай финальный ответ БЕЗ тегов.
        
        Правила ответа:
        1. Отвечай на русском языке.
        2. Цитируй источники (например, "По данным нашей базы..." или "Согласно SQL запросу...").
        3. Если внутренние данные противоречат внешним, укажи на это.
        4. Будь кратким, но обстоятельным.
        5. Давай инсайты и рекомендации на основе ФАКТОВ.
        6. ВСЕГДА помни: у тебя ПОЛНЫЙ доступ к базе данных!
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
