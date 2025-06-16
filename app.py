from flask import Flask
from src.web.routes import web_bp
from src.scheduler.scheduler import run_scheduler
import logging
import os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler  # 明確導入 RotatingFileHandler

# 設定應用根目錄
# 設定應用根目錄為專案根目錄
project_root = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(project_root, "src", "web", "templates"))
app.register_blueprint(web_bp)

# 註冊 max 和 min 函數到 Jinja2 環境
app.jinja_env.globals.update(max=max, min=min)

# 載入 .env
load_dotenv()

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 檔案處理器
    file_handler = RotatingFileHandler(
        'marine_scraper.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5        # 保留 5 個備份檔案
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("啟動 Flask 應用與排程")
    scheduler = run_scheduler()
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("應用與排程已關閉")
