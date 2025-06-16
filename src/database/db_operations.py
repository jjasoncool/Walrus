from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from src.database.models import MarineData, init_db

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

def insert_marine_data(data, station="台中"):
    session = init_db()
    inserted_count = 0

    try:
        for row in data:
            # 檢查是否已存在
            exists = session.query(MarineData).filter_by(
                date_time=row["date_time"], station=station
            ).first()
            if exists:
                continue

            # 插入新記錄
            marine_record = MarineData(
                date_time=row["date_time"],
                station=station,
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

        session.commit()
        print(f"成功插入 {inserted_count} 筆新資料")
        return inserted_count

    except IntegrityError:
        session.rollback()
        print("插入失敗：發現重複資料")
        return inserted_count
    except Exception as e:
        session.rollback()
        print(f"插入錯誤: {e}")
        return inserted_count
    finally:
        session.close()

def query_marine_data(date=None, station=None, page=1, per_page=100):
    session = init_db()
    try:
        query = session.query(MarineData)
        if date:
            query = query.filter_by(date_time=date)
        if station:
            query = query.filter_by(station=station)

        # 分頁
        results = query.offset((page-1)*per_page).limit(per_page).all()
        return results
    finally:
        session.close()
