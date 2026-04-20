# RenderStudio Agent

本機 Python Agent，驅動 SketchUp 2024 + V-Ray 6（macOS 14+）。

## Dev

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example ~/Library/Application\ Support/RenderStudio/.env
python -m renderstudio_agent
```

## 啟動參數（env）

- `RS_API_BASE` — 後端 URL
- `RS_AGENT_TOKEN` — 首次 register 後存入
- `SKETCHUP_APP` — SketchUp 2024 路徑
- `IDLE_BEFORE_RUN_SECONDS` — 使用者閒置門檻（預設 300s）

## Rust 擴充（可選）

幾何計算熱點用 PyO3/Rust 加速。未裝 Rust toolchain 時跳過：

```bash
pip install -e '.[rust]'
cd rust_geometry && maturin develop
```
