# MEMORY.md - Long-Term Memory

## 🌸 Flora 的長期記憶

### 🛠️ 系統與工具設定
- **獨立運行權限 (v2026.3.23-2)**: 已將 npm 全域路徑遷移至 `~/.npm-global`。Flora 現在具備自主更新 (`openclaw update`) 與安裝技能 (`clawhub install`) 的能力，無需 sudo。
- **SearXNG 搜尋引擎**: 運行於 Docker，本地位址為 `http://localhost:8888`。
- **Weather-Pro 專業氣象**: 已配置 WeatherAPI 與 Sunsethue 金鑰，支援空氣品質、攝影黃金時段及霞光預測。
- **算力集群 (LiteLLM)**: 在 NAS 上部署了 LiteLLM Proxy (Port 4000)，整合了 PC GPU (192.60.1.110) 與 NAS CPU (localhost) 的算力。Flora 現在會優先使用 PC 的顯卡進行高速運算，並在 PC 離線時自動回退至 NAS。已通過雙節點壓力測試。
- **教育與創意資源**: 建立了貴子坑環境教育導覽腳本（分低、中、高年級版）及完整的動物 Emoji 分類資料庫 (`memory/animal_representatives.md`)。

### 📋 專案與技術筆記
- **GitHub 備份**: 建立私有倉庫 `borshenq/open-claw`，作為工作區與記憶的雲端備份點。
- **資安清理**: 已從 GitHub 刪除含敏感資訊的舊專案 (`-my-pm-system-vue-supabase`, `school`) 並清理本地 Docker 殘骸。
- **網頁爬蟲**: 曾建立 Playwright 腳本 (`scraper.js`)，目前仍保留於本地。

### 👤 使用者偏好 (Borsheng)
- **稱呼**: 喜歡被稱為 Borsheng。
- **風格**: 偏好溫暖、幽默風趣的助理風格。
- **居住/活動區域**: 北投。

---
*最後更新日期: 2026-03-24*
