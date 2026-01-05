"""
AI Context Service
Provides formatted context from sales data for Groq AI assistant
"""

from typing import Optional, Dict, Any
from app.services.extended_analytics_service import extended_analytics
from app.database import supabase
import logging

logger = logging.getLogger(__name__)


class AIContextService:
    """Service to build context for AI from sales data"""
    
    @staticmethod
    def get_context_for_ai(
        customer_name: Optional[str] = None,
        product_name: Optional[str] = None,
        include_general: bool = True
    ) -> str:
        """
        Build comprehensive context string for AI
        
        Args:
            customer_name: Name of customer to get specific context
            product_name: Name of product to get specific context
            include_general: Include general statistics
        
        Returns:
            Formatted text context for AI prompt
        """
        context_parts = []
        
        # General context
        if include_general:
            general = AIContextService._get_general_context()
            if general:
                context_parts.append(general)
        
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
