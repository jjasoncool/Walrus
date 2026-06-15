# Walrus 海洋資料採集與管理系統

Walrus 是一個專門用於海洋數據的採集、存儲和查詢的系統。它可以自動從多個來源抓取海洋觀測數據、存儲到資料庫中，並提供 Web 界面進行查詢和匯出。

## 功能特點

- **多站點資料採集**：支援從多個海洋觀測站點採集數據
- **自動化排程**：使用 APScheduler 定時抓取最新數據
- **資料庫管理**：使用 SQLAlchemy 和 Alembic 進行資料庫操作和遷移
- **Web 查詢介面**：使用 Flask 提供簡潔的 Web 查詢界面
- **資料匯出**：支援將查詢結果匯出為 Excel 格式
- **生產環境部署**：集成 Gunicorn 支援高效能部署

## 專案結構

```
walrus/
├── alembic/              # 資料庫遷移配置
├── log/                  # 日誌文件
├── src/
│   ├── database/         # 資料庫模型和操作
│   ├── scraper/          # 數據抓取相關程式
│   ├── scheduler/        # 排程任務
│   └── web/              # Web 介面和路由
├── app.py               # 主應用程式
├── manage.sh            # 服務管理指令
└── walrus.service       # systemd 服務配置
```

## 環境設定指令 (Environment Setup)

### Conda 環境管理

#### 建立新的 Conda 環境
```bash
# 使用 Python 3.13 在專案目錄下建立新環境
conda create -p ./env python=3.13
```

#### 啟動環境
```bash
# 切換至專案目錄後啟動環境
conda activate ./env
```

#### 套件管理
```bash
# 安裝套件
conda install [package_name]

# 從 conda-forge 頻道安裝套件
conda install -c conda-forge [package_name]
```

#### 環境備份與還原
```bash
# 匯出環境設定
conda env export -p ./env > environment.yml

# 從 environment.yml 還原環境
conda env create -p ./env -f environment.yml
```

#### 移除環境
```bash
# 移除專案環境
conda env remove -p ./env -y
```

## 程式操作指令 (Application Commands)

### Alembic 資料庫遷移指令
```bash
# 檢查資料庫遷移狀態
alembic check

# 建立新的遷移檔案
alembic revision --autogenerate -m "migration message"

# 執行資料庫遷移
alembic upgrade head

# 回復上一次遷移
alembic downgrade -1
```

## 專案啟動步驟

1. 建立並啟動 Conda 環境
```bash
conda create -p ./env python=3.13
conda activate ./env
```

2. 安裝依賴套件
```bash
conda env create -p ./env -f environment.yml
```

3. 執行資料庫遷移
```bash
alembic upgrade head
```

4. 啟動應用程式
   - 開發模式
   ```bash
   python app.py
   ```
   - 生產模式
   ```bash
   python app.py --mode prod
   ```

## 近海漁業預報截圖

本系統支援每日自動擷取中央氣象署「近海漁業」線上頁面主要內容區截圖。截圖任務使用 Playwright 操作線上頁面，逐一切換 NSea 海域並截取 `main.main-content`。

### Playwright / Chromium 安裝

Windows 與 Linux 使用相同 Python API；差異主要在瀏覽器 runtime 與 Linux 系統相依套件。請在專案 conda/venv 環境中安裝：

```bash
pip install playwright
playwright install chromium
```

Linux server 若缺少 Chromium 系統相依套件，Playwright 會在錯誤訊息中提示需要安裝的套件。可依部署環境使用系統套件管理工具安裝；若環境允許，也可參考 Playwright 官方建議：

```bash
playwright install-deps chromium
```

> 注意：`playwright install-deps` 可能需要系統管理權限；若 production 主機不能使用 sudo，請請系統管理者依 Playwright 提示安裝相依套件。

### 手動測試單一海域操作

Phase 1 診斷腳本可確認 CWA 線上頁面切換與截圖是否正常：

```bash
python -m src.snapshot.test_nsea_page_control --area-id NSea03
```

