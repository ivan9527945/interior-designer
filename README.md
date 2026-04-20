# RenderStudio

Web + 本機 Agent 的室內渲染自動化平台。

- **frontend/** — Next.js 14 App Router (React 18, Tailwind, shadcn/ui)
- **backend/** — FastAPI + Celery + Postgres + Redis + MinIO
- **agent/** — Python asyncio 本機 Agent（macOS，驅動 SketchUp + V-Ray）
- **shared/** — 三端共用 StyleSchema JSON Schema
- **infra/** — docker-compose + K8s manifests

完整設計請見 `docs/` 下的 PRD、TechSpec、Implementation 三份文件。

---

## Prerequisites

| 工具 | 版本 | 安裝 |
|---|---|---|
| Node.js | 20 LTS | `nvm install 20` |
| pnpm | 10.x | `npm i -g pnpm` |
| Python | **3.11** | `brew install python@3.11` |
| Rust | 1.75+（Agent 可選） | `rustup default stable` |
| Docker | 最新（可選，見備援） | Docker Desktop |

**不用 Docker 的備援路徑**：

```bash
brew install postgresql@15 redis minio/stable/minio
brew services start postgresql@15 redis minio
createdb renderstudio
```

---

## Quickstart

```bash
# 安裝前端依賴
pnpm install

# 首次建立後端與 Agent 虛擬環境
make bootstrap

# 同步 StyleSchema → shared/style_schema.json
make sync-schema

# 起三個服務（個別終端機）
make dev-frontend      # http://localhost:3000
make dev-backend       # http://localhost:8000
make dev-agent
```

---

## Monorepo Layout

```
renderstudio/
├── frontend/            # Next.js 14
├── backend/             # FastAPI
├── agent/               # Python Agent
├── shared/              # style_schema.json (單一事實來源)
├── infra/
│   ├── docker-compose.dev.yml
│   └── k8s/
├── docs/
├── .github/workflows/
├── pnpm-workspace.yaml
├── Makefile
└── README.md
```

---

## 環境變數

複製 `.env.example` 檔案為 `.env` 填入實際值。

- `backend/.env.example` → `backend/.env`
- `frontend/.env.example` → `frontend/.env.local`
- `agent/.env.example` → `~/Library/Application Support/RenderStudio/.env`

無 `ANTHROPIC_API_KEY` 時，Style engine 自動走 fixture stub（開發階段可用）。

---

## Status

目前處於 **Sprint 1 骨架階段**。三個子專案可啟動，但功能尚未實作（大部分 router handler 回 `501 Not Implemented`）。

詳細進度見 `docs/Implementation.md` 的 Sprint 清單。
