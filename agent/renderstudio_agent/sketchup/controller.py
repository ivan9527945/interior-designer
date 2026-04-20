"""SketchUp 啟動控制 — 規格 §5.4。

骨架版：只包裝 asyncio.create_subprocess_exec，不真的啟動 SketchUp。
Sprint 2 實作時拿掉 TODO guard。
"""

import asyncio
import json
import os
from pathlib import Path

import structlog

from renderstudio_agent.config import get_settings

log = structlog.get_logger(__name__)


class SketchUpError(RuntimeError):
    pass


async def run_sketchup(ruby_script: Path, args: dict, skp_out: Path, timeout: int = 600) -> None:
    settings = get_settings()
    app_bin = (
        Path(settings.SKETCHUP_APP) / "Contents/MacOS/SketchUp"
        if settings.SKETCHUP_APP.endswith(".app")
        else Path(settings.SKETCHUP_APP)
    )

    # TODO (Sprint 2): 拿掉這行 guard
    raise NotImplementedError("Sprint 2 — 真的啟動 SketchUp 執行 ruby script")

    env = {**os.environ, "RS_ARGS_JSON": json.dumps(args), "RS_OUTPUT": str(skp_out)}
    proc = await asyncio.create_subprocess_exec(
        str(app_bin),
        "-RubyStartup",
        str(ruby_script),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise SketchUpError(f"timeout after {timeout}s") from None

    if proc.returncode != 0:
        log.error("sketchup_failed", stderr=stderr.decode(errors="ignore"))
        raise SketchUpError(stderr.decode(errors="ignore"))