若要觀察瀏覽器實際操作：

```bash
python -m src.snapshot.test_nsea_page_control --area-id NSea03 --headed
```

成功後會輸出測試圖：

```text
storage/debug/nsea_NSea03_test.png
```

### 手動產生每日全部海域截圖

```bash
python -m src.snapshot.nsea_screenshot
```

指定日期：

```bash
python -m src.snapshot.nsea_screenshot --date 2026-06-15
```

輸出位置預設為：

```text
storage/nsea_forecast_screenshots/YYYY/MM/DD/
```

每次任務會產生各海域 PNG 與 `metadata.json`。若有海域失敗，且 `.env` 中 `EMAIL_ENABLED=true`，系統會寄出 email summary。

### 相關 `.env` 設定

```env
NSEA_SCREENSHOT_TIME=12:10
NSEA_SCREENSHOT_SOURCE_URL=https://www.cwa.gov.tw/V8/C/M/NSea.html
NSEA_SCREENSHOT_STORAGE_DIR=storage/nsea_forecast_screenshots
NSEA_SCREENSHOT_TIMEOUT_MS=30000

EMAIL_ENABLED=false
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true
EMAIL_FROM=walrus@example.com
EMAIL_TO=admin@example.com
```

排程啟動後，近海漁業預報截圖任務會依 `NSEA_SCREENSHOT_TIME` 每日執行一次，預設為 `12:10`。

## 服務管理

### 使用管理指令
```bash
# 啟動服務
./manage.sh start

# 停止服務
./manage.sh stop

# 重啟服務
./manage.sh restart

# 查看狀態
./manage.sh status
```

### 管理指令配置
管理指令 `manage.sh` 使用自動路徑檢測，無需手動配置路徑：

- **智能路徑檢測**：指令會自動檢測其所在目錄，無論從哪裡執行都能正確運作
- **多重備援機制**：支援多種路徑解析方法，確保在不同環境中的穩定性
- **調試模式**：可通過設定 `DEBUG=1` 環境變數來顯示路徑解析詳情

```bash
# 標準執行
./manage.sh start

# 使用調試模式
DEBUG=1 ./manage.sh start
```

指令使用以下路徑進行操作：
- 應用程式目錄：自動檢測指令所在目錄
- Python 執行檔：自動檢測為 `<應用程式目錄>/env/bin/python`
- PID 文件：存放在 `<應用程式目錄>/walrus.pid`
- 日誌文件：存放在 `<應用程式目錄>/log/` 目錄下

### 使用 systemd
請參考 `systemd_setup.md` 獲取更詳細的 systemd 服務設置和管理說明。

## 日誌位置
- 應用程式日誌: `log/walrus_stdout.log` 和 `log/walrus_stderr.log`
- Gunicorn 日誌: `log/gunicorn_error.log` 和 `log/gunicorn_access.log`
- 爬蟲日誌: `log/marine_scraper.log`

## 依賴管理

由於本專案使用 Conda 環境，直接使用 `pip freeze` 產生的 requirements.txt 會包含 Conda 特定路徑，不適合直接在其他環境中使用。建議使用以下方法生成標準的 requirements.txt：

### 生成標準 requirements.txt

1. 首先創建 `requirements.in` 文件，列出主要依賴（不包含版本號）：

```bash
# 創建或編輯 requirements.in
cat > requirements.in << EOF
# Walrus Marine Data Service 核心依賴
Flask
APScheduler
SQLAlchemy
alembic
requests
beautifulsoup4
python-dotenv
playwright
gunicorn
whitenoise
fake-useragent
openpyxl
pandas

# 開發依賴
pip-tools
EOF
```

2. 使用 pip-tools 生成標準 requirements.txt：

```bash
# 安裝 pip-tools
pip install pip-tools

# 生成不含雜湊值的 requirements.txt
pip-compile requirements.in --output-file requirements.txt

# 或生成包含雜湊值的 requirements.txt（更安全）
pip-compile requirements.in --generate-hashes --output-file requirements.txt
```
