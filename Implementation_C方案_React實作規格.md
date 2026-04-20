# RenderStudio — C 方案（Web + 本機 Agent）React 實作規格

> Version 0.1 · 2026-04-20 · Internal
> 對應 PRD v0.1 與 TechSpec v0.1

---

## 0. TL;DR — 這份文件是什麼

這份文件**把「C 方案」落成工程可以照著蓋的東西**，包含：

- 完整系統架構圖（Mermaid + ASCII）
- React（Next.js 14）前端的目錄結構、關鍵元件、狀態管理策略
- 後端（FastAPI）的 API 契約與模組切分
- 本機 Agent（Python）的核心流程與狀態機
- Postgres 資料表 schema
- 依 Sprint 切分的可勾選實作清單（Sprint 0～5，共約 11～14 週）
- 環境變數、部署、CI/CD、測試策略

工程師看完這份應該能直接開 Jira / Linear ticket 開工。

---

## 1. 系統架構圖

### 1.1 高階元件圖（Mermaid）

```mermaid
graph TB
    subgraph Client["🌐 設計師瀏覽器 (Chrome/Safari)"]
        FE[Next.js 14<br/>React 18<br/>Tailwind + shadcn/ui]
    end

    subgraph Cloud["☁️ 雲端 (公司內網 K8s)"]
        API[FastAPI<br/>API Server]
        Worker[Celery Worker<br/>Job Dispatcher]
        DB[(PostgreSQL 15<br/>metadata)]
        Redis[(Redis<br/>queue + cache)]
        Store[(MinIO / S3<br/>DWG/SKP/PNG)]
        Auth[Keycloak<br/>OIDC SSO]
        LLM[Claude API<br/>風格解析]
    end

    subgraph Local["💻 設計師 Mac (macOS 14+)"]
        Agent[RenderStudio Agent<br/>Python + Rust FFI]
        SU[SketchUp 2024<br/>Pro]
        VR[V-Ray 6<br/>for SketchUp]
        ODA[ODA File Converter<br/>DWG → DXF]
    end

    FE -- HTTPS + SSE --> API
    FE -- OIDC --> Auth
    API --- DB
    API --- Redis
    API --- Store
    API -- tool call --> LLM
    API --> Worker
    Worker --- Redis
    Agent -- long-poll / gRPC --> API
    Agent -- 讀寫 --> Store
    Agent --> ODA
    Agent -- Ruby API --> SU
    SU -- V-Ray Plugin --> VR

    style FE fill:#4f46e5,color:#fff
    style API fill:#10b981,color:#fff
    style Agent fill:#f59e0b,color:#fff
    style LLM fill:#8b5cf6,color:#fff
```

### 1.2 ASCII 版（給不支援 Mermaid 的閱讀器）

```
┌─────────────────────────────────────────────────────────────────┐
│                  🌐 設計師瀏覽器 (Chrome/Safari)                 │
│            Next.js 14 · React 18 · Tailwind · shadcn/ui         │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS + SSE (渲染進度推送)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ☁️  雲端 (公司內網 K8s)                         │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐                │
│  │  FastAPI   │  │  Celery    │  │ Claude API   │               │
│  │   API      │──▶  Worker    │  │ (文字/視覺)   │               │
│  └─────┬──────┘  └─────┬──────┘  └──────────────┘               │
│        │               │                                        │
│  ┌─────▼──────┐  ┌─────▼──────┐  ┌──────────────┐               │
│  │ Postgres   │  │   Redis    │  │  MinIO/S3    │               │
│  │  metadata  │  │  queue     │  │ dwg/skp/png  │               │
│  └────────────┘  └────────────┘  └──────────────┘               │
│                                                                 │
│                    ┌──────────────┐                             │
│                    │  Keycloak    │                             │
│                    │   (OIDC)     │                             │
│                    └──────────────┘                             │
└────────────────────────┬────────────────────────────────────────┘
                         │ long-poll (Agent 主動拉) + gRPC
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             💻 設計師 Mac (macOS 14+ / Apple Silicon)             │
│                                                                 │
│    ┌───────────────────────────────────────────────────┐        │
│    │         RenderStudio Agent (Python + Rust)        │        │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │        │
│    │  │   Job    │  │   DXF    │  │  SketchUp    │    │        │
│    │  │  Poller  │──▶  Parser  │──▶ Controller   │    │        │
│    │  └──────────┘  └──────────┘  └──────┬───────┘    │        │
│    │                                      │            │        │
│    │                                      ▼            │        │
│    │                          ┌───────────────────┐    │        │
│    │                          │ V-Ray Controller  │    │        │
│    │                          └───────────────────┘    │        │
│    └───────────────────────────┬───────────────────────┘        │
│                                │                                │
│   ┌────────────────────────────▼────────────────────────┐       │
│   │  SketchUp 2024 Pro  +  V-Ray 6 for SketchUp        │       │
│   │  （沿用設計師既有授權，Agent 不另外買）               │       │
│   └────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 核心資料流（提交一次渲染的完整 Sequence）

```mermaid
sequenceDiagram
    participant U as 設計師<br/>（瀏覽器）
    participant FE as Next.js
    participant API as FastAPI
    participant DB as Postgres
    participant S3 as MinIO
    participant LLM as Claude
    participant Q as Redis Queue
    participant AG as 本機 Agent
    participant SU as SketchUp
    participant VR as V-Ray

    U->>FE: 拖入平面/立面 DWG
    FE->>API: POST /uploads/presign
    API->>S3: generate presigned PUT URL
    FE->>S3: 直接 PUT DWG
    FE->>API: POST /spaces (dwg_file_id)
    API->>DB: INSERT space
    U->>FE: 輸入「北歐極簡，淺橡木⋯」
    FE->>API: POST /style/parse/text
    API->>LLM: Claude + tool schema=Style
    LLM-->>API: StyleSchema JSON
    API->>DB: cache style
    API-->>FE: StyleSchema
    U->>FE: 按「提交渲染」
    FE->>API: POST /renders
    API->>DB: INSERT render(status=pending)
    API->>Q: enqueue job
    AG->>API: GET /agent/next-job (long-poll)
    API->>Q: pop
    API-->>AG: job (dwg_url, style, settings)
    AG->>S3: GET dwg
    AG->>AG: DXF 解析
    AG->>API: POST /agent/job/{id}/report (parsing→modeling)
    API->>FE: SSE progress update
    AG->>SU: 啟動 + Ruby script
    SU-->>AG: .skp ready
    AG->>API: POST report (modeling→rendering)
    AG->>VR: trigger render via SketchUp
    VR-->>AG: output.png
    AG->>S3: PUT output.png
    AG->>API: POST report (completed)
    API->>DB: UPDATE render
    API->>FE: SSE completed + preview URL
    FE->>U: 渲染完成通知
