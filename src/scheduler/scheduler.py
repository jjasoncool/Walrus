from apscheduler.schedulers.background import BackgroundScheduler
from src.scraper import scrape_marine_data
from src.snapshot.nsea_screenshot import capture_all_nsea_screenshots
from src.config import Config
import logging

logger = logging.getLogger(__name__)

def run_scheduler(hour=None, minute=00):

    scheduler = BackgroundScheduler()
    # 解析 SCRAPE_TIME (格式: HH:MM)
    if hour is None:
        hour, minute = Config.SCRAPE_TIME.split(":")
    hour = int(hour)
    minute = int(minute)
    scheduler.add_job(scrape_marine_data, "cron", hour=hour, minute=minute)
    nsea_hour, nsea_minute = Config.NSEA_SCREENSHOT_TIME.split(":")
    scheduler.add_job(capture_all_nsea_screenshots, "cron", hour=int(nsea_hour), minute=int(nsea_minute))
    scheduler.start()
    logger.info(f"排程已啟動，將於每日 {hour:02d}:{minute:02d} 執行 scrape_marine_data")
    logger.info(f"近海漁業預報截圖排程已啟動，將於每日 {int(nsea_hour):02d}:{int(nsea_minute):02d} 執行")
    return scheduler
