# RenderStudio Frontend

Next.js 14 App Router + Tailwind + shadcn/ui + Zustand + TanStack Query + next-auth v5 beta.

## Dev

```bash
pnpm install
cp .env.example .env.local
pnpm --filter frontend dev
```

OPEN http://localhost:3000 → 自動 redirect 到 `/dashboard`。

## 主要路由

- `/dashboard`、`/projects`、`/styles`、`/queue`、`/gallery`、`/team`、`/agent`
- `/projects/new`（上傳）
- `/projects/[id]/spaces/[sid]/{style,config,result/[rid]}`
- `/login`、`/api/auth/[...nextauth]`
