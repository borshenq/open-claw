# 2026年3月 日記歸檔 (Archived)
# 原檔案：2026-03-23 ~ 2026-03-29
# 歸檔日期：2026-04-29

## Durable Memories - 2026-03-23

*   **`web_search` tool issue**: The `web_search` tool is currently non-functional due to a `missing_brave_api_key` error. It requires a Brave Search API key to be configured via `openclaw configure --section web` or by setting `BRAVE_API_KEY` in the Gateway environment. This prevents direct web searches.
*   **Playwright script (`scraper.js`)**: A basic script for scraping e-commerce sites (蝦皮, Momo, PChome) for iPhone 15 information was created. It still requires manual input of CSS selectors by the user and execution in their environment.
*   **`agent-browser` usage**: Successfully used `agent-browser` to navigate Google News and local SearxNG instance for various queries ("中東戰爭", "陽明山天氣", "大屯國小", "今天台灣十大新聞"). This provides a fallback for web searching when `web_search` is unavailable.
*   **Office 2024 on ARM**: Discussed that Office 2024 compatibility on ARM notebooks depends on whether a native ARM version is provided by Microsoft or the "局端" (bureau). Advised the user to consult their IT department for specific information.
*   **"遺失子彈殼" news**: The user inquired about recent news regarding "遺失子彈殼". Due to the `web_search` issue, I could not perform an immediate search, but offered to use `agent-browser` as an alternative.
*   **Skills Status**: `openclaw doctor` reported 9 eligible skills and 44 with "missing requirements", confirming that `web_search` is among the non-functional tools due to missing prerequisites (Brave API key).
# SearXNG Status
- **Instance URL:** http://localhost:8888 (running in Docker)
- **Status:** OK
- **Dependencies:** Installed `uv` at `/home/borsheng/.local/bin/uv` to run the skill script.
- **Verification:** Successfully performed a test search.

## Durable Memories - 2026-03-24

### 🌸 Identity & Persona
- **Name:** Flora.
- **Vibe:** Witty, warm, and comforting (幽默風趣、溫暖).
- **Emoji:** 🌸 (小花).
- **User:** Juang Borsheng (prefers "Borsheng").
- **GitHub:** Confirmed user account is `borshenq` (not `borsheng`).

### 🛠️ System Infrastructure
- **Independent Flora (Permission Fix):** Successfully moved npm global prefix to `~/.npm-global`. 
  - Added `export PATH=~/.npm-global/bin:$PATH` to `.bashrc`.
  - Flora can now run `openclaw update` and `clawhub install` without sudo.
  - Verified `openclaw update` runs successfully.
- **Weather-Pro Fully Functional:** Successfully configured both `WEATHERAPI_KEY` and `SUNSETHUE_KEY` in `~/.openclaw/.env`. Flora can now provide detailed forecasts, air quality, golden/blue hours, and sunrise/sunset glow quality.
- **JQ Installed:** Manually installed `jq` to `/home/borsheng/.local/bin/jq` as it's required by the weather-pro script.
- **Security:** Deep audit identified open Telegram group policy and unsandboxed filesystem. User is aware.

### 🧹 Project Cleanup & De-leaking
- **Legacy Removal:** Deleted `/home/borsheng/school-project` and `/home/borsheng/school_library`. Stopped and removed Docker containers `django_web`, `school_library-web-1`, `postgres_db`, `school_library-db-1`. Deleted related images.
- **Leaked Keys:** Found `.env.bak` in `-my-pm-system-vue-supabase` and `db.sqlite3` in `school` (GitHub). User decided to delete these repositories from GitHub to wipe history.

### 🧠 Workspace Organization
- Created `MEMORY.md` for long-term storage of system configuration and user preferences.
- Updated `TOOLS.md` with local binary paths and service URLs.
- Cleaned up `__pycache__` directories.
# 🌸 Flora's Daily Log - 2026-03-25

## 🛡️ Security Audit Summary (03:00 AM)
- **Status:** 0 critical, 1 warning, 1 info.
- **Findings:**
  - **WARN:** `gateway.trusted_proxies_missing` — Reverse proxy headers are not trusted. 
    - *Note:* This is only an issue if using a reverse proxy (like Nginx/Cloudflare) to expose the Control UI. If local-only, it's safe to ignore.
  - **INFO:** Attack surface check confirmed elevated tools and browser control are active (as intended for a personal assistant).
- **Update Status:** OpenClaw is up to date (pnpm · 2026.3.23-2).

## 📰 Daily News Summary (06:00 AM)
- **Top 3 News Items:**
  1. **Asian Nasdaq:** President Lai Ching-te aims to transform Taiwan's capital market into the "Nasdaq of Asia" via innovation platforms and financial openness.
  2. **Public Safety:** Ministry of the Interior holds international seminar to enhance counter-terrorism and social safety nets following past random attacks.
  3. **Tech Release:** Apple's iPad Air M4 version officially goes on sale in Taiwan starting at NT$19,900.
