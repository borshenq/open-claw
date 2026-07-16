# MEMORY.md - Long-Term Memory

## 🌸 Flora 的長期記憶

### 🎯 使用者背景（Borsheng）
- **稱呼**: Borsheng（Juang Borsheng）
- **活動區域**: 台灣（Asia/Taipei, UTC+8），北投
- **GitHub**: borshenq
- **風格偏好**: 溫暖、幽默風趣的助理風格（wit + warmth）。

### 🛠️ 系統與工具設定（2026-03 建置，2026-07 重建）
- **獨立運行權限**: npm 全域路徑 ~/.npm-global，已加入 PATH，無須 sudo。
- **SearXNG 搜尋引擎**: Docker 運行於 `http://localhost:8888`，用 uv 執行 script。
- **Weather-Pro 氣象**: 已配置 WEATHERAPI_KEY 與 SUNSETHUE_KEY（存於 ~/.openclaw/.env），支援空品、黃金時段、霞光預測。
- **算力集群（LiteLLM）**: 在 NAS 上部署了 LiteLLM Proxy（Port 4000），整合 PC GPU（192.60.1.110）與 NAS CPU 算力。PC GPU 優先級 1（速度快約 4.5x），NAS 優先級 10。路由模式 latency-based-routing。
- **本地 TTS**: sherpa-onnx-tts + 中文語音模型，可本地生成語音。
- **Homebrew**: 已安裝於 ~/.linuxbrew。
- **開發工具**: jq 已安裝於 ~/.local/bin/jq。

### 🏢 DTPS 網路環境
- **網段**: 192.60.1.0/24（約 50 台在線主機，含印表機、伺服器、NAS、攝影機等）
- **防火牆**: FortiGate（備份於 backups/firewall/）
- **掃描報告**: network_scan_2026-06-17.md（全埠掃描結果）
- **印表機位置**: 已記錄於 flora-memory-repo/printer_location_log.md

### 📋 專案與技術筆記
- **GitHub 備份**: 私有倉庫 `borshenq/open-claw`（flora-memory-repo），包含完整記憶、技能、基礎設施配置。
- **資安清理**: 已從 GitHub 刪除含敏感資訊的舊專案。
- **網頁爬蟲**: Playwright 腳本 scraper.js 保留於本地。
- **貴子坑環境教育**: 已開發低、中、高年級導覽腳本。
- **動物 Emoji 資料庫**: 已建立完整分類資料（memory/animal_representatives.md）。

### 📈 專案進展
- **🏫 傷病報表系統（2026-07-14）**: Flask + SQLite 網頁系統，跑在 VM 192.60.1.153:5000，含帳號登入/記錄輸入/統計報表(Chart.js)/CSV匯出。學生資料 82 人（一~五年甲班）。已設 crontab @reboot 開機啟動。
- **📋 DTPS 設備清單工具（2026-07-12）**: `device_inventory.py` 整合 SNMP 掃描，37→46 台設備全數在線。Flask `/portscan` 路由支援 Web 掃描 22 常見埠。
- **🌐 網路拓撲圖（2026-07-12）**: 手繪 SVG 校園網路拓撲，含 FortiGate → Core Switch → Edge Switches → 終端。Flask `/networkmap` 路由上線。
- **📦 SNMP 探勘（2026-07-12）**: 發現 Aruba CX8100-48F（核心交換器）、Aruba 2930F×4、Cisco Catalyst 9K、FortiGate 500E。Community 分析：public/private/SnmpPublic@TPC/internal。

### 🌐 網路變動記錄
- **OpenClaw VM IP**: 原 .107（已退役），現用 DHCP 取得 .153
- **2026-07**: 持續監控 192.60.1.0/24，chron job `network-alert-check` 透過 Telegram 自動通知埠口/主機變動
- **離線主機**: .107（退役）、.115（可疑 Windows，曾開 80/135/445）、.118（間歇離線）

### 📅 記憶時間軸（已知）
- 2026-03-23 ~ 2026-04-27: 主要活躍期間
- 2026-06-17: 網路掃描（50 主機）、防火牆備份
- 2026-07-11: 颱風天盤點——核心主機全部健在
- 2026-07-12: DTPS SNMP 大採集（46 設備、網路拓撲圖）
- 2026-07-14: 學生傷病報表系統上線
- 2026-07-16: 重啟重建、Git 大整理、TOOLS.md 更新、Fast.io 平臺探勘、防火牆備份上傳

### 🧹 備註
- 這是 2026-07-16 從 flora-memory-repo 重建的記憶庫。
- Soul/Identity/User 檔案已於同日重新確認。
- 日記備份完整（2026-03 ~ 2026-07-16，約 41 筆）。
- Git 倉庫已清理：1 commit（879de29）、1 branch（master）、working tree clean。
  - 已刪除遠端 main 分支
  - 清除 16 個生成檔案
  - 更新 .gitignore
  - 59 commit 壓縮為 1 commit
- TOOLS.md 已全面更新（約 40+ 工具），移除 LiteLLM Proxy / Homebrew，Fast.io 精簡為一行
- Fast.io 平台探勘完成：API 金鑰驗證、19+ MCP 工具可用、10,000 點額度 0 使用
- Fast.io 防火牆備份資料夾已建立，已上傳完整 FortiGate config（14,060 行）
- 已從 TOOLS.md 移除 Homebrew、LiteLLM Proxy

---
*最後更新日期: 2026-07-16*
