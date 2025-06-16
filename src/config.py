import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "marine_data.db")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///marine_data.db")
    SCRAPE_TIME = os.getenv("SCRAPE_TIME", "00:00")
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
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
