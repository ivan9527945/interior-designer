import { AgentStatusBadge } from "../agent/AgentStatusBadge";

// Sprint 5 Suspense 審查：
// AgentStatusBadge 為 "use client" 元件，內部透過 Zustand store 同步讀取
// Agent 連線狀態（無 async/await、無 use()、無 Server Component 資料串流），
// 因此此處無需加 <Suspense> boundary。
// 若未來引入非同步使用者資料元件（如 UserAvatar、NotificationBell），
// 請在該元件外層加上 <Suspense fallback={<span />}>。

export function TopBar() {
  return (
    <header className="flex h-14 items-center justify-between border-b px-6">
      <div className="text-sm text-muted-foreground">
        RenderStudio · Sprint 1 skeleton
      </div>
      <div className="flex items-center gap-3">
        <AgentStatusBadge />
      </div>
    </header>
  );
}
