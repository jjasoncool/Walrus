# 使用 systemd 管理 Walrus Marine Data Service

這個文檔說明如何使用 systemd 將 Walrus Marine Data Service 設置為系統服務。本設置使用 `manage.sh` 指令來管理服務，確保管理方式的一致性。

## 安裝服務

1. 確保 `manage.sh` 指令具有執行權限：

```bash
chmod +x /home/egst/Projects/walrus/manage.sh
```

2. 複製服務文件到 systemd 服務目錄：

```bash
sudo cp /home/egst/Projects/walrus/walrus.service /etc/systemd/system/
```

3. 重新載入 systemd 配置：

```bash
sudo systemctl daemon-reload
```

4. 啟用服務（設置開機自動啟動）：

```bash
sudo systemctl enable walrus.service
```

## 管理服務

### 啟動服務

```bash
sudo systemctl start walrus.service
```

### 停止服務

```bash
sudo systemctl stop walrus.service
```

### 重啟服務

```bash
sudo systemctl restart walrus.service
```

### 查看服務狀態

```bash
sudo systemctl status walrus.service
```

### 查看服務日誌

您可以查看應用程式的日誌：

```bash
tail -f /home/egst/Projects/walrus/log/walrus_stdout.log
tail -f /home/egst/Projects/walrus/log/walrus_stderr.log
```

或者查看 systemd 日誌：

```bash
sudo journalctl -u walrus.service
```

## 自定義配置

如果您需要修改服務的設定（如埠號、工作進程數量等），請編輯 `manage.sh` 指令：

```bash
nano /home/egst/Projects/walrus/manage.sh
```

找到並修改 `APP_CMD` 變數，例如：

```bash
APP_CMD="$PYTHON_CMD $APP_DIR/app.py --mode prod --port 8000 --workers 4"
```

修改後，重啟服務：

```bash
sudo systemctl restart walrus.service
```

## 優點

使用 `manage.sh` 指令來管理 systemd 服務有以下優點：

1. **一致性**：無論是手動還是通過 systemd，都使用相同的啟動/停止機制
2. **簡化管理**：所有配置都集中在 `manage.sh` 指令中
3. **靈活性**：可以在指令中添加額外的啟動前/後處理邏輯
4. **透明性**：能夠清楚地看到服務是如何啟動和停止的

## 疑難排解

如果服務無法啟動，請檢查：

1. 檢查 PID 文件權限：
   ```bash
   ls -la /home/egst/Projects/walrus/walrus.pid
   ```
   如果存在，確保用戶有讀寫權限。

2. 檢查日誌目錄：
   ```bash
   mkdir -p /home/egst/Projects/walrus/log
   ```
   確保日誌目錄存在且用戶有寫入權限。

3. 手動運行 `manage.sh` 測試：
   ```bash
   /home/egst/Projects/walrus/manage.sh start
   /home/egst/Projects/walrus/manage.sh status
   ```

4. 檢查 systemd 錯誤：
   ```bash
   sudo journalctl -u walrus.service -n 50
   ```
