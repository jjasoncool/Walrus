import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.config import Config


def parse_snapshot_date(value: str | None = None) -> date:
    if not value:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()


def snapshot_dir(snapshot_date: date, base_dir: str | Path | None = None) -> Path:
    base = Path(base_dir or Config.NSEA_SCREENSHOT_STORAGE_DIR)
    return base / f"{snapshot_date:%Y}" / f"{snapshot_date:%m}" / f"{snapshot_date:%d}"


def area_image_filename(area_id: str, slug: str) -> str:
    return f"{area_id}_{slug}.png"


def metadata_path(snapshot_date: date, base_dir: str | Path | None = None) -> Path:
    return snapshot_dir(snapshot_date, base_dir) / "metadata.json"


def snapshot_index_path(base_dir: str | Path | None = None) -> Path:
    return Path(base_dir or Config.NSEA_SCREENSHOT_STORAGE_DIR) / "index.json"


def write_metadata(snapshot_date: date, metadata: dict[str, Any], base_dir: str | Path | None = None) -> Path:
    path = metadata_path(snapshot_date, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_snapshot_index(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = snapshot_index_path(base_dir)
    if not path.exists():
        return {"dates": []}
    return json.loads(path.read_text(encoding="utf-8"))


def update_snapshot_index(snapshot_date: date, metadata: dict[str, Any], base_dir: str | Path | None = None) -> Path:
    """更新近海漁業截圖總索引，供 Web 快速取得可瀏覽日期清單。"""
    path = snapshot_index_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    index = read_snapshot_index(base_dir)
    existing_dates = {
        item.get("date"): item
        for item in index.get("dates", [])
        if item.get("date")
    }

    snapshot_date_text = snapshot_date.isoformat()
    existing_dates[snapshot_date_text] = {
        "date": snapshot_date_text,
        "metadata_path": str(metadata_path(snapshot_date, base_dir).relative_to(path.parent)),
        "total": metadata.get("total", 0),
        "success": metadata.get("success", 0),
        "failed": metadata.get("failed", 0),
        "created_at": metadata.get("created_at", ""),
        "finished_at": metadata.get("finished_at", ""),
    }

    index = {
        "title": "近海漁業預報截圖索引",
        "updated_at": metadata.get("finished_at", ""),
        "dates": sorted(existing_dates.values(), key=lambda item: item["date"], reverse=True),
    }
    path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_metadata(snapshot_date: date, base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = metadata_path(snapshot_date, base_dir)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))