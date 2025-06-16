import requests
from bs4 import BeautifulSoup
from src.database import insert_marine_data, update_marine_data, get_empty_dates, query_marine_data
from src.config import Config
from datetime import datetime, timedelta
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_marine_data():
    total_sent = 0
    try:
        # 1. 撈取現有 30 天內全空資料
        empty_dates_dict = {station: set(get_empty_dates(station)) for station in Config.STATIONS.keys()}
        for station, empty_dates in empty_dates_dict.items():
            logger.info(f"站點 {station} 預載 {len(empty_dates)} 筆全空值日期")

        for station, sources in Config.STATIONS.items():
            logger.info(f"開始處理站點: {station}")
            all_data = []

            # 2. 抓取網站資料
            for source in sources:
                url = source["url"]
                source_name = source["source"]
                # 模擬瀏覽器請求
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # 擷取所有 tr 元素
                rows = soup.find_all("tr")
                if not rows:
                    logger.warning(f"{station} - {source_name} 未找到任何 tr 元素")
                    continue

                # 擷取資料行
                data = []
                for row in rows:
                    cols = row.find_all(["th", "td"])
                    if len(cols) < 13:  # 確保有足夠欄位
                        logger.warning(f"{station} - {source_name} 行資料不完整，跳過: {cols}")
                        continue

                    # 解析時間
                    date_time_raw = cols[0].text.strip().replace("<br />", " ")
                    date_time = parse_date_time(date_time_raw)
                    if not date_time:
                        continue

                    # 解析欄位，使用 parse_field
                    try:
                        tide_height = parse_field(cols[1], float)
                        wave_height = parse_field(cols[2], float)
                        wave_direction = parse_field(cols[3].find("span", class_="sr-only") or cols[3], str)
                        wave_period = parse_field(cols[4], float)
                        wind_speed_ms = parse_field(cols[5].find_all("div")[0] if cols[5].find_all("div") else None, float)
                        wind_speed_level = parse_field(cols[5].find_all("div")[1] if cols[5].find_all("div") and len(cols[5].find_all("div")) > 1 else None, int)
                        wind_direction = parse_field(cols[6].find("span", class_="sr-only") or cols[6], str)
                        max_wind_speed_ms = parse_field(cols[7].find_all("div")[0] if cols[7].find_all("div") else None, float)
                        max_wind_speed_level = parse_field(cols[7].find_all("div")[1] if cols[7].find_all("div") and len(cols[7].find_all("div")) > 1 else None, int)
                        sea_temperature = parse_field(cols[8].find("span", class_="tempC") or cols[8], float)
                        air_temperature = parse_field(cols[9].find("span", class_="tempC") or cols[9], float)
                        air_pressure = parse_field(cols[10], float)
                        sea_current_direction = parse_field(cols[11].find("span", class_="sr-only") or cols[11], str)
                        sea_current_speed_ms = parse_field(cols[12].find_all("div")[0] if cols[12].find_all("div") else None, float)
                        sea_current_speed_knots = parse_field(cols[12].find_all("div")[1] if cols[12].find_all("div") and len(cols[12].find_all("div")) > 1 else None, float)
                    except IndexError as e:
                        logger.warning(f"{station} - {source_name} 欄位索引錯誤: {e}")
                        continue

                    data.append({
                        "date_time": date_time,
                        "station": station,
                        "tide_height": tide_height,
                        "wave_height": wave_height,
                        "wave_direction": wave_direction,
                        "wave_period": wave_period,
                        "wind_speed_ms": wind_speed_ms,
                        "wind_speed_level": wind_speed_level,
                        "wind_direction": wind_direction,
                        "max_wind_speed_ms": max_wind_speed_ms,
                        "max_wind_speed_level": max_wind_speed_level,
                        "sea_temperature": sea_temperature,
                        "air_temperature": air_temperature,
                        "air_pressure": air_pressure,
                        "sea_current_direction": sea_current_direction,
                        "sea_current_speed_ms": sea_current_speed_ms,
                        "sea_current_speed_knots": sea_current_speed_knots
                    })

                all_data.extend(data)
                logger.info(f"{station} - {source_name} 成功擷取 {len(data)} 筆資料")

            # 3. 判斷與更新
            to_update = [item for item in all_data if item["date_time"] in empty_dates_dict[station] and
                        any(item.get(key) is not None for key in item.keys() if key not in ["date_time", "station"])]
            update_count = update_marine_data(to_update) if to_update else 0

            # 4. 插入其他數據
            to_insert = [item for item in all_data if item not in to_update]
            insert_count = insert_marine_data(to_insert) if to_insert else 0

            # 統計送出數據數量
            sent_count = len(all_data)
            total_sent += sent_count
            logger.info(f"{station} 總共送出 {sent_count} 筆資料，更新 {update_count} 筆，插入 {insert_count} 筆")

            # 驗證與昨天的資料（僅為日誌記錄，不影響插入）
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_data = query_marine_data(date=yesterday.strftime("%Y-%m-%d"))
            for new_record in all_data:
                for old_record in yesterday_data:
                    if (new_record["date_time"] == old_record.date_time and
                        new_record["station"] == old_record.station):
                        if any(new_record.get(key) != getattr(old_record, key) for key in new_record.keys() if key != "date_time" and key != "station"):
                            logger.warning(f"{station} 數據不一致: {new_record['date_time']} - 新: {new_record}, 舊: {old_record}")

    except Exception as e:
        import traceback
        logger.error(f"爬蟲錯誤: {e}\n{traceback.format_exc()}")
        return 0

def parse_date_time(raw_text):
    try:
        month_day, time = raw_text.split(")")
        month, day = month_day.split("(")[0].split("/")
        current_year = datetime.now().year
        date_time = f"{current_year}-{month.zfill(2)}-{day.zfill(2)} {time.strip()}"
        return date_time
    except Exception as e:
        logger.warning(f"時間解析失敗: {e}")
        return None

def parse_field(value, field_type=float, empty_values=["-", ""]):
    """
    解析單一欄位值，處理空值並轉換類型。

    Args:
        value: BeautifulSoup 元素或文本值
        field_type: 目標類型 (float, int, str)
        empty_values: 視為空值的字符串列表

    Returns:
        轉換後的值或 None（若為空值或轉換失敗）
    """
    try:
        text = value.text.strip() if hasattr(value, "text") else str(value).strip()
        if text in empty_values or not text:
            return None
        return field_type(text)
    except (ValueError, AttributeError, TypeError) as e:
        logger.warning(f"解析欄位失敗: {e}, 返回 None")
        return None
