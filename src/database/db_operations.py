from sqlalchemy.exc import IntegrityError
from src.database.models import MarineData, init_db
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

def is_record_all_empty(record):
    """檢查記錄是否所有數值欄位為空"""
    numeric_fields = ["tide_height", "wave_height", "wave_period", "wind_speed_ms",
                      "wind_speed_level", "max_wind_speed_ms", "max_wind_speed_level",
                      "sea_temperature", "air_temperature", "air_pressure",
                      "sea_current_speed_ms", "sea_current_speed_knots"]
    return all(getattr(record, field) is None for field in numeric_fields)

def get_empty_dates(station, days=30):
    """獲取指定站點 30 天內的全空值日期"""
    session = init_db()
    try:
        cutoff = datetime.now() - timedelta(days=days)
        empty_dates = session.query(MarineData.date_time).filter(
            MarineData.station == station,
            MarineData.date_time >= cutoff.strftime("%Y-%m-%d")
        ).filter(
            *[
                getattr(MarineData, field) == None for field in [
                    "tide_height", "wave_height", "wave_period", "wind_speed_ms",
                    "wind_speed_level", "max_wind_speed_ms", "max_wind_speed_level",
                    "sea_temperature", "air_temperature", "air_pressure",
                    "sea_current_speed_ms", "sea_current_speed_knots"
                ]
            ]
        ).all()
        return [date[0] for date in empty_dates]
    finally:
        session.close()

def update_marine_data(data):
    session = init_db()
    updated_count = 0

    try:
        for row in data:
            # 檢查是否為全空值日期且新數據非全空
            if any(row.get(key) is not None for key in row.keys() if key not in ["date_time", "station"]):
                update_dict = {key: row[key] for key in row.keys() if key not in ["date_time", "station"]}
                update_dict["updated_at"] = datetime.now()  # 更新 updated_at
                session.query(MarineData).filter_by(
                    date_time=row["date_time"], station=row["station"]
                ).update(update_dict)
                updated_count += 1

        session.commit()
        logger.info(f"成功更新 {updated_count} 筆資料")
        return updated_count

    except IntegrityError:
        session.rollback()
        logger.warning("更新失敗：發現異常")
        return updated_count
    except Exception as e:
        session.rollback()
        logger.error(f"更新錯誤: {e}")
        return updated_count
    finally:
        session.close()

def insert_marine_data(data):
    session = init_db()
    inserted_count = 0

    try:
        for row in data:
            # 檢查是否已存在
            existing = session.query(MarineData).filter_by(
                date_time=row["date_time"], station=row["station"]
            ).first()
            if not existing:
                marine_record = MarineData(
                    date_time=row["date_time"],
                    station=row["station"],
                    tide_height=row["tide_height"],
                    wave_height=row["wave_height"],
                    wave_direction=row["wave_direction"],
                    wave_period=row["wave_period"],
                    wind_speed_ms=row["wind_speed_ms"],
                    wind_speed_level=row["wind_speed_level"],
                    wind_direction=row["wind_direction"],
                    max_wind_speed_ms=row["max_wind_speed_ms"],
                    max_wind_speed_level=row["max_wind_speed_level"],
                    sea_temperature=row["sea_temperature"],
                    air_temperature=row["air_temperature"],
                    air_pressure=row["air_pressure"],
                    sea_current_direction=row["sea_current_direction"],
                    sea_current_speed_ms=row["sea_current_speed_ms"],
                    sea_current_speed_knots=row["sea_current_speed_knots"]
                )
                session.add(marine_record)
                inserted_count += 1
            # 若已存在，跳過（覆蓋由 update_marine_data 處理）

        session.commit()
        logger.info(f"成功插入 {inserted_count} 筆資料")
        return inserted_count

    except IntegrityError:
        session.rollback()
        logger.warning("插入失敗：發現重複資料")
        return inserted_count
    except Exception as e:
        session.rollback()
        logger.error(f"插入錯誤: {e}")
        return inserted_count
    finally:
        session.close()

def query_marine_data(date_start=None, date_end=None, station=None, page=1, per_page=100):
    session = init_db()
    try:
        query = session.query(MarineData)
        if station and station.strip():  # 確保站點不是空字符串
            query = query.filter_by(station=station)
        elif date_start is None and date_end is None:
            query = query.filter_by(station="台中")  # 預設 station=台中

        if date_start or date_end:
            if date_start:
                # 轉換為字串格式 "YYYY-MM-DD 00:00" 以匹配資料庫中的存儲格式
                start_date_str = datetime.strptime(date_start, "%Y-%m-%d").replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M")
                query = query.filter(MarineData.date_time >= start_date_str)
                logger.info(f"查詢開始日期: {start_date_str}")

            if date_end:
                # 轉換為字串格式 "YYYY-MM-DD 23:59" 以匹配資料庫中的存儲格式
                end_date_str = datetime.strptime(date_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M")
                query = query.filter(MarineData.date_time <= end_date_str)
                logger.info(f"查詢結束日期: {end_date_str}")
        else:
            # 預設 3 天內數據
            three_days_ago = (datetime.now().date() - timedelta(days=3)).strftime("%Y-%m-%d")
            query = query.filter(MarineData.date_time >= three_days_ago)
            logger.info(f"使用預設查詢範圍: 從 {three_days_ago} 開始")

        # 按照 date_time 降序排列（最新的資料優先顯示）
        query = query.order_by(MarineData.date_time.desc())

        # 計算總數
        total = query.count()

        # 當 per_page 為 None 時，獲取全部結果（用於導出Excel）
        if per_page is None:
            results = query.all()
            logger.info(f"查詢全部數據: 共 {total} 筆資料")
        else:
            # 正常分頁
            results = query.offset((page-1)*per_page).limit(per_page).all()

        return results, total
    finally:
        session.close()
