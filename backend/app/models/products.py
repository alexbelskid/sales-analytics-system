from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = None
    price: float = Field(..., ge=0)
    cost_price: Optional[float] = Field(default=0, ge=0)
    category: Optional[str] = None
    description: Optional[str] = None
    unit: str = "шт"
    in_stock: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductWithStats(Product):
    total_sold: int = 0
    total_revenue: float = 0
