# TOOLS.md - Flora 的工具清單

## 🔍 搜尋引擎
- **SearXNG**: ✅ `http://localhost:8888`（Docker 運行，uv 執行腳本，含 Google/DuckDuckGo/Bing/Brave/Wikipedia）
- **Web Search**: ⚠️ 缺少 Brave API Key

## 🌐 瀏覽器自動化
- **agent-browser**: ✅ 可用，適合網頁爬蟲 / 內容抓取

## 🗄️ Fast.io — 檔案協作平台（含檔案管理/分享/團隊協作/工作流/AI問答）

## 🐍 開發工具
- **uv**: `/home/borsheng/.local/bin/uv` — Python 套件管理器
- **jq**: `/home/borsheng/.local/bin/jq` — JSON 處理
- **GitHub CLI**: 可用（GitHub 操作/PR/Issue）
- **gh-issues skill**: 可自動修復 GitHub Issue

## ☁️ Google Workspace（gog skill）
- **Gmail**: 讀取、搜尋、發送郵件
- **Calendar**: 建立/查詢活動
- **Drive**: 檔案管理
- **Docs**: 建立/編輯文件
- **Sheets**: 試算表操作
- **Contacts**: 通訊錄管理

## 🎨 畫圖與視覺化
- **diagram-maker**: 繪製 SVG/HTML 示意圖、流程圖、拓撲圖
- **meme-maker**: 梗圖產生器
- **canvas**: 在節點上顯示 HTML 內容

## 🎋 傳統文化
- **lot-draw**: 六十甲子籤（抽籤解籤）

## 🤖 模型與 AI
- **gemini**: Google Gemini CLI 操作（Prompt/Summary/Generation）
- **spike**: 可行性驗證 Prototype 沙盒

## 🌤️ 氣象與環境
- **weather-pro**: 完整氣象套件（溫度/雨量/空品/風速/濕度）
  - APIS: WeatherAPI + SunsetHue
  - 功能：黃金時段、霞光預測、日出日落
- **weather**: 基礎氣象查詢

## 📝 筆記與文件
- **notion**: Notion API（頁面/資料庫/區塊管理）
- **nano-pdf**: PDF 操作
- **speed-read / summarize**: 文字摘要

## 🔌 本地工具
- **sherpa-onnx-tts**: 本地中文語音合成
- **sherpa-onnx-whisper**: 本地語音辨識
- **video-frames**: 影片幀提取
- **session-logs**: Session 記錄工具

## 🧠 開發輔助
- **skill-creator**: 建立/編輯/審核技能檔
- **node-inspect-debugger**: Node.js 除錯（Inspector/CDP）
- **python-debugpy**: Python 除錯（pdb/debugpy）

## 🔐 系統
- **healthcheck**: SSH/防火牆/更新/備份/磁碟加密安全審計
- **node-connect**: 節點配對/QR code/連線診斷

## 📁 工作目錄
- **Workspace**: `/home/borsheng/.openclaw/workspace`
- **Memory Logs**: `./memory/YYYY-MM-DD.md`
- **GitHub 備份**: `./flora-memory-repo` → `borshenq/open-claw`
