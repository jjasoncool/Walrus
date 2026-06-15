import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "marine_data.db")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///marine_data.db")
    SCRAPE_TIME = os.getenv("SCRAPE_TIME", "00:00")
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    NSEA_SCREENSHOT_TIME = os.getenv("NSEA_SCREENSHOT_TIME", "12:10")
    NSEA_SCREENSHOT_SOURCE_URL = os.getenv("NSEA_SCREENSHOT_SOURCE_URL", "https://www.cwa.gov.tw/V8/C/M/NSea.html")
    NSEA_SCREENSHOT_STORAGE_DIR = os.getenv("NSEA_SCREENSHOT_STORAGE_DIR", "storage/nsea_forecast_screenshots")
    NSEA_SCREENSHOT_TIMEOUT_MS = int(os.getenv("NSEA_SCREENSHOT_TIMEOUT_MS", 30000))
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")
    EMAIL_TO = os.getenv("EMAIL_TO", "")
    STATIONS = {
        "台中": [
            {
                "source": "48hrs",
                "url": "https://www.cwa.gov.tw/V8/C/M/OBS_Marine/48hrsSeaObs_MOD/MC6F01.html",
            },
            {
                "source": "30days",
                "url": "https://www.cwa.gov.tw/V8/C/M/OBS_Marine/30daysSeaObs_MOD/MC6F01.html",
            },
        ]
    }
    NSEA_AREAS = {
        "NSea01": {"name": "彭佳嶼基隆海面", "slug": "pengjiayu-keelung"},
        "NSea02": {"name": "釣魚台海面", "slug": "diaoyutai"},
        "NSea03": {"name": "新竹鹿港沿海", "slug": "hsinchu-lukang"},
        "NSea04": {"name": "鹿港東石沿海", "slug": "lukang-dongshi"},
        "NSea05": {"name": "東石安平沿海", "slug": "dongshi-anping"},
        "NSea06": {"name": "安平高雄沿海", "slug": "anping-kaohsiung"},
        "NSea07": {"name": "高雄枋寮沿海", "slug": "kaohsiung-fangliao"},
        "NSea08": {"name": "枋寮恆春沿海", "slug": "fangliao-hengchun"},
        "NSea09": {"name": "鵝鑾鼻沿海", "slug": "eluanbi"},
        "NSea10": {"name": "成功臺東沿海", "slug": "chenggong-taitung"},
        "NSea10_1": {"name": "臺東大武沿海", "slug": "taitung-dawu"},
        "NSea11": {"name": "綠島蘭嶼海面", "slug": "ludao-lanyu"},
        "NSea12": {"name": "花蓮沿海", "slug": "hualien"},
        "NSea13": {"name": "宜蘭蘇澳沿海", "slug": "yilan-suao"},
        "NSea14": {"name": "澎湖海面", "slug": "penghu"},
        "NSea15": {"name": "馬祖海面", "slug": "matsu"},
        "NSea16": {"name": "金門海面", "slug": "kinmen"},
    }
