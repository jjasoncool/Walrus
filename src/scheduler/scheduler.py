from apscheduler.schedulers.background import BackgroundScheduler
from src.scraper import scrape_marine_data
from src.config import Config
import logging

logger = logging.getLogger(__name__)

def run_scheduler():
    scheduler = BackgroundScheduler()
    # 解析 SCRAPE_TIME (格式: HH:MM)
    hour, minute = Config.SCRAPE_TIME.split(":")
    scheduler.add_job(scrape_marine_data, "cron", hour=hour, minute=minute)
    scheduler.start()
    logger.info(f"排程已啟動，每日 {Config.SCRAPE_TIME} 執行 scrape_marine_data")
    return scheduler
