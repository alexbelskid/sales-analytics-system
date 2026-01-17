# Knowledge Base Directory

This directory contains dynamic and static knowledge that enhances the AI's contextual understanding.

## Files

### `company_context.json`
Dynamic knowledge base that stores:
- **facts**: User-taught facts about the company (e.g., new warehouses, partnerships)
- **belarus_context**: Static Belarus market data (regions, cities, tax rates, logistics)
- **metadata**: Version and update tracking

### Schema

```json
{
  "facts": [
    {
      "id": "uuid",
      "category": "logistics|products|regions|partners|other",
      "fact": "В Гродно у нас теперь новый склад",
      "created_at": "ISO-8601 timestamp",
      "created_by": "user|system",
      "confidence": 0.0-1.0
    }
  ],
  "belarus_context": {
    "regions": ["array of oblast names"],
    "major_cities": ["array of city names"],
    "tax_rate_vat": 20,
    "currency": "BYN",
    "logistics_notes": "string",
    "retail_specifics": "string"
  }
}
```

## Usage

The AI services automatically load this context when processing queries to provide:
- Regional expertise
- Company-specific knowledge
- Market context for strategic recommendations

## Updating Facts

Facts can be added via:
1. API endpoint: `POST /api/ai/teach-fact`
2. Direct JSON editing (for bulk updates)
3. User messages (automatic extraction - future feature)
