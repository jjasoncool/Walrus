import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db
from src.scraper import scrape_marine_data
from src.scheduler.scheduler import run_scheduler

import datetime

if __name__ == "__main__":
    init_db()  # 初始化資料庫
    # Get current time
    now = datetime.datetime.now()
    # Calculate next minute
    next_minute = now + datetime.timedelta(minutes=1)
    # Extract hour and minute
    hour = next_minute.hour
    minute = next_minute.minute
    print(f"Test Scheduled for: {hour}:{minute:02d}")
    scheduler = run_scheduler(hour=hour, minute=minute)  # 啟動排程
    scrape_marine_data()
    # 保持運行以測試排程（可按 Ctrl+C 結束）
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
