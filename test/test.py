import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db
from src.scraper import scrape_marine_data
from src.scheduler.scheduler import run_scheduler
from src.config import Config

if __name__ == "__main__":
    init_db()  # 初始化資料庫
    scheduler = run_scheduler()  # 啟動排程
    scrape_marine_data()
    # 保持運行以測試排程（可按 Ctrl+C 結束）
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
