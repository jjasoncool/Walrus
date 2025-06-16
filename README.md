# Walrus 專案說明文件

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
```bash
python app.py
```
