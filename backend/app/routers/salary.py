from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from io import BytesIO
import pandas as pd
from app.database import supabase
from app.models.agents import SalaryCalculation

router = APIRouter()


@router.get("/calculate", response_model=List[SalaryCalculation])
async def calculate_salary(
    year: int = Query(..., ge=2000, le=2100, description="Год"),
    month: int = Query(..., ge=1, le=12, description="Месяц"),
    agent_id: Optional[str] = Query(None, description="ID агента (для одного агента)")
):
    """
    Расчёт зарплаты агентов.
    
    Формула: Оклад + (Продажи × % комиссии) + Бонус - Штраф
    
    Бонус начисляется если продажи >= bonus_threshold
    """
    try:
        # Получаем агентов
        agents_query = supabase.table("agents").select("*").eq("is_active", True)
        if agent_id:
            agents_query = agents_query.eq("id", agent_id)
        agents = agents_query.execute().data
        
        if not agents:
            raise HTTPException(404, "Агенты не найдены")
        
        results = []
        
        # Определяем границы месяца
        if month == 12:
            next_month = f"{year + 1}-01-01"
        else:
            next_month = f"{year}-{month + 1:02d}-01"
        current_month = f"{year}-{month:02d}-01"
        
        agent_ids = [agent["id"] for agent in agents]

        # Получаем продажи для всех агентов за месяц одним запросом
        all_sales = supabase.table("sales")\
            .select("agent_id, total_amount")\
            .in_("agent_id", agent_ids)\
            .gte("sale_date", current_month)\
            .lt("sale_date", next_month)\
            .execute()
            
        sales_by_agent = {}
        for sale in all_sales.data:
            aid = sale.get("agent_id")
            if aid not in sales_by_agent:
                sales_by_agent[aid] = []
            sales_by_agent[aid].append(sale)

        # Получаем сохранённые расчёты для всех агентов одним запросом
        all_calcs = supabase.table("salary_calculations")\
            .select("agent_id, penalty, bonus, notes")\
            .in_("agent_id", agent_ids)\
            .eq("year", year)\
            .eq("month", month)\
            .execute()

        calcs_by_agent = {c.get("agent_id"): c for c in all_calcs.data}

        for agent in agents:
            # Получаем продажи агента из кэша
            agent_sales = sales_by_agent.get(agent["id"], [])
            total_sales = sum(float(s.get("total_amount", 0)) for s in agent_sales)
            
            # Расчёт комиссии
            commission_rate = float(agent.get("commission_rate", 5.0))
            commission = total_sales * (commission_rate / 100)
            
            # Бонус (если превышен порог)
            base_salary = float(agent.get("base_salary", 0))
            bonus_threshold = float(agent.get("bonus_threshold", 100000))
            bonus_amount = float(agent.get("bonus_amount", 5000))
            
            bonus = bonus_amount if total_sales >= bonus_threshold else 0
            
            # Проверяем есть ли сохранённый расчёт со штрафами
            saved_calc = calcs_by_agent.get(agent["id"])
            
            penalty = 0
            if saved_calc:
                penalty = float(saved_calc.get("penalty", 0))
                # Если бонус был вручную изменён
                if saved_calc.get("bonus") is not None:
                    bonus = float(saved_calc.get("bonus", 0))
            
            total_salary = base_salary + commission + bonus - penalty
            
            results.append(SalaryCalculation(
                agent_id=agent["id"],
                agent_name=agent["name"],
                year=year,
                month=month,
                base_salary=round(base_salary, 2),
                sales_amount=round(total_sales, 2),
                commission_rate=commission_rate,
                commission=round(commission, 2),
                bonus=round(bonus, 2),
                penalty=round(penalty, 2),
                total_salary=round(total_salary, 2)
            ))
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_salary_calculation(
    agent_id: str,
    year: int,
    month: int,
    bonus: float = 0,
    penalty: float = 0,
    notes: Optional[str] = None
):
    """
    Сохранение/обновление расчёта зарплаты с бонусами и штрафами.
    """
    try:
        # Получаем агента для расчёта
        agent = supabase.table("agents").select("*").eq("id", agent_id).execute()
        if not agent.data:
            raise HTTPException(404, "Агент не найден")
        
        agent = agent.data[0]
        
        # Рассчитываем продажи
        if month == 12:
            next_month = f"{year + 1}-01-01"
        else:
            next_month = f"{year}-{month + 1:02d}-01"
        current_month = f"{year}-{month:02d}-01"
        
        sales_result = supabase.table("sales")\
            .select("total_amount")\
            .eq("agent_id", agent_id)\
            .gte("sale_date", current_month)\
            .lt("sale_date", next_month)\
            .execute()
        
        total_sales = sum(float(s.get("total_amount", 0)) for s in sales_result.data)
        base_salary = float(agent.get("base_salary", 0))
        commission = total_sales * (float(agent.get("commission_rate", 5.0)) / 100)
        total_salary = base_salary + commission + bonus - penalty
        
        # Upsert
        result = supabase.table("salary_calculations").upsert({
            "agent_id": agent_id,
            "year": year,
            "month": month,
            "base_salary": base_salary,
            "sales_amount": total_sales,
            "commission": commission,
            "bonus": bonus,
            "penalty": penalty,
            "total_salary": total_salary,
            "notes": notes
        }, on_conflict="agent_id,year,month").execute()
        
        return {"status": "saved", "data": result.data[0]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_salary_excel(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12)
):
    """Экспорт расчёта зарплат в Excel"""
    try:
        data = await calculate_salary(year, month)
        
        # Конвертируем в DataFrame
        records = [
            {
                "Агент": s.agent_name,
                "Оклад": s.base_salary,
                "Продажи": s.sales_amount,
                "% комиссии": s.commission_rate,
                "Комиссия": s.commission,
                "Бонус": s.bonus,
                "Штраф": s.penalty,
                "ИТОГО": s.total_salary
            }
            for s in data
        ]
        
        df = pd.DataFrame(records)
        
        # Добавляем итоговую строку
        totals = df[["Оклад", "Продажи", "Комиссия", "Бонус", "Штраф", "ИТОГО"]].sum()
        totals["Агент"] = "ИТОГО"
        totals["% комиссии"] = ""
        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=f'Зарплаты {month:02d}.{year}')
        
        output.seek(0)
        
        filename = f"salary_{year}_{month:02d}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """Список агентов с настройками ЗП"""
    result = supabase.table("agents")\
        .select("id, name, email, base_salary, commission_rate, bonus_threshold, bonus_amount, is_active")\
        .order("name")\
        .execute()
    return result.data


@router.put("/agents/{agent_id}")
async def update_agent_salary_settings(
    agent_id: str,
    base_salary: Optional[float] = None,
    commission_rate: Optional[float] = None,
    bonus_threshold: Optional[float] = None,
    bonus_amount: Optional[float] = None
):
    """Обновление настроек ЗП агента"""
    update_data = {}
    if base_salary is not None:
        update_data["base_salary"] = base_salary
    if commission_rate is not None:
        update_data["commission_rate"] = commission_rate
    if bonus_threshold is not None:
        update_data["bonus_threshold"] = bonus_threshold
    if bonus_amount is not None:
        update_data["bonus_amount"] = bonus_amount
    
    if not update_data:
        raise HTTPException(400, "Нет данных для обновления")
    
    result = supabase.table("agents").update(update_data).eq("id", agent_id).execute()
    
    if not result.data:
        raise HTTPException(404, "Агент не найден")
    
    return result.data[0]
