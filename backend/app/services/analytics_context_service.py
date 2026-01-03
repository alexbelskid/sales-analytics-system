"""
Analytics Service for AI Context
Provides dynamic data from database for Gemini AI context injection
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.database import supabase
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service to fetch analytics data for AI context"""
    
    def get_sales_summary(self, limit: int = 5) -> Dict[str, Any]:
        """
        Get top products by sales amount
        Returns summary for AI context
        """
        if supabase is None:
            return self._get_demo_sales_summary()
        
        try:
            # Get sales with items and products
            result = supabase.table("sale_items").select(
                "quantity, amount, products(name)"
            ).execute()
            
            # Aggregate by product
            product_totals = {}
            for item in result.data:
                product_name = item.get("products", {}).get("name", "Неизвестный")
                if product_name not in product_totals:
                    product_totals[product_name] = {"quantity": 0, "amount": 0}
                product_totals[product_name]["quantity"] += item.get("quantity", 0)
                product_totals[product_name]["amount"] += float(item.get("amount", 0))
            
            # Sort by amount and take top N
            sorted_products = sorted(
                product_totals.items(),
                key=lambda x: x[1]["amount"],
                reverse=True
            )[:limit]
            
            return {
                "top_products": [
                    {"name": name, "total": data["amount"], "quantity": data["quantity"]}
                    for name, data in sorted_products
                ]
            }
        except Exception as e:
            logger.error(f"Error getting sales summary: {e}")
            return self._get_demo_sales_summary()
    
    def get_clients_summary(self, limit: int = 5) -> Dict[str, Any]:
        """
        Get top clients by total purchases
        """
        if supabase is None:
            return self._get_demo_clients_summary()
        
        try:
            # Get sales grouped by customer
            result = supabase.table("sales").select(
                "total_amount, customers(name)"
            ).execute()
            
            # Aggregate by customer
            customer_totals = {}
            for sale in result.data:
                customer_name = sale.get("customers", {}).get("name", "Неизвестный")
                if customer_name not in customer_totals:
                    customer_totals[customer_name] = 0
                customer_totals[customer_name] += float(sale.get("total_amount", 0))
            
            # Sort and take top N
            sorted_customers = sorted(
                customer_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return {
                "top_clients": [
                    {"name": name, "total": total}
                    for name, total in sorted_customers
                ]
            }
        except Exception as e:
            logger.error(f"Error getting clients summary: {e}")
            return self._get_demo_clients_summary()
    
    def get_monthly_stats(self) -> Dict[str, Any]:
        """
        Get statistics for current month
        """
        if supabase is None:
            return self._get_demo_monthly_stats()
        
        try:
            # Calculate first day of current month
            now = datetime.now()
            first_day = now.replace(day=1).date().isoformat()
            
            result = supabase.table("sales").select("total_amount").gte(
                "sale_date", first_day
            ).execute()
            
            total_revenue = sum(float(s.get("total_amount", 0)) for s in result.data)
            total_orders = len(result.data)
            avg_order = total_revenue / total_orders if total_orders > 0 else 0
            
            return {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "average_order": round(avg_order, 2),
                "period": f"{now.strftime('%B %Y')}"
            }
        except Exception as e:
            logger.error(f"Error getting monthly stats: {e}")
            return self._get_demo_monthly_stats()
    
    def get_products_catalog(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get products with prices for AI context
        """
        if supabase is None:
            return self._get_demo_products()
        
        try:
            result = supabase.table("products").select(
                "name, price, category, in_stock"
            ).limit(limit).execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return self._get_demo_products()
    
    def get_full_context_for_ai(self) -> Dict[str, Any]:
        """
        Get all relevant data for AI context in one call
        """
        return {
            "sales_summary": self.get_sales_summary(),
            "clients_summary": self.get_clients_summary(),
            "monthly_stats": self.get_monthly_stats(),
            "products": self.get_products_catalog()
        }
    
    def format_for_prompt(self) -> str:
        """
        Format all analytics data as text for Gemini prompt
        """
        context = self.get_full_context_for_ai()
        
        lines = []
        
        # Monthly stats
        stats = context["monthly_stats"]
        lines.append("═══ СТАТИСТИКА ЗА ТЕКУЩИЙ МЕСЯЦ ═══")
        lines.append(f"📊 Период: {stats.get('period', 'Текущий месяц')}")
        lines.append(f"💰 Выручка: {stats['total_revenue']:,.2f} BYN")
        lines.append(f"📦 Заказов: {stats['total_orders']}")
        lines.append(f"📈 Средний чек: {stats['average_order']:,.2f} BYN")
        lines.append("")
        
        # Top products
        top_products = context["sales_summary"]["top_products"]
        if top_products:
            lines.append("═══ ТОП ПРОДУКТОВ ═══")
            for i, p in enumerate(top_products, 1):
                lines.append(f"{i}. {p['name']} — {p['total']:,.2f} BYN ({p['quantity']} шт)")
            lines.append("")
        
        # Top clients
        top_clients = context["clients_summary"]["top_clients"]
        if top_clients:
            lines.append("═══ ТОП КЛИЕНТОВ ═══")
            for i, c in enumerate(top_clients, 1):
                lines.append(f"{i}. {c['name']} — {c['total']:,.2f} BYN")
            lines.append("")
        
        # Products catalog
        products = context["products"]
        if products:
            lines.append("═══ КАТАЛОГ ТОВАРОВ ═══")
            for p in products:
                stock_status = "✅ В наличии" if p.get("in_stock", 0) > 0 else "❌ Нет"
                lines.append(f"• {p['name']} — {p['price']:,.2f} BYN [{stock_status}]")
        
        return "\n".join(lines)
    
    # Demo data methods for when Supabase is not configured
    def _get_demo_sales_summary(self) -> Dict[str, Any]:
        return {
            "top_products": [
                {"name": "Шоколад молочный", "total": 245000, "quantity": 1230},
                {"name": "Вафли весовые", "total": 189000, "quantity": 945},
                {"name": "Печенье ассорти", "total": 156000, "quantity": 780},
                {"name": "Конфеты коробка", "total": 134000, "quantity": 670},
                {"name": "Зефир белый", "total": 98000, "quantity": 490},
            ]
        }
    
    def _get_demo_clients_summary(self) -> Dict[str, Any]:
        return {
            "top_clients": [
                {"name": "ООО Альфа-Трейд", "total": 450000},
                {"name": "ИП Петров А.В.", "total": 380000},
                {"name": "ЗАО Бета-Маркет", "total": 320000},
                {"name": "ООО СладкийМир", "total": 275000},
                {"name": "ИП Сидорова Е.М.", "total": 210000},
            ]
        }
    
    def _get_demo_monthly_stats(self) -> Dict[str, Any]:
        return {
            "total_revenue": 2450000,
            "total_orders": 156,
            "average_order": 15705,
            "period": "Январь 2026"
        }
    
    def _get_demo_products(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Шоколад молочный 100г", "price": 5.50, "category": "Шоколад", "in_stock": 500},
            {"name": "Вафли весовые 1кг", "price": 12.00, "category": "Вафли", "in_stock": 200},
            {"name": "Печенье ассорти 500г", "price": 8.50, "category": "Печенье", "in_stock": 350},
            {"name": "Конфеты коробка 250г", "price": 15.00, "category": "Конфеты", "in_stock": 180},
            {"name": "Зефир белый 300г", "price": 7.00, "category": "Зефир", "in_stock": 120},
        ]


# Global instance
analytics_service = AnalyticsService()