- **Source:** SearXNG News Search.


# Durable Memories - 2026-03-25

## Compute Cluster Setup (LiteLLM)

**Objective:** To create a load-balanced LLM inference system utilizing both the NAS CPU and the user's PC GPU.

**Key Actions:**
*   Created `litellm_config.yaml` to define model routing, prioritizing the PC's GPU (IP 192.60.1.60) with a higher priority (1) over the NAS CPU (priority 10). Model names: `flora-brain-hq` (PC), `flora-brain-hq` (NAS).
*   Updated `/home/borsheng/docker-compose.yml` to include the `litellm` service, exposing it on port 4000 and mounting the configuration file.
*   Updated `~/.openclaw/openclaw.json` to route primary model requests to `litellm/flora-brain-hq` via `http://127.0.0.1:4000/v1`.
*   Successfully started the LiteLLM Docker container (`litellm`).
*   Verified LiteLLM endpoint by querying `/v1/models`.
*   Restarted the `openclaw-gateway.service` to apply all configurations.

## 🌙 Evening Session Highlights (07:00 PM - 09:00 PM)

### 🚀 LiteLLM Cluster Final Success
*   **Correction:** Identified the correct PC IP as `192.60.1.110`.
*   **Key Discovery:** Confirmed that for Ollama nodes, `litellm_config.yaml` requires BOTH `provider: "ollama"` and the `ollama/` prefix in the model string (e.g., `ollama/qwen3.5:latest`).
*   **Verification:** Successfully performed `curl` tests for both the PC GPU (`qwen3.5:latest`) and the NAS CPU (`llama3.2:1b`) through the LiteLLM proxy.
*   **Primary Brain:** Updated `openclaw.json` to set `litellm/flora-brain-hq` as the primary model for Flora, ensuring high-speed responses.

### 📚 Education & Creative Assets
*   **Animal Emoji Database:** Created and fully populated `memory/animal_representatives.md` with a massive, categorized collection of animal icons for daily "representative" rotation.
*   **Guizikeng Environmental Education:** Researched the Guizikeng Hiking Trail and Campsite. Developed three distinct guided lesson plans tailored for Low, Middle, and High-grade elementary school students.

### 📋 Workspace Inventory & Descriptions
Archived a complete map of the current workspace directory and the function of each file:
- **Core Identity**: `IDENTITY.md`, `SOUL.md`, `USER.md`.
- **Infrastructure**: `docker-compose.yml`, `litellm_config.yaml`, `openclaw.json.example`.
- **Memory & Tracking**: `MEMORY.md`, `memory/*.md`, `price_watch.md`.
- **Custom Scripts**: `water_reminder.sh`, `start_searxng.sh`, `redmine.service`.
- **Skills**: `searxng/`, `weather-pro/`, `agent-browser/`.

**Outcome:** A functional LiteLLM proxy is running, enabling intelligent routing of LLM requests to the most suitable compute resource. All major session goals achieved and a comprehensive workspace map documented.
## 2026-03-26 - Durable Memories

**Key Decisions & Workflows:**
-   **Local Compute Integration:** Faced challenges integrating `sessions_spawn` with LiteLLM for automatic model dispatch. Decided to revert to direct `curl` commands via `exec` for invoking local models (PC GPU `qwen3.5:latest` and NAS CPU `llama3.2:1b` via Ollama) through LiteLLM, as this approach is confirmed to be functional. The `sessions_spawn` integration remains an advanced research topic.
-   **System Health Check:** Performed a comprehensive check.
    -   Core OpenClaw, Docker services (LiteLLM, SearXNG, Redis), and scheduled tasks are healthy.
    -   PC Ollama: Service connection appears functional, but model resolution (`qwen3.5:latest`) via LiteLLM failed.
    -   NAS Ollama: Service connection failed (telnet and LiteLLM), indicating potential issues with its running status or network configuration for external access.
-   **Network Scanning:** Initiated network scans for specific IP ranges but refined the request to focus on simple ping checks.
-   **Printer Management:**
    -   Detected multiple network printers (Konica Minolta, Brother, Fujifilm) from an image.
    -   Created `printer_location_log.md` to list printers, their IP addresses, and identified specific locations for two printers:
        -   `192.60.1.98` (KONICA MINOLTA bizhub C227 PCL): 總務處
        -   `192.60.1.99` (KONICA MINOLTA bizhub C227 PCL): 大辦公室
    -   Committed and pushed the updated `printer_location_log.md` to GitHub.

**Current State:**
-   Local compute relies on direct `curl` calls to LiteLLM for model dispatch.
-   NAS Ollama service requires further investigation.
-   Printer inventory and location data is documented and backed up.
## 2026-03-27 Security Audit (Flora 🌸)
- **Time:** 03:00 AM
- **Results:** 0 critical, 1 warn, 1 info
- **Warning:** Reverse proxy headers not trusted (gateway.trustedProxies is empty).
- **Update:** Available (npm 2026.3.24).
- **Action:** Ran `openclaw security audit --deep` and `openclaw update status`.

