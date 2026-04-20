"""SketchUp 啟動控制 — 規格 §5.4。

macOS 上沒有官方 headless 模式。
MVP 策略：subprocess 直接啟動，靠 -RubyStartup 跑 script，完成後 SketchUp 自動 quit。
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import structlog

from renderstudio_agent.config import get_settings

log = structlog.get_logger(__name__)

_SCRIPTS_DIR = Path(__file__).parent / "ruby_scripts"


class SketchUpError(RuntimeError):
    pass


def _app_binary() -> Path:
    settings = get_settings()
    app = settings.SKETCHUP_APP
    if app.endswith(".app"):
        return Path(app) / "Contents/MacOS/SketchUp"
    return Path(app)


async def run_sketchup(ruby_script: Path, args: dict, skp_out: Path, timeout: int = 600) -> None:
    """非同步啟動 SketchUp，執行 ruby_script，等待完成或超時。"""
    app_bin = _app_binary()
    if not app_bin.exists():
        raise SketchUpError(
            f"SketchUp not found at {app_bin}. "
            "Set SKETCHUP_APP env var or install SketchUp 2024."
        )

    env = {
        **os.environ,
        "RS_ARGS_JSON": json.dumps(args, ensure_ascii=False),
        "RS_OUTPUT": str(skp_out),
    }

    log.info("sketchup_launch", script=ruby_script.name, out=str(skp_out))
    proc = await asyncio.create_subprocess_exec(
        str(app_bin),
        "-RubyStartup", str(ruby_script),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise SketchUpError(f"SketchUp timed out after {timeout}s") from None

    if proc.returncode != 0:
        err = stderr.decode(errors="ignore")
        log.error("sketchup_failed", returncode=proc.returncode, stderr=err)
        raise SketchUpError(err)

    log.info("sketchup_done", returncode=proc.returncode)


async def generate_model(scene: dict, skp_out: Path) -> None:
    """Step 1: DXF scene JSON → .skp 模型。"""
    script = _SCRIPTS_DIR / "generate_model.rb"
    await run_sketchup(script, scene, skp_out)


async def apply_materials(skp_in: Path, style_schema: dict, skp_out: Path) -> None:
    """Step 2: 套材質。"""
    script = _SCRIPTS_DIR / "apply_materials.rb"
    args = {"skp_in": str(skp_in), "style": style_schema}
    await run_sketchup(script, args, skp_out)


async def place_furniture(skp_in: Path, rooms: list[dict], style_schema: dict, skp_out: Path) -> None:
    """Step 3: 擺放家具。"""
    script = _SCRIPTS_DIR / "place_furniture.rb"
    args = {"skp_in": str(skp_in), "rooms": rooms, "style": style_schema}
    await run_sketchup(script, args, skp_out)


async def trigger_render(skp_in: Path, vray_params: dict, output_png: Path) -> None:
    """Step 4: 觸發 V-Ray 渲染 → output_png。"""
    script = _SCRIPTS_DIR / "render.rb"
    args = {
        "skp_in": str(skp_in),
        "vray": vray_params,
        "output_png": str(output_png),
    }
    # render.rb 以 skp_in 為輸入路徑（透過 RS_ARGS_JSON），output 傳 output_png
    env_out = output_png
    await run_sketchup(script, args, env_out, timeout=1800)
