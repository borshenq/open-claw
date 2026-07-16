#!/bin/bash
# === 系統依賴安裝 ===
set -e

echo "📦 更新套件清單..."
sudo apt-get update

echo "📦 安裝 agent-browser 需要的系統套件..."
sudo apt-get install -y \
  libxcb-shm0 libx11-xcb1 libx11-6 libxcb1 libxext6 libxrandr2 \
  libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 \
  libgtk-3-0t64 libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0t64 \
  libcairo-gobject2 libcairo2 libgdk-pixbuf-2.0-0 libxrender1 \
  libasound2t64 libfreetype6 libfontconfig1 libdbus-1-3 libnss3 \
  libnspr4 libatk-bridge2.0-0t64 libdrm2 libxkbcommon0 libatspi2.0-0t64 \
  libcups2t64 libxshmfence1 libgbm1 \
  fonts-noto-color-emoji fonts-noto-cjk fonts-freefont-ttf

echo "✅ 系統依賴安裝完成！"

echo ""
echo "📦 安裝其他實用工具..."
sudo apt-get install -y \
  ffmpeg \
  gh \
  jq

echo "✅ 工具安裝完成！"

echo ""
echo "📦 驗證 agent-browser 不再需要 --no-sandbox..."
ls ~/.agent-browser/browsers/chrome-* 2>/dev/null && echo "✅ Chrome 就緒"

echo ""
echo "🎉 全部完成！請重啟你的終端機或執行: source ~/.bashrc"