```

---

## 2. 技術堆疊總表

| 層 | 技術 | 版本 | 理由 |
|---|---|---|---|
| 前端框架 | Next.js (App Router) | 14.x | React 18 框架、路由清晰、SSR 可選 |
| UI | Tailwind CSS + shadcn/ui | 3.x / latest | 開發速度快、Mockup 已用 Tailwind |
| 狀態管理 | Zustand（全域）+ TanStack Query（API 快取） | 4.x / 5.x | 比 Redux 輕、SSE 整合容易 |
| 表單 | React Hook Form + Zod | 7.x / 3.x | 型別安全 |
| 即時推送 | Server-Sent Events (SSE) | — | 比 WebSocket 輕、HTTP 友善 |
| 檔案上傳 | 直傳 MinIO (presigned URL) | — | 不經 API，省頻寬 |
| 認證 | next-auth + Keycloak OIDC | 5.x | 公司 SSO |
| 後端 | FastAPI + Uvicorn | Python 3.11 | async、OpenAPI 自動產 |
| Task 排程 | Celery + Redis | 5.x / 7.x | 成熟穩定 |
| DB | PostgreSQL | 15 | JSON 欄位存 Style Schema |
| 物件儲存 | MinIO（或 S3） | latest | 可內網部署 |
| AI | Anthropic Claude Sonnet 4.6 | API | 支援 tool-use 結構化輸出 + Vision |
| Agent | Python 3.11 + PyO3 Rust FFI | — | 重幾何計算用 Rust 加速 |
| Agent 打包 | PyInstaller + Apple notarize | — | macOS .pkg |
| 監控 | Grafana + Loki + Prometheus | latest | 自架 |
| CI/CD | GitHub Actions + ArgoCD | — | — |
| 容器 | Docker + K8s | — | 後端部署 |

> **若堅持純 React（Vite 而非 Next.js）**：把「Next.js + next-auth」換成「Vite + React Router v6 + react-oidc-context」即可，其他不變。差別主要在路由與認證整合，不影響架構。

---

## 3. 前端（React / Next.js）詳細設計

### 3.1 目錄結構

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # 全域 layout（含 <QueryProvider>、側邊欄）
│   ├── page.tsx                  # → redirect to /dashboard
│   ├── (auth)/
│   │   └── login/page.tsx        # SSO 重導入口
│   ├── (app)/                    # 登入後的區塊
│   │   ├── layout.tsx            # Sidebar + 頂欄
│   │   ├── dashboard/page.tsx
│   │   ├── projects/
│   │   │   ├── page.tsx          # 列表
│   │   │   ├── new/page.tsx      # 新建（第 1 步：上傳）
│   │   │   └── [id]/
│   │   │       ├── page.tsx      # 專案詳情
│   │   │       └── spaces/[sid]/
│   │   │           ├── style/page.tsx   # 第 2 步：選風格
│   │   │           ├── config/page.tsx  # 第 3 步：渲染設定
│   │   │           └── result/[rid]/page.tsx
│   │   ├── styles/
│   │   │   ├── page.tsx          # 風格庫
│   │   │   └── [id]/edit/page.tsx
│   │   ├── queue/page.tsx        # 渲染佇列
│   │   ├── gallery/page.tsx      # 成果廊
│   │   ├── team/page.tsx         # 團隊管理
│   │   └── agent/page.tsx        # 本機 Agent 狀態
│   └── api/                      # Next.js API routes（僅 proxy、不放商業邏輯）
│       └── auth/[...nextauth]/route.ts
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── TopBar.tsx
│   │   └── Stepper.tsx
│   ├── upload/
│   │   ├── DwgDropzone.tsx       # 平面/立面上傳
│   │   └── UploadProgress.tsx
│   ├── style/
│   │   ├── StyleTabs.tsx         # 三 tab 切換
│   │   ├── PresetGrid.tsx
│   │   ├── TextStyleInput.tsx
│   │   ├── VisualStyleInput.tsx
│   │   └── SchemaPreview.tsx     # 顯示 AI 解析結果供微調
│   ├── render/
│   │   ├── RenderConfig.tsx
│   │   ├── CameraPicker.tsx      # 視角選擇
│   │   ├── QualitySelector.tsx
│   │   └── RenderJobCard.tsx     # 佇列中單張卡片（SSE 進度）
│   ├── gallery/
│   │   ├── RenderViewer.tsx      # 4K 圖檢視器
│   │   └── ShareDialog.tsx       # 7 天分享連結
│   ├── agent/
│   │   ├── AgentStatusBadge.tsx  # 右上角綠點
│   │   └── AgentDetails.tsx
│   └── ui/                       # shadcn/ui 元件
│       ├── button.tsx
│       ├── dialog.tsx
│       └── ...
│
├── lib/
│   ├── api.ts                    # axios instance + interceptor
│   ├── auth.ts                   # next-auth 設定
│   ├── sse.ts                    # EventSource wrapper，自動重連
│   ├── schemas/
│   │   ├── style.ts              # Zod schema = Style JSON Schema 的 TS 版
│   │   ├── render.ts
│   │   └── project.ts
│   └── constants.ts
│
├── stores/                       # Zustand stores
│   ├── useAuthStore.ts
│   ├── useProjectStore.ts        # 當前選中的 project/space
│   ├── useRenderQueueStore.ts    # 即時佇列（SSE 驅動）
│   └── useAgentStore.ts          # Agent 線上狀態
│
├── hooks/
│   ├── useRenderProgress.ts      # 訂閱特定 render 的 SSE
│   ├── usePresignedUpload.ts
│   └── useStyleParse.ts
│
├── public/
├── styles/globals.css
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### 3.2 狀態管理策略

| 資料類型 | 工具 | 為什麼 |
|---|---|---|
| 伺服器資料（projects, styles, renders） | **TanStack Query** | 快取、樂觀更新、refetch；避免手寫 loading/error |
| 全域 UI 狀態（側邊欄開合、當前專案） | **Zustand** | 輕、無樣板 |
| 表單 | **React Hook Form + Zod** | Style Schema 的型別可直接複用到表單驗證 |
| 即時狀態（render 進度、Agent 心跳） | **Zustand + SSE hook** | SSE 收到事件直接推到 store，所有訂閱組件自動更新 |
| 認證 | **next-auth session** | 無需手動管理 |

### 3.3 關鍵組件實作要點

#### 3.3.1 `DwgDropzone.tsx` — 直傳 MinIO

```tsx
export function DwgDropzone({ kind, onUploaded }: { kind: 'plan'|'elevation', onUploaded: (fileId: string) => void }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/acad': ['.dwg', '.dxf'] },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024,
    onDrop: async ([file]) => {
      // 1) 跟後端要 presigned URL
      const { url, fileId } = await api.post('/uploads/presign', {
        filename: file.name, contentType: file.type, kind,
      });
      // 2) 直傳 MinIO
      await axios.put(url, file, { onUploadProgress: ... });
      // 3) 通知後端落 DB
      await api.post('/uploads/complete', { fileId });
      onUploaded(fileId);
    },
  });
  // ... UI
}
```

重點：**DWG 檔不經過 FastAPI**（否則 100 MB 檔會吃爆 API 記憶體）。用 presigned URL 讓瀏覽器直接 PUT 到 MinIO。

#### 3.3.2 `useRenderProgress.ts` — SSE 訂閱

```ts
export function useRenderProgress(renderId: string) {
  const setProgress = useRenderQueueStore(s => s.setProgress);
  useEffect(() => {
    const es = new EventSource(`/api/renders/${renderId}/stream`, { withCredentials: true });
    es.addEventListener('progress', (e) => {
      const data = JSON.parse(e.data) as { status: string; percent: number; phase: string };
      setProgress(renderId, data);
    });
    es.addEventListener('completed', (e) => {
      const { previewUrl } = JSON.parse(e.data);
      setProgress(renderId, { status: 'completed', percent: 100, previewUrl });
      es.close();
    });
    es.onerror = () => {
      // 自動重連邏輯（內建於 EventSource，但錯超過 3 次切到 polling fallback）
    };
    return () => es.close();
  }, [renderId]);
}
```

#### 3.3.3 `SchemaPreview.tsx` — AI 解析結果可微調

AI 解析完 Style Schema 後，**一定要顯示給使用者確認**（參考 mockup 的「AI 解析出的參數（可微調）」區塊）。每個欄位（色溫、主色、地板、牆面…）都是可編輯的，存回後端。

```tsx
const form = useForm<StyleSchema>({
  resolver: zodResolver(StyleSchemaZ),
  defaultValues: parsedSchema,
});
```

### 3.4 環境變數（前端）

```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE=https://api.renderstudio.internal
NEXT_PUBLIC_MINIO_ENDPOINT=https://storage.renderstudio.internal
NEXTAUTH_URL=https://renderstudio.internal
NEXTAUTH_SECRET=...
KEYCLOAK_ISSUER=https://auth.company.internal/realms/company
KEYCLOAK_CLIENT_ID=renderstudio
KEYCLOAK_CLIENT_SECRET=...
```

---

## 4. 後端（FastAPI）詳細設計

### 4.1 目錄結構

```
backend/
├── app/
│   ├── main.py                   # FastAPI app + routers
│   ├── config.py                 # pydantic-settings
│   ├── db.py                     # SQLAlchemy session
│   ├── deps.py                   # get_current_user, get_db
│   ├── middleware/
│   │   └── auth.py               # OIDC token verify
│   ├── routers/
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── spaces.py
│   │   ├── uploads.py            # presigned URL
│   │   ├── style.py              # /style/parse/text, /style/parse/visual
│   │   ├── renders.py
│   │   ├── agents.py             # /agent/register, /agent/next-job, /agent/heartbeat
│   │   └── stream.py             # SSE endpoint
│   ├── models/                   # SQLAlchemy ORM
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── space.py
│   │   ├── file.py
│   │   ├── style.py
│   │   ├── render.py
│   │   └── agent.py
│   ├── schemas/                  # Pydantic I/O
│   │   ├── style.py              # StyleSchema（= TS 版同構）
│   │   └── ...
│   ├── services/
│   │   ├── storage.py            # MinIO presigned
│   │   ├── style_engine.py       # Claude 呼叫
│   │   ├── job_dispatcher.py     # 進 Redis queue
│   │   └── sse_broker.py         # 進度事件 pub/sub
│   └── tasks/                    # Celery
│       ├── celery_app.py
│       └── notifications.py      # Slack / email
├── alembic/                      # DB migrations
├── tests/
├── pyproject.toml                # poetry
├── Dockerfile
└── docker-compose.dev.yml
```

### 4.2 API 契約（主要端點）

| Method | Path | 說明 | Request | Response |
|---|---|---|---|---|
| POST | `/auth/session` | OIDC callback 換 session | `{ code, state }` | `{ accessToken, user }` |
| GET | `/projects` | 列 projects | — | `Project[]` |
| POST | `/projects` | 建 project | `{ name }` | `Project` |
| POST | `/projects/{id}/spaces` | 建 space | `{ name, planFileId, elevationFileId }` | `Space` |
| POST | `/uploads/presign` | 取 presigned URL | `{ filename, contentType, kind }` | `{ url, fileId, expiresAt }` |
| POST | `/uploads/complete` | 上傳完成回報 | `{ fileId }` | `{ ok: true }` |
| POST | `/spaces/{id}/parse` | 觸發 DXF 解析 | — | `{ jobId }` (非同步) |
| GET | `/spaces/{id}/parsed` | 取解析結果 | — | `ParsedPlan` |
| POST | `/style/parse/text` | 文字 → Schema | `{ description }` | `StyleSchema` |
| POST | `/style/parse/visual` | 圖 → Schema | multipart: images[] + description | `StyleSchema` |
| GET | `/styles` | 列風格庫 | `?kind=preset\|team` | `Style[]` |
| POST | `/styles` | 建風格 | `{ name, schema, kind }` | `Style` |
| POST | `/renders` | 建 render job | `{ spaceId, styleId, settings }` | `Render` |
| GET | `/renders` | 列 renders | `?status=&spaceId=` | `Render[]` |
| GET | `/renders/{id}` | 單筆 | — | `Render` |
| GET | `/renders/{id}/stream` | SSE 進度 | — | `text/event-stream` |
| POST | `/agent/register` | Agent 啟動註冊 | `{ machineName, osVersion, sketchupVersion, vrayVersion, gpu }` | `{ agentId, token }` |
| POST | `/agent/heartbeat` | 每 5s 心跳 | `{ agentId, cpu, gpu, diskFree }` | `{ ok }` |
| GET | `/agent/next-job` | Agent 長輪詢拿任務 | — | `Job \| null` |
| POST | `/agent/job/{id}/report` | Agent 回報進度 | `{ status, phase, percent, error? }` | `{ ok }` |
| POST | `/agent/job/{id}/output` | Agent 回報輸出檔 | `{ fileIds[] }` | `{ ok }` |

### 4.3 核心 Pydantic Schema

```python
# app/schemas/style.py
from pydantic import BaseModel, Field
from typing import Literal

