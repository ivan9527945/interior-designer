"""StyleSchema — 單一事實來源（Pydantic → JSON Schema → Zod）。

規格 §4.3。使用 Pydantic v2 的 `Annotated[str, StringConstraints]`
取代 v1 的 `constr`。
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

HexColor = Annotated[str, StringConstraints(pattern=r"^#[0-9A-Fa-f]{6}$")]

FurnitureLanguage = Literal[
    "nordic-minimal",
    "wabi-sabi",
    "industrial",
    "modern",
    "luxury",
    "american-country",
    "french",
]
Direction = Literal["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
Ambient = Literal["soft", "hard", "overcast", "golden-hour"]
CameraType = Literal["eye-level", "axonometric", "aerial", "custom"]
Finish = Literal["matte", "satin", "gloss"]
Tone = Literal["light", "medium", "dark"]


class Material(BaseModel):
    type: str = Field(..., description="oak, latex_paint, marble ...")
    finish: Finish = "matte"
    tone: Tone = "medium"
    color: HexColor | None = None


class Lighting(BaseModel):
    sun_kelvin: int = Field(..., ge=2500, le=10000)
    direction: Direction
    intensity: float = Field(..., ge=0, le=3)
    ambient: Ambient


class Camera(BaseModel):
    type: CameraType = "eye-level"
    fov: int = 50
    height_mm: int = 1600


class StyleSchema(BaseModel):
    color_palette: list[HexColor] = Field(..., min_length=3, max_length=5)
    floor: Material
    wall: Material
    ceiling: Material
    lighting: Lighting
    furniture_language: FurnitureLanguage
    camera: Camera
