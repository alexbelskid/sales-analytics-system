"""
Agent Analytics Models
Pydantic models for agent sales plans, daily sales, and performance forecasts
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


# ============================================================================
# Agent Sales Plans
# ============================================================================

class AgentSalesPlanBase(BaseModel):
    agent_id: UUID
    period_start: date
    period_end: date
    plan_amount: float = Field(..., ge=0, description="Planned sales amount for the period")
    region: Optional[str] = Field(None, max_length=100, description="Region: БРЕСТ, ВИТЕБСК, ГОМЕЛЬ, ГРОДНО, МИНСК")


class AgentSalesPlanCreate(AgentSalesPlanBase):
    pass


class AgentSalesPlan(AgentSalesPlanBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Agent Daily Sales
# ============================================================================

class AgentDailySalesBase(BaseModel):
    agent_id: UUID
    sale_date: date
    amount: float = Field(..., ge=0, description="Sales amount for the day")
    region: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100, description="БелПочта, Потребкооперация, ПИРОТЕХНИКА")


class AgentDailySalesCreate(AgentDailySalesBase):
    pass


class AgentDailySales(AgentDailySalesBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Agent Performance Forecasts
# ============================================================================

class AgentPerformanceForecastBase(BaseModel):
    agent_id: UUID
    forecast_date: date
    period_start: date
    period_end: date
    predicted_amount: float = Field(..., ge=0, description="AI predicted sales amount")
    predicted_fulfillment_percent: float = Field(..., ge=0, description="AI predicted plan fulfillment %")
    confidence_score: Optional[float] = Field(None, ge=0, le=100, description="Forecast confidence (0-100%)")
    ai_insights: Optional[Dict[str, Any]] = Field(None, description="AI analysis and recommendations")


class AgentPerformanceForecastCreate(AgentPerformanceForecastBase):
    pass


class AgentPerformanceForecast(AgentPerformanceForecastBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Agent Performance Analytics (Computed)
# ============================================================================

class DailySalesTrend(BaseModel):
    """Single day sales data point"""
    sale_date: date
    amount: float
    category: Optional[str] = None


class AgentPerformance(BaseModel):
    """Comprehensive agent performance metrics"""
    agent_id: UUID
    agent_name: str
    agent_email: str
    region: str
    
    # Current period metrics
    plan_amount: float = Field(0, description="Current period plan")
    actual_sales: float = Field(0, description="Current period actual sales")
    fulfillment_percent: float = Field(0, description="% of plan completed")
    
    # Forecast data
    forecast_fulfillment_percent: Optional[float] = Field(None, description="AI predicted fulfillment %")
    forecast_amount: Optional[float] = Field(None, description="AI predicted final amount")
    confidence_score: Optional[float] = Field(None, description="Forecast confidence")
    
    # Historical data
    daily_sales_trend: List[DailySalesTrend] = Field(default_factory=list, description="Daily sales for charts")
    
    # Rankings and AI insights
    ranking: Optional[int] = Field(None, description="Rank among all agents")
    ranking_in_region: Optional[int] = Field(None, description="Rank within region")
    ai_insights: Optional[Dict[str, Any]] = Field(None, description="AI-generated insights")
    
    # Lifetime stats
    total_lifetime_sales: float = Field(0, description="All-time sales")
    
    class Config:
        from_attributes = True


class AgentPerformanceDetailed(AgentPerformance):
    """Extended agent performance with category breakdown"""
    category_breakdown: Dict[str, float] = Field(default_factory=dict, description="Sales by category")
    monthly_history: List[Dict[str, Any]] = Field(default_factory=list, description="Historical monthly performance")


# ============================================================================
# Regional Performance
# ============================================================================

class RegionalPerformance(BaseModel):
    """Performance metrics aggregated by region"""
    region: str
    total_plan: float = Field(0, description="Total plan for all agents in region")
    total_sales: float = Field(0, description="Total actual sales in region")
    fulfillment_percent: float = Field(0, description="% of regional plan completed")
    agents_count: int = Field(0, description="Number of active agents")
    top_performers: List[AgentPerformance] = Field(default_factory=list, description="Top 5 agents in region")


# ============================================================================
# Dashboard Aggregates
# ============================================================================

class AgentDashboardMetrics(BaseModel):
    """Top-level dashboard metrics for agent analytics"""
    total_agents: int = Field(0, description="Total active agents")
    total_plan: float = Field(0, description="Total plan across all agents")
    total_sales: float = Field(0, description="Total actual sales")
    overall_fulfillment_percent: float = Field(0, description="Overall % of plan")
    
    # Regional breakdown
    regional_performance: List[RegionalPerformance] = Field(default_factory=list)
    
    # Top performers globally
    top_performers: List[AgentPerformance] = Field(default_factory=list, description="Top 10 agents globally")
    bottom_performers: List[AgentPerformance] = Field(default_factory=list, description="Bottom 10 agents needing attention")
    
    # Time period
    period_start: date
    period_end: date


# ============================================================================
# Import/Export Models
# ============================================================================

class GoogleSheetsImportRequest(BaseModel):
    """Request to import data from Google Sheets"""
    spreadsheet_url: str = Field(..., description="Google Sheets URL")
    sheet_name: str = Field("TDSheet", description="Sheet tab name")
    period_start: date
    period_end: date


class GoogleSheetsImportResult(BaseModel):
    """Result of Google Sheets import operation"""
    success: bool
    agents_imported: int = 0
    plans_imported: int = 0
    daily_sales_imported: int = 0
    errors: List[str] = Field(default_factory=list)
    message: str


# ============================================================================
# AI Analysis Models
# ============================================================================

class AIInsightType(str):
    """Types of AI insights"""
    PERFORMANCE_ALERT = "performance_alert"  # Agent underperforming
    TREND_POSITIVE = "trend_positive"  # Positive sales trend
    TREND_NEGATIVE = "trend_negative"  # Negative sales trend
    RECOMMENDATION = "recommendation"  # Action recommendation
    ANOMALY = "anomaly"  # Unusual pattern detected
    PREDICTION = "prediction"  # Future forecast


class AIInsight(BaseModel):
    """Single AI-generated insight"""
    insight_type: str
    title: str
    description: str
    severity: str = Field("info", description="info, warning, critical")
    confidence: float = Field(..., ge=0, le=100, description="Confidence in this insight")
    action_items: List[str] = Field(default_factory=list, description="Recommended actions")


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis of agent performance"""
    agent_id: UUID
    period_start: date
    period_end: date
    include_forecast: bool = True
    include_recommendations: bool = True


class AIAnalysisResponse(BaseModel):
    """AI analysis result for an agent"""
    agent_id: UUID
    agent_name: str
    analysis_date: datetime
    
    # Overall assessment
    performance_score: float = Field(..., ge=0, le=100, description="Overall performance score")
    performance_category: str = Field(..., description="Excellent, Good, Average, Below Average, Poor")
    
    # Insights
    insights: List[AIInsight] = Field(default_factory=list)
    
    # Forecast
    forecast: Optional[AgentPerformanceForecast] = None
    
    # Recommendations
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