HexColor = constr(pattern=r"^#[0-9A-Fa-f]{6}$")

class Material(BaseModel):
    type: str                    # oak, latex_paint, marble...
    finish: Literal["matte","satin","gloss"] = "matte"
    tone: Literal["light","medium","dark"] = "medium"
    color: HexColor | None = None

class Lighting(BaseModel):
    sun_kelvin: int = Field(..., ge=2500, le=10000)
    direction: Literal["N","NE","E","SE","S","SW","W","NW"]
    intensity: float = Field(..., ge=0, le=3)
    ambient: Literal["soft","hard","overcast","golden-hour"]

class Camera(BaseModel):
    type: Literal["eye-level","axonometric","aerial","custom"]
    fov: int = 50
    height_mm: int = 1600

class StyleSchema(BaseModel):
    color_palette: list[HexColor] = Field(..., min_length=3, max_length=5)
    floor: Material
    wall: Material
    ceiling: Material
    lighting: Lighting
    furniture_language: Literal["nordic-minimal","wabi-sabi","industrial","modern","luxury","american-country","french"]
    camera: Camera
```

### 4.4 Style Engine 關鍵程式（Claude 呼叫）

```python
# app/services/style_engine.py
from anthropic import AsyncAnthropic
from app.schemas.style import StyleSchema

