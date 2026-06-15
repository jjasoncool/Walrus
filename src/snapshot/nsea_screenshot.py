"""正式近海漁業預報截圖任務。

此模組直接操作 CWA 線上頁面：
https://www.cwa.gov.tw/V8/C/M/NSea.html

對每個 NSea 海域呼叫頁面既有 JS `GetMOD('C', area_id, 'NSea')`，
等待資料載入後截取 `main.main-content`，並以檔案庫形式儲存 PNG 與 metadata.json。
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from src.config import Config
from src.notification.email_notifier import send_nsea_failure_summary
from src.snapshot.file_store import area_image_filename, parse_snapshot_date, snapshot_dir, update_snapshot_index, write_metadata

logger = logging.getLogger(__name__)
TAIPEI_TZ = timezone(timedelta(hours=8))


def wait_for_area_data(page, area_name: str, timeout_ms: int) -> None:
    page.wait_for_function(
        """
        ({ areaName }) => {
            const seaName = document.querySelector('#SeaName')?.innerText?.trim() || '';
            const forecastTime = document.querySelector('#Forecast_Time')?.innerText?.trim() || '';
            const rangeTime = document.querySelector('#Range_Time')?.innerText?.trim() || '';
            const table = document.querySelector('#accordion table');
            return seaName.includes(areaName) && forecastTime && rangeTime && !!table;
        }
        """,
        arg={"areaName": area_name},
        timeout=timeout_ms,
    )


def read_page_text(page, selector: str) -> str:
    try:
        return page.locator(selector).inner_text(timeout=2000).strip()
    except Exception:
        return ""


def capture_all_nsea_screenshots(
    snapshot_date_value: str | None = None,
    output_base_dir: str | Path | None = None,
    timeout_ms: int | None = None,
    headed: bool = False,
    notify_on_failure: bool = True,
) -> dict[str, Any]:
    snapshot_date = parse_snapshot_date(snapshot_date_value)
    timeout_ms = timeout_ms or Config.NSEA_SCREENSHOT_TIMEOUT_MS
    output_dir = snapshot_dir(snapshot_date, output_base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(TAIPEI_TZ)
    area_results: list[dict[str, Any]] = []

    logger.info("開始近海漁業預報截圖：%s", snapshot_date.isoformat())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        page = browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=1)
        try:
            page.goto(Config.NSEA_SCREENSHOT_SOURCE_URL, wait_until="networkidle", timeout=timeout_ms)
            page.wait_for_function("typeof GetMOD === 'function'", timeout=timeout_ms)

            for area_id, area_info in Config.NSEA_AREAS.items():
                area_name = area_info["name"]
                slug = area_info["slug"]
                file_name = area_image_filename(area_id, slug)
                output_path = output_dir / file_name

                result = {
                    "area_id": area_id,
                    "area_name": area_name,
                    "file_name": file_name,
                    "forecast_time": "",
                    "range_time": "",
                    "status": "failed",
                    "error": None,
                }

                try:
                    logger.info("切換並截圖：%s %s", area_id, area_name)
                    page.evaluate("([areaId]) => GetMOD('C', areaId, 'NSea')", [area_id])
                    wait_for_area_data(page, area_name, timeout_ms)

                    result["forecast_time"] = read_page_text(page, "#Forecast_Time")
                    result["range_time"] = read_page_text(page, "#Range_Time")

                    main_content = page.locator("main.main-content")
                    main_content.wait_for(state="visible", timeout=timeout_ms)
                    main_content.screenshot(path=str(output_path))

                    if not output_path.exists() or output_path.stat().st_size == 0:
                        raise RuntimeError("截圖檔案未產生或大小為 0")

                    result["status"] = "success"
                    logger.info("完成：%s", output_path)
                except PlaywrightTimeoutError as exc:
                    result["error"] = f"等待資料或截圖逾時：{exc}"
                    logger.error("%s %s 失敗：%s", area_id, area_name, result["error"])
                except Exception as exc:
                    result["error"] = str(exc)
                    logger.error("%s %s 失敗：%s", area_id, area_name, result["error"])

                area_results.append(result)
        finally:
            browser.close()

    finished_at = datetime.now(TAIPEI_TZ)
    failures = [item for item in area_results if item["status"] != "success"]
    metadata = {
        "snapshot_date": snapshot_date.isoformat(),
        "title": "近海漁業預報截圖",
        "created_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "source_url": Config.NSEA_SCREENSHOT_SOURCE_URL,
        "capture_target": "main.main-content",
        "total": len(area_results),
        "success": len(area_results) - len(failures),
        "failed": len(failures),
        "areas": area_results,
    }
    metadata_file = write_metadata(snapshot_date, metadata, output_base_dir)
    logger.info("metadata 已寫入：%s", metadata_file)
    index_file = update_snapshot_index(snapshot_date, metadata, output_base_dir)
    logger.info("截圖索引已更新：%s", index_file)

    if failures and notify_on_failure:
        send_nsea_failure_summary(snapshot_date.isoformat(), failures)

    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="產生每日近海漁業預報截圖檔案庫")
    parser.add_argument("--date", default=None, help="截圖日期 YYYY-MM-DD；預設今天")
    parser.add_argument("--output-dir", default=None, help="覆寫輸出根目錄；預設讀 NSEA_SCREENSHOT_STORAGE_DIR")
    parser.add_argument("--timeout-ms", type=int, default=None, help="覆寫等待逾時毫秒數")
    parser.add_argument("--headed", action="store_true", help="顯示瀏覽器視窗，方便除錯")
    parser.add_argument("--no-email", action="store_true", help="即使失敗也不寄 email")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()
    metadata = capture_all_nsea_screenshots(
        snapshot_date_value=args.date,
        output_base_dir=args.output_dir,
        timeout_ms=args.timeout_ms,
        headed=args.headed,
        notify_on_failure=not args.no_email,
    )
    print(f"完成：{metadata['success']}/{metadata['total']} 成功，輸出日期 {metadata['snapshot_date']}")


if __name__ == "__main__":
    main()