"""Style Engine — Claude tool-use 呼叫。有 API key 時呼叫真 Claude；否則 fixture fallback。"""

import hashlib
import json

import structlog

from app.config import get_settings
from app.schemas.style import StyleSchema

log = structlog.get_logger(__name__)

_FIXTURE = StyleSchema.model_validate(
    {
        "color_palette": ["#F5F1E8", "#D9C7A3", "#4A3F35"],
        "floor": {"type": "oak", "finish": "matte", "tone": "light", "color": "#C9A97A"},
        "wall": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#F5F1E8"},
        "ceiling": {"type": "latex_paint", "finish": "matte", "tone": "light", "color": "#FFFFFF"},
        "lighting": {"sun_kelvin": 5200, "direction": "SW", "intensity": 1.2, "ambient": "soft"},
        "furniture_language": "nordic-minimal",
        "camera": {"type": "eye-level", "fov": 50, "height_mm": 1600},
    }
)

_STYLE_TOOL = {
    "name": "emit_style",
    "description": "Return a concrete StyleSchema based on the user's interior design description.",
    "input_schema": StyleSchema.model_json_schema(),
}


def _clamp(schema: dict) -> dict:
    """把 AI 出界的數值 clamp 在 StyleSchema 允許範圍內。"""
    lighting = schema.get("lighting", {})
    kelvin = lighting.get("sun_kelvin", 5000)
    lighting["sun_kelvin"] = max(2500, min(10000, int(kelvin)))
    intensity = lighting.get("intensity", 1.0)
    lighting["intensity"] = max(0.0, min(3.0, float(intensity)))
    schema["lighting"] = lighting
    palette = schema.get("color_palette", [])
    schema["color_palette"] = palette[:5] if len(palette) > 5 else (palette or ["#FFFFFF"])
    return schema


async def _get_redis():
    """取得 Redis 連線；失敗回傳 None。"""
    try:
        import redis.asyncio as aioredis  # noqa: PLC0415

        client = aioredis.from_url(get_settings().REDIS_URL, decode_responses=True)
        await client.ping()
        return client
    except Exception as e:
        log.warning("style_engine_redis_unavailable", error=str(e))
        return None


async def parse_text_style(description: str) -> StyleSchema:
    settings = get_settings()

    # --- Redis cache ---
    cache_key = "style:text:" + hashlib.sha256(description.encode()).hexdigest()
    redis = await _get_redis()
    if redis is not None:
        try:
            cached = await redis.get(cache_key)
            if cached:
                log.info("style_engine_cache_hit", key=cache_key)
                return StyleSchema.model_validate(json.loads(cached))
        except Exception as e:
            log.warning("style_engine_redis_get_failed", error=str(e))

    if not settings.ANTHROPIC_API_KEY:
        log.info("style_engine_fixture_fallback", reason="no_api_key")
        return _FIXTURE

    from anthropic import AsyncAnthropic  # noqa: PLC0415

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    try:
        resp = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2000,
            tools=[_STYLE_TOOL],
            tool_choice={"type": "tool", "name": "emit_style"},
            messages=[{
                "role": "user",
                "content": (
                    "將以下室內設計描述轉為 StyleSchema。"
                    "只從 enum 值中選擇，不要自創。描述：\n" + description
                ),
            }],
        )
        tool_use = next(b for b in resp.content if b.type == "tool_use")
        raw = _clamp(dict(tool_use.input))
        result = StyleSchema.model_validate(raw)

        # 存入 cache
        if redis is not None:
            try:
                await redis.set(cache_key, result.model_dump_json(), ex=86400)
            except Exception as e:
                log.warning("style_engine_redis_set_failed", error=str(e))

        return result
    except Exception as e:
        log.warning("style_engine_claude_failed_fallback", error=str(e))
        return _FIXTURE


async def parse_visual_style(description: str, base64_images: list[str]) -> StyleSchema:
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY or not base64_images:
        return _FIXTURE

    from anthropic import AsyncAnthropic  # noqa: PLC0415

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    content: list[dict] = []
    for b64 in base64_images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": b64,
            },
        })
    content.append({
        "type": "text",
        "text": "依照圖片風格與以下描述，輸出 StyleSchema。描述：" + description,
    })

    try:
        resp = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2000,
            tools=[_STYLE_TOOL],
            tool_choice={"type": "tool", "name": "emit_style"},
            messages=[{"role": "user", "content": content}],
        )
        tool_use = next(b for b in resp.content if b.type == "tool_use")
        raw = _clamp(dict(tool_use.input))
        return StyleSchema.model_validate(raw)
    except Exception as e:
        log.warning("style_engine_vision_failed_fallback", error=str(e))
        return _FIXTURE
