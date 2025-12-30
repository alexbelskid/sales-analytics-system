from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.forecast_service import ForecastService

router = APIRouter()
forecast_service = ForecastService()


class ForecastPoint(BaseModel):
    date: str
    predicted: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    forecast: List[ForecastPoint]
    model_info: dict
    generated_at: datetime


class TrainResponse(BaseModel):
    status: str
    records_used: int
    metrics: dict
    trained_at: datetime


@router.get("/predict", response_model=ForecastResponse)
async def predict_sales(
    months_ahead: int = Query(default=3, ge=1, le=12, description="Количество месяцев для прогноза"),
    product_id: Optional[str] = Query(None, description="ID товара для прогноза"),
    customer_id: Optional[str] = Query(None, description="ID клиента для прогноза")
):
    """
    Прогнозирование продаж на N месяцев вперёд.
    
    Использует Prophet модель с учётом:
    - Годовой сезонности
    - Недельной сезонности
    - Трендов
    """
    try:
        prediction = await forecast_service.predict(
            months_ahead=months_ahead,
            product_id=product_id,
            customer_id=customer_id
        )
        
        forecast_points = [
            ForecastPoint(
                date=date,
                predicted=round(pred, 2),
                lower_bound=round(lower, 2),
                upper_bound=round(upper, 2)
            )
            for date, pred, lower, upper in zip(
                prediction["dates"],
                prediction["forecast"],
                prediction["lower"],
                prediction["upper"]
            )
        ]
        
        return ForecastResponse(
            forecast=forecast_points,
            model_info={
                "model": "Prophet",
                "months_ahead": months_ahead,
                "confidence_interval": "80%"
            },
            generated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка прогнозирования: {str(e)}")


@router.post("/train", response_model=TrainResponse)
async def train_model():
    """
    Переобучение модели на актуальных данных.
    
    Рекомендуется запускать:
    - После загрузки новых данных
    - Раз в неделю/месяц
    """
    try:
        result = await forecast_service.train()
        
        return TrainResponse(
            status="trained",
            records_used=result.get("records_used", 0),
            metrics=result.get("metrics", {}),
            trained_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обучения: {str(e)}")


@router.get("/anomalies")
async def detect_anomalies(
    threshold: float = Query(default=2.0, ge=1.0, le=5.0, description="Порог аномалии (в стд. отклонениях)")
):
    """
    Обнаружение аномалий в продажах.
    
    Находит дни, когда продажи значительно отличались от прогноза.
    """
    try:
        anomalies = await forecast_service.detect_anomalies(threshold=threshold)
        return {
            "anomalies": anomalies,
            "threshold": threshold,
            "description": f"Дни с отклонением более {threshold} стандартных отклонений"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasonality")
async def get_seasonality():
    """
    Анализ сезонности продаж.
    
    Возвращает:
    - Годовую сезонность (по месяцам)
    - Недельную сезонность (по дням недели)
    """
    try:
        seasonality = await forecast_service.get_seasonality()
        return seasonality
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
