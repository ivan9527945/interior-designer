"""Style Engine — Claude 呼叫。

規格 §4.4。Sprint 3 會真的接 Anthropic SDK；骨架階段無 API key 時
回 fixture stub，讓前端能跑完整 request/response。
"""

from app.config import get_settings
from app.schemas.style import StyleSchema

_FIXTURE = StyleSchema.model_validate(
    {
        "color_palette": ["#F5F1E8", "#D9C7A3", "#4A3F35"],
        "floor": {"type": "oak", "finish": "matte", "tone": "light", "color": "#C9A97A"},
        "wall": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#F5F1E8"},
        "ceiling": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#FFFFFF"},
        "lighting": {
            "sun_kelvin": 5200,
            "direction": "SW",
            "intensity": 1.2,
            "ambient": "soft",
        },
        "furniture_language": "nordic-minimal",
        "camera": {"type": "eye-level", "fov": 50, "height_mm": 1600},
    }
)


async def parse_text_style(description: str) -> StyleSchema:
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY:
        # Stub fallback — 讓沒 API key 的開發環境也能跑
        return _FIXTURE

    # TODO (Sprint 3): 接 Anthropic SDK
    # from anthropic import AsyncAnthropic
    # client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    # STYLE_TOOL = {
    #     "name": "emit_style",
    #     "description": "Return a concrete StyleSchema based on the user's description.",
    #     "input_schema": StyleSchema.model_json_schema(),
    # }
    # resp = await client.messages.create(
    #     model=settings.ANTHROPIC_MODEL,
    #     max_tokens=2000,
    #     tools=[STYLE_TOOL],
    #     tool_choice={"type": "tool", "name": "emit_style"},
    #     messages=[{"role": "user", "content": f"將以下室內設計描述轉為 StyleSchema...\n{description}"}],
    # )
    # tool_use = next(b for b in resp.content if b.type == "tool_use")
    # return StyleSchema(**tool_use.input)
    return _FIXTURE


async def parse_visual_style(description: str, image_urls: list[str]) -> StyleSchema:
    # TODO (Sprint 3): Claude Vision
    return _FIXTURE
