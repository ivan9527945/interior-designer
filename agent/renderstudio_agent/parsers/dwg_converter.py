"""呼叫 ODA File Converter 把 DWG 轉成 DXF。

ODA File Converter 預設安裝路徑（macOS）：
  /Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter
"""

import subprocess
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)

_ODA_PATHS = [
    Path("/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"),
    Path("/usr/local/bin/ODAFileConverter"),
]


def _find_oda() -> Path | None:
    for p in _ODA_PATHS:
        if p.exists():
            return p
    return None


def convert(dwg: Path, out_dir: Path) -> Path:
    """DWG → DXF。回傳產出的 .dxf 路徑。

    ODA CLI 格式：
      ODAFileConverter <inputFolder> <outputFolder> <version> <type> <recurse> <audit>
    version: ACAD2018, type: DXF, recurse: 0, audit: 1
    """
    oda = _find_oda()
    if oda is None:
        raise FileNotFoundError(
            "ODA File Converter not found. "
            "Download from https://www.opendesign.com/guestfiles/oda_file_converter"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(oda),
        str(dwg.parent),
        str(out_dir),
        "ACAD2018",
        "DXF",
        "0",
        "1",
    ]
    log.info("dwg_convert_start", dwg=str(dwg), cmd=" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"ODA converter failed: {result.stderr}")

    dxf_path = out_dir / dwg.with_suffix(".dxf").name
    if not dxf_path.exists():
        # ODA sometimes keeps filename exactly
        candidates = list(out_dir.glob("*.dxf"))
        if not candidates:
            raise FileNotFoundError(f"ODA produced no DXF in {out_dir}")
        dxf_path = candidates[0]

    log.info("dwg_convert_done", dxf=str(dxf_path))
    return dxf_path
