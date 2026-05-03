# MEMORY.md - Long-Term Memory

## 🌸 Flora 的長期記憶

### 🎯 使用者背景（Borsheng）
- **稱呼**: 喜歡被稱為 Borsheng。
- **活動區域**: 台北北投為主，曾問過台南天氣。
- **職業/角色**: 教育相關工作者（與明德國中、貴子坑環境教育有關）。
- **風格偏好**: 溫暖、幽默風趣的助理風格。
- **系統使用行為**: 常用 Telegram 互動，偏好簡潔直接的對話。曾嘗試測試 weather、Fast.io、GitHub等功能。

### 🛠️ 系統與工具設定
- **獨立運行權限 (v2026.3.23-2)**: npm 全域路徑在 `~/.npm-global`。Flora 可自主更新 (`openclaw update`) 與安裝技能 (`clawhub install`)，無需 sudo。
- **SearXNG 搜尋引擎**: Docker 運行，本地位址 `http://localhost:8888`。
- **Weather-Pro 專業氣象**: 已配置 WeatherAPI 與 Sunsethue 金鑰，支援空氣品質、攝影黃金時段及霞光預測。
- **算力集群 (LiteLLM)**: NAS 部署 LiteLLM Proxy (Port 4000)，整合 PC GPU (192.60.1.110) 與 NAS CPU (localhost)。優先使用 PC 顯卡，離線時回退至 NAS。
- **模型偏好**: 主要使用 google/gemini-flash-latest。曾討論過升級 AI Plus 方案及 Google Gemini Advanced 的差異。
- **GitHub 備份**: 私有倉庫 `borshenq/open-claw` 作為工作區備份。最後自動備份時間：2026-04-15。
- **Ontology 知識圖譜**: 位於 `memory/ontology/graph.jsonl`，有少量資料。

### 📋 專案與資源
- **教育資源**: 貴子坑環境教育導覽腳本（低、中、高年級版）、動物 Emoji 分類資料庫 (`memory/animal_representatives.md`)。
- **工作區腳本**: 曾建立 Playwright 網頁爬蟲腳本 (`scraper.js`)。
- **資安清理**: 已從 GitHub 刪除含敏感資訊的舊專案。

### 📅 近期行程
- **2026/04/27（一）**: Borsheng 請假。
- **2026/04/28（二）**: 明德國中黃老師入校 09:00-12:00（小型座談、觀課、回饋）。

### 📝 待辦事項（參考）
- 朋友的圖書館系統
- 老師的網教學網站
- 社團報名系統
- [ ] 採購枕頭 🛏️（2026-05-03 新增）

### 🌐 網路拓撲記錄（2026-04-30）
- 從 OpenClaw VM 掃描整個 `192.60.1.0/24` 網段，紀錄於 `memory/network_topology.md`
- **主機**: Synology DS925+ (`.127`) — AMD Ryzen V1500B / 8GB / 2TB SSD，跑 VMM 虛擬機
- **虛擬機**: Ubuntu VM (openclaw, `.107`) — OpenClaw Gateway、Redmine、FastAPI、SearXNG
- **路由器**: Ubiquiti UniFi Gateway (`.254`)
- **交換器**: D-Link × 10 台、Cisco × 1、Siemon × 3
- **虛擬化**: VMware ESXi 主機 (`.7`)
- **NAS × 3**: DS925+、FS RackStation (`.5`)、w2 RackStation (`.6`)
- **印表機**: Brother MFC-L2715DW × 2、FUJIFILM ApeosPrint C325 dw、HP
- **UPS**: 台達 Delta × 5 台
- **攝影機**: Axis × 2
- **SNMP**: community `public` 從此 VM 無法連通
- **環境**: 學校/環教中心機房（DNS: tp.edu.tw），備註「南港廠裡」

### 🧹 記憶清理記錄
- **2026-04-29**: 整理並刪除了 2026/4/15~4/28 期間大量無內容的 Session Log（因連線超時/空互動產生的記錄，佔 150KB+，無實際對話價值）。濃縮長期記憶至此檔。

---
*最後更新日期: 2026-04-30*
