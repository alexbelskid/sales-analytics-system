# Sales Analytics BI Architecture

## 1. Overview
Проект использует архитектуру **Modern Data Stack** на базе Python и SQL.
**Supabase** выступает в роли единого хранилища данных (Single Source of Truth), обслуживающего как операционные задачи, так и аналитику.

---

## 2. Data Flow

```mermaid
graph LR
    User[User Upload CSV] -->|FastAPI| Extractor[Python Extractor]
    Extractor -->|Load| Raw[(Supabase: raw schema)]
    
    subgraph "Supabase DWH (dbt transformation)"
        Raw -->|Clean| Staging[Staging Views]
        Staging -->|Join/Calc| Inter[Intermediate]
        Inter -->|Agg| Marts[Marts Tables]
    end
    
    Marts -->|SQLAlchemy| Backend[FastAPI Backend]
    Backend -->|JSON| Frontend[Next.js Dashboard]
```

---

## 3. Компоненты

### 3.1 Extractors (`bi/src/extractors/`)
Отвечают за загрузку данных в схему `raw`.

**Пример: CSV Extractor**
Загружает данные, добавляя метаданные (время загрузки, имя файла).

```python
# bi/src/extractors/csv_loader.py
import pandas as pd
from sqlalchemy import create_engine
import os

def load_csv_to_supabase(file_path: str, table_name: str, connection_string: str):
    """
    Загружает CSV в схему 'raw' Supabase, используя Pandas + SQLAlchemy (fastest method).
    """
    # 1. Читаем CSV
    df = pd.read_csv(file_path)
    
    # 2. Добавляем метаданные
    df['_loaded_at'] = pd.Timestamp.now()
    
    # 3. Подключаемся и загружаем
    engine = create_engine(connection_string)
    
    with engine.connect() as conn:
        df.to_sql(
            name=table_name,
            con=conn,
            schema='raw',
            if_exists='append', # Или 'replace' для полной перезагрузки
            index=False,
            method='multi',     # Оптимизация вставки
            chunksize=1000
        )
    print(f"Successfully loaded {len(df)} rows into raw.{table_name}")
```

### 3.2 Transformers (`bi/models/` - dbt)
dbt управляет всей логикой трансформации SQL.

**Конфигурация (`profiles.yml`):**
```yaml
sales_analytics:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('SUPABASE_DB_HOST') }}"
      user: "{{ env_var('SUPABASE_DB_USER') }}"
      pass: "{{ env_var('SUPABASE_DB_PASSWORD') }}"
      port: 5432
      dbname: postgres
      schema: public # schema по умолчанию, модели раскидываются по конфигам
      threads: 4
```

**Пример модели Staging (`models/staging/stg_sales.sql`):**
```sql
{{ config(materialized='view', schema='staging') }}

SELECT
    id as raw_id,
    "Date"::date as sale_date,
    "Product"::varchar as product_name,
    "Amount"::numeric as amount,
    _loaded_at
FROM {{ source('raw', 'sales_upload') }}
```

**Пример модели Marts (`models/marts/fct_daily_sales.sql`):**
```sql
{{ config(materialized='table', schema='marts') }}

SELECT
    sale_date,
    product_name,
    SUM(amount) as total_revenue,
    COUNT(*) as transaction_count
FROM {{ ref('stg_sales') }}
GROUP BY 1, 2
```

### 3.3 Orchestration (`bi/pipelines/`)
Airflow или простой Cron скрипт, запускающий последовательность.

**Пример DAG (`etl_sales.py`):**
1. **Task 1**: `python bi/src/main.py load_csv` (Extract & Load)
2. **Task 2**: `dbt run` (Transform)
3. **Task 3**: `dbt test` (Validate)

---

## 4. Конфигурационные файлы

### `.env` (в корне проекта)
```bash
# Supabase API (для работы с файлами, auth)
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Supabase DB Direct Connection (для dbt и SQLAlchemy)
# Важно: использовать порт 5432 (Session) или 6543 (Pooler)
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.xyz.supabase.co:5432/postgres
SUPABASE_DB_HOST=db.xyz.supabase.co
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_password
```

### `bi/config/database.yml`
```yaml
schemas:
  raw: 
    description: "Сырые данные без обработки"
  staging:
    description: "Очищенные views"
  marts:
    description: "Бизнес-витрины для дашбордов"
```

---

## 5. Интеграция с Backend (FastAPI)

FastAPI должен читать данные только из схемы `marts`.

```python
# backend/app/api/analytics.py
from sqlalchemy import text

@router.get("/dashboard/sales")
async def get_sales_metrics(db: AsyncSession = Depends(get_db)):
    # Читаем из подготовленной dbt таблицы marts.fct_daily_sales
    # Это работает мгновенно, в отличие от расчета по сырым данным
    query = text("SELECT * FROM marts.fct_daily_sales ORDER BY sale_date DESC LIMIT 30")
    result = await db.execute(query)
    return result.mappings().all()
```
