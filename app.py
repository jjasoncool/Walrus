#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask import Flask
from src.web.routes import web_bp
from src.scheduler.scheduler import run_scheduler
import logging
import os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler  # 明確導入 RotatingFileHandler
from whitenoise import WhiteNoise  # 導入 WhiteNoise

# 配置根日誌記錄器
def setup_logging():
    # 移除所有已存在的處理器，避免重複記錄
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 設置根日誌記錄器級別
    root_logger.setLevel(logging.INFO)

    # 創建格式化器，支持中文
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 控制台處理器，確保中文正確顯示
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # 檔案處理器，使用UTF-8編碼
    # 確保日誌目錄存在
    log_dir = os.path.join(project_root, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'marine_scraper.log'),
        maxBytes=1024*1024,  # 1MB
        backupCount=5,       # 保留 5 個備份檔案
        encoding='utf-8'     # 確保使用UTF-8編碼
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    return root_logger

# 設定應用根目錄為專案根目錄
project_root = os.path.abspath(os.path.dirname(__file__))

# 在模塊級別設置日誌
logger = setup_logging()

app = Flask(__name__,
            template_folder=os.path.join(project_root, "src", "web", "templates"),
            static_folder=os.path.join(project_root, "src", "web", "static"),
            static_url_path='/static')
app.register_blueprint(web_bp)

# 配置 WhiteNoise 處理靜態文件
# 確保靜態文件目錄存在
static_folder = os.path.join(project_root, "src", "web", "static")
if not os.path.exists(static_folder):
    os.makedirs(static_folder)
    logger.info(f"創建靜態文件目錄: {static_folder}")
else:
    logger.info(f"使用現有靜態文件目錄: {static_folder}")

# 將 WhiteNoise 集成到 WSGI 應用中
app.wsgi_app = WhiteNoise(app.wsgi_app)
# 添加靜態文件目錄，設置前綴和緩存時間
app.wsgi_app.add_files(static_folder, prefix='static/')
logger.info("WhiteNoise 已配置用於靜態文件處理")

# 註冊 max 和 min 函數到 Jinja2 環境
app.jinja_env.globals.update(max=max, min=min)

# 載入 .env
load_dotenv()

# 添加一個記錄請求的處理器
@app.before_request
def before_request_logging():
    logger.info("收到請求")

if __name__ == "__main__":
    import argparse

    # 解析命令行參數
    parser = argparse.ArgumentParser(description='Walrus Marine Data Service')
    parser.add_argument('--mode', choices=['dev', 'prod'], default='dev',
                       help='執行模式: dev (開發模式) 或 prod (生產模式)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='服務主機 (預設: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                       help='服務埠號 (預設: 5000)')
    parser.add_argument('--workers', type=int, default=None,
                       help='工作進程數量 (僅在生產模式下有效)')
    args = parser.parse_args()

    # 啟動排程器
    scheduler = run_scheduler()

    try:
        if args.mode == 'dev':
            # 開發模式: 使用 Flask 內建伺服器
            logger.info(f"開發模式: 啟動 Flask 應用於 {args.host}:{args.port}")
            app.run(host=args.host, port=args.port, debug=True)
        else:
            # 生產模式: 使用 Gunicorn
            try:
                import multiprocessing
                from gunicorn.app.base import BaseApplication

                # 計算工作進程數量，如果未指定則使用 CPU 核心數 * 2 + 1
                workers = args.workers
                if workers is None:
                    workers = (multiprocessing.cpu_count() * 2) + 1

                class GunicornApp(BaseApplication):
                    def __init__(self, app, options=None):
                        self.options = options or {}
                        self.application = app
                        super().__init__()

                    def load_config(self):
                        for key, value in self.options.items():
                            if key in self.cfg.settings and value is not None:
                                self.cfg.set(key.lower(), value)

                    def load(self):
                        return self.application

                # Gunicorn 配置
                options = {
                    'bind': f"{args.host}:{args.port}",
                    'workers': workers,
                    'worker_class': 'sync',  # 使用同步工作進程，穩定可靠
                    'timeout': 120,
                    'keepalive': 5,
                    'loglevel': 'info',
                    'errorlog': os.path.join(project_root, 'log', 'gunicorn_error.log'),
                    'accesslog': os.path.join(project_root, 'log', 'gunicorn_access.log'),
                    'proc_name': 'walrus'
                }

                logger.info(f"生產模式: 啟動 Gunicorn 於 {args.host}:{args.port} 使用 {workers} 個工作進程")
                GunicornApp(app, options).run()
            except ImportError as e:
                logger.error(f"無法啟動生產模式: {e}. 請確認已安裝 gunicorn: conda install gunicorn")
                sys.exit(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("應用與排程已關閉")