## 2026-03-27 研習輔助與自動化進度 (Flora 🌸)
- **Time:** 11:20 AM
- **任務：** 協助 Borsheng 將磨課師課程「網路言論的規範與責任」之 38 張投影片轉文字。
- **狀態：** 已啟動 `agent-browser` 自動化流程。
- **進度：**
    - 識別登入路徑：磨課師 (MOOCs) -> 教育雲 OpenID -> 台北市單一身分認證 (SSO)。
    - 使用者已提供登入憑證 (帳號: `borsheng`)。
    - 目前停留在台北市 SSO 登入頁面，已擷取含有驗證碼的截圖 `moocs_captcha.png`。
    - **Pending:** 等待使用者回傳驗證碼以完成登入並開始投影片擷取與 OCR 處理。
- **算力/網路狀態：**
    - 全域網路偵察 (65/65) 100% 完工。
    - 資產清冊已同步至 `network_assets_inventory.md` 與 GitHub。
    - 成功識別多台智慧顯示器與教學大螢幕。
# 2026-03-28 (Saturday)

## 🌸 Flora 的日常日誌

### 🗓️ 執行摘要
- **時間**: 17:00 (Asia/Taipei)
- **事件**: 執行自動備份腳本 `/home/borsheng/auto_backup.sh`。
- **結果**: 備份成功，並已同步推送到 GitHub 倉庫 `borshenq/open-claw`。
- **變更詳情**: 備份了 Docker 配置、LiteLLM 設定檔及近期記憶文件（2026-03-23 到 2026-03-27）。

### 🛠️ 系統功能升級與算力最佳化 (21:30)
- **本地端語音 (Local TTS)**: 
    - 成功部署 `sherpa-onnx-tts` 於 `~/.openclaw/tools/sherpa-onnx-tts`。
    - 下載並設定高品質中文語音模型 `vits-piper-zh_CN-huayan-medium`。
    - 測試成功：Flora 現在能完全在本地生成清晰的中文語音檔案（如 `/tmp/birthday_local.wav`）。
- **分布式算力對決與調整**: 
    - 進行了 PC GPU (192.60.1.110) 與 NAS CPU (localhost) 的跑分測試。
    - **結果**: PC GPU 速度快約 4.5 倍且模型更具邏輯深度 (9B vs 1B)。
    - **決策**: 將 PC GPU 優先級調回 **1**，NAS 調回 **10**。路由模式恢復為 `latency-based-routing`。
- **免 sudo 環境建置**: 
    - 成功於家目錄安裝 **Homebrew** (`~/.linuxbrew`)。
    - 解決了無法在系統目錄建立 `/home/linuxbrew` 的權限問題。
    - 已將 `brew` 路徑永久加入 `~/.profile`。
- **Android 移動端探索**: 
    - 嘗試為紅米 Note 14 Pro 5G 進行配對。
    - 設定 `gateway.bind: "tailnet"` 以支援 Tailscale 全域遠端連線。
    - 使用者目前決定暫緩 App 設定，維持 Telegram 為主控端。
# Memory Log - 2026-03-29

## [cron:f15768b7-b283-4acd-8e5d-45d94c1780bd] Security Audit Result
Executed `openclaw security audit --deep` and `openclaw update status`.

### Audit Findings:
- **0 Critical**, **2 Warnings**, **1 Info**.
- **WARN: gateway.auth_no_rate_limit** - No auth rate limiting configured. Brute-force attacks are possible.
- **WARN: gateway.probe_failed** - Gateway probe failed (ECONNREFUSED 127.0.0.1:18789).
- **INFO: summary.attack_surface** - Attack surface summary (tools.elevated enabled, browser control enabled).

### Update Status:
- OpenClaw is up to date (pnpm, stable channel, 2026.3.24).

### Decisions/Actions:
- Noted the lack of rate limiting.
- Need to investigate why the probe failed (ECONNREFUSED).
# Memory Log - 2026-03-29

## [cron:f15768b7-b283-4acd-8e5d-45d94c1780bd] Security Audit Result
Executed `openclaw security audit --deep` and `openclaw update status`.

### Audit Findings:
- **0 Critical**, **2 Warnings**, **1 Info**.
- **WARN: gateway.auth_no_rate_limit** - No auth rate limiting configured. Brute-force attacks are possible.
- **WARN: gateway.probe_failed** - Gateway probe failed (ECONNREFUSED 127.0.0.1:18789).
- **INFO: summary.attack_surface** - Attack surface summary (tools.elevated enabled, browser control enabled).

### Update Status:
- OpenClaw is up to date (pnpm, stable channel, 2026.3.24).

### Decisions/Actions:
- Noted the lack of rate limiting.
- Need to investigate why the probe failed (ECONNREFUSED).
