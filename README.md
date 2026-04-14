# 🛠️ FastAPI 報修系統 (Repair System)

這是一個基於 **FastAPI** 框架開發的報修管理系統，具備完整的使用者註冊、登入、報修單提交、進度追蹤與維修日誌功能。

---

## 📂 檔案清單與說明

### 核心程式目錄 (`app/`)
這是網站運行的核心邏輯與介面：

*   **`main.py`**：**網站主程式**。定義了所有 URL 路由（如 `/login`, `/report`, `/dashboard`），處理請求並進行頁面渲染。
*   **`models.py`**：**資料庫模型**。定義了資料庫中的資料結構（User, RepairRequest, RepairLog）。
*   **`database.py`**：**資料庫設定**。負責與 SQLite 資料庫建立連線。
*   **`auth.py`**：**安全驗證**。處理密碼加密、登入檢查及產生安全憑證 (JWT Token)。
*   **`email_utils.py`**：**郵件工具**。負責在報修狀態變更時發送通知信。
*   **`static/`**：**靜態資源**。包含 CSS、JavaScript 與使用者上傳的維修照片 (`uploads/`)。
*   **`templates/`**：**網頁模板**。使用 Jinja2 渲染的 HTML 介面，包含：
    *   `base.html`: 共用外框。
    *   `index.html`: 系統首頁。
    *   `login.html` / `register.html`: 帳號登入與註冊。
    *   `report.html`: 提交報修單介面。
    *   `dashboard.html`: 維修單管理儀表板。
    *   `detail.html`: 詳細報修資訊與維修日誌紀錄。
    *   **文件模板**: `docs.html` (使用說明), `architecture.html` (架構), `database_docs.html` (結構), `maintenance.html` (維護)。

### 根目錄工具
*   **`sql_app.db`**：主要的 SQLite 資料庫檔案。
*   **`seed_data.py`**：資料初始化腳本。執行後可清空資料並重建 10 筆測試資料。
*   **`requirements.txt`**：Python 依賴套件清單。
*   **`tests/`**：自動化 API 測試腳本（如 `test_auth.py`）。
*   **`venv/`**：Python 虛擬環境目錄。
*   **`README.md`**：本說明文件。

---

## 🚀 快速開始

### 1. 安裝環境與依賴
確保您已安裝 Python 3.10+，並在專案根目錄執行：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate # Windows
pip install -r requirements.txt
```

### 2. 初始化資料庫 (選用)
如果您想清空資料庫並匯入測試資料（預設帳號：`admin`/`admin123`, `student1`/`password123`）：
```bash
python seed_data.py
```

### 3. 啟動伺服器
```bash
python -m uvicorn app.main:app --reload
```
啟動後，請訪問：[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📚 系統說明文件
本系統內建了詳細的技術文件，啟動後可透過以下路徑存取：
*   **使用說明**：`/docs`
*   **系統架構**：`/architecture`
*   **資料庫結構**：`/database`
*   **維護指南**：`/maintenance`
