"""
AI Context Service
Provides formatted context from sales data for Groq AI assistant
"""

from typing import Optional, Dict, Any
from app.services.extended_analytics_service import extended_analytics
from app.database import supabase, supabase_admin
import logging

logger = logging.getLogger(__name__)

# CRITICAL FIX: Use admin client to bypass RLS for reading agent data!
# Regular supabase client has RLS which blocks reading agents table
_db = supabase_admin or supabase


class AIContextService:
    """Service to build context for AI from sales data"""
    
    @staticmethod
    def get_context_for_ai(
        customer_name: Optional[str] = None,
        product_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        include_general: bool = True,
        include_agents: bool = True,
        include_imports: bool = False
    ) -> str:
        """
        Build comprehensive context string for AI from REAL DATABASE DATA ONLY
        
        Args:
            customer_name: Name of customer to get specific context
            product_name: Name of product to get specific context
            agent_name: Name of agent to get specific context
            include_general: Include general sales statistics
            include_agents: Include agent analytics from DB
            include_imports: Include import history information
        
        Returns:
            Formatted text context for AI prompt (ALL DATA FROM REAL DB)
        """
        context_parts = []
        
        # General context
        if include_general:
            general = AIContextService._get_general_context()
            if general:
                context_parts.append(general)
        
        # Agent analytics context (NEW!)
        if include_agents:
            agents = AIContextService._get_agent_analytics_context()
            if agents:
                context_parts.append(agents)
        
        # Customer-specific context
        if customer_name:
            customer = AIContextService._get_customer_context(customer_name)
            if customer:
                context_parts.append(customer)
        
        # Product-specific context
        if product_name:
            product = AIContextService._get_product_context(product_name)
            if product:
                context_parts.append(product)
        
        # Agent-specific context (NEW!)
        if agent_name:
            agent = AIContextService._get_agent_details_context(agent_name)
            if agent:
                context_parts.append(agent)
        
        # Import history context (NEW!)
        if include_imports:
            imports = AIContextService._get_import_history_context()
            if imports:
                context_parts.append(imports)
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    @staticmethod
    def _get_general_context() -> str:
        """Get general sales statistics"""
        try:
            # Get summary
            summary = extended_analytics.get_summary(force_refresh=False)
            top_products = extended_analytics.get_top_products(limit=3, force_refresh=False)
            top_customers = extended_analytics.get_top_customers(limit=3, force_refresh=False)
            
            # Format context
            lines = [
                "📊 ОБЩАЯ СТАТИСТИКА ПРОДАЖ:",
                f"• Общая выручка: {summary.get('total_revenue', 0):,.0f} Br",
                f"• Количество сделок: {summary.get('total_sales', 0)}",
                f"• Средний чек: {summary.get('average_check', 0):,.0f} Br",
                f"• Уникальных клиентов: {summary.get('unique_customers', 0)}",
                f"• Уникальных товаров: {summary.get('unique_products', 0)}",
            ]
            
            if top_products:
                lines.append("\n🏆 ТОП-3 ТОВАРА:")
                for i, p in enumerate(top_products, 1):
                    lines.append(f"  {i}. {p.get('name', 'Неизвестный')} — {p.get('total_revenue', 0):,.0f} Br")
            
            if top_customers:
                lines.append("\n👥 ТОП-3 КЛИЕНТА:")
                for i, c in enumerate(top_customers, 1):
                    lines.append(f"  {i}. {c.get('name', 'Неизвестный')} — {c.get('total_purchases', 0):,.0f} Br")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error getting general context: {e}")
            return ""
    
    @staticmethod
    def _get_customer_context(customer_name: str) -> str:
        """Get context for specific customer"""
        if supabase is None:
            return ""
        
        try:
            # Search for customer
            normalized = customer_name.lower().strip()
            result = supabase.table('customers').select('*').ilike(
                'normalized_name', f'%{normalized}%'
            ).limit(1).execute()
            
            if not result.data:
                return ""
            
            customer = result.data[0]
            customer_id = customer['id']
            
            # Get customer's sales
            sales_result = supabase.table('sales').select(
                'amount, sale_date, products(name)'
            ).eq('customer_id', customer_id).order('sale_date', desc=True).limit(50).execute()
            
            # Calculate product preferences
            product_counts = {}
            total_amount = 0
            last_purchase = None
            
            for sale in sales_result.data:
                product_name = sale.get('products', {}).get('name', 'Неизвестный')
                product_counts[product_name] = product_counts.get(product_name, 0) + 1
                total_amount += float(sale.get('amount', 0))
                
                if not last_purchase:
                    last_purchase = sale.get('sale_date')
            
            # Top products for this customer
            top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            lines = [
                f"👤 КЛИЕНТ: {customer.get('name', customer_name)}",
                f"• Сумма покупок: {customer.get('total_purchases', total_amount):,.0f} Br",
                f"• Количество заказов: {customer.get('purchases_count', len(sales_result.data))}",
                f"• Средний чек: {total_amount / max(len(sales_result.data), 1):,.0f} Br",
            ]
            
            if last_purchase:
                lines.append(f"• Последняя покупка: {last_purchase}")
            
            if top_products:
                lines.append("• Любимые товары:")
                for name, count in top_products:
                    lines.append(f"  — {name} ({count} раз)")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error getting customer context: {e}")
            return ""
    
    @staticmethod
    def _get_product_context(product_name: str) -> str:
        """Get context for specific product"""
        if supabase is None:
            return ""
        
        try:
            # Search for product
            normalized = product_name.lower().strip()
            result = supabase.table('products').select('*').ilike(
                'normalized_name', f'%{normalized}%'
            ).limit(1).execute()
            
            if not result.data:
                return ""
            
            product = result.data[0]
            product_id = product['id']
            
            # Get product's sales with customers
            sales_result = supabase.table('sales').select(
                'amount, quantity, sale_date, customers(name)'
            ).eq('product_id', product_id).limit(100).execute()
            
            # Calculate customer distribution
            customer_totals = {}
            total_quantity = 0
            total_revenue = 0
            
            for sale in sales_result.data:
                customer_name = sale.get('customers', {}).get('name', 'Неизвестный')
                amount = float(sale.get('amount', 0))
                customer_totals[customer_name] = customer_totals.get(customer_name, 0) + amount
                total_quantity += float(sale.get('quantity', 0))
                total_revenue += amount
            
            # Top customers for this product
            top_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            avg_price = total_revenue / max(total_quantity, 1)
            
            lines = [
                f"📦 ТОВАР: {product.get('name', product_name)}",
                f"• Категория: {product.get('category', 'Не указана')}",
                f"• Общая выручка: {product.get('total_revenue', total_revenue):,.0f} Br",
                f"• Продано единиц: {product.get('total_quantity', total_quantity):,.0f}",
                f"• Средняя цена: {avg_price:,.0f} Br",
                f"• Количество продаж: {product.get('sales_count', len(sales_result.data))}",
            ]
            
            if top_customers:
                lines.append("• Основные покупатели:")
                for name, amount in top_customers:
                    lines.append(f"  — {name}: {amount:,.0f} Br")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error getting product context: {e}")
            return ""
    
    @staticmethod
    def _get_agent_analytics_context(period_days: int = 30) -> str:
        """
        Get agent analytics context from REAL DATABASE DATA ONLY
        
        This method queries actual data from agent_sales_plans and agent_daily_sales tables.
        NO FAKE DATA IS GENERATED.
        
        Args:
            period_days: Number of days to look back for analytics
            
        Returns:
            Formatted text context with real agent performance data
        """
        if _db is None:
            return ""
        
        try:
            from datetime import datetime, timedelta
            
            # Calculate period
            period_end = datetime.now().date()
            period_start = period_end - timedelta(days=period_days)
            
            # Get all active agents
            agents_result = _db.table('agents').select('*').eq('is_active', True).execute()
            
            if not agents_result.data:
                return "⚠️ Нет данных об агентах в БД. Загрузите данные через импорт Excel."
            
            agents = agents_result.data
            agent_ids = [a['id'] for a in agents]
            
            # Get plans that OVERLAP with the period (correct logic!)
            # A plan overlaps if: plan_start <= period_end AND plan_end >= period_start
            plans_result = _db.table('agent_sales_plans').select('*').in_(
                'agent_id', agent_ids
            ).lte('period_start', period_end.isoformat()).gte(
                'period_end', period_start.isoformat()
            ).execute()
            
            plans_by_agent = {p['agent_id']: p for p in (plans_result.data or [])}
            
            # Get actual sales for the period
            sales_result = _db.table('agent_daily_sales').select('*').in_(
                'agent_id', agent_ids
            ).gte('sale_date', period_start.isoformat()).lte(
                'sale_date', period_end.isoformat()
            ).execute()
            
            # Aggregate sales by agent
            sales_by_agent = {}
            for sale in (sales_result.data or []):
                agent_id = sale['agent_id']
                sales_by_agent[agent_id] = sales_by_agent.get(agent_id, 0) + float(sale['amount'])
            
            # Calculate totals
            total_plan = sum(float(p.get('plan_amount', 0)) for p in plans_by_agent.values())
            total_sales = sum(sales_by_agent.values())
            overall_fulfillment = (total_sales / total_plan * 100) if total_plan > 0 else 0
            
            # Build performance list
            performances = []
            for agent in agents:
                agent_id = agent['id']
                plan = plans_by_agent.get(agent_id)
                plan_amount = float(plan['plan_amount']) if plan else 0
                actual_sales = sales_by_agent.get(agent_id, 0)
                fulfillment = (actual_sales / plan_amount * 100) if plan_amount > 0 else 0
                
                if plan_amount > 0 or actual_sales > 0:  # Only include agents with data
                    performances.append({
                        'name': agent['name'],
                        'region': agent.get('region', 'Unknown'),
                        'plan': plan_amount,
                        'sales': actual_sales,
                        'fulfillment': fulfillment
                    })
            
            # Sort by fulfillment
            performances.sort(key=lambda x: x['fulfillment'], reverse=True)
            
            lines = [
                f"📊 АНАЛИТИКА АГЕНТОВ (за {period_days} дней):",
                f"• Источник данных: PostgreSQL БД (только реальные загруженные данные)",
                f"• Всего агентов: {len(agents)}",
                f"• Агентов с данными: {len(performances)}",
                f"• Общий план: {total_plan:,.0f} Br",
                f"• Фактические продажи: {total_sales:,.0f} Br",
                f"• Общее выполнение: {overall_fulfillment:.1f}%",
            ]
            
            if performances:
                lines.append("\n🏆 ТОП-5 АГЕНТОВ ПО ВЫПОЛНЕНИЮ ПЛАНА:")
                for i, p in enumerate(performances[:5], 1):
                    lines.append(
                        f"  {i}. {p['name']} ({p['region']}) — "
                        f"План: {p['plan']:,.0f} Br, "
                        f"Факт: {p['sales']:,.0f} Br, "
                        f"Выполнение: {p['fulfillment']:.1f}%"
                    )
                
                if len(performances) > 5:
                    lines.append("\n⚠️ АГЕНТЫ С НИЗКИМ ВЫПОЛНЕНИЕМ:")
                    for p in performances[-3:]:
                        if p['fulfillment'] < 80:
                            lines.append(
                                f"  • {p['name']} ({p['region']}) — "
                                f"Выполнение: {p['fulfillment']:.1f}%"
                            )
            
            # Add import history info
            try:
                imports = _db.table('import_history').select(
                    'filename, imported_rows, completed_at'
                ).eq('import_type', 'agents').eq('status', 'completed').order(
                    'completed_at', desc=True
                ).limit(3).execute()
                
                if imports.data:
                    lines.append("\n📁 ПОСЛЕДНИЕ ИМПОРТЫ ДАННЫХ:")
                    for imp in imports.data:
                        lines.append(
                            f"  • {imp['filename']} — "
                            f"{imp['imported_rows']} записей — "
                            f"{imp['completed_at'][:10]}"
                        )
            except:
                pass
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error getting agent analytics context: {e}")
            return f"⚠️ Ошибка получения данных агентов: {str(e)}"
    
    @staticmethod
    def _get_agent_details_context(agent_name: str) -> str:
        """
        Get detailed context for a specific agent from REAL DATABASE DATA ONLY
        
        Args:
            agent_name: Name of the agent to get details for
            
        Returns:
            Formatted text with agent's performance data from DB
        """
        if supabase is None:
            return ""
        
        try:
            from datetime import datetime, timedelta
            
            # Search for agent
            normalized = agent_name.lower().strip()
            result = _db.table('agents').select('*').ilike(
                'name', f'%{normalized}%'
            ).limit(1).execute()
            
            if not result.data:
                return f"❌ Агент '{agent_name}' не найден в БД."
            
            agent = result.data[0]
            agent_id = agent['id']
            
            # Get current month period
            today = datetime.now().date()
            period_start = today.replace(day=1)
            
            # Get plan
            plan_result = _db.table('agent_sales_plans').select('*').eq(
                'agent_id', agent_id
            ).gte('period_start', period_start.isoformat()).limit(1).execute()
            
            plan = plan_result.data[0] if plan_result.data else None
            plan_amount = float(plan['plan_amount']) if plan else 0
            
            # Get daily sales
            sales_result = _db.table('agent_daily_sales').select('*').eq(
                'agent_id', agent_id
            ).gte('sale_date', period_start.isoformat()).order(
                'sale_date', desc=True
            ).execute()
            
            daily_sales = sales_result.data or []
            total_sales = sum(float(s['amount']) for s in daily_sales)
            fulfillment = (total_sales / plan_amount * 100) if plan_amount > 0 else 0
            
            # Group by category
            category_breakdown = {}
            for s in daily_sales:
                cat = s.get('category', 'General')
                category_breakdown[cat] = category_breakdown.get(cat, 0) + float(s['amount'])
            
            lines = [
                f"👤 АГЕНТ: {agent['name']}",
                f"• Источник данных: PostgreSQL БД (реальные данные)",
                f"• Регион: {agent.get('region', 'Unknown')}",
                f"• Email: {agent.get('email', 'Не указан')}",
                f"• Статус: {'Активен' if agent.get('is_active') else 'Неактивен'}",
                f"\n📊 ТЕКУЩИЙ ПЕРИОД:",
                f"• План: {plan_amount:,.0f} Br",
                f"• Фактические продажи: {total_sales:,.0f} Br",
                f"• Выполнение плана: {fulfillment:.1f}%",
                f"• Количество продаж: {len(daily_sales)}",
            ]
            
            if category_breakdown:
                lines.append("\n📦 ПРОДАЖИ ПО КАТЕГОРИЯМ:")
                for cat, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"  • {cat}: {amount:,.0f} Br")
            
            if daily_sales:
                lines.append(f"\n📅 ПОСЛЕДНИЕ ПРОДАЖИ:")
                for s in daily_sales[:5]:
                    lines.append(
                        f"  • {s['sale_date']}: {float(s['amount']):,.0f} Br "
                        f"({s.get('category', 'General')})"
                    )
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error getting agent details: {e}")
            return f"⚠️ Ошибка получения данных агента: {str(e)}"
    
    @staticmethod
    def _get_import_history_context() -> str:
        """Get information about data imports from REAL DATABASE"""
        if supabase is None:
            return ""
        
        try:
            imports = _db.table('import_history').select(
                'filename, total_rows, imported_rows, status, completed_at, import_type'
            ).eq('status', 'completed').order('completed_at', desc=True).limit(5).execute()
            
            if not imports.data:
                return "⚠️ Нет истории импортов. Данные еще не загружались."
            
            lines = [
                "📁 ИСТОРИЯ ИМПОРТОВ ДАННЫХ:",
                "• Все данные загружены из реальных Excel файлов",
            ]
            
            total_imported = 0
            for imp in imports.data:
                imported = imp.get('imported_rows', 0)
                total_imported += imported
                lines.append(
                    f"  • {imp['filename']} — "
                    f"{imported} записей — "
                    f"{imp.get('import_type', 'unknown')} — "
                    f"{imp['completed_at'][:10]}"
                )
            
            lines.append(f"\n• ВСЕГО ИМПОРТИРОВАНО ЗАПИСЕЙ: {total_imported}")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error getting import history: {e}")
            return ""
    
    @staticmethod
    def build_prompt_context(email_body: str) -> str:
        """
        Analyze email and build relevant context
        
        Attempts to detect customer or product mentions in email
        and provides relevant context
        """
        context = AIContextService.get_context_for_ai(include_general=True)
        
        # TODO: Use NLP to extract customer/product names from email
        # For now, just return general context
        
        return context


# Singleton instance
ai_context = AIContextService()
