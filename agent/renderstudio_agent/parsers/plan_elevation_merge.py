"""合併平面圖與立面圖解析結果。

平面圖提供：牆體、門窗、房間輪廓
立面圖提供：牆高度、窗台高度、窗高度
"""

from __future__ import annotations


def _infer_ceiling_height(elevation_data: dict) -> float:
    """從立面圖估算天花板高度（mm）。沒有立面圖時用台灣標準 2700mm。"""
    walls = elevation_data.get("walls", [])
    if not walls:
        return 2700.0
    heights = [w.get("length", 0) for w in walls if w.get("y0", 0) < 100]
    if heights:
        return float(max(heights))
    return 2700.0


def merge(plan_data: dict, elevation_data: dict | None = None) -> dict:
    """回傳合併後的 scene dict，供 SketchUp controller 使用。"""
    ev = elevation_data or {}
    ceiling_height = _infer_ceiling_height(ev)

    return {
        "walls": plan_data.get("walls", []),
        "openings": plan_data.get("openings", []),
        "rooms": plan_data.get("rooms", []),
        "ceiling_height_mm": ceiling_height,
        "elevation": {
            "walls": ev.get("walls", []),
            "openings": ev.get("openings", []),
        },
        "bbox": plan_data.get("bbox", {}),
        "unit": plan_data.get("unit", "mm"),
    }
