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
