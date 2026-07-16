---
name: "lot-draw"
description: "Draw a Chinese fortune lot (六十甲子籤) with poem and full interpretation"
---

# Lot Draw (求籤)

Draw a Chinese sixty-cycle fortune lot (六十甲子籤) with poem and full interpretation.

## Triggers
- `/draw` — draw a random fortune lot
- `/qian` — same as `/draw`

## Data Files
- **籤詩**: `/home/borsheng/.openclaw/workspace/memory/sixty_lots.json` — all 60 lots with poetry
- **解籤**: `/home/borsheng/.openclaw/workspace/memory/sixty_lots_interpret.json` — interpretations for all 60 lots

## Procedure

1. Generate a random number between 1 and 60
2. Read the lot data from the local JSON files (no API call needed)
3. Parse `fs_command` for attributes (屬X利X．宜其X方)
4. Split `fs_poetry` by comma for multi-line display
5. Output the FULL interpretation list (all lines, numbered), NOT a summarized version

## Output Format
```
🎋 六十甲子籤・第X籤【干支】
屬X利X．宜其X方

籤詩：
詩句第一行
詩句第二行
詩句第三行
詩句第四行

📖 完整解說（共N句）：
1️⃣ 第一句解說
2️⃣ 第二句解說
...
N️⃣ 第N句解說
```

## Notes
- All data is stored locally, zero network dependency
- Output ALL interpretation lines — do NOT summarize or condense
- Response in Traditional Chinese
