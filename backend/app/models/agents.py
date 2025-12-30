from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str
    phone: Optional[str] = None
    base_salary: float = Field(default=0, ge=0)
    commission_rate: float = Field(default=5.0, ge=0, le=100)
    bonus_threshold: float = Field(default=100000, ge=0)
    bonus_amount: float = Field(default=5000, ge=0)


class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalaryCalculation(BaseModel):
    agent_id: UUID
    agent_name: str
    year: int
    month: int
    base_salary: float
    sales_amount: float
    commission_rate: float
    commission: float
    bonus: float = 0
    penalty: float = 0
    total_salary: float


class SalaryCalculationCreate(BaseModel):
    agent_id: UUID
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    bonus: float = Field(default=0, ge=0)
    penalty: float = Field(default=0, ge=0)
    notes: Optional[str] = None
