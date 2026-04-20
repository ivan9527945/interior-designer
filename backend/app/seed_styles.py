"""Seed script — 插入 7 個預設風格（kind="preset"）。同名已存在則跳過。"""

import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models.style import Style

_PRESET_STYLES = [
    {
        "name": "nordic-minimal",
        "schema_json": {
            "color_palette": ["#F5F1E8", "#D9C7A3", "#FFFFFF", "#E8E0D5", "#4A3F35"],
            "floor": {"type": "oak", "finish": "matte", "tone": "light", "color": "#C9A97A"},
            "wall": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#FFFFFF"},
            "ceiling": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#FFFFFF"},
            "lighting": {"sun_kelvin": 5500, "direction": "N", "intensity": 1.1, "ambient": "soft"},
            "furniture_language": "nordic-minimal",
            "camera": {"type": "eye-level", "fov": 50, "height_mm": 1600},
        },
    },
    {
        "name": "wabi-sabi",
        "schema_json": {
            "color_palette": ["#9B9B8A", "#F5F0E8", "#C4B9A8", "#7A7468", "#E8E0D0"],
            "floor": {"type": "concrete", "finish": "matte", "tone": "medium", "color": "#9B9B8A"},
            "wall": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#F5F0E8"},
            "ceiling": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#F0EBE3"},
            "lighting": {"sun_kelvin": 4000, "direction": "SW", "intensity": 0.9, "ambient": "overcast"},
            "furniture_language": "wabi-sabi",
            "camera": {"type": "eye-level", "fov": 50, "height_mm": 1600},
        },
    },
    {
        "name": "industrial",
        "schema_json": {
            "color_palette": ["#5C4033", "#3D3D3D", "#8B7355", "#2C2C2C", "#6B6B6B"],
            "floor": {"type": "concrete", "finish": "matte", "tone": "dark", "color": "#3D3D3D"},
            "wall": {"type": "brick", "finish": "matte", "tone": "medium", "color": "#5C4033"},
            "ceiling": {"type": "concrete", "finish": "matte", "tone": "dark", "color": "#2C2C2C"},
            "lighting": {"sun_kelvin": 3200, "direction": "E", "intensity": 1.4, "ambient": "hard"},
            "furniture_language": "industrial",
            "camera": {"type": "eye-level", "fov": 55, "height_mm": 1600},
        },
    },
    {
        "name": "modern",
        "schema_json": {
            "color_palette": ["#FFFFFF", "#F0F0F0", "#D4C5A9", "#C8C8C8", "#E8E8E8"],
            "floor": {"type": "marble", "finish": "polished", "tone": "light", "color": "#F0EDE8"},
            "wall": {"type": "latex_paint", "finish": "semi-gloss", "tone": "light", "color": "#FFFFFF"},
            "ceiling": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#FFFFFF"},
            "lighting": {"sun_kelvin": 4500, "direction": "SW", "intensity": 1.3, "ambient": "golden-hour"},
            "furniture_language": "modern",
            "camera": {"type": "eye-level", "fov": 50, "height_mm": 1600},
        },
    },
    {
        "name": "luxury",
        "schema_json": {
            "color_palette": ["#1A1A1A", "#C9A84C", "#2D2D2D", "#B8963E", "#0D0D0D"],
            "floor": {"type": "marble", "finish": "polished", "tone": "dark", "color": "#1A1A1A"},
            "wall": {"type": "marble", "finish": "polished", "tone": "dark", "color": "#1A1A1A"},
            "ceiling": {"type": "latex_paint", "finish": "semi-gloss", "tone": "dark", "color": "#0D0D0D"},
            "lighting": {"sun_kelvin": 3000, "direction": "SW", "intensity": 1.5, "ambient": "hard"},
            "furniture_language": "luxury",
            "camera": {"type": "eye-level", "fov": 45, "height_mm": 1600},
        },
    },
    {
        "name": "american-country",
        "schema_json": {
            "color_palette": ["#F5F0DC", "#C4A882", "#8B6914", "#E8DCC8", "#A0825A"],
            "floor": {"type": "oak", "finish": "satin", "tone": "medium", "color": "#C4A882"},
            "wall": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#F5F0DC"},
            "ceiling": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#FAFAF5"},
            "lighting": {"sun_kelvin": 4200, "direction": "S", "intensity": 1.1, "ambient": "soft"},
            "furniture_language": "american-country",
            "camera": {"type": "eye-level", "fov": 52, "height_mm": 1600},
        },
    },
    {
        "name": "french",
        "schema_json": {
            "color_palette": ["#F8F6F0", "#E8E0D5", "#C8C0B5", "#D4CFC5", "#B0A898"],
            "floor": {"type": "oak", "finish": "satin", "tone": "light", "color": "#D4C5A9"},
            "wall": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#F8F6F0"},
            "ceiling": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#FFFFFF"},
            "lighting": {"sun_kelvin": 5000, "direction": "NW", "intensity": 1.0, "ambient": "soft"},
            "furniture_language": "french",
            "camera": {"type": "eye-level", "fov": 48, "height_mm": 1600},
        },
    },
]


async def main() -> None:
    async with SessionLocal() as session:
        for preset in _PRESET_STYLES:
            existing = await session.execute(
                select(Style).where(Style.name == preset["name"], Style.kind == "preset")
            )
            if existing.scalar_one_or_none() is not None:
                print(f"[skip] {preset['name']} already exists")
                continue

            style = Style(
                name=preset["name"],
                kind="preset",
                schema_json=preset["schema_json"],
            )
            session.add(style)
            print(f"[insert] {preset['name']}")

        await session.commit()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
