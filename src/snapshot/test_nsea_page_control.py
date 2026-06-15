"""Phase 1：測試線上 CWA 近海漁業頁面切換與截圖。

此腳本只驗證 B-1 操作策略：
1. 使用 Playwright 開啟 CWA 線上 NSea 頁面
2. 直接呼叫頁面既有 JS：GetMOD('C', area_id, 'NSea')
3. 等待 main.main-content 內的 SeaName、Forecast_Time、accordion table 更新
4. 截取 main.main-content 到 storage/debug

執行前請先在 conda 環境安裝 Playwright 與 Chromium：
    pip install playwright
    playwright install chromium

範例：
    python -m src.snapshot.test_nsea_page_control --area-id NSea03 --area-name 新竹鹿港沿海
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


LOGGER = logging.getLogger(__name__)

SOURCE_URL = "https://www.cwa.gov.tw/V8/C/M/NSea.html"
DEFAULT_OUTPUT_DIR = Path("storage") / "debug"

NSEA_AREAS = {
    "NSea01": "彭佳嶼基隆海面",
    "NSea02": "釣魚台海面",
    "NSea03": "新竹鹿港沿海",
    "NSea04": "鹿港東石沿海",
    "NSea05": "東石安平沿海",
    "NSea06": "安平高雄沿海",
    "NSea07": "高雄枋寮沿海",
    "NSea08": "枋寮恆春沿海",
    "NSea09": "鵝鑾鼻沿海",
    "NSea10": "成功臺東沿海",
    "NSea10_1": "臺東大武沿海",
    "NSea11": "綠島蘭嶼海面",
    "NSea12": "花蓮沿海",
    "NSea13": "宜蘭蘇澳沿海",
    "NSea14": "澎湖海面",
    "NSea15": "馬祖海面",
    "NSea16": "金門海面",
}


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def wait_for_area_data(page, area_name: str, timeout_ms: int) -> None:
    """等待 CWA 頁面完成指定海域資料載入。"""
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


def capture_area(area_id: str, area_name: str, output_dir: Path, timeout_ms: int, headless: bool) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"nsea_{safe_filename(area_id)}_test.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(viewport={"width": 1440, "height": 1200}, device_scale_factor=1)
        try:
            LOGGER.info("開啟 CWA NSea 頁面：%s", SOURCE_URL)
            page.goto(SOURCE_URL, wait_until="networkidle", timeout=timeout_ms)
            page.wait_for_function("typeof GetMOD === 'function'", timeout=timeout_ms)

            LOGGER.info("切換海域：%s %s", area_id, area_name)
            page.evaluate("([areaId]) => GetMOD('C', areaId, 'NSea')", [area_id])
            wait_for_area_data(page, area_name, timeout_ms)

            main_content = page.locator("main.main-content")
            main_content.wait_for(state="visible", timeout=timeout_ms)
            main_content.screenshot(path=str(output_path))

            LOGGER.info("截圖完成：%s", output_path)
            return output_path
        except PlaywrightTimeoutError as exc:
            raise RuntimeError(f"等待 CWA 頁面或 {area_id} 資料逾時：{exc}") from exc
        finally:
            browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="測試 CWA NSea 頁面海域切換與 main.main-content 截圖")
    parser.add_argument("--area-id", default="NSea03", choices=sorted(NSEA_AREAS.keys()), help="要測試的 NSea 海域代碼")
    parser.add_argument("--area-name", default=None, help="海域中文名稱；未提供時使用內建對照表")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="測試截圖輸出資料夾")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="等待逾時毫秒數")
    parser.add_argument("--headed", action="store_true", help="顯示瀏覽器視窗，方便觀察線上頁面操作")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()
    area_name = args.area_name or NSEA_AREAS[args.area_id]
    output_path = capture_area(
        area_id=args.area_id,
        area_name=area_name,
        output_dir=Path(args.output_dir),
        timeout_ms=args.timeout_ms,
        headless=not args.headed,
    )
    print(output_path)


if __name__ == "__main__":
    main()