client = AsyncAnthropic()

STYLE_TOOL = {
    "name": "emit_style",
    "description": "Return a concrete StyleSchema based on the user's description.",
    "input_schema": StyleSchema.model_json_schema(),
}

async def parse_text_style(description: str) -> StyleSchema:
    resp = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[STYLE_TOOL],
        tool_choice={"type": "tool", "name": "emit_style"},
        messages=[{
            "role": "user",
            "content": f"將以下室內設計描述轉為 StyleSchema。只從 enum 值中選擇，不要自創。描述：\n{description}",
        }],
    )
    tool_use = next(b for b in resp.content if b.type == "tool_use")
    return StyleSchema(**tool_use.input)
```

---

## 5. Agent（Python）詳細設計

### 5.1 目錄結構

```
agent/
├── renderstudio_agent/
│   ├── __main__.py               # entry: poll loop
│   ├── config.py
│   ├── api_client.py             # 與後端通訊
│   ├── poller.py                 # long-poll 取任務
│   ├── state_machine.py          # Job 狀態轉換
│   ├── parsers/
│   │   ├── dxf_parser.py         # 主入口（ezdxf）
│   │   ├── dwg_converter.py      # 呼叫 ODA File Converter
│   │   ├── wall_extractor.py
│   │   ├── door_window.py
│   │   ├── room_detector.py      # 找封閉迴圈
│   │   └── plan_elevation_merge.py
│   ├── sketchup/
│   │   ├── controller.py         # subprocess 開 SketchUp
│   │   ├── ruby_scripts/
│   │   │   ├── generate_model.rb
│   │   │   ├── apply_materials.rb
│   │   │   ├── place_furniture.rb
│   │   │   └── render.rb
│   │   └── asset_sync.py         # 同步公司材質庫
│   ├── vray/
│   │   ├── adapter.py            # V-Ray 6 參數映射
│   │   ├── presets/
│   │   │   ├── draft.json
│   │   │   ├── standard.json
│   │   │   └── premium.json
│   │   └── style_to_vray.py
│   ├── heartbeat.py
│   ├── diag_server.py            # http://localhost:9787/diag
│   └── utils.py
├── rust_geometry/                # PyO3 擴充（幾何計算熱點）
│   ├── Cargo.toml
│   └── src/lib.rs
├── installer/
│   ├── build_pkg.sh              # pyinstaller + pkgbuild
│   ├── launch_agent.plist        # ~/Library/LaunchAgents/
│   └── notarize.sh
├── tests/
├── pyproject.toml
└── README.md
```

### 5.2 主循環

```python
# renderstudio_agent/__main__.py
async def main():
    agent = await register_or_login()
    heartbeat_task = asyncio.create_task(heartbeat_loop(agent))
    diag_task = asyncio.create_task(start_diag_server())

    while True:
        try:
            job = await poll_next_job(agent)         # long-poll up to 30s
            if job:
                await execute_job(agent, job)
        except Exception as e:
            logger.exception("main loop error")
            await asyncio.sleep(5)
