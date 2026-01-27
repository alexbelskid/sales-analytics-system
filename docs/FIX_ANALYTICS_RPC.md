# 🔧 Исправление ошибки "column reference total_revenue is ambiguous"

## Проблема

В логах backend видна ошибка:
```
RPC not available for top-products: {'code': '42702', 'message': 'column reference "total_revenue" is ambiguous'}
```

Это происходит потому, что в базе данных отсутствует RPC-функция `get_top_products_by_sales`, которую пытается вызвать backend.

## Решение

Необходимо создать RPC-функции в Supabase для оптимизированных аналитических запросов.

## Инструкция по применению

### Вариант 1: Через Supabase SQL Editor (Рекомендуется)

1. **Откройте Supabase SQL Editor:**
   - Перейдите: https://app.supabase.com/project/hnunemnxpmyhexzcvmtb/sql

2. **Скопируйте SQL из файла:**
   - Откройте файл: `database/create_analytics_functions.sql`
   - Скопируйте весь контент файла

3. **Выполните SQL:**
   - Вставьте SQL в редактор
   - Нажмите кнопку "Run" или `Cmd/Ctrl + Enter`

4. **Проверьте результат:**
   - Должны создаться 3 функции без ошибок
   - В выводе вы увидите подтверждение выполнения

### Вариант 2: Используя psql (для опытных пользователей)

```bash
# Если у вас установлен PostgreSQL клиент:
psql "postgresql://postgres:[YOUR-PASSWORD]@db.hnunemnxpmyhexzcvmtb.supabase.co:5432/postgres" \
  -f database/create_analytics_functions.sql
```

## Что создается

SQL скрипт создает 3 RPC-функции:

### 1. `get_top_products_by_sales(p_limit, p_days)`
Возвращает топ товаров по выручке за последние N дней.

**Параметры:**
- `p_limit` (INT): Количество товаров (по умолчанию 10)
- `p_days` (INT): За последние N дней (по умолчанию 90)

**Возвращает:**
```
product_id      TEXT
product_name    TEXT
total_revenue   NUMERIC
orders_count    BIGINT
total_quantity  NUMERIC
```

### 2. `get_top_customers_by_revenue(p_limit, p_days)`
Возвращает топ клиентов по выручке.

**Параметры:**
- `p_limit` (INT): Количество клиентов
- `p_days` (INT): За последние N дней

**Возвращает:**
```
customer_id       TEXT
customer_name     TEXT
total_revenue     NUMERIC
orders_count      BIGINT
avg_order_value   NUMERIC
```

### 3. `get_sales_trend(p_period)`
Возвращает тренд продаж по периодам.

**Параметры:**
- `p_period` (TEXT): 'day', 'week', или 'month'

**Возвращает:**
```
period_date       DATE
total_revenue     NUMERIC
orders_count      BIGINT
avg_order_value   NUMERIC
```

## Проверка после применения

После выполнения SQL:

1. **Перезапустите backend:**
   ```bash
   ./stop.sh
   ./start.sh
   ```

2. **Проверьте логи:**
   ```bash
   tail -f backend.log
   ```
   
   Ошибка `RPC not available for top-products` должна исчезнуть.

3. **Протестируйте endpoint:**
   ```bash
   curl "http://localhost:8000/api/analytics/top-products?limit=5"
   ```
   
   Должен вернуть данные без ошибок.

## Технические детали

### Почему это исправляет проблему?

В оригинальном запросе была неоднозначность:
- Таблица `sales` имеет колонку `total_amount`
- Таблица `products` имеет колонку `total_revenue`
- При JOIN возникала неоднозначность какую `total_revenue` использовать

Наши функции явно указывают:
```sql
SELECT 
    s.product_id::TEXT,
    p.name AS product_name,
    SUM(s.total_amount)::NUMERIC AS total_revenue,  -- Явно из sales
    COUNT(DISTINCT s.id)::BIGINT AS orders_count,
    SUM(s.quantity)::NUMERIC AS total_quantity
FROM sales s
LEFT JOIN products p ON s.product_id = p.id
GROUP BY s.product_id, p.name
```

### Преимущества RPC-функций

1. **Производительность**: Агрегация происходит на стороне БД
2. **Безопасность**: Используют `SECURITY DEFINER`
3. **Переиспользование**: Одна функция для всех запросов
4. **Кэширование**: Backend кэширует результаты
5. **Читабельность**: Код backend становится проще

## Альтернативное решение (если RPC недоступен)

Если не можете создать RPC-функции, backend использует fallback логику:
1. Пытается вызвать RPC
2. Если не получается, агрегирует данные из таблицы `sales`
3. В крайнем случае, использует pre-calculated данные из `products`

Но RPC-функции дают лучшую производительность и решают проблему ambiguous column.

## Troubleshooting

### Ошибка: "permission denied for function"
```sql
-- Выполните в SQL Editor:
GRANT EXECUTE ON FUNCTION get_top_products_by_sales(INT, INT) TO service_role;
GRANT EXECUTE ON FUNCTION get_top_customers_by_revenue(INT, INT) TO service_role;
GRANT EXECUTE ON FUNCTION get_sales_trend(TEXT) TO service_role;
```

### Ошибка: "function already exists"
```sql
-- Удалите существующие функции:
DROP FUNCTION IF EXISTS get_top_products_by_sales(INT, INT);
DROP FUNCTION IF EXISTS get_top_customers_by_revenue(INT, INT);
DROP FUNCTION IF EXISTS get_sales_trend(TEXT);
```

### Schema cache не обновляется
```sql
-- Форсируем обновление:
NOTIFY pgrst, 'reload schema';
```

## Дополнительная информация

- **Файл SQL**: `database/create_analytics_functions.sql`
- **Backend код**: `backend/app/routers/analytics.py` (строка 249)
- **Логи ошибки**: `backend.log` (строка 27)

---

**Статус**: ✅ Готово к применению  
**Версия**: 1.0  
**Дата**: 27 января 2025
