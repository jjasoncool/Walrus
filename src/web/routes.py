from flask import Blueprint, request, render_template, send_file
from src.database import query_marine_data
from src.config import Config
import logging
import pandas as pd
import os
import tempfile
from datetime import datetime

web_bp = Blueprint("web", __name__)

@web_bp.route("/", methods=["GET", "POST"])
def query_data():
    results = []
    stations = list(Config.STATIONS.keys())  # 動態生成站點選項

    # 從 URL 參數中獲取頁碼和查詢參數
    page = int(request.args.get("page", 1))

    # 從 URL 參數獲取查詢條件（支持 GET 方法）
    date_start = request.args.get("date_start")
    date_end = request.args.get("date_end")
    station = request.args.get("station")

    # 如果有查詢條件，進行查詢
    if date_start or date_end or station:
        results, total = query_marine_data(date_start, date_end, station, page)
    else:
        # 沒有查詢條件時顯示默認結果
        results, total = query_marine_data(page=page)

    logging.info(f"查詢結果: 第{page}頁, {len(results)} 筆資料, 總計: {total} 筆資料")

    return render_template("query.html", results=results, stations=stations, page=page, total=total)

@web_bp.route("/export_excel", methods=["GET"])
def export_excel():
    # 從 URL 參數獲取查詢條件
    date_start = request.args.get("date_start")
    date_end = request.args.get("date_end")
    station = request.args.get("station")

    # 查詢數據，不分頁，獲取全部結果
    results, _ = query_marine_data(date_start, date_end, station, page=1, per_page=None)

    if not results:
        logging.warning("匯出Excel: 沒有數據可供匯出")
        return "沒有數據可供匯出", 404

    # 將查詢結果轉換為 DataFrame
    df = pd.DataFrame([r.__dict__ for r in results])

    # 移除 SQLAlchemy 的特殊屬性
    if '_sa_instance_state' in df.columns:
        df = df.drop('_sa_instance_state', axis=1)

    # 定義欄位對映：資料庫欄位名稱 -> Excel欄位標題（與HTML表格一致）
    column_mapping = {
        'date_time': '日期',
        'station': '站點',
        'tide_height': '潮高(m)',
        'wave_height': '浪高(m)',
        'wave_direction': '浪向',
        'wave_period': '波週期(秒)',
        'wind_speed_ms': '風速(m/s)',
        'wind_speed_level': '風速(級)',
        'wind_direction': '風向',
        'max_wind_speed_ms': '最大風速(m/s)',
        'max_wind_speed_level': '最大風速(級)',
        'sea_temperature': '海溫(℃)',
        'air_temperature': '氣溫(℃)',
        'air_pressure': '氣壓(百帕)',
        'sea_current_direction': '海流流向',
        'sea_current_speed_ms': '流速(m/s)',
        'sea_current_speed_knots': '流速(節)',
        'recorded_at': '記錄時間'
    }

    # 按照HTML表格的順序重新排列欄位
    ordered_columns = [
        'date_time', 'station', 'tide_height', 'wave_height',
        'wave_direction', 'wave_period', 'wind_speed_ms',
        'wind_speed_level', 'wind_direction', 'max_wind_speed_ms',
        'max_wind_speed_level', 'sea_temperature', 'air_temperature',
        'air_pressure', 'sea_current_direction', 'sea_current_speed_ms',
        'sea_current_speed_knots', 'recorded_at'
    ]

    # 選擇需要的欄位並按照指定順序排列
    df = df[ordered_columns]

    # 重命名欄位為中文名稱
    df = df.rename(columns=column_mapping)

    # 創建臨時文件
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name

    # 生成文件名稱，加入查詢條件和時間戳
    filename_parts = ["marine_data"]
    if station:
        filename_parts.append(f"station_{station}")
    if date_start:
        filename_parts.append(f"from_{date_start}")
    if date_end:
        filename_parts.append(f"to_{date_end}")

    # 添加時間戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_parts.append(timestamp)

    filename = "_".join(filename_parts) + ".xlsx"

    # 保存到Excel
    df.to_excel(tmp_path, index=False, sheet_name="海洋資料")

    logging.info(f"匯出Excel: {len(results)} 筆資料已匯出到 {filename}")

    return send_file(
        tmp_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
