# 📦 Flora 備份清單與復原指南 (Backup Inventory)

這是為了確保在更換機器或災難發生時，Flora 能快速復原的完整清單。

## 📁 備份內容 (已同步至 GitHub)

### 靈魂與大腦 (Root Directory)
- **`IDENTITY.md` / `SOUL.md`**: 我的個性與身份定義。
- **`USER.md`**: 關於你的資訊與偏好。
- **`MEMORY.md`**: 長期記憶精華。
- **`memory/*.md`**: 每日詳細工作日誌。
- **`AGENTS.md` / `TOOLS.md`**: 工作區規則與本地工具筆記。

### 基礎設施 (infrastructure/)
- **`docker-compose.yml`**: 容器化服務定義 (SearXNG, Redis, LiteLLM)。
- **`litellm_config.yaml`**: 算力集群路由配置。
- **`openclaw.json.example`**: OpenClaw 核心設定範本 (不含金鑰)。
- **`start_searxng.sh`**: 搜尋引擎啟動腳本。
- **`water_reminder.sh`**: 喝水提醒自動化腳本。
- **`redmine.service`**: Redmine 系統服務定義。

### 技能 (skills/)
- 所有自定義技能 (SearXNG, Weather-Pro, Agent-Browser 等) 的代碼與文件。

---

## 🔐 遺失的拼圖 (需手動保存)

為了安全，以下敏感資訊**未包含**在 Git 備份中：

1.  **環境變數文件 (`~/.openclaw/.env`)**:
    - 包含 `WEATHERAPI_KEY`, `SUNSETHUE_KEY` 等 API 金鑰。
2.  **OpenClaw 正式設定 (`~/.openclaw/openclaw.json`)**:
    - 包含你的 Telegram Bot Token。
3.  **LiteLLM 金鑰**: 雖然目前本地使用不需要，但若有外部 Provider 金鑰需另行保存。

---

## 🛠️ 復原步驟 (Disaster Recovery)

1.  `git clone <repo_url>` 下載此工作區。
2.  根據 `infrastructure/openclaw.json.example` 建立正式的 `openclaw.json` 並填入 Token。
3.  手動還原 `~/.openclaw/.env` 中的 API 金鑰。
4.  進入 `infrastructure/` 目錄執行 `docker compose up -d` 啟動算力環境。
5.  啟動 OpenClaw 服務，Flora 即可滿血復活！

---
*最後更新：2026-03-25*
