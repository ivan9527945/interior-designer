"""門窗抽出。

識別策略：
- 圖層名稱含 DOOR / WINDOW / A-DOOR / A-WIND / 門 / 窗
- INSERT entity（block 插入）在這些圖層
- 或 ARC entity（常見的門弧）
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)

_DOOR_KEYWORDS = {"door", "a-door", "doors", "a-dor", "門", "门"}
_WIN_KEYWORDS = {"window", "a-wind", "win", "窗"}


def _kind_from_layer(layer: str) -> str | None:
    name = layer.lower()
    if any(k in name for k in _DOOR_KEYWORDS):
        return "door"
    if any(k in name for k in _WIN_KEYWORDS):
        return "window"
    return None


def _arc_to_opening(e: Any) -> dict | None:
    try:
        center = e.dxf.center
        return {
            "type": "arc",
            "kind": "door",
            "cx": float(center.x), "cy": float(center.y),
            "radius": float(e.dxf.radius),
            "start_angle": float(e.dxf.start_angle),
            "end_angle": float(e.dxf.end_angle),
            "layer": e.dxf.layer,
        }
    except AttributeError:
        return None


def _insert_to_opening(e: Any, kind: str) -> dict | None:
    try:
        insert = e.dxf.insert
        return {
            "type": "block",
            "kind": kind,
            "x": float(insert.x), "y": float(insert.y),
            "rotation": float(getattr(e.dxf, "rotation", 0)),
            "scale_x": float(getattr(e.dxf, "xscale", 1)),
            "scale_y": float(getattr(e.dxf, "yscale", 1)),
            "block_name": e.dxf.name,
            "layer": e.dxf.layer,
        }
    except AttributeError:
        return None


def extract_openings(entities: list) -> list[dict]:
    """回傳門窗清單。"""
    openings: list[dict] = []
    for e in entities:
        layer = getattr(e.dxf, "layer", "")
        kind = _kind_from_layer(layer)
        dxftype = e.dxftype()

        if dxftype == "INSERT" and kind:
            op = _insert_to_opening(e, kind)
            if op:
                openings.append(op)

        elif dxftype == "ARC":
            # Arc in door layer OR any large arc (door sweep)
            if kind == "door" or (not kind and "door" in layer.lower()):
                op = _arc_to_opening(e)
                if op:
                    openings.append(op)

    log.info("openings_extracted", count=len(openings))
    return openings
