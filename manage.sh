#!/bin/bash

# 簡單的指令用於管理 Walrus Marine Data Service
# 使用方式: ./manage.sh [start|stop|restart|status]

# 設定變數
APP_DIR="/home/egst/Projects/walrus"
PID_FILE="$APP_DIR/walrus.pid"
LOG_DIR="$APP_DIR/log"
PYTHON_CMD="$APP_DIR/env/bin/python"
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
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
