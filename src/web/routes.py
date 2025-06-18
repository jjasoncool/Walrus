from flask import Blueprint, request, render_template
from src.database import query_marine_data
from src.config import Config
import logging

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
