import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import scrape_marine_data
from src.database import init_db
from src.config import Config

if __name__ == "__main__":
    init_db()  # 初始化資料庫
    scrape_marine_data()
