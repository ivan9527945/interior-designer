from app.schemas.style import StyleSchema


def test_style_schema_minimal_valid():
    s = StyleSchema.model_validate(
        {
            "color_palette": ["#FFFFFF", "#000000", "#AAAAAA"],
            "floor": {"type": "oak", "finish": "matte", "tone": "light"},
            "wall": {"type": "latex", "finish": "matte", "tone": "light"},
            "ceiling": {"type": "latex", "finish": "matte", "tone": "light"},
            "lighting": {"sun_kelvin": 5000, "direction": "S", "intensity": 1.0, "ambient": "soft"},
            "furniture_language": "modern",
            "camera": {"type": "eye-level", "fov": 50, "height_mm": 1600},
        }
    )
    assert s.furniture_language == "modern"


def test_json_schema_export_has_required_fields():
    schema = StyleSchema.model_json_schema()
    assert "properties" in schema
    for k in ("color_palette", "floor", "wall", "ceiling", "lighting", "furniture_language", "camera"):
        assert k in schema["properties"]
