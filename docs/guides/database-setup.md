# Настройка Supabase Storage для файлового хранилища

## Шаги настройки

### 1. Создать Storage Bucket в Supabase

1. Открой Supabase Dashboard: https://supabase.com/dashboard/project/hnunemnxpmyhexzcvmtb
2. Перейди в раздел **Storage** (слева в меню)
3. Нажми **"New bucket"**
4. Заполни форму:
   - **Name**: `import-files`
   - **Public bucket**: ❌ (оставь выключенным - файлы приватные)
   - **File size limit**: 100 MB
   - **Allowed MIME types**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel`
5. Нажми **"Create bucket"**

### 2. Настроить политики доступа (RLS)

После создания bucket'а нужно настроить политики:

1. В списке buckets нажми на `import-files`
2. Перейди на вкладку **"Policies"**
3. Нажми **"New policy"**
4. Выбери **"Custom policy"**
5. Создай политику для чтения:
   ```sql
   -- Policy name: Allow authenticated read
   -- Operation: SELECT
   -- Target roles: authenticated
   
   CREATE POLICY "Allow authenticated read"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'import-files' AND auth.role() = 'authenticated');
   ```

6. Создай политику для записи:
   ```sql
   -- Policy name: Allow authenticated upload
   -- Operation: INSERT
   -- Target roles: authenticated
   
   CREATE POLICY "Allow authenticated upload"
   ON storage.objects FOR INSERT
   WITH CHECK (bucket_id = 'import-files' AND auth.role() = 'authenticated');
   ```

**ВАЖНО**: Если используешь service_role key (как сейчас), политики RLS не нужны - service_role обходит все ограничения.

### 3. Запустить миграцию БД

Выполни SQL миграцию для добавления поля `storage_path`:

1. Открой **SQL Editor** в Supabase Dashboard
2. Скопируй содержимое файла `database/migrations/004_add_storage_path_to_import_history.sql`
3. Вставь в редактор и нажми **"Run"**

Или через терминал:

```bash
cd "/Users/alexbelski/Desktop/new bi project"
cat database/migrations/004_add_storage_path_to_import_history.sql
```

Скопируй вывод и выполни в SQL Editor.

### 4. Проверить настройки

После настройки bucket'а и миграции:

1. Загрузи тестовый Excel файл через UI
2. Проверь, что файл появился в Storage (Storage → import-files → imports/)
3. Проверь, что в таблице `import_history` появилось поле `storage_path`
4. Нажми кнопку "Скачать" и убедись, что файл скачивается

## Структура хранилища

Файлы будут храниться по пути:
```
import-files/
  └── imports/
      ├── 20260111_182054_sales_data.xlsx
      ├── 20260111_183012_agents_report.xlsx
      └── ...
```

Формат имени: `{timestamp}_{original_filename}`

## Troubleshooting

### Ошибка "bucket not found"
- Убедись, что bucket называется точно `import-files`
- Проверь, что bucket создан в правильном проекте

### Ошибка "permission denied"
- Проверь, что используешь `service_role` key в `.env`
- Или настрой RLS политики (см. шаг 2)

### Файл не скачивается
- Проверь, что `storage_path` не NULL в `import_history`
- Проверь логи бэкенда на ошибки
- Убедись, что файл существует в Storage
