"use client";

import { useAgentStore } from "@/stores/useAgentStore";

export function AgentStatusBadge() {
  const online = useAgentStore((s) => s.online);
  return (
    <div className="flex items-center gap-2 text-sm">
      <span
        className={`inline-block h-2 w-2 rounded-full ${online ? "bg-emerald-500" : "bg-gray-400"}`}
      />
      <span className="text-muted-foreground">Agent {online ? "線上" : "離線"}</span>
    </div>
  );
}
