#!/bin/bash
# Upload Excel file to the API directly

EXCEL_FILE="/Users/alexbelski/Downloads/Продажи ТМ 08.01.2026 85022.xls"
API_URL="https://sales-analytics-system-psi.vercel.app/api/agent-analytics/import-excel?period_start=2026-01-01&period_end=2026-01-31"

echo "Uploading file: $EXCEL_FILE"
echo "To: $API_URL"
echo ""

# Upload the file
curl -X POST "$API_URL" \
  -F "file=@$EXCEL_FILE" \
  -v

echo ""
echo "Upload complete!"
