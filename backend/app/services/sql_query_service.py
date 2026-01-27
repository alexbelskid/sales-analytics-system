"""
SQL Query Service - Natural Language to SQL
Generates and executes safe SQL queries from user questions
"""

from typing import Dict, List, Optional, Any
import logging
import sqlparse
from statistics import mean
from groq import Groq
from app.config import settings
from app.database import supabase
from app.services.secure_query_service import secure_query_service, SecurityViolationError

logger = logging.getLogger(__name__)


class SQLQueryService:
    """Service for generating SQL queries from natural language"""
    
    # Database schema for LLM context
    SCHEMA_CONTEXT = """
    Database Schema for Sales Analytics System:
    
    TABLES:
    
    1. sales (Продажи)
       - id: UUID (primary key)
       - customer_id: UUID (foreign key to customers)
       - agent_id: UUID (foreign key to agents)
       - sale_date: DATE
       - total_amount: DECIMAL (общая сумма)
       - discount: DECIMAL (скидка)
       - status: VARCHAR (completed, pending, cancelled)
       - notes: TEXT
       - created_at: TIMESTAMPTZ
    
    2. sale_items (Позиции продаж)
       - id: UUID
       - sale_id: UUID (foreign key to sales)
       - product_id: UUID (foreign key to products)
       - quantity: INTEGER (количество)
       - unit_price: DECIMAL (цена за единицу)
       - discount: DECIMAL
       - amount: DECIMAL (сумма позиции)
    
    3. customers (Клиенты)
       - id: UUID
       - name: VARCHAR (имя клиента)
       - email: VARCHAR
       - phone: VARCHAR
       - company: VARCHAR (компания)
       - address: TEXT
    
    4. products (Товары)
       - id: UUID
       - name: VARCHAR (название товара) -- NOTE: column is 'name', NOT 'product_name'
       - normalized_name: VARCHAR (нормализованное название)
       - category: VARCHAR (категория)
       - total_quantity: INTEGER (общее количество)
       - total_revenue: DECIMAL (общая выручка)
       - sales_count: INTEGER (количество продаж)
    
    5. agents (Агенты/Менеджеры)
       - id: UUID
       - name: VARCHAR (имя агента)
       - email: VARCHAR
       - phone: VARCHAR
       - base_salary: DECIMAL (базовая зарплата)
       - commission_rate: DECIMAL (процент комиссии)
       - is_active: BOOLEAN
    
    6. salary_calculations (Расчёты зарплат)
       - id: UUID
       - agent_id: UUID
       - year: INTEGER
       - month: INTEGER
       - base_salary: DECIMAL
       - sales_amount: DECIMAL (сумма продаж)
       - commission: DECIMAL (комиссия)
       - bonus: DECIMAL
       - total_salary: DECIMAL
    
    IMPORTANT NOTES:
    - All monetary values are in Belarusian Rubles (BYN)
    - Dates are in format YYYY-MM-DD
    - To get sales with product details, JOIN sales -> sale_items -> products
    - To get sales with customer details, JOIN sales -> customers
    - To get sales with agent details, JOIN sales -> agents
    
    ANALYTICS VIEWS (for comprehensive analysis, use these instead of complex JOINs):
    
    7. sales_analytics_complete (Полная аналитика продаж)
       - id, sale_date, total_amount, discount, status
       - agent_name, agent_email, agent_phone
       - customer_name, customer_email
       - items_count, total_items_quantity
       - products (comma-separated list)
       Use for: Complete sales overview with all related data
    
    8. product_performance (Производительность товаров)
       - id, name, category
       - total_quantity, total_revenue, sales_count
       - unique_sales, avg_price, max_price, min_price
       - last_sale_date
       Use for: Product analysis and performance metrics
    
    9. agent_performance (Производительность агентов)
       - id, name, email, phone
       - base_salary, commission_rate
       - total_sales, total_revenue, avg_sale_amount
       - first_sale_date, last_sale_date, unique_customers
       Use for: Agent performance and commission calculations
    
    10. daily_sales_summary (Ежедневная сводка продаж)
        - sale_day, sales_count, total_revenue
        - avg_sale_amount, active_agents, unique_customers
        Use for: Daily trends and patterns
    
    11. top_products_by_revenue (Топ товары по выручке)
        - name, category, total_revenue
        - total_quantity, sales_count, avg_price_per_unit
        Use for: Best performing products
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎯 DATA ACCESS POLICY (STEP 2 FIX - CRITICAL):
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ✅ YOU HAVE FULL ACCESS TO ALL DATA:
      • 22,000+ sales records
      • 500+ products
      • All agents, customers, categories
    
    📋 LIMIT STRATEGY:
      1. "топ N", "первые N", "лучшие N" → LIMIT N
      2. "все", "полный список", "complete" → NO LIMIT
      3. Aggregations (COUNT/SUM/AVG/MAX/MIN) → NO LIMIT
      4. Vague queries ("покажи продажи") → LIMIT 100 (safety)
      5. NEVER limit when user explicitly asks for "all"
    
    🚀 PERFORMANCE TIPS:
      • Use views for better performance on complex queries
      • Add indexes in WHERE clauses for speed
      • Use EXPLAIN ANALYZE to check query performance
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    # Allowed tables (whitelist for security)
    ALLOWED_TABLES = {
        "sales", "sale_items", "customers", "products", "agents", "salary_calculations"
    }
    
    # Sample queries for few-shot learning (STEP 2 FIX - Smart LIMIT examples)
    SAMPLE_QUERIES = """
    EXAMPLES OF SMART LIMIT USAGE:
    
    Q: "Сколько мы продали в мае 2025?" (Aggregation - NO LIMIT needed)
    SQL: SELECT SUM(total_amount) as total FROM sales WHERE sale_date >= '2025-05-01' AND sale_date < '2025-06-01';
    
    Q: "Топ 5 продуктов по продажам за последний месяц" (Explicit "топ 5" - USE LIMIT 5)
    SQL: SELECT p.name, SUM(si.quantity) as total_qty, SUM(si.amount) as total_amount 
         FROM sale_items si 
         JOIN products p ON si.product_id = p.id 
         JOIN sales s ON si.sale_id = s.id 
         WHERE s.sale_date >= CURRENT_DATE - INTERVAL '1 month' 
         GROUP BY p.name 
         ORDER BY total_amount DESC 
         LIMIT 5;
    
    Q: "Все товары с продажами" (User wants ALL - NO LIMIT!)
    SQL: SELECT name, total_quantity, total_revenue, sales_count 
         FROM product_performance 
         WHERE total_quantity > 0 
         ORDER BY total_revenue DESC;
    
    Q: "Покажи полный список агентов" (User wants COMPLETE list - NO LIMIT!)
    SQL: SELECT name, email, region, is_active 
         FROM agents 
         ORDER BY name;
    
    Q: "Статистика по всем агентам" (ALL agents - NO LIMIT!)
    SQL: SELECT name, total_sales, total_revenue, avg_sale_amount, unique_customers 
         FROM agent_performance 
         WHERE total_sales > 0 
         ORDER BY total_revenue DESC;
    
    Q: "Сколько всего продаж?" (COUNT aggregation - NO LIMIT needed)
    SQL: SELECT COUNT(*) as total_sales, SUM(total_amount) as total_revenue 
         FROM sales;
    
    Q: "Продажи за последнюю неделю" (Vague query - safety LIMIT 100)
    SQL: SELECT * FROM sales_analytics_complete 
         WHERE sale_date >= CURRENT_DATE - INTERVAL '7 days' 
         ORDER BY sale_date DESC 
         LIMIT 100;
    
    Q: "Какой агент продал больше всего в прошлом квартале?" (Only need best - LIMIT 1)
    SQL: SELECT a.name, SUM(s.total_amount) as total 
         FROM sales s 
         JOIN agents a ON s.agent_id = a.id 
         WHERE s.sale_date >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months')
           AND s.sale_date < DATE_TRUNC('quarter', CURRENT_DATE)
         GROUP BY a.name 
         ORDER BY total DESC 
         LIMIT 1;
    
    Q: "Все продажи молочных продуктов в апреле" (User wants ALL - NO LIMIT!)
    SQL: SELECT p.name, SUM(si.quantity) as qty, SUM(si.amount) as amount
         FROM sale_items si
         JOIN products p ON si.product_id = p.id
         JOIN sales s ON si.sale_id = s.id
         WHERE p.category LIKE '%молоч%' 
           AND s.sale_date >= '2025-04-01' 
           AND s.sale_date < '2025-05-01'
         GROUP BY p.name
         ORDER BY amount DESC;
    
    Q: "Покажи все категории товаров" (DISTINCT query for reference data - NO LIMIT!)
    SQL: SELECT DISTINCT category, COUNT(*) as products_count 
         FROM products 
         WHERE category IS NOT NULL 
         GROUP BY category 
         ORDER BY products_count DESC;
    """
    
    def __init__(self):
        """Initialize SQL query service with GROQ"""
        self.client = Groq(api_key=settings.groq_api_key)
        self.supabase = supabase
    
    def is_available(self) -> bool:
        """Check if SQL query generation is available"""
        return self.client is not None and supabase is not None
    
    async def generate_sql(self, question: str) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question
        
        Args:
            question: User question in natural language (Russian or English)
            
        Returns:
            {
                "success": bool,
                "sql": str,
                "explanation": str,
                "error": Optional[str]
            }
        """
        if not self.client:
            return {
                "success": False,
                "sql": "",
                "explanation": "",
                "error": "OpenAI API not configured"
            }
        
        system_prompt = f"""You are an expert SQL query generator for a Belarus-based sales analytics system.
        
        Context: You work for a confectionery company in Belarus. Consider:
        - Regional specifics: 6 oblasts (Минская, Брестская, Гродненская, Гомельская, Могилевская, Витебская)
        - Currency: All monetary values are in BYN (Belarusian Rubles)
        - Tax system: 20% VAT applies to sales
        - Logistics: Major transport corridors М1, М5, М6
        - Retail: Mix of hypermarkets (Евроопт, Корона) and regional chains
        
{self.SCHEMA_CONTEXT}

{self.SAMPLE_QUERIES}

RULES:
1. Generate PostgreSQL-compatible SQL queries
2. Use ONLY the tables listed in the schema
3. Return ONLY valid SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
4. Use proper JOINs when needed
5. Add meaningful column aliases (as total, as count, etc.)
6. For date ranges, use proper date functions
7. SMART LIMIT USAGE (STEP 2 FIX - CRITICAL):
   - For "топ N", "первые N", "лучшие N" → use LIMIT N
   - For "все", "полный список", "complete list" → NO LIMIT (return ALL data)
   - For aggregations (COUNT, SUM, AVG, MAX, MIN) → NO LIMIT needed
   - For exploratory queries without specific "all" or "top N" → LIMIT 100 (safety)
   - NEVER arbitrarily limit data when user asks for "all" or "complete"
   - Maximum safety limit: 10,000 rows (only for unbounded queries)
8. Use Russian column aliases when appropriate (as итого, as количество)
9. Consider regional analysis when customer addresses or agent locations are relevant
10. When analyzing sales trends, consider Belarus market seasonality

EXAMPLES OF LIMIT USAGE:
  ✅ "Покажи все товары" → SELECT * FROM products ORDER BY name; (NO LIMIT!)
  ✅ "Топ 10 продуктов" → SELECT * FROM products LIMIT 10;
  ✅ "Сколько всего продаж?" → SELECT COUNT(*) FROM sales; (NO LIMIT!)
  ✅ "Список агентов" → SELECT * FROM agents; (NO LIMIT - they asked for all)
  ⚠️  "Покажи продажи" → SELECT * FROM sales LIMIT 100; (safety limit for vague query)


Return your response in this JSON format:
{{
    "sql": "SELECT ... FROM ...",
    "explanation": "Brief explanation in Russian of what this query does and its strategic value"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # GROQ model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate SQL query for: {question}"}
                ],
                temperature=0.1,  # Low temperature for more consistent SQL
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            sql = result.get("sql", "")
            explanation = result.get("explanation", "")
            
            # Validate the generated SQL
            validation = self._validate_sql(sql)
            if not validation["valid"]:
                return {
                    "success": False,
                    "sql": sql,
                    "explanation": explanation,
                    "error": f"SQL validation failed: {validation['error']}"
                }
            
            return {
                "success": True,
                "sql": sql,
                "explanation": explanation,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"SQL generation error: {e}")
            return {
                "success": False,
                "sql": "",
                "explanation": "",
                "error": str(e)
            }
    
    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query for security and correctness
        
        Args:
            sql: SQL query string
            
        Returns:
            {"valid": bool, "error": Optional[str]}
        """
        if not sql:
            return {"valid": False, "error": "Empty SQL query"}
        
        # Parse SQL
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return {"valid": False, "error": "Failed to parse SQL"}
            
            statement = parsed[0]
            
            # Check if it's a SELECT statement
            if not statement.get_type() == "SELECT":
                return {"valid": False, "error": "Only SELECT queries are allowed"}
            
            # Convert to uppercase for checking
            sql_upper = sql.upper()
            
            # Block dangerous keywords
            dangerous_keywords = [
                "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", 
                "ALTER", "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
            ]
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return {"valid": False, "error": f"Dangerous keyword '{keyword}' not allowed"}
            
            # Extract table names
            tokens = statement.tokens
            table_names = self._extract_table_names(tokens)
            
            # Check if all tables are in whitelist
            for table in table_names:
                if table.lower() not in self.ALLOWED_TABLES:
                    return {"valid": False, "error": f"Table '{table}' not in whitelist"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _extract_table_names(self, tokens) -> List[str]:
        """Extract table names from SQL tokens"""
        tables = []
        from_seen = False
        
        for token in tokens:
            if from_seen:
                if token.ttype is None:
                    # This might be a table name or identifier list
                    table_name = str(token).strip().split()[0]
                    # Remove quotes and schema prefixes
                    table_name = table_name.replace('"', '').replace("'", "")
                    if '.' in table_name:
                        table_name = table_name.split('.')[-1]
                    if table_name and not table_name.upper() in ['AS', 'ON', 'WHERE', 'GROUP', 'ORDER', 'JOIN']:
                        tables.append(table_name)
                from_seen = False
            
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                from_seen = True
            elif token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'JOIN':
                from_seen = True
        
        return tables
    
    async def execute_query(self, sql: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results
        
        Args:
            sql: Validated SQL query
            
        Returns:
            {
                "success": bool,
                "data": List[Dict],
                "row_count": int,
                "error": Optional[str]
            }
        """
        if not supabase:
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "error": "Database not configured"
            }
        
        # Validate first
        validation = self._validate_sql(sql)
        if not validation["valid"]:
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "error": validation["error"]
            }
        
        try:
            # Execute via secure_query_service (replaces broken RPC)
            result = secure_query_service.execute_safe_query(sql)
            
            if not result["success"]:
                return {
                    "success": False,
                    "data": [],
                    "row_count": 0,
                    "error": result.get("error", "Query execution failed"),
                    "message": "Ошибка выполнения запроса к базе данных."
                }
            
            data = result.get("data", [])
            row_count = len(data)
            
            # NULL SAFETY: Handle empty results with explicit message
            if row_count == 0:
                return {
                    "success": True,
                    "data": [],
                    "row_count": 0,
                    "error": None,
                    "message": "Данные за этот период отсутствуют. Попробуйте расширить диапазон дат или изменить фильтры.",
                    "summary": None
                }
            
            # SMART CONTEXT: Summarize large datasets
            summary = None
            if row_count > 50:
                summary = self._summarize_data(data)
                # Keep only first 5 rows + summary instead of full dump
                data = data[:5]
            
            return {
                "success": True,
                "data": data,
                "row_count": row_count,
                "error": None,
                "message": None,
                "summary": summary,
                "truncated": row_count > 50
            }
            
        except SecurityViolationError as e:
            logger.warning(f"Security violation blocked: {e}")
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "error": f"Запрос заблокирован: {str(e)}",
                "message": "Запрос содержит недопустимые операции."
            }
        except ConnectionError as e:
            logger.error(f"Database connection error: {e}")
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "error": f"Ошибка подключения к БД: {str(e)}",
                "message": "Не удалось подключиться к базе данных. Проверьте настройки."
            }
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "error": str(e),
                "message": "Произошла ошибка при выполнении запроса."
            }
    
    def _summarize_data(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Smart Data Summarizer - creates statistical summary for large datasets
        Instead of sending 10k rows to LLM, send first 5 + stats
        """
        if not data:
            return None
        
        summary = {
            "total_rows": len(data),
            "sample_rows": 5,
            "columns": list(data[0].keys()) if data else [],
            "stats": {}
        }
        
        # Calculate statistics for numeric columns
        for key in summary["columns"]:
            values = []
            for row in data:
                val = row.get(key)
                if isinstance(val, (int, float)) and val is not None:
                    values.append(float(val))
            
            if values:
                summary["stats"][key] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": round(mean(values), 2),
                    "sum": round(sum(values), 2),
                    "count": len(values)
                }
        
        return summary
    
    async def query_from_question(self, question: str) -> Dict[str, Any]:
        """
        Generate and execute SQL query from natural language question
        
        Args:
            question: User question
            
        Returns:
            Complete result with SQL, data, and explanation
        """
        # Generate SQL
        gen_result = await self.generate_sql(question)
        
        if not gen_result["success"]:
            return {
                "success": False,
                "question": question,
                "sql": gen_result.get("sql", ""),
                "explanation": gen_result.get("explanation", ""),
                "data": [],
                "row_count": 0,
                "error": gen_result["error"]
            }
        
        # Execute SQL
        exec_result = await self.execute_query(gen_result["sql"])
        
        return {
            "success": exec_result["success"],
            "question": question,
            "sql": gen_result["sql"],
            "explanation": gen_result["explanation"],
            "data": exec_result["data"],
            "row_count": exec_result["row_count"],
            "error": exec_result.get("error")
        }


# Global instance
sql_query_service = SQLQueryService()
