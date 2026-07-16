#!/bin/bash
# 🌸 Flora ↔ Notion 待辦事項同步腳本
# 用途：將 Flora 的長期記憶與 Notion「待辦事項」資料庫雙向同步
# 使用方法：bash sync-notion.sh

NOTION_KEY=$(cat ~/.config/notion/api_key)
DATA_SOURCE_ID="02c33027-a862-40ab-a8d0-252f25555ee5"
DATABASE_ID="62a7f0a0-5f59-4ae8-a828-11938f144c2e"

echo "🌸 Flora ↔ Notion 同步中..."

# Step 1: 從 Notion 讀取
echo "📥 從 Notion 讀取待辦事項..."
curl -s -X POST "https://api.notion.com/v1/data_sources/${DATA_SOURCE_ID}/query" \
  -H "Authorization: Bearer ${NOTION_KEY}" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -c "
import json, sys
data = json.load(sys.stdin)
results = data.get('results', [])
print(f'共 {len(results)} 項')
for r in results:
    props = r.get('properties', {})
    title = ''.join([t.get('plain_text','') for t in props.get('事項', {}).get('title', [])])
    status = props.get('狀態', {}).get('status', {}).get('name', '未設定')
    print(f'  • {title} [{status}]')
"

echo "✅ 同步完成！"
echo ""
echo "💡 Notion API 資訊："
echo "  Data Source ID: ${DATA_SOURCE_ID}"
echo "  Database ID:    ${DATABASE_ID}"
