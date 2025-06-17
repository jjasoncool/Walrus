from flask import Flask
from src.web.routes import web_bp
from src.scheduler.scheduler import run_scheduler
import logging
import os
import sys
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler  # 明確導入 RotatingFileHandler

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
    file_handler = RotatingFileHandler(
        'marine_scraper.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5,       # 保留 5 個備份檔案
        encoding='utf-8'     # 確保使用UTF-8編碼
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    return root_logger

# 在模塊級別設置日誌
logger = setup_logging()

# 設定應用根目錄
# 設定應用根目錄為專案根目錄
project_root = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(project_root, "src", "web", "templates"))
app.register_blueprint(web_bp)

# 註冊 max 和 min 函數到 Jinja2 環境
app.jinja_env.globals.update(max=max, min=min)

# 載入 .env
load_dotenv()

# 添加一個記錄請求的處理器
@app.before_request
def before_request_logging():
    logger.info("收到請求")

if __name__ == "__main__":
    logger.info("直接執行模式：啟動 Flask 應用與排程")

    scheduler = run_scheduler()
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("應用與排程已關閉")
