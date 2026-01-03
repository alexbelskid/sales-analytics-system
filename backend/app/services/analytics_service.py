from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.database import supabase
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Provides analytics from database for AI context using Supabase client"""
    
    def get_sales_summary(self, days: int = 30) -> List[Dict[str, Any]]:
        """Top products for last N days"""
        if supabase is None:
            return []
            
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            # Fetch sales items with product names
            # Note: We fetch all and aggregate in Python because Postgrest aggregation is limited
            result = supabase.table("sale_items").select(
                "quantity, amount, products(name), sales!inner(sale_date)"
            ).gte("sales.sale_date", cutoff_date).execute()
            
            product_totals = {}
            for item in result.data:
                p_name = item.get("products", {}).get("name", "Неизвестный")
                if p_name not in product_totals:
                    product_totals[p_name] = {"quantity": 0, "total": 0}
                product_totals[p_name]["quantity"] += item.get("quantity", 0)
                product_totals[p_name]["total"] += float(item.get("amount", 0))
            
            # Sort and format
            sorted_products = sorted(
                product_totals.items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )[:10]
            
            return [
                {
                    "product": name,
                    "quantity": data["quantity"],
                    "total": data["total"]
                }
                for name, data in sorted_products
            ]
        except Exception as e:
            logger.error(f"Error in get_sales_summary: {e}")
            return []

    def get_clients_summary(self, days: int = 30) -> List[Dict[str, Any]]:
        """Top clients for last N days"""
        if supabase is None:
            return []
            
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            result = supabase.table("sales").select(
                "total_amount, customers(name)"
            ).gte("sale_date", cutoff_date).execute()
            
            client_totals = {}
            for sale in result.data:
                c_name = sale.get("customers", {}).get("name", "Неизвестный")
                if c_name not in client_totals:
                    client_totals[c_name] = {"orders": 0, "total": 0}
                client_totals[c_name]["orders"] += 1
                client_totals[c_name]["total"] += float(sale.get("total_amount", 0))
                
            sorted_clients = sorted(
                client_totals.items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )[:10]
            
            return [
                {
                    "client": name,
                    "orders": data["orders"],
                    "total": data["total"]
                }
                for name, data in sorted_clients
            ]
        except Exception as e:
            logger.error(f"Error in get_clients_summary: {e}")
            return []

    def get_monthly_stats(self) -> Dict[str, Any]:
        """Stats for current month"""
        if supabase is None:
            return {"revenue": 0, "orders": 0, "customers": 0, "period": "текущий месяц"}
            
        try:
            now = datetime.now()
            first_day = now.replace(day=1).date().isoformat()
            
            result = supabase.table("sales").select(
                "total_amount, customer_id"
            ).gte("sale_date", first_day).execute()
            
            revenue = sum(float(s.get("total_amount", 0)) for s in result.data)
            orders = len(result.data)
            customers = len(set(s.get("customer_id") for s in result.data if s.get("customer_id")))
            
            return {
                "revenue": revenue,
                "orders": orders,
                "customers": customers,
                "period": "текущий месяц"
            }
        except Exception as e:
            logger.error(f"Error in get_monthly_stats: {e}")
            return {"revenue": 0, "orders": 0, "customers": 0, "period": "текущий месяц"}

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Knowledge base stats"""
        if supabase is None:
            return {"total": 0, "categories": []}
            
        try:
            result = supabase.table("knowledge_base").select("category").execute()
            
            counts = {}
            for item in result.data:
                cat = item.get("category", "other")
                counts[cat] = counts.get(cat, 0) + 1
                
            return {
                "total": len(result.data),
                "categories": [
                    {"name": name, "count": count}
                    for name, count in counts.items()
                ]
            }
        except Exception as e:
            logger.error(f"Error in get_knowledge_stats: {e}")
            return {"total": 0, "categories": []}

    def get_training_stats(self) -> Dict[str, Any]:
        """AI training stats"""
        if supabase is None:
            return {"total": 0, "avg_confidence": 0}
            
        try:
            result = supabase.table("training_examples").select("confidence_score").execute()
            
            total = len(result.data)
            avg_conf = sum(float(ex.get("confidence_score", 0)) for ex in result.data) / total if total > 0 else 0
            
            return {
                "total": total,
                "avg_confidence": avg_conf
            }
        except Exception as e:
            logger.error(f"Error in get_training_stats: {e}")
            return {"total": 0, "avg_confidence": 0}
