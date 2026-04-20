"""DXF 主入口 — ezdxf 讀取。骨架階段只丟 NotImplementedError。"""

from pathlib import Path


def parse(dxf_path: Path) -> dict:
    """Sprint 0 PoC 會真的用 ezdxf 拆出 walls/doors/windows/rooms。"""
    raise NotImplementedError("Sprint 2 實作 — 整合 Sprint 0 的 PoC 腳本")
