"""V-Ray 6 preset loader + resolution/sample override。"""

from __future__ import annotations

import json
from pathlib import Path

_PRESETS_DIR = Path(__file__).parent / "presets"


def apply_preset(preset_name: str, overrides: dict | None = None) -> dict:
    """載入 preset JSON，套 overrides，回傳最終 V-Ray 參數 dict。

    preset_name: 'draft' | 'standard' | 'premium'
    overrides:   { width, height, gi, denoiser, ... }
    """
    path = _PRESETS_DIR / f"{preset_name}.json"
    if not path.exists():
        path = _PRESETS_DIR / "standard.json"
    with path.open(encoding="utf-8") as f:
        data: dict = json.load(f)

    res = data.get("resolution", [1920, 1080])
    result = {
        "width": res[0],
        "height": res[1],
        "min_samples": 1,
        "max_samples": data.get("samples", 16),
        "gi": data.get("gi", True),
        "denoiser": data.get("denoiser", True),
    }
    if overrides:
        result.update({k: v for k, v in overrides.items() if v is not None})
    return result
