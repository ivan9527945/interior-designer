import { AgentStatusBadge } from "../agent/AgentStatusBadge";

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
