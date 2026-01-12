#!/bin/bash
# Upload converted CSV file to the API

CSV_FILE="/Users/alexbelski/Downloads/Продажи_TM_converted.csv"
API_URL="https://sales-analytics-system-psi.vercel.app/api/agent-analytics/import-excel?period_start=2026-01-01&period_end=2026-01-31"

echo "Uploading CSV file: $CSV_FILE"
echo "To: $API_URL"
echo ""

# Upload the file
curl -X POST "$API_URL" \
  -F "file=@$CSV_FILE" \
  -H "Accept: application/json"

echo ""
echo "Upload complete!"
