"""
Extended Analytics Service
Provides analytics from imported Excel data with caching
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.database import supabase
from app.services.cache_service import cache
import logging

logger = logging.getLogger(__name__)

# Cache TTL in seconds
CACHE_TTL = 300  # 5 minutes


class ExtendedAnalyticsService:
    """Analytics service for imported sales data"""
    
    @staticmethod
    def get_top_products(
        limit: int = 10,
        year: Optional[int] = None,
        month: Optional[int] = None,
        store_id: Optional[str] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get top products by revenue
        
        Args:
            limit: Number of products to return
            year: Filter by year
            month: Filter by month
            store_id: Filter by store
            force_refresh: Bypass cache
        """
        cache_key = f"ext_analytics:top_products:{limit}:{year}:{month}:{store_id}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        if supabase is None:
            return []
        
        try:
            # Build query
            query = supabase.table('sales').select(
                'product_id, quantity, amount, products(id, name, category)'
            )
            
            if year:
                query = query.eq('year', year)
            if month:
                query = query.eq('month', month)
            if store_id:
                query = query.eq('store_id', store_id)
            
            result = query.execute()
            
            # Aggregate by product
            product_totals: Dict[str, Dict] = {}
            for sale in result.data:
                product = sale.get('products', {})
                if not product:
                    continue
                
                p_id = product.get('id', '')
                p_name = product.get('name', 'Неизвестный')
                p_category = product.get('category', '')
                
                if p_id not in product_totals:
                    product_totals[p_id] = {
                        'product_id': p_id,
                        'name': p_name,
                        'category': p_category,
                        'total_quantity': 0,
                        'total_revenue': 0,
                        'sales_count': 0
                    }
                
                product_totals[p_id]['total_quantity'] += float(sale.get('quantity', 0))
                product_totals[p_id]['total_revenue'] += float(sale.get('amount', 0))
                product_totals[p_id]['sales_count'] += 1
            
            # Sort by revenue and limit
            sorted_products = sorted(
                product_totals.values(),
                key=lambda x: x['total_revenue'],
                reverse=True
            )[:limit]
            
            # Round values
            for p in sorted_products:
                p['total_quantity'] = round(p['total_quantity'], 2)
                p['total_revenue'] = round(p['total_revenue'], 2)
            
            cache.set(cache_key, sorted_products, CACHE_TTL)
            return sorted_products
            
        except Exception as e:
            logger.error(f"get_top_products error: {e}")
            return []
    
    @staticmethod
    def get_top_customers(
        limit: int = 10,
        year: Optional[int] = None,
        month: Optional[int] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Get top customers by total purchases"""
        cache_key = f"ext_analytics:top_customers:{limit}:{year}:{month}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        if supabase is None:
            return []
        
        try:
            query = supabase.table('sales').select(
                'customer_id, amount, sale_date, customers(id, name)'
            )
            
            if year:
                query = query.eq('year', year)
            if month:
                query = query.eq('month', month)
            
            result = query.execute()
            
            # Aggregate by customer
            customer_totals: Dict[str, Dict] = {}
            for sale in result.data:
                customer = sale.get('customers', {})
                if not customer:
                    continue
                
                c_id = customer.get('id', '')
                c_name = customer.get('name', 'Неизвестный')
                
                if c_id not in customer_totals:
                    customer_totals[c_id] = {
                        'customer_id': c_id,
                        'name': c_name,
                        'total_purchases': 0,
                        'orders_count': 0,
                        'last_purchase': None
                    }
                
                customer_totals[c_id]['total_purchases'] += float(sale.get('amount', 0))
                customer_totals[c_id]['orders_count'] += 1
                
                sale_date = sale.get('sale_date')
                if sale_date:
                    if not customer_totals[c_id]['last_purchase'] or sale_date > customer_totals[c_id]['last_purchase']:
                        customer_totals[c_id]['last_purchase'] = sale_date
            
            # Sort and limit
            sorted_customers = sorted(
                customer_totals.values(),
                key=lambda x: x['total_purchases'],
                reverse=True
            )[:limit]
            
            # Round and calculate average
            for c in sorted_customers:
                c['total_purchases'] = round(c['total_purchases'], 2)
                c['average_order'] = round(c['total_purchases'] / max(c['orders_count'], 1), 2)
            
            cache.set(cache_key, sorted_customers, CACHE_TTL)
            return sorted_customers
            
        except Exception as e:
            logger.error(f"get_top_customers error: {e}")
            return []
    
    @staticmethod
    def get_sales_trend(
        period: str = 'month',  # 'day', 'week', 'month'
        year: Optional[int] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Get sales trend over time"""
        cache_key = f"ext_analytics:sales_trend:{period}:{year}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        if supabase is None:
            return []
        
        try:
            query = supabase.table('sales').select(
                'sale_date, amount, year, month, week'
            )
            
            if year:
                query = query.eq('year', year)
            
            result = query.order('sale_date').execute()
            
            # Group by period
            period_totals: Dict[str, Dict] = {}
            for sale in result.data:
                sale_date = sale.get('sale_date', '')
                
                if period == 'day':
                    period_key = sale_date
                elif period == 'week':
                    period_key = f"{sale.get('year', '')}-W{sale.get('week', ''):02d}"
                else:  # month
                    period_key = f"{sale.get('year', '')}-{sale.get('month', ''):02d}"
                
                if period_key not in period_totals:
                    period_totals[period_key] = {
                        'period': period_key,
                        'amount': 0,
                        'count': 0
                    }
                
                period_totals[period_key]['amount'] += float(sale.get('amount', 0))
                period_totals[period_key]['count'] += 1
            
            # Sort by period
            sorted_periods = sorted(period_totals.values(), key=lambda x: x['period'])
            
            # Calculate average
            for p in sorted_periods:
                p['amount'] = round(p['amount'], 2)
                p['average'] = round(p['amount'] / max(p['count'], 1), 2)
            
            cache.set(cache_key, sorted_periods, CACHE_TTL)
            return sorted_periods
            
        except Exception as e:
            logger.error(f"get_sales_trend error: {e}")
            return []
    
    @staticmethod
    def get_sales_by_stores(
        year: Optional[int] = None,
        month: Optional[int] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Get sales breakdown by stores"""
        cache_key = f"ext_analytics:sales_by_stores:{year}:{month}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        if supabase is None:
            return []
        
        try:
            query = supabase.table('sales').select(
                'store_id, amount, stores(id, name, region, channel)'
            )
            
            if year:
                query = query.eq('year', year)
            if month:
                query = query.eq('month', month)
            
            result = query.execute()
            
            # Aggregate by store
            store_totals: Dict[str, Dict] = {}
            for sale in result.data:
                store = sale.get('stores', {})
                store_id = sale.get('store_id') or 'unknown'
                
                if store_id not in store_totals:
                    store_totals[store_id] = {
                        'store_id': store_id,
                        'name': store.get('name', 'Неизвестный') if store else 'Без магазина',
                        'region': store.get('region', '') if store else '',
                        'channel': store.get('channel', '') if store else '',
                        'total_revenue': 0,
                        'sales_count': 0
                    }
                
                store_totals[store_id]['total_revenue'] += float(sale.get('amount', 0))
                store_totals[store_id]['sales_count'] += 1
            
            # Sort by revenue
            sorted_stores = sorted(
                store_totals.values(),
                key=lambda x: x['total_revenue'],
                reverse=True
            )
            
            for s in sorted_stores:
                s['total_revenue'] = round(s['total_revenue'], 2)
            
            cache.set(cache_key, sorted_stores, CACHE_TTL)
            return sorted_stores
            
        except Exception as e:
            logger.error(f"get_sales_by_stores error: {e}")
            return []
    
    @staticmethod
    def get_summary(
        year: Optional[int] = None,
        month: Optional[int] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Get overall summary statistics"""
        cache_key = f"ext_analytics:summary:{year}:{month}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        if supabase is None:
            return {
                'total_revenue': 0,
                'total_sales': 0,
                'average_check': 0,
                'unique_customers': 0,
                'unique_products': 0,
                'top_product': None,
                'top_customer': None
            }
        
        try:
            query = supabase.table('sales').select('amount, customer_id, product_id')
            
            if year:
                query = query.eq('year', year)
            if month:
                query = query.eq('month', month)
            
            result = query.execute()
            sales = result.data
            
            total_revenue = sum(float(s.get('amount', 0)) for s in sales)
            total_sales = len(sales)
            unique_customers = len(set(s.get('customer_id') for s in sales if s.get('customer_id')))
            unique_products = len(set(s.get('product_id') for s in sales if s.get('product_id')))
            
            # Get top product and customer
            top_products = ExtendedAnalyticsService.get_top_products(
                limit=1, year=year, month=month, force_refresh=True
            )
            top_customers = ExtendedAnalyticsService.get_top_customers(
                limit=1, year=year, month=month, force_refresh=True
            )
            
            summary = {
                'total_revenue': round(total_revenue, 2),
                'total_sales': total_sales,
                'average_check': round(total_revenue / max(total_sales, 1), 2),
                'unique_customers': unique_customers,
                'unique_products': unique_products,
                'top_product': top_products[0] if top_products else None,
                'top_customer': top_customers[0] if top_customers else None,
                'period': {
                    'year': year,
                    'month': month
                }
            }
            
            cache.set(cache_key, summary, 60)  # 1 minute cache for summary
            return summary
            
        except Exception as e:
            logger.error(f"get_summary error: {e}")
            return {
                'total_revenue': 0,
                'total_sales': 0,
                'average_check': 0,
                'unique_customers': 0,
                'unique_products': 0,
                'top_product': None,
                'top_customer': None
            }


# Singleton instance
extended_analytics = ExtendedAnalyticsService()