```

### 5.3 Job 狀態機

```
pending ─pull─▶ assigned ─dxf_ok─▶ parsing ─ok─▶ modeling ─ok─▶ material ─ok─▶ rendering ─ok─▶ completed
                    │                   │            │             │              │
                    └─ fail/timeout ─────────────────────────────────────────────▶ error
                    │
                    └─ user_cancel ────────────────────────────────────────────▶ cancelled
```

每個轉換都會 `POST /agent/job/{id}/report`，後端接到後 broker 成 SSE event 推給瀏覽器。

### 5.4 SketchUp 啟動（關鍵細節）

```python
# agent/sketchup/controller.py
def run_sketchup(ruby_script: str, args: dict, skp_out: Path):
    cmd = [
        "/Applications/SketchUp 2024/SketchUp.app/Contents/MacOS/SketchUp",
        "-RubyStartup", str(ruby_script),
    ]
    env = os.environ.copy()
    env["RS_ARGS_JSON"] = json.dumps(args)  # Ruby 從 ENV 讀
    env["RS_OUTPUT"] = str(skp_out)
    proc = subprocess.Popen(cmd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return_code = proc.wait(timeout=600)
    if return_code != 0:
        raise SketchUpError(proc.stderr.read().decode())
```

**重要**：SketchUp 在 macOS 上沒有官方 headless 模式。MVP 的做法是「只在使用者閒置 5 分鐘以上才跑」，且使用者可以手動暫停 Agent。v1.2 會探索用 `LSUIElement` 隱藏 dock icon。

---

## 6. 資料庫 Schema（Postgres）

```sql
-- users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','designer','viewer')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- projects
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  owner_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now(),
  archived_at TIMESTAMPTZ
);

