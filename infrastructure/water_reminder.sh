#!/bin/bash
# 1. 取得 AI 生成的創意文字提醒
REMINDER_TEXT=$(docker exec openclaw openclaw agent --to 8344400160 --message "請用活潑、具創意且每次不同的口吻提醒我喝水。只需回覆提醒內容文字，不要包含其他標籤或格式。" --json | docker exec -i openclaw jq -r '.result.payloads[0].text')

# 2. 如果文字不為空，進行語音合成
if [ ! -z "$REMINDER_TEXT" ]; then
    # 建立暫存目錄
    docker exec openclaw mkdir -p /home/node/.openclaw/workspace/temp_media
    
    # 生成原始語音檔
    docker exec openclaw node /home/node/.openclaw/workspace/skills/edge-tts/scripts/tts-converter.js "$REMINDER_TEXT" --voice zh-TW-HsiaoChenNeural --output /home/node/.openclaw/workspace/temp_media/raw_reminder.mp3
    
    # 使用 ffmpeg 加入 ID3 標籤 (解決 Unknown Artist 問題)
    docker exec openclaw ffmpeg -y -i /home/node/.openclaw/workspace/temp_media/raw_reminder.mp3 \
        -metadata title="喝水提醒" \
        -metadata artist="OpenClaw 機器人" \
        -codec copy /home/node/.openclaw/workspace/temp_media/water_reminder.mp3
    
    # 3. 發送語音訊息到 Telegram
    # docker exec openclaw openclaw message send --channel telegram --target 8344400160 --media /home/node/.openclaw/workspace/temp_media/water_reminder.mp3
fi
