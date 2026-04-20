#!/usr/bin/env python3
"""Sprint 0 PoC — 端到端驗證腳本。

用法：
  python run_poc.py plan.dxf [elevation.dxf] style.json

  # 若有 DWG 而非 DXF：
  python run_poc.py plan.dwg [elevation.dwg] style.json

輸出：output.png（同目錄）+ poc_timing.json（每階段耗時）
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path


def _time(label: str, start: float) -> float:
    elapsed = time.perf_counter() - start
    print(f"  [{label}] {elapsed:.1f}s")
    return elapsed


def _load_style(style_path: Path) -> dict:
    with style_path.open(encoding="utf-8") as f:
        return json.load(f)


def _ensure_dxf(path: Path) -> Path:
    """DWG → DXF 轉換（若需要）。"""
    if path.suffix.lower() == ".dxf":
        return path
    from renderstudio_agent.parsers.dwg_converter import convert  # noqa: PLC0415

    out_dir = path.parent / "_dxf_converted"
    return convert(path, out_dir)


def _run_parse(dxf_path: Path) -> dict:
    from renderstudio_agent.parsers.dxf_parser import parse  # noqa: PLC0415

    return parse(dxf_path)


def _run_merge(plan_data: dict, elevation_data: dict | None) -> dict:
    from renderstudio_agent.parsers.plan_elevation_merge import merge  # noqa: PLC0415

    return merge(plan_data, elevation_data)


async def _run_model(scene: dict, skp_out: Path) -> None:
    from renderstudio_agent.sketchup.controller import generate_model  # noqa: PLC0415

    await generate_model(scene, skp_out)


async def _run_materials(skp_in: Path, style: dict, skp_out: Path) -> None:
    from renderstudio_agent.sketchup.controller import apply_materials  # noqa: PLC0415

    await apply_materials(skp_in, style, skp_out)


async def _run_render(skp_in: Path, style: dict, quality: str, output_png: Path) -> None:
    from renderstudio_agent.vray.adapter import apply_preset  # noqa: PLC0415
    from renderstudio_agent.vray.style_to_vray import map_style  # noqa: PLC0415
    from renderstudio_agent.sketchup.controller import trigger_render  # noqa: PLC0415

    vray_base = apply_preset(quality)
    vray_style = map_style(style)
    vray_params = {**vray_base, **vray_style}
    await trigger_render(skp_in, vray_params, output_png)


async def poc(
    plan_path: Path,
    elevation_path: Path | None,
    style_path: Path,
    quality: str,
    out_dir: Path,
) -> None:
    timings: dict[str, float] = {}
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("RenderStudio Sprint 0 PoC")
    print(f"  plan:      {plan_path}")
    print(f"  elevation: {elevation_path or '(none)'}")
    print(f"  style:     {style_path}")
    print(f"  quality:   {quality}")
    print("=" * 60)

    style = _load_style(style_path)

    # ── 1. DWG → DXF ──────────────────────────────────────────
    t = time.perf_counter()
    print("\n[1] DWG 轉換 / 驗證 DXF…")
    plan_dxf = _ensure_dxf(plan_path)
    elevation_dxf = _ensure_dxf(elevation_path) if elevation_path else None
    timings["dwg_convert"] = _time("DWG→DXF", t)

    # ── 2. DXF 解析 ────────────────────────────────────────────
    t = time.perf_counter()
    print("\n[2] DXF 解析…")
    plan_data = _run_parse(plan_dxf)
    elevation_data = _run_parse(elevation_dxf) if elevation_dxf else None
    print(f"    walls={len(plan_data['walls'])}  openings={len(plan_data['openings'])}  rooms={len(plan_data['rooms'])}")
    timings["dxf_parse"] = _time("解析", t)

    # ── 3. 合併 ────────────────────────────────────────────────
    scene = _run_merge(plan_data, elevation_data)

    # ── 4. 建模 ────────────────────────────────────────────────
    t = time.perf_counter()
    print("\n[3] SketchUp 建模…")
    skp_base = out_dir / "model.skp"
    await _run_model(scene, skp_base)
    timings["modeling"] = _time("建模", t)

    # ── 5. 材質 ────────────────────────────────────────────────
    t = time.perf_counter()
    print("\n[4] 套材質…")
    skp_mat = out_dir / "model_mat.skp"
    await _run_materials(skp_base, style, skp_mat)
    timings["material"] = _time("材質", t)

    # ── 6. 渲染 ────────────────────────────────────────────────
    t = time.perf_counter()
    print("\n[5] V-Ray 渲染…")
    output_png = out_dir / "output.png"
    await _run_render(skp_mat, style, quality, output_png)
    timings["render"] = _time("渲染", t)

    # ── 7. 結果 ────────────────────────────────────────────────
    total = sum(timings.values())
    timings["total"] = total
    timing_file = out_dir / "poc_timing.json"
    timing_file.write_text(json.dumps(timings, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print(f"✓ 完成！output.png → {output_png}")
    print(f"  總耗時：{total:.1f}s")
    print(f"  timing → {timing_file}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="RenderStudio Sprint 0 PoC")
    parser.add_argument("plan", type=Path, help="平面圖 .dwg 或 .dxf")
    parser.add_argument("elevation_or_style", type=Path,
                        help="立面圖 .dwg/.dxf 或 style.json（如果無立面圖則直接傳 style.json）")
    parser.add_argument("style_optional", type=Path, nargs="?",
                        help="style.json（若第 2 參數是立面圖才需要）")
    parser.add_argument("--quality", choices=["draft", "standard", "premium"], default="standard")
    parser.add_argument("--out", type=Path, default=Path("poc_output"))
    args = parser.parse_args()

    # 判斷是否有立面圖
    p2 = args.elevation_or_style
    if p2.suffix.lower() == ".json":
        elevation = None
        style_path = p2
    else:
        elevation = p2
        if not args.style_optional:
            print("ERROR: 提供立面圖時請同時提供 style.json", file=sys.stderr)
            sys.exit(1)
        style_path = args.style_optional

    asyncio.run(poc(args.plan, elevation, style_path, args.quality, args.out))


if __name__ == "__main__":
    main()
