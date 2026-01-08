# Database Optimization

## RLS Performance Fix

Этот скрипт исправляет проблемы производительности Row Level Security (RLS) политик.

### Проблемы

1. **Дублирующиеся политики** - Множественные permissive политики для одной таблицы замедляют запросы
2. **Неоптимизированные auth вызовы** - `auth.role()` пересчитывается для каждой строки

### Решение

Скрипт `fix_rls_performance.sql`:
- Удаляет дублирующиеся политики
- Объединяет политики для authenticated и service_role
- Оборачивает `auth.role()` в `SELECT` для кэширования

### Применение

Выполните в Supabase SQL Editor:

```sql
-- Скопируйте и выполните содержимое fix_rls_performance.sql
```

### Затронутые таблицы

- `agents`
- `sale_items`
- `email_settings`
- `incoming_emails`
- `email_responses`
- `response_tone_settings`
- `response_templates`

### Результат

✅ Уменьшение количества политик с ~100+ до 7  
✅ Оптимизация проверки ролей  
✅ Улучшение производительности запросов

---

## AI Assistant Tables

Скрипт `create_ai_tables.sql` создаёт таблицы для AI Ассистента.

### Таблицы

- `knowledge_base` - База знаний (продукты, условия, контакты, FAQ)
- `training_examples` - Примеры для обучения AI

### Применение

Выполните в Supabase SQL Editor:

```sql
-- Скопируйте и выполните содержимое create_ai_tables.sql
```

### Результат

✅ Таблицы с правильной структурой  
✅ RLS политики для доступа  
✅ Индексы для быстрого поиска
