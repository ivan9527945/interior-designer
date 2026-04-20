"""從 DXF entities 抽出牆體線段。

牆體識別策略（優先順序）：
1. 圖層名稱含 WALL / A-WALL / 牆 / 墙（不分大小寫）
2. 實體類型：LINE / LWPOLYLINE / POLYLINE（寬度 > 0 視為帶厚牆）
3. 同層的 LINE 群組
"""

from __future__ import annotations

import math
from typing import Any

import structlog

log = structlog.get_logger(__name__)

_WALL_LAYER_KEYWORDS = {"wall", "a-wall", "牆", "墙", "walls"}


def _is_wall_layer(layer_name: str) -> bool:
    name = layer_name.lower()
    return any(kw in name for kw in _WALL_LAYER_KEYWORDS)


def _seg_length(x0: float, y0: float, x1: float, y1: float) -> float:
    return math.hypot(x1 - x0, y1 - y0)


def _line_to_seg(e: Any) -> dict | None:
    try:
        start = e.dxf.start
        end = e.dxf.end
        return {
            "type": "line",
            "x0": float(start.x), "y0": float(start.y),
            "x1": float(end.x), "y1": float(end.y),
            "layer": e.dxf.layer,
            "length": _seg_length(start.x, start.y, end.x, end.y),
        }
    except AttributeError:
        return None


def _lwpoly_to_segs(e: Any) -> list[dict]:
    segs: list[dict] = []
    try:
        pts = list(e.get_points())  # (x, y, start_width, end_width, bulge)
        layer = e.dxf.layer
        for i in range(len(pts) - 1):
            x0, y0 = pts[i][0], pts[i][1]
            x1, y1 = pts[i + 1][0], pts[i + 1][1]
            segs.append({
                "type": "polyline_seg",
                "x0": float(x0), "y0": float(y0),
                "x1": float(x1), "y1": float(y1),
                "layer": layer,
                "length": _seg_length(x0, y0, x1, y1),
            })
        if e.is_closed and len(pts) > 1:
            x0, y0 = pts[-1][0], pts[-1][1]
            x1, y1 = pts[0][0], pts[0][1]
            segs.append({
                "type": "polyline_seg",
                "x0": float(x0), "y0": float(y0),
                "x1": float(x1), "y1": float(y1),
                "layer": layer,
                "length": _seg_length(x0, y0, x1, y1),
            })
    except Exception as exc:
        log.warning("lwpoly_parse_error", error=str(exc))
    return segs


def extract_walls(entities: list) -> list[dict]:
    """回傳牆體線段清單。entities 是 ezdxf modelspace 的 entity list。"""
    segs: list[dict] = []
    for e in entities:
        layer = getattr(e.dxf, "layer", "")
        dxftype = e.dxftype()

        if dxftype == "LINE":
            seg = _line_to_seg(e)
            if seg and (
                _is_wall_layer(layer) or seg["length"] > 10  # 至少 10mm 的線才算
            ):
                segs.append(seg)

        elif dxftype == "LWPOLYLINE":
            for seg in _lwpoly_to_segs(e):
                if _is_wall_layer(layer) or seg["length"] > 10:
                    segs.append(seg)

    # 過濾掉明顯太短的雜線（< 50mm）
    segs = [s for s in segs if s["length"] >= 50]
    log.info("walls_extracted", count=len(segs))
    return segs
