from apscheduler.schedulers.blocking import BlockingScheduler
from src.scraper import scrape_marine_data
from src.config import Config

def run_scheduler():
    scheduler = BlockingScheduler()
    # 解析 SCRAPE_TIME (格式: HH:MM)
    hour, minute = map(int, Config.SCRAPE_TIME.split(":"))
    scheduler.add_job(scrape_marine_data, "cron", hour=hour, minute=minute)
    print(f"排程器啟動，每天 {Config.SCRAPE_TIME} 執行爬蟲...")
    scheduler.start()
