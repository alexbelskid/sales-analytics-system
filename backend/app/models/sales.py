from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class SaleItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    discount: float = Field(default=0, ge=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    id: UUID
    sale_id: UUID
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    customer_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    sale_date: date
    discount: float = Field(default=0, ge=0)
    notes: Optional[str] = None


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]


class Sale(SaleBase):
    id: UUID
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SaleWithItems(Sale):
    items: List[SaleItem] = []


class DashboardMetrics(BaseModel):
    total_revenue: float
    total_sales: int
    average_check: float
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class SalesTrend(BaseModel):
    period: str
    amount: float
    count: int


class TopCustomer(BaseModel):
    customer_id: UUID
    name: str
    total: float


class TopProduct(BaseModel):
    product_id: UUID
    name: str
    total_quantity: int
    total_amount: float
