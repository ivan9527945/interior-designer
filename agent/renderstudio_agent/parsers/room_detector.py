"""找封閉迴圈 → 判斷房間。

演算法：
1. 把牆體線段當 edge，用 networkx 建 planar graph
2. 找 minimal cycle basis（每個封閉多邊形 = 一個房間）
3. 計算面積、重心、標記房間類型（依大小猜）

fallback（不需 networkx）：直接用 shapely unary_union + polygonize。
"""

from __future__ import annotations

import math
from typing import Any

import structlog

log = structlog.get_logger(__name__)


def _area(polygon_pts: list[tuple[float, float]]) -> float:
    """Shoelace formula。"""
    n = len(polygon_pts)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        x0, y0 = polygon_pts[i]
        x1, y1 = polygon_pts[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0


def _centroid(pts: list[tuple[float, float]]) -> tuple[float, float]:
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return cx, cy


def _guess_room_type(area_sqmm: float) -> str:
    # 面積單位：mm²（平面圖通常 1:100）
    sqm = area_sqmm / 1_000_000  # mm² → m²（假設 1:1 mm = 1 mm）
    if sqm < 4:
        return "bathroom"
    if sqm < 8:
        return "bedroom_small"
    if sqm < 16:
        return "bedroom"
    if sqm < 30:
        return "living_room"
    return "open_plan"


def _snap(v: float, tol: float = 10.0) -> float:
    return round(v / tol) * tol


def detect_rooms(walls: list[dict]) -> list[dict]:
    """從牆體線段找封閉房間多邊形。

    回傳 list of:
      { id, type, area_m2, centroid_x, centroid_y, polygon: [(x,y)...] }
    """
    try:
        return _detect_with_shapely(walls)
    except ImportError:
        log.warning("shapely_not_installed_fallback_simple")
        return _detect_simple(walls)


def _detect_with_shapely(walls: list[dict]) -> list[dict]:
    from shapely.geometry import LineString  # noqa: PLC0415
    from shapely.ops import polygonize, unary_union  # noqa: PLC0415

    lines = []
    for w in walls:
        pt0 = (_snap(w["x0"]), _snap(w["y0"]))
        pt1 = (_snap(w["x1"]), _snap(w["y1"]))
        if pt0 != pt1:
            lines.append(LineString([pt0, pt1]))

    if not lines:
        return []

    merged = unary_union(lines)
    polygons = list(polygonize(merged))

    rooms: list[dict] = []
    for i, poly in enumerate(polygons):
        area_sqmm = poly.area
        cx, cy = poly.centroid.x, poly.centroid.y
        coords = list(poly.exterior.coords)
        rooms.append({
            "id": f"room_{i}",
            "type": _guess_room_type(area_sqmm),
            "area_m2": round(area_sqmm / 1_000_000, 2),
            "centroid_x": round(cx, 1),
            "centroid_y": round(cy, 1),
            "polygon": [(round(x, 1), round(y, 1)) for x, y in coords],
        })

    log.info("rooms_detected_shapely", count=len(rooms))
    return rooms


def _detect_simple(walls: list[dict]) -> list[dict]:
    """No shapely — 直接把所有端點 bounding-box 當一個房間（粗估）。"""
    if not walls:
        return []
    xs = [w["x0"] for w in walls] + [w["x1"] for w in walls]
    ys = [w["y0"] for w in walls] + [w["y1"] for w in walls]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    area = (maxx - minx) * (maxy - miny)
    return [{
        "id": "room_0",
        "type": _guess_room_type(area),
        "area_m2": round(area / 1_000_000, 2),
        "centroid_x": round((minx + maxx) / 2, 1),
        "centroid_y": round((miny + maxy) / 2, 1),
        "polygon": [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)],
    }]
