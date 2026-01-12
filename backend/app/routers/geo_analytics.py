from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from app.database import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class GeoPoint(BaseModel):
    """Geographic point with sales data"""
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    revenue: float
    orders: int
    customers: int
    avg_check: float


class GeoResponse(BaseModel):
    """Geo analytics response"""
    points: List[GeoPoint]
    total_revenue: float
    total_orders: int
    center: Optional[dict] = None


# Default coordinates for common regions (Belarus)
REGION_COORDINATES = {
    "Минск": {"lat": 53.9045, "lon": 27.5615},
    "Минская область": {"lat": 53.9, "lon": 27.5},
    "Брест": {"lat": 52.0976, "lon": 23.6877},
    "Брестская область": {"lat": 52.1, "lon": 25.0},
    "Гродно": {"lat": 53.6884, "lon": 23.8258},
    "Гродненская область": {"lat": 53.7, "lon": 24.5},
    "Витебск": {"lat": 55.1904, "lon": 30.2049},
    "Витебская область": {"lat": 55.2, "lon": 29.5},
    "Могилёв": {"lat": 53.9168, "lon": 30.3449},
    "Могилевская область": {"lat": 53.9, "lon": 30.0},
    "Гомель": {"lat": 52.4345, "lon": 30.9754},
    "Гомельская область": {"lat": 52.4, "lon": 30.5},
    # Russia major cities
    "Москва": {"lat": 55.7558, "lon": 37.6173},
    "Санкт-Петербург": {"lat": 59.9343, "lon": 30.3351},
    "Новосибирск": {"lat": 55.0084, "lon": 82.9357},
    "Екатеринбург": {"lat": 56.8389, "lon": 60.6057},
    "Казань": {"lat": 55.8304, "lon": 49.0661},
}


@router.get("/geo", response_model=GeoResponse)
async def get_geo_analytics(
    period_start: date = Query(None, description="Начало периода"),
    period_end: date = Query(None, description="Конец периода"),
    days: int = Query(default=90, ge=7, le=365, description="Период в днях (если даты не указаны)")
):
    """
    Geo аналитика: продажи по регионам с координатами для карты.
    
    Возвращает:
    - Регионы с суммой продаж
    - Координаты для отображения на карте
    - Количество клиентов и заказов по региону
    """
    if supabase is None:
        return GeoResponse(points=[], total_revenue=0, total_orders=0)
    
    try:
        # Calculate date range
        if not period_start or not period_end:
            period_end = date.today()
            period_start = period_end - timedelta(days=days)
        
        # Get sales with customer data - need to join with customers for region
        sales_result = supabase.table("sales").select(
            "customer_id, total_amount, quantity"
        ).gte("sale_date", period_start.isoformat()).lte("sale_date", period_end.isoformat()).execute()
        
        if not sales_result.data:
            return GeoResponse(points=[], total_revenue=0, total_orders=0)
        
        # Get unique customer IDs
        customer_ids = list(set(s.get("customer_id") for s in sales_result.data if s.get("customer_id")))
        
        if not customer_ids:
            return GeoResponse(points=[], total_revenue=0, total_orders=0)
        
        # Get customer regions
        customers_result = supabase.table("customers").select(
            "id, region, latitude, longitude"
        ).in_("id", customer_ids).execute()
        
        # Build lookup
        customer_lookup = {c["id"]: c for c in (customers_result.data or [])}
        
        # Aggregate by region
        region_data = {}
        for sale in sales_result.data:
            customer = customer_lookup.get(sale.get("customer_id"), {})
            region = customer.get("region") or "Unknown"
            
            if region not in region_data:
                region_data[region] = {
                    "revenue": 0,
                    "orders": 0,
                    "customers": set(),
                    "lat": customer.get("latitude"),
                    "lon": customer.get("longitude")
                }
            
            region_data[region]["revenue"] += float(sale.get("total_amount", 0) or 0)
            region_data[region]["orders"] += 1
            if sale.get("customer_id"):
                region_data[region]["customers"].add(sale["customer_id"])
            
            # Update coordinates if available from customer
            if customer.get("latitude") and not region_data[region]["lat"]:
                region_data[region]["lat"] = customer["latitude"]
                region_data[region]["lon"] = customer["longitude"]
        
        # Build response
        points = []
        total_revenue = 0
        total_orders = 0
        
        for region, data in region_data.items():
            # Get coordinates from lookup if not from customer
            lat = data["lat"]
            lon = data["lon"]
            
            if not lat and region in REGION_COORDINATES:
                lat = REGION_COORDINATES[region]["lat"]
                lon = REGION_COORDINATES[region]["lon"]
            
            avg_check = data["revenue"] / data["orders"] if data["orders"] > 0 else 0
            
            points.append(GeoPoint(
                region=region,
                latitude=lat,
                longitude=lon,
                revenue=round(data["revenue"], 2),
                orders=data["orders"],
                customers=len(data["customers"]),
                avg_check=round(avg_check, 2)
            ))
            
            total_revenue += data["revenue"]
            total_orders += data["orders"]
        
        # Sort by revenue descending
        points.sort(key=lambda x: x.revenue, reverse=True)
        
        # Calculate center point
        valid_coords = [(p.latitude, p.longitude) for p in points if p.latitude and p.longitude]
        center = None
        if valid_coords:
            center = {
                "lat": sum(c[0] for c in valid_coords) / len(valid_coords),
                "lon": sum(c[1] for c in valid_coords) / len(valid_coords)
            }
        
        return GeoResponse(
            points=points,
            total_revenue=round(total_revenue, 2),
            total_orders=total_orders,
            center=center
        )
        
    except Exception as e:
        logger.error(f"Geo analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
