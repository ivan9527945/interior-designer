"""StyleSchema → V-Ray 參數映射。

把 StyleSchema 的 lighting / camera 欄位轉成 V-Ray 可用的參數。
"""

from __future__ import annotations

_KELVIN_TO_EXPOSURE: dict[str, float] = {
    "warm": 0.4,   # 3000 K
    "neutral": 0.0,
    "cool": -0.2,  # 6500 K
}

_AMBIENT_TO_GI: dict[str, dict] = {
    "soft": {"gi": True, "gi_strength": 1.0},
    "hard": {"gi": True, "gi_strength": 0.6},
    "overcast": {"gi": True, "gi_strength": 1.4},
    "golden-hour": {"gi": True, "gi_strength": 1.2},
}

_DIRECTION_TO_SUN_ANGLES: dict[str, tuple[float, float]] = {
    # (azimuth_deg, altitude_deg)
    "N": (0, 45), "NE": (45, 45), "E": (90, 45), "SE": (135, 45),
    "S": (180, 45), "SW": (225, 45), "W": (270, 45), "NW": (315, 45),
}

_CAMERA_FOV: dict[str, int] = {
    "eye-level": 50,
    "axonometric": 1,   # very narrow = orthographic-like
    "aerial": 70,
    "custom": 50,
}


def map_style(style: dict) -> dict:
    """回傳 V-Ray override dict（將和 preset 合併）。"""
    lighting = style.get("lighting", {})
    camera = style.get("camera", {})

    direction = lighting.get("direction", "SW")
    sun_az, sun_alt = _DIRECTION_TO_SUN_ANGLES.get(direction, (225, 45))

    kelvin = lighting.get("sun_kelvin", 5200)
    intensity = lighting.get("intensity", 1.2)
    ambient = lighting.get("ambient", "soft")
    gi_cfg = _AMBIENT_TO_GI.get(ambient, {"gi": True, "gi_strength": 1.0})

    cam_type = camera.get("type", "eye-level")
    fov = camera.get("fov") or _CAMERA_FOV.get(cam_type, 50)
    cam_height = camera.get("height_mm", 1600)

    # 色溫 → 白平衡（V-Ray color_balance kelvin）
    color_balance = max(2500, min(10000, kelvin))

    return {
        "sun_azimuth": sun_az,
        "sun_altitude": sun_alt,
        "sun_intensity": float(intensity),
        "color_balance_kelvin": color_balance,
        "gi": gi_cfg["gi"],
        "gi_strength": gi_cfg["gi_strength"],
        "camera_fov": fov,
        "camera_height_mm": cam_height,
        "camera_type": cam_type,
    }
