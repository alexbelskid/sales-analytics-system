# Quick Test Guide - AI Brain Configuration

## Prerequisites
- Backend running: `cd backend && uvicorn app.main:app --reload`
- Frontend running: `cd frontend && npm run dev`
- API keys configured (GROQ_API_KEY or OPENAI_API_KEY)

---

## Test 1: Memory Injection (Teach a Fact)

### Step 1: Teach the AI about a new warehouse

```bash
curl -X POST http://localhost:8000/api/ai/teach-fact \
  -H "Content-Type: application/json" \
  -d '{
    "fact": "В Гродно у нас теперь новый склад на 500 кв.м., открылся в январе 2026",
    "category": "logistics"
  }'
```

Expected response:
```json
{
  "success": true,
  "fact_id": "some-uuid",
  "message": "Факт успешно сохранён в категории 'logistics'"
}
```

### Step 2: Verify the fact was saved

```bash
curl http://localhost:8000/api/ai/facts
```

You should see your fact in the response.

### Step 3: Test AI memory

Go to http://localhost:3000/ai-assistant and ask:

**Question:** "Где у нас склады?"

**Expected:** AI should mention the new Grodno warehouse you just taught it.

---

## Test 2: Strategic Analysis with Belarus Context

Go to http://localhost:3000/ai-assistant

**Question:** "Стоит ли нам расширяться в Брест?"

**What to look for:**
- ✅ AI analyzes current Brest sales (from database)
- ✅ AI searches for Brest economic conditions (from web)
- ✅ AI provides strategic recommendation
- ✅ AI mentions Belarus-specific factors (logistics, regional specifics)
- ✅ Response is in Russian
- ✅ Sources are cited ("По данным нашей базы...", "Согласно новостям...")

---

## Test 3: Belarus Market Expertise

**Question:** "Какие налоги на продажи в РБ?"

**Expected:**
- ✅ AI mentions 20% VAT
- ✅ AI references Belarus tax legislation
- ✅ Response demonstrates Belarus market knowledge

---

## Test 4: Data Priority (DB First)

**Question:** "Какие продажи в Минске за последний месяц?"

**What to look for:**
- ✅ AI queries the database first (check browser console for API calls)
- ✅ AI generates SQL query for Minsk sales
- ✅ AI provides data from internal database
- ✅ Only searches web if database has no data

---

## Test 5: View All Facts

```bash
# Get all facts
curl http://localhost:8000/api/ai/facts

# Get facts by category
curl http://localhost:8000/api/ai/facts?category=logistics

# Get Belarus context
curl http://localhost:8000/api/ai/belarus-context
```

---

## Test 6: Teach Multiple Facts

```bash
# Add product fact
curl -X POST http://localhost:8000/api/ai/teach-fact \
  -H "Content-Type: application/json" \
  -d '{
    "fact": "Наш новый продукт Шоколадные конфеты Премиум запущен в декабре 2025",
    "category": "products"
  }'

# Add partnership fact
curl -X POST http://localhost:8000/api/ai/teach-fact \
  -H "Content-Type: application/json" \
  -d '{
    "fact": "Подписали контракт с сетью Евроопт на эксклюзивную поставку в Минске",
    "category": "partners"
  }'

# Add regional fact
curl -X POST http://localhost:8000/api/ai/teach-fact \
  -H "Content-Type: application/json" \
  -d '{
    "fact": "В Могилевской области открыли 3 новых точки продаж в январе 2026",
    "category": "regions"
  }'
```

Then ask the AI:
- "Какие у нас новые продукты?"
- "С какими сетями мы работаем?"
- "Где мы расширяемся?"

The AI should reference the facts you taught it.

---

## Expected AI Behavior

### ✅ Persona
- Responds as Strategic Director of Development
- Provides strategic insights, not just data
- Identifies growth opportunities and risks

### ✅ Belarus Expertise
- Knows 6 oblasts
- Understands logistics (М1, М5, М6 corridors)
- Knows tax system (20% VAT)
- Familiar with retail landscape (Евроопт, Корона)

### ✅ Data Priority
- Always checks database first
- Searches web only when needed
- Never fabricates data
- Cites sources

### ✅ Memory
- Remembers taught facts
- Uses them in future responses
- Organizes by category

---

## Troubleshooting

### AI doesn't mention taught facts
1. Check if fact was saved: `curl http://localhost:8000/api/ai/facts`
2. Restart backend to clear cache
3. Make sure question is relevant to the fact

### AI gives generic responses
1. Verify API keys are configured
2. Check backend logs for errors
3. Ensure Groq or OpenAI API is working

### Database queries fail
1. Check Supabase connection
2. Verify `execute_safe_query` function exists in database
3. Check backend logs for SQL errors

---

## Success Criteria

After running all tests, the AI should:
- ✅ Behave as Strategic Director with Belarus expertise
- ✅ Remember and use taught facts
- ✅ Prioritize database over web search
- ✅ Provide strategic recommendations
- ✅ Cite sources properly
- ✅ Never fabricate information
