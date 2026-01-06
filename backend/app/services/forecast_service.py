import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from app.database import supabase

# Prophet импортируется lazy для ускорения старта
_prophet_model = None


class ForecastService:
    """
    Сервис прогнозирования продаж на основе Prophet.
    
    Особенности:
    - Учёт годовой и недельной сезонности
    - Обнаружение аномалий
    - Lazy loading модели
    """
    
    def __init__(self):
        self.model = None
        self.last_trained = None
        self.training_data = None
    
    async def train(
        self,
        product_id: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Обучение Prophet модели на исторических данных.
        
        Args:
            product_id: Опционально, обучение на данных конкретного товара
            customer_id: Опционально, обучение на данных конкретного клиента
        
        Returns:
            Метрики обучения
        """
        try:
            from prophet import Prophet
        except ImportError:
            return {
                "status": "error",
                "message": "Prophet не установлен. Установите: pip install prophet",
                "records_used": 0,
                "metrics": {}
            }
        
        # Получаем исторические данные
        query = supabase.table("sales").select("sale_date, total_amount")
        
        if product_id:
            # Фильтр по товару через sale_items
            sales_with_product = supabase.table("sale_items")\
                .select("sale_id")\
                .eq("product_id", product_id)\
                .execute()
            if sales_with_product.data:
                sale_ids = [s["sale_id"] for s in sales_with_product.data]
                query = query.in_("id", sale_ids)
        
        if customer_id:
            query = query.eq("customer_id", customer_id)
        
        result = query.execute()
        
        if not result.data or len(result.data) < 10:
            return {
                "status": "error",
                "message": "Недостаточно данных для обучения (минимум 10 записей)",
                "records_used": len(result.data) if result.data else 0,
                "metrics": {}
            }
        
        # Подготовка данных для Prophet
        df = pd.DataFrame(result.data)
        df['ds'] = pd.to_datetime(df['sale_date'])
        df['y'] = df['total_amount'].astype(float)
        
        # Агрегация по дням
        df = df.groupby('ds')['y'].sum().reset_index()
        
        # Обучаем Prophet
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0
        )
        
        self.model.fit(df)
        self.last_trained = datetime.now()
        self.training_data = df
        
        return {
            "status": "success",
            "records_used": len(df),
            "date_range": {
                "from": df['ds'].min().strftime('%Y-%m-%d'),
                "to": df['ds'].max().strftime('%Y-%m-%d')
            },
            "metrics": {
                "total_days": len(df),
                "avg_daily_sales": round(df['y'].mean(), 2),
                "max_daily_sales": round(df['y'].max(), 2)
            }
        }
    
    async def predict(
        self,
        months_ahead: int = 3,
        product_id: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Прогноз продаж на N месяцев вперёд.
        
        Args:
            months_ahead: Количество месяцев для прогноза (1-12)
            product_id: Опционально, прогноз для конкретного товара
            customer_id: Опционально, прогноз для конкретного клиента
        
        Returns:
            Прогноз с доверительными интервалами
        """
        # Проверяем, нужно ли переобучить модель
        if self.model is None:
            await self.train(product_id, customer_id)
        
        if self.model is None:
            # Fallback: простой прогноз на основе среднего
            return await self._simple_forecast(months_ahead)
        
        # Создаём будущие даты
        days_ahead = months_ahead * 30
        future = self.model.make_future_dataframe(periods=days_ahead)
        
        # Прогнозируем
        forecast = self.model.predict(future)
        
        # Берём только будущие даты
        future_forecast = forecast.tail(days_ahead)
        
        # Агрегируем по месяцам для удобства
        future_forecast['month'] = future_forecast['ds'].dt.to_period('M')
        monthly = future_forecast.groupby('month').agg({
            'yhat': 'sum',
            'yhat_lower': 'sum',
            'yhat_upper': 'sum'
        }).reset_index()
        
        return {
            "dates": [str(m) for m in monthly['month']],
            "forecast": monthly['yhat'].clip(lower=0).tolist(),
            "lower": monthly['yhat_lower'].clip(lower=0).tolist(),
            "upper": monthly['yhat_upper'].clip(lower=0).tolist(),
            "daily": {
                "dates": future_forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                "forecast": future_forecast['yhat'].clip(lower=0).tolist(),
                "lower": future_forecast['yhat_lower'].clip(lower=0).tolist(),
                "upper": future_forecast['yhat_upper'].clip(lower=0).tolist()
            }
        }
    
    async def _simple_forecast(self, months_ahead: int) -> Dict[str, Any]:
        """Простой прогноз без Prophet"""
        result = supabase.table("sales").select("sale_date, total_amount").execute()
        
        if not result.data:
            return {
                "dates": [],
                "forecast": [],
                "lower": [],
                "upper": []
            }
        
        df = pd.DataFrame(result.data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['month'] = df['sale_date'].dt.to_period('M')
        
        monthly = df.groupby('month')['total_amount'].sum()
        avg_monthly = monthly.mean()
        std_monthly = monthly.std() if len(monthly) > 1 else avg_monthly * 0.2
        
        future_months = pd.period_range(
            start=df['sale_date'].max() + timedelta(days=1),
            periods=months_ahead,
            freq='M'
        )
        
        return {
            "dates": [str(m) for m in future_months],
            "forecast": [round(avg_monthly, 2)] * months_ahead,
            "lower": [round(avg_monthly - std_monthly, 2)] * months_ahead,
            "upper": [round(avg_monthly + std_monthly, 2)] * months_ahead
        }
    
    async def detect_anomalies(self, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Обнаружение аномалий в исторических продажах.
        
        Args:
            threshold: Порог аномалии в стандартных отклонениях
        
        Returns:
            Список аномальных дней
        """
        result = supabase.table("sales").select("sale_date, total_amount").execute()
        
        if not result.data or len(result.data) < 10:
            return []
        
        df = pd.DataFrame(result.data)
        df['ds'] = pd.to_datetime(df['sale_date'])
        df['y'] = df['total_amount'].astype(float)
        df = df.groupby('ds')['y'].sum().reset_index()
        
        # Статистики
        mean = df['y'].mean()
        std = df['y'].std()
        
        # Находим аномалии
        df['z_score'] = (df['y'] - mean) / std
        df['is_anomaly'] = abs(df['z_score']) > threshold
        
        anomalies = df[df['is_anomaly']].copy()
        anomalies['type'] = anomalies['z_score'].apply(
            lambda x: 'high' if x > 0 else 'low'
        )
        
        return [
            {
                "date": row['ds'].strftime('%Y-%m-%d'),
                "amount": round(row['y'], 2),
                "expected": round(mean, 2),
                "deviation": round(row['z_score'], 2),
                "type": row['type']
            }
            for _, row in anomalies.iterrows()
        ]
    
    async def get_seasonality(self) -> Dict[str, Any]:
        """
        Анализ сезонности продаж.
        
        Returns:
            Данные о месячной и дневной сезонности
        """
        # Get all sales (date and amount)
        result = supabase.table("sales").select("sale_date, total_amount").execute()
        
        if not result.data:
            return {"monthly": [], "weekly": []}
        
        df = pd.DataFrame(result.data)
        df['ds'] = pd.to_datetime(df['sale_date'])
        df['y'] = df['total_amount'].astype(float)
        
        # 1. Monthly Seasonality
        # Group by Year-Month first to get monthly totals
        df['ym'] = df['ds'].dt.to_period('M')
        monthly_totals = df.groupby('ym')['y'].sum().reset_index()
        monthly_totals['month'] = monthly_totals['ym'].dt.month
        
        # Average total sales for each month (1-12) across all available years
        avg_sales_by_month = monthly_totals.groupby('month')['y'].mean()
        
        # Overall average monthly sales
        overall_avg_monthly = monthly_totals['y'].mean()
        
        # Calculate index
        if overall_avg_monthly > 0:
            monthly_seasonality = (avg_sales_by_month / overall_avg_monthly * 100).round(1)
        else:
            monthly_seasonality = pd.Series([100]*12, index=range(1, 13))
        
        month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
                       'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
        
        # 2. Weekly Seasonality
        # Group by specific date to get daily totals
        daily_totals = df.groupby('ds')['y'].sum().reset_index()
        daily_totals['weekday'] = daily_totals['ds'].dt.dayofweek
        
        # Average total sales for each weekday (0-6)
        avg_sales_by_weekday = daily_totals.groupby('weekday')['y'].mean()
        overall_avg_daily = daily_totals['y'].mean()
        
        if overall_avg_daily > 0:
            weekly_seasonality = (avg_sales_by_weekday / overall_avg_daily * 100).round(1)
        else:
            weekly_seasonality = pd.Series([100]*7, index=range(7))
        
        day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        
        return {
            "monthly": [
                {"month": month_names[i-1], "index": float(monthly_seasonality.get(i, 100))}
                for i in range(1, 13)
            ],
            "weekly": [
                {"day": day_names[i], "index": float(weekly_seasonality.get(i, 100))}
                for i in range(7)
            ]
        }
