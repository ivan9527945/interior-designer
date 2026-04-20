"""DXF 主入口 — ezdxf 讀取 + 解析牆體、門窗、房間。"""

from __future__ import annotations

from pathlib import Path

import ezdxf
import structlog

from renderstudio_agent.parsers.door_window import extract_openings
from renderstudio_agent.parsers.room_detector import detect_rooms
from renderstudio_agent.parsers.wall_extractor import extract_walls

log = structlog.get_logger(__name__)


def _detect_unit(doc: ezdxf.document.Drawing) -> str:
    """嘗試從 $INSUNITS 判斷單位。"""
    try:
        insunits = doc.header.get("$INSUNITS", 0)
        # 4 = mm, 6 = meters, 1 = inch
        mapping = {4: "mm", 6: "m", 1: "in", 2: "ft"}
        return mapping.get(int(insunits), "mm")
    except Exception:
        return "mm"


def _bbox(walls: list[dict]) -> dict:
    if not walls:
        return {}
    xs = [w["x0"] for w in walls] + [w["x1"] for w in walls]
    ys = [w["y0"] for w in walls] + [w["y1"] for w in walls]
    return {
        "min_x": min(xs), "min_y": min(ys),
        "max_x": max(xs), "max_y": max(ys),
        "width": max(xs) - min(xs),
        "height": max(ys) - min(ys),
    }


def parse(dxf_path: Path) -> dict:
    """讀取 DXF，回傳:

    {
        "walls": [...],
        "openings": [...],
        "rooms": [...],
        "bbox": {...},
        "unit": "mm",
        "layers": [...],
    }
    """
    log.info("dxf_parse_start", path=str(dxf_path))
    doc = ezdxf.readfile(str(dxf_path))
    msp = doc.modelspace()
    entities = list(msp)

    unit = _detect_unit(doc)
    layers = [layer.dxf.name for layer in doc.layers]

    walls = extract_walls(entities)
    openings = extract_openings(entities)
    rooms = detect_rooms(walls)
    bbox = _bbox(walls)

    result = {
        "walls": walls,
        "openings": openings,
        "rooms": rooms,
        "bbox": bbox,
        "unit": unit,
        "layers": layers,
        "entity_count": len(entities),
    }
    log.info(
        "dxf_parse_done",
        walls=len(walls), openings=len(openings), rooms=len(rooms),
    )
    return result