-- spaces (客廳、主臥 etc)
CREATE TABLE spaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  plan_file_id UUID REFERENCES files(id),
  elevation_file_id UUID REFERENCES files(id),
  parsed_plan JSONB,  -- cache 解析結果
  created_at TIMESTAMPTZ DEFAULT now()
);

-- files (S3/MinIO 物件索引)
CREATE TABLE files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  s3_key TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('dwg','dxf','skp','png','exr','vrmat','ref_image','preview')),
  size_bytes BIGINT,
  sha256 TEXT,
  owner_id UUID REFERENCES users(id),
  uploaded_at TIMESTAMPTZ DEFAULT now()
);

-- styles
CREATE TABLE styles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('preset','team','personal')),
  schema_json JSONB NOT NULL,
  thumbnail_file_id UUID REFERENCES files(id),
  owner_id UUID REFERENCES users(id),  -- team/personal 才有
  created_at TIMESTAMPTZ DEFAULT now()
);

-- renders
CREATE TABLE renders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id UUID REFERENCES spaces(id),
  style_id UUID REFERENCES styles(id),
  settings JSONB NOT NULL,  -- { quality, resolution, camera, formats }
  status TEXT NOT NULL CHECK (status IN ('pending','assigned','parsing','modeling','material','rendering','completed','error','cancelled')),
  phase_percent INT DEFAULT 0,
  agent_id UUID REFERENCES agents(id),
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  error_message TEXT,
  output_file_ids UUID[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- agents
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  machine_name TEXT,
  os_version TEXT,
  sketchup_version TEXT,
  vray_version TEXT,
  gpu TEXT,
  last_heartbeat_at TIMESTAMPTZ,
  allow_foreign_jobs BOOLEAN DEFAULT true,
  token TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- audit_logs
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action TEXT NOT NULL,
  resource_type TEXT,
  resource_id UUID,
  ip INET,
  user_agent TEXT,
  at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_renders_status ON renders(status) WHERE status NOT IN ('completed','error','cancelled');
CREATE INDEX idx_renders_space ON renders(space_id);
CREATE INDEX idx_files_kind ON files(kind);
CREATE INDEX idx_agents_heartbeat ON agents(last_heartbeat_at);
```

---

## 7. 實作清單（按 Sprint）

> 每個 Sprint 約 2 週，3 人團隊（1 全端 + 1 後端/Agent + 1 Agent/DevOps）。

### Sprint 0 — 技術驗證（第 1～2 週）

目標：**證明技術鏈可行**。不寫 UI，只在終端機跑得出一張圖。

- [ ] 取得公司 SketchUp 2024 + V-Ray 6 的 macOS 授權（至少 1 台開發機）
- [ ] 安裝 ODA File Converter，驗證 DWG → DXF 成功
- [ ] Python 用 ezdxf 讀一張真實平面 DWG，印出 walls/doors/windows
- [ ] 寫 `generate_model.rb`：手動餵 JSON 進去，SketchUp 能自動建出正確牆體、門窗挖孔
- [ ] 寫 `render.rb`：在 SketchUp 內用 V-Ray Ruby API 觸發一張 1080p 渲染
- [ ] 端到端跑通：`python run_poc.py plan.dxf elevation.dxf style.json` → 產出 `output.png`
- [ ] 記錄每個階段的耗時（作為未來效能目標的 baseline）
- [ ] Claude API tool-use 驗證：文字 → StyleSchema JSON，確認 schema 正確、命中率 > 90%

**Gate：** PoC 腳本能跑通一張真實案子。若卡住 > 3 天需升級討論是否改方案。

### Sprint 1 — 骨架搭建（第 3～4 週）

目標：**上傳 → 看到一張假的渲染結果**（實際還沒真正渲染，用假圖）。

**前端（Frontend）**

- [ ] `pnpm create next-app` 建立專案
- [ ] 接 Keycloak SSO（next-auth）
- [ ] Tailwind + shadcn/ui 初始化
- [ ] 實作 Sidebar + TopBar layout
- [ ] `/dashboard` 頁（顯示 KPI 卡片）
- [ ] `/projects/new` 上傳頁（用 `DwgDropzone`）
- [ ] `/queue` 頁（顯示假的進行中 job 卡片）
- [ ] `/gallery` 頁（顯示假渲染結果）
- [ ] Zustand stores 骨架
- [ ] TanStack Query provider + mock API

**後端**

- [ ] FastAPI 專案骨架 + Dockerfile
- [ ] Postgres schema migration（alembic）
- [ ] `/auth/session` 驗 Keycloak JWT
- [ ] MinIO bucket 建好、presigned URL endpoint
- [ ] `POST /projects` / `GET /projects`
- [ ] `POST /spaces` / `GET /spaces/{id}`
- [ ] `POST /uploads/presign` / `POST /uploads/complete`
- [ ] 基礎 error handling + logging（structlog）

**DevOps**

- [ ] 本地 docker-compose：postgres + redis + minio + keycloak
- [ ] GitHub Actions：lint + test + build image
- [ ] 專案 monorepo 結構（pnpm workspace 或 turborepo）

**Gate：** 設計師能登入、建專案、上傳 DWG、看到檔案進 MinIO。

### Sprint 2 — 核心渲染流程（第 5～6 週）

目標：**真的能從 DWG 跑出真渲染圖**。

**Agent**

- [ ] Python 專案骨架
- [ ] `POST /agent/register` + token 儲存
- [ ] 心跳 loop（每 5 秒）
- [ ] Long-poll `/agent/next-job`
- [ ] DXF parser（整合 Sprint 0 的 PoC）
- [ ] SketchUp controller（subprocess）
- [ ] `generate_model.rb` 整合（吃 JSON）
- [ ] V-Ray 標準畫質 preset 整合
- [ ] `POST /agent/job/{id}/report` 進度回報
- [ ] 輸出 PNG 上傳回 MinIO + 回報 `output_file_ids`
- [ ] 錯誤處理與任務失敗回報

**後端**

- [ ] `POST /renders` 建 job + enqueue Redis
- [ ] `GET /agent/next-job` 從 queue pop
- [ ] `POST /agent/job/{id}/report` 更新 DB 狀態
- [ ] `GET /renders/{id}/stream` SSE 實作（用 `sse-starlette`）

**前端**

- [ ] `/queue` 改接真 SSE
- [ ] `RenderJobCard` 顯示真進度條、階段標記
- [ ] `/gallery/[id]` 顯示真渲染結果、下載按鈕
- [ ] 本機 Agent 狀態顯示（側邊欄右上角綠點）

**Gate：** 設計師從瀏覽器觸發一張真渲染，10～30 分內看到結果。

### Sprint 3 — 風格引擎（第 7～8 週）

目標：**三種風格輸入模式全上**。

**後端**

- [ ] Anthropic SDK 整合 + 環境變數
- [ ] `POST /style/parse/text` + prompt 範本
- [ ] `POST /style/parse/visual` 含多圖支援（Vision）
- [ ] StyleSchema 驗證與 clamp（AI 出界值自動修正）
- [ ] 預設風格庫 seed script（7 個基礎風）
- [ ] `/styles` CRUD
- [ ] Style cache（相同文字描述走 Redis cache 24hr）

**前端**

- [ ] `/projects/[id]/spaces/[sid]/style/` 頁 3-tab
- [ ] `PresetGrid` 接真 API
- [ ] `TextStyleInput`：輸入 → 呼叫 API → 顯示 `SchemaPreview`
- [ ] `VisualStyleInput`：多圖上傳 + 預覽
- [ ] `SchemaPreview`：色票/材質/燈光可編輯，表單綁 StyleSchema Zod

**Agent**

- [ ] 材質庫同步機制（啟動時從 MinIO pull）
- [ ] StyleSchema → V-Ray 參數的 adapter
- [ ] 家具擺放初版（固定位置，以房間類型判斷）

**Gate：** 設計師用文字描述、或拖一張 IG 圖，都能看到有合理風格的渲染結果。

### Sprint 4 — 封閉測試打磨（第 9～10 週）

目標：**讓 5 位真實設計師用**。

- [ ] Agent macOS .pkg 打包 + notarize
- [ ] 自動更新機制
- [ ] 診斷頁 `http://localhost:9787/diag`
- [ ] `/agent` 頁（Web 端看 Agent 狀態 / 設定）
- [ ] 團隊風格庫建立與分享
- [ ] 重新渲染（沿用 skp 模型，只重算材質燈光）
- [ ] 7 天分享連結（含水印、IP 限制）
- [ ] Slack 通知整合
- [ ] 所有畫質 preset（草圖 / 標準 / 精品）
- [ ] 錯誤頁面與 retry 流程
- [ ] 效能優化：第一次開啟頁面 < 2 秒 FCP
- [ ] CSAT 問卷站內 popover

### Sprint 5 — 上線（第 11 週）

- [ ] 全公司設計師登入測試
- [ ] 寫使用手冊（Notion / 公司 Wiki）
- [ ] 辦 45 分鐘 hands-on 訓練
- [ ] 監控告警（Grafana dashboard + PagerDuty）
- [ ] 備份機制（Postgres + MinIO 每日快照）
- [ ] 正式 launch + 首週貼身支援

---

## 8. 完整目錄結構（Monorepo）

```
renderstudio/
├── frontend/                     # Next.js 14
├── backend/                      # FastAPI
├── agent/                        # Python Agent
├── shared/
│   └── style_schema.json         # 三端共用的 JSON Schema（前端用 Zod gen、後端用 Pydantic、Agent 用 pydantic）
├── infra/
│   ├── docker-compose.dev.yml
│   ├── k8s/
│   │   ├── api.yaml
│   │   ├── worker.yaml
│   │   ├── postgres.yaml
│   │   ├── redis.yaml
│   │   ├── minio.yaml
│   │   ├── keycloak.yaml
│   │   └── ingress.yaml
│   └── terraform/                # 可選：若用公有雲
├── docs/
│   ├── PRD.md
│   ├── TechSpec.md
│   ├── Implementation.md         # 本檔
│   ├── Runbook.md                # 值班手冊
│   └── ADR/                      # Architecture Decision Records
│       ├── 001-hybrid-architecture.md
│       ├── 002-nextjs-over-vite.md
│       └── 003-celery-over-rq.md
├── .github/workflows/
├── pnpm-workspace.yaml           # 若前端用 pnpm
├── Makefile
└── README.md
```

---

## 9. 測試策略

| 層級 | 工具 | 重點 |
|---|---|---|
| 前端單元 | Vitest + React Testing Library | Zod schema、hooks、小元件 |
| 前端 E2E | Playwright | 登入 → 上傳 → 渲染完整流程 |
| 後端單元 | pytest | style parser、API handler、DB repository |
| 後端整合 | pytest + testcontainers | 真 Postgres + MinIO |
| Agent | pytest + 真 DWG 測試檔 | DXF 解析的 golden files |
| 端到端 | Playwright + 真 Agent（staging） | 每次 release 前跑 |

### Golden Files

準備 10 組真實的 DWG 測試檔（包含乾淨與髒資料），每個配對：
- 預期解析出來的 JSON（walls/doors/windows 數量、面積）
- 預期的 .skp 檔特徵（頂點數、面數範圍）

Agent 解析出的結果 diff > 10% 就 fail CI。

---

## 10. 環境變數總表

### 後端

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/renderstudio
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
MINIO_BUCKET=renderstudio
ANTHROPIC_API_KEY=sk-ant-...
KEYCLOAK_ISSUER=https://auth.company.internal/realms/company
KEYCLOAK_AUDIENCE=renderstudio
SSE_KEEPALIVE_SECONDS=15
JOB_LONG_POLL_TIMEOUT=30
```

### Agent

```bash
# ~/Library/Application Support/RenderStudio/.env
RS_API_BASE=https://api.renderstudio.internal
RS_AGENT_TOKEN=...                 # 首次註冊時存入
SKETCHUP_APP=/Applications/SketchUp 2024/SketchUp.app
VRAY_VERSION=6.2
IDLE_BEFORE_RUN_SECONDS=300        # 使用者閒置 5 分才跑
ALLOW_FOREIGN_JOBS=true
```

---

## 11. 部署（公司內網 K8s）

```
kubectl apply -f infra/k8s/
```

最小配置：

| 服務 | replicas | CPU/RAM | 備註 |
|---|---|---|---|
| api | 2 | 1 / 2Gi | HPA 依 CPU |
| worker | 2 | 0.5 / 1Gi | Celery |
| postgres | 1 (managed) | 2 / 4Gi | RDS / CloudSQL 或 on-prem |
| redis | 1 | 0.5 / 1Gi | — |
| minio | 3 | 1 / 2Gi | HA 模式 |
| keycloak | 2 | 1 / 2Gi | — |
| frontend | 2 | 0.5 / 1Gi | Next.js node server |

Ingress：`renderstudio.internal.company.com` → frontend
`api.renderstudio.internal` → api
`storage.renderstudio.internal` → minio

---

## 12. 未來擴充（v1.1+，先不做但留口）

- 跨機器渲染排程：Agent `allow_foreign_jobs` 欄位已預留
- Chaos Cloud fallback：加一個 `rendering_target` 欄位到 render settings
- 業主互動連結：extend `files` 表加 `share_tokens`
- Revit / Rhino：新增 parser 類別、不改架構
- 整合 ERP：暴露 webhook（render 完成時推到企業系統）

---

## 13. 風險與備援方案

| 風險 | 備援 |
|---|---|
| SketchUp Ruby API break 升級 | Agent 版本鎖 SketchUp 2024；升級前在 staging 跑 regression |
| Claude API 斷線 | rule-based fallback parser（關鍵字匹配預設風格） |
| Agent 全數離線 | Web UI 可接 Chaos Cloud fallback（v1.2） |
| 後端 DB 掛 | MinIO + Redis 快照；Agent 本地 queue 可撐 4 小時 |
| 使用者端 V-Ray 授權失效 | Agent 啟動時驗證，失效則在 Web 端顯示紅色警示，禁止提交新 render |

---

## 14. 總結：開工順序

1. **Week 1-2**：Sprint 0 PoC，三人團隊一起撞到第一張渲染圖能跑通
2. **Week 3-4**：Sprint 1 骨架，確立前後端協定
3. **Week 5-6**：Sprint 2 真渲染流程貫通
4. **Week 7-8**：Sprint 3 風格引擎，讓「選風格」這件事真正可用
5. **Week 9-10**：Sprint 4 封測，修 bug、打磨體驗
6. **Week 11**：Sprint 5 上線、帶訓練

**判斷工作是否完成的唯一標準**：Lisa（資深）與 Kevin（資淺）都能在不請教工程師的情況下，從他們自己的 Mac 瀏覽器把一個真實案子跑出至少 3 張達標的渲染圖，並給業主分享連結。

---

> 文件結束。任何問題或要細化某個 Sprint、某個元件，告訴我要展開哪個。
