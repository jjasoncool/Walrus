#!/bin/bash

# 簡單的指令用於管理 Walrus Marine Data Service
# 使用方式: ./manage.sh [start|stop|restart|status]

# 自動檢測程式位置並設定應用目錄 - 增強版
get_script_path() {
    # 首先嘗試使用 readlink (適用於大多數 Linux 系統)
    local path
    if command -v readlink >/dev/null 2>&1; then
        path=$(readlink -f "$0" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$path" ]; then
            echo "$path"
            return 0
        fi
    fi

    # 如果 readlink 失敗，嘗試使用 realpath
    if command -v realpath >/dev/null 2>&1; then
        path=$(realpath "$0" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$path" ]; then
            echo "$path"
            return 0
        fi
    fi

    # 如果上述方法都失敗，嘗試手動解析
    local dir=""
    local script="$0"

    # 處理相對路徑
    if [[ "$script" != /* ]]; then
        dir="$PWD"
        script="$dir/$script"
    fi

    # 移除所有 "./" 部分
    script="${script//\/.\//\/}"

    # 處理 "../" 部分
    while [[ "$script" == */../* ]]; do
        script="${script/\/[^\/]*\/\.\.\//\/}"
    done

    echo "$script"
}

SCRIPT_PATH=$(get_script_path)
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

# 立即顯示程式路徑（不論測試模式是否開啟）
echo "程式位置: $SCRIPT_PATH"
echo "程式目錄: $SCRIPT_DIR"
echo "當前目錄: $PWD"

# 預設值
APP_DIR="$SCRIPT_DIR"
PYTHON_CMD="$APP_DIR/env/bin/python"

# 如果存在 .env 檔案，則載入環境變數
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "載入 .env 設定..."
    # 使用 . 而不是 source（更兼容各種 shell）
    . "$SCRIPT_DIR/.env"
fi

# 測試輸出
if [ "${DEBUG:-0}" = "1" ]; then
    echo "測試資訊:"
    echo "  SCRIPT_PATH: $SCRIPT_PATH"
    echo "  SCRIPT_DIR: $SCRIPT_DIR"
    echo "  APP_DIR: $APP_DIR"
    echo "  PYTHON_CMD: $PYTHON_CMD"
    echo "  執行位置: $PWD"
fi

# 僅顯示路徑資訊然後退出（用於測試）
if [ "$1" = "debug-path" ]; then
    echo "測試完成，依要求退出"
    exit 0
fi

# 確保 APP_DIR 有值
if [ -z "$APP_DIR" ]; then
    APP_DIR="$SCRIPT_DIR"
fi

# 確保 PYTHON_CMD 有值
if [ -z "$PYTHON_CMD" ]; then
    PYTHON_CMD="$APP_DIR/env/bin/python"
fi

# 設定變數
PID_FILE="$APP_DIR/walrus.pid"
LOG_DIR="$APP_DIR/log"
APP_CMD="$PYTHON_CMD $APP_DIR/app.py --mode prod"

# 確保日誌目錄存在
mkdir -p $LOG_DIR

# 啟動功能
start() {
    echo "正在啟動 Walrus Marine Data Service..."

    # 檢查服務是否已經在運行
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "服務已在運行，PID: $PID"
            return 1
        else
            # PID 文件存在但進程不存在，刪除舊的 PID 文件
            rm -f $PID_FILE
        fi
    fi

    # 後台啟動應用
    nohup $APP_CMD > $LOG_DIR/walrus_stdout.log 2> $LOG_DIR/walrus_stderr.log & echo $! > $PID_FILE

    # 等待一會兒檢查進程是否啟動
    sleep 2
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "服務已成功啟動，PID: $PID"
            echo "日誌保存在: $LOG_DIR/walrus_stdout.log 和 $LOG_DIR/walrus_stderr.log"
            return 0
        fi
    fi

    echo "啟動失敗，請檢查日誌"
    return 1
}

# 停止功能
stop() {
    echo "正在停止 Walrus Marine Data Service..."

    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            # 發送終止訊號
            kill $PID

            # 等待進程結束
            echo "等待服務停止..."
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null; then
                    break
                fi
                sleep 1
            done

            # 如果進程仍在運行，強制終止
            if ps -p $PID > /dev/null; then
                echo "服務未能正常停止，正在強制終止..."
                kill -9 $PID
            fi

            rm -f $PID_FILE
            echo "服務已停止"
        else
            echo "服務未在運行，但 PID 文件存在"
            rm -f $PID_FILE
        fi
    else
        echo "服務未在運行"
    fi
}

# 重啟功能
restart() {
    stop
    sleep 2
    start
}

# 檢查狀態功能
status() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "服務正在運行，PID: $PID"
            return 0
        else
            echo "服務未在運行，但 PID 文件存在"
            return 1
        fi
    else
        echo "服務未在運行"
        return 2
    fi
}

# 命令處理
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    debug-path)
        # 已在前面處理，添加這裡只是為了讓幫助信息更完整
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|debug-path}"
        echo "  start      - 啟動服務"
        echo "  stop       - 停止服務"
        echo "  restart    - 重啟服務"
        echo "  status     - 查看服務狀態"
        echo "  debug-path - 僅顯示路徑資訊用於測試"
        exit 1
        ;;
esac

exit 0
