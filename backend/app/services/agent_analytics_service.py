"""
Agent Analytics Service
Business logic for agent performance tracking, forecasting, and analysis
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from uuid import UUID
import logging

from app.database import supabase
from app.models.agent_analytics import (
    AgentPerformance,
    AgentPerformanceDetailed,
    RegionalPerformance,
    AgentDashboardMetrics,
    AgentSalesPlan,
    AgentDailySales,
    DailySalesTrend,
)
from app.services.cache_service import cache

logger = logging.getLogger(__name__)

# Cache TTL in seconds
DASHBOARD_CACHE_TTL = 120  # 2 minutes
AGENT_DETAILS_CACHE_TTL = 60  # 1 minute


class AgentAnalyticsService:
    """Service for agent analytics operations"""
    
    def __init__(self):
        self.supabase = supabase
        self.cache = cache
    
    # ========================================================================
    # Dashboard Metrics
    # ========================================================================
    
    async def get_dashboard_metrics(
        self,
        period_start: date,
        period_end: date,
        region: Optional[str] = None
    ) -> AgentDashboardMetrics:
        """Get overall dashboard metrics for agent performance"""
        try:
            # Check cache first
            cache_key = f"dashboard:{period_start}:{period_end}:{region or 'all'}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Dashboard cache hit: {cache_key}")
                return cached
            
            # Get all active agents
            query = self.supabase.table("agents").select("*").eq("is_active", True)
            if region:
                query = query.eq("region", region)
            
            agents_result = query.execute()
            agents = agents_result.data
            
            if not agents:
                return AgentDashboardMetrics(
                    period_start=period_start,
                    period_end=period_end
                )
            
            agent_ids = [a['id'] for a in agents]
            
            # Get plans for the period
            plans_result = self.supabase.table("agent_sales_plans").select("*").in_(
                "agent_id", agent_ids
            ).eq("period_start", period_start.isoformat()).eq(
                "period_end", period_end.isoformat()
            ).execute()
            
            plans_by_agent = {p['agent_id']: p for p in (plans_result.data or [])}
            
            # Get actual sales for the period
            sales_result = self.supabase.table("agent_daily_sales").select("*").in_(
                "agent_id", agent_ids
            ).gte("sale_date", period_start.isoformat()).lte(
                "sale_date", period_end.isoformat()
            ).execute()
            
            # Aggregate sales by agent
            sales_by_agent: Dict[str, float] = {}
            for sale in (sales_result.data or []):
                agent_id = sale['agent_id']
                sales_by_agent[agent_id] = sales_by_agent.get(agent_id, 0) + float(sale['amount'])
            
            # Calculate totals
            total_plan = sum(float(p.get('plan_amount', 0)) for p in plans_by_agent.values())
            total_sales = sum(sales_by_agent.values())
            overall_fulfillment = (total_sales / total_plan * 100) if total_plan > 0 else 0
            
            # Get regional performance
            regional_performance = await self._get_regional_performance(
                period_start, period_end, agents, plans_by_agent, sales_by_agent
            )
            
            # Get top and bottom performers
            performances = await self._calculate_performances(
                agents, plans_by_agent, sales_by_agent, period_start, period_end
            )
            
            # Sort by fulfillment
            performances_sorted = sorted(performances, key=lambda x: x.fulfillment_percent, reverse=True)
            
            result = AgentDashboardMetrics(
                total_agents=len(agents),
                total_plan=total_plan,
                total_sales=total_sales,
                overall_fulfillment_percent=round(overall_fulfillment, 2),
                regional_performance=regional_performance,
                top_performers=performances_sorted[:10],
                bottom_performers=list(reversed(performances_sorted[-10:])),
                period_start=period_start,
                period_end=period_end
            )
            
            # Cache the result
            self.cache.set(cache_key, result, DASHBOARD_CACHE_TTL)
            return result
        
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            raise
    
    # ========================================================================
    # Agent Performance
    # ========================================================================
    
    async def get_agent_performance(
        self,
        agent_id: UUID,
        period_start: date,
        period_end: date,
        detailed: bool = False
    ) -> AgentPerformance | AgentPerformanceDetailed:
        """Get performance metrics for a specific agent"""
        try:
            # Check cache first
            cache_key = f"agent:{agent_id}:{period_start}:{period_end}:{detailed}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Agent cache hit: {cache_key}")
                return cached
            
            # Get agent info
            agent_result = self.supabase.table("agents").select("*").eq("id", str(agent_id)).single().execute()
            agent = agent_result.data
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Get plan
            plan_result = self.supabase.table("agent_sales_plans").select("*").eq(
                "agent_id", str(agent_id)
            ).eq("period_start", period_start.isoformat()).eq(
                "period_end", period_end.isoformat()
            ).execute()
            
            plan = plan_result.data[0] if plan_result.data else None
            plan_amount = float(plan['plan_amount']) if plan else 0
            
            # Get daily sales
            sales_result = self.supabase.table("agent_daily_sales").select("*").eq(
                "agent_id", str(agent_id)
            ).gte("sale_date", period_start.isoformat()).lte(
                "sale_date", period_end.isoformat()
            ).execute()
            
            daily_sales = sales_result.data or []
            actual_sales = sum(float(s['amount']) for s in daily_sales)
            fulfillment = (actual_sales / plan_amount * 100) if plan_amount > 0 else 0
            
            # Get forecast
            forecast_result = self.supabase.table("agent_performance_forecasts").select("*").eq(
                "agent_id", str(agent_id)
            ).eq("period_start", period_start.isoformat()).eq(
                "period_end", period_end.isoformat()
            ).order("forecast_date", desc=True).limit(1).execute()
            
            forecast = forecast_result.data[0] if forecast_result.data else None
            
            # Build daily sales trend
            daily_trend = [
                DailySalesTrend(
                    sale_date=datetime.fromisoformat(s['sale_date']).date(),
                    amount=float(s['amount']),
                    category=s.get('category')
                )
                for s in daily_sales
            ]
            
            # Calculate ranking (simplified - would need all agents for accurate ranking)
            ranking = await self._calculate_agent_ranking(agent_id, period_start, period_end)
            
            performance = AgentPerformance(
                agent_id=UUID(agent['id']),
                agent_name=agent['name'],
                agent_email=agent['email'],
                region=agent.get('region', 'Unknown'),
                plan_amount=plan_amount,
                actual_sales=actual_sales,
                fulfillment_percent=round(fulfillment, 2),
                forecast_fulfillment_percent=float(forecast['predicted_fulfillment_percent']) if forecast else None,
                forecast_amount=float(forecast['predicted_amount']) if forecast else None,
                confidence_score=float(forecast['confidence_score']) if forecast and forecast.get('confidence_score') else None,
                daily_sales_trend=daily_trend,
                ranking=ranking,
                ai_insights=forecast.get('ai_insights') if forecast else None,
                total_lifetime_sales=float(agent.get('total_lifetime_sales', 0))
            )
            
            if detailed:
                # Calculate category breakdown
                category_breakdown = {}
                for s in daily_sales:
                    cat = s.get('category', 'Other')
                    category_breakdown[cat] = category_breakdown.get(cat, 0) + float(s['amount'])
                
                # Get monthly history (last 6 months)
                monthly_history = await self._get_monthly_history(agent_id)
                
                result = AgentPerformanceDetailed(
                    **performance.dict(),
                    category_breakdown=category_breakdown,
                    monthly_history=monthly_history
                )
                self.cache.set(cache_key, result, AGENT_DETAILS_CACHE_TTL)
                return result
            
            # Cache and return basic performance
            self.cache.set(cache_key, performance, AGENT_DETAILS_CACHE_TTL)
            return performance
        
        except Exception as e:
            logger.error(f"Error getting agent performance: {e}")
            raise
    
    async def get_all_agents_performance(
        self,
        period_start: date,
        period_end: date,
        region: Optional[str] = None,
        min_fulfillment: Optional[float] = None,
        max_fulfillment: Optional[float] = None
    ) -> List[AgentPerformance]:
        """Get performance for all agents with optional filters"""
        try:
            query = self.supabase.table("agents").select("*").eq("is_active", True)
            if region:
                query = query.eq("region", region)
            
            agents_result = query.execute()
            agents = agents_result.data or []
            
            if not agents:
                return []
            
            agent_ids = [a['id'] for a in agents]
            
            # Get plans
            plans_result = self.supabase.table("agent_sales_plans").select("*").in_(
                "agent_id", agent_ids
            ).eq("period_start", period_start.isoformat()).eq(
                "period_end", period_end.isoformat()
            ).execute()
            
            plans_by_agent = {p['agent_id']: p for p in (plans_result.data or [])}
            
            # Get sales
            sales_result = self.supabase.table("agent_daily_sales").select("*").in_(
                "agent_id", agent_ids
            ).gte("sale_date", period_start.isoformat()).lte(
                "sale_date", period_end.isoformat()
            ).execute()
            
            sales_by_agent: Dict[str, float] = {}
            for sale in (sales_result.data or []):
                agent_id = sale['agent_id']
                sales_by_agent[agent_id] = sales_by_agent.get(agent_id, 0) + float(sale['amount'])
            
            # Calculate performances
            performances = await self._calculate_performances(
                agents, plans_by_agent, sales_by_agent, period_start, period_end
            )
            
            # Apply filters
            if min_fulfillment is not None:
                performances = [p for p in performances if p.fulfillment_percent >= min_fulfillment]
            if max_fulfillment is not None:
                performances = [p for p in performances if p.fulfillment_percent <= max_fulfillment]
            
            return performances
        
        except Exception as e:
            logger.error(f"Error getting all agents performance: {e}")
            raise
    
    # ========================================================================
    # Regional Analytics
    # ========================================================================
    
    async def get_regional_performance(
        self,
        region: str,
        period_start: date,
        period_end: date
    ) -> RegionalPerformance:
        """Get performance metrics for a specific region"""
        try:
            # Use SQL function if available
            try:
                result = self.supabase.rpc('get_regional_performance', {
                    'p_region': region,
                    'p_period_start': period_start.isoformat(),
                    'p_period_end': period_end.isoformat()
                }).execute()
                
                if result.data and len(result.data) > 0:
                    row = result.data[0]
                    
                    # Get top performers in region
                    top_performers = await self.get_all_agents_performance(
                        period_start, period_end, region=region
                    )
                    top_performers = sorted(top_performers, key=lambda x: x.fulfillment_percent, reverse=True)[:5]
                    
                    return RegionalPerformance(
                        region=row['region'],
                        total_plan=float(row['total_plan']),
                        total_sales=float(row['total_sales']),
                        fulfillment_percent=round(float(row['fulfillment_percent']), 2),
                        agents_count=int(row['agents_count']),
                        top_performers=top_performers
                    )
            except Exception as rpc_error:
                logger.warning(f"RPC function not available: {rpc_error}, using fallback")
            
            # Fallback: manual calculation
            agents_result = self.supabase.table("agents").select("*").eq(
                "region", region
            ).eq("is_active", True).execute()
            
            agents = agents_result.data or []
            agent_ids = [a['id'] for a in agents]
            
            if not agent_ids:
                return RegionalPerformance(region=region)
            
            # Get plans and sales
            plans_result = self.supabase.table("agent_sales_plans").select("*").in_(
                "agent_id", agent_ids
            ).eq("period_start", period_start.isoformat()).eq(
                "period_end", period_end.isoformat()
            ).execute()
            
            sales_result = self.supabase.table("agent_daily_sales").select("*").in_(
                "agent_id", agent_ids
            ).gte("sale_date", period_start.isoformat()).lte(
                "sale_date", period_end.isoformat()
            ).execute()
            
            total_plan = sum(float(p['plan_amount']) for p in (plans_result.data or []))
            total_sales = sum(float(s['amount']) for s in (sales_result.data or []))
            fulfillment = (total_sales / total_plan * 100) if total_plan > 0 else 0
            
            # Get top performers
            top_performers = await self.get_all_agents_performance(
                period_start, period_end, region=region
            )
            top_performers = sorted(top_performers, key=lambda x: x.fulfillment_percent, reverse=True)[:5]
            
            return RegionalPerformance(
                region=region,
                total_plan=total_plan,
                total_sales=total_sales,
                fulfillment_percent=round(fulfillment, 2),
                agents_count=len(agents),
                top_performers=top_performers
            )
        
        except Exception as e:
            logger.error(f"Error getting regional performance: {e}")
            raise
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _get_regional_performance(
        self,
        period_start: date,
        period_end: date,
        agents: List[Dict],
        plans_by_agent: Dict,
        sales_by_agent: Dict
    ) -> List[RegionalPerformance]:
        """Calculate regional performance from agent data"""
        regions = {}
        
        for agent in agents:
            region = agent.get('region', 'Unknown')
            if region not in regions:
                regions[region] = {
                    'plan': 0,
                    'sales': 0,
                    'count': 0
                }
            
            agent_id = agent['id']
            plan = plans_by_agent.get(agent_id)
            if plan:
                regions[region]['plan'] += float(plan['plan_amount'])
            
            regions[region]['sales'] += sales_by_agent.get(agent_id, 0)
            regions[region]['count'] += 1
        
        result = []
        for region, data in regions.items():
            fulfillment = (data['sales'] / data['plan'] * 100) if data['plan'] > 0 else 0
            result.append(RegionalPerformance(
                region=region,
                total_plan=data['plan'],
                total_sales=data['sales'],
                fulfillment_percent=round(fulfillment, 2),
                agents_count=data['count'],
                top_performers=[]  # Would need separate query
            ))
        
        return result
    
    async def _calculate_performances(
        self,
        agents: List[Dict],
        plans_by_agent: Dict,
        sales_by_agent: Dict,
        period_start: date,
        period_end: date
    ) -> List[AgentPerformance]:
        """Calculate performance for list of agents"""
        performances = []
        
        for agent in agents:
            agent_id = agent['id']
            plan = plans_by_agent.get(agent_id)
            plan_amount = float(plan['plan_amount']) if plan else 0
            actual_sales = sales_by_agent.get(agent_id, 0)
            fulfillment = (actual_sales / plan_amount * 100) if plan_amount > 0 else 0
            
            performances.append(AgentPerformance(
                agent_id=UUID(agent_id),
                agent_name=agent['name'],
                agent_email=agent['email'],
                region=agent.get('region', 'Unknown'),
                plan_amount=plan_amount,
                actual_sales=actual_sales,
                fulfillment_percent=round(fulfillment, 2),
                total_lifetime_sales=float(agent.get('total_lifetime_sales', 0))
            ))
        
        return performances
    
    async def _calculate_agent_ranking(
        self,
        agent_id: UUID,
        period_start: date,
        period_end: date
    ) -> Optional[int]:
        """Calculate agent's ranking among all agents"""
        try:
            # Get all performances
            performances = await self.get_all_agents_performance(period_start, period_end)
            performances_sorted = sorted(performances, key=lambda x: x.fulfillment_percent, reverse=True)
            
            for idx, perf in enumerate(performances_sorted, 1):
                if perf.agent_id == agent_id:
                    return idx
            
            return None
        except Exception as e:
            logger.error(f"Error calculating ranking: {e}")
            return None
    
    async def _get_monthly_history(self, agent_id: UUID, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly performance history for an agent"""
        history = []
        
        for i in range(months):
            # Calculate month period
            today = date.today()
            end_date = date(today.year, today.month, 1) - timedelta(days=i*30)
            start_date = date(end_date.year, end_date.month, 1)
            
            try:
                perf = await self.get_agent_performance(agent_id, start_date, end_date)
                history.append({
                    'month': end_date.strftime('%Y-%m'),
                    'plan': perf.plan_amount,
                    'sales': perf.actual_sales,
                    'fulfillment': perf.fulfillment_percent
                })
            except:
                continue
        
        return list(reversed(history))


# Global instance
agent_analytics_service = AgentAnalyticsService()